import streamlit as st
import os
from google import genai
from google.genai import types

# ==================== UI SETUP ====================
st.set_page_config(page_title="FitBite AI - Smart Order", page_icon="🥗", layout="centered")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("""
    <style>
    .stApp { background-color: #0b0f12 !important; color: #ffffff !important; }
    .info-card { background-color: #161c20; padding: 12px; border-radius: 10px; border: 1px solid #2e7d32; text-align: center; margin-bottom: 10px; }
    .welcome-box { background-color: #112214; padding: 20px; border-radius: 15px; border-left: 6px solid #4caf50; margin-top: 15px; margin-bottom: 20px; color: #e8f5e9; }
    h1, h2, h3, .stSubheader { color: #4caf50 !important; font-family: 'Kanit', sans-serif; }
    .stMultiSelect label, .stTextArea label, .stTextInput label, .stSelectbox label { color: #4caf50 !important; font-weight: bold !important; }
    .stMarkdown, p, li { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==================== HEADER ====================
st.title("🥗 FitBite AI")
st.markdown("### *Personalized Nutritionist & Smart Form Order*")

col_time, col_deliv = st.columns(2)
with col_time: st.markdown("<div class='info-card'><span style='color: #4caf50;'>🕒 เปิดบริการทุกวัน</span><br>09:00 น. - 18:00 น.</div>", unsafe_allow_html=True)
with col_deliv: st.markdown("<div class='info-card'><span style='color: #ff9800;'>🛵 รอบจัดส่งเดลิเวอรี</span><br>11:00 | 14:00 | 17:00</div>", unsafe_allow_html=True)
st.markdown("<div class='welcome-box'><strong>ก้าวใหม่ของการสั่งอาหารคลีน!</strong><br>กรอกรายละเอียดด้านล่าง AI จะช่วยสรุปบิล คำนวณแคลอรี่ และตรวจสอบภูมิแพ้ให้ทันทีค่ะ</div>", unsafe_allow_html=True)

# ==================== FORM ====================
st.subheader("📋 ฟอร์มสั่งซื้ออาหาร")
with st.container():
    col1, col2 = st.columns(2)
    with col1: customer_name = st.text_input("👤 ชื่อลูกค้า:")
    with col2: customer_phone = st.text_input("📞 เบอร์โทร:")

    mains = ["1. สลัดอกไก่ย่างพริกไทยดำ (119.-)", "2. ข้าวไรซ์เบอร์รี่ปลากระพงนึ่ง (149.-)", "3. พาสต้าโฮลวีทซอสเพสโต้กุ้ง (159.-)", "4. ข้าวหน้าเนื้อย่างยากินิกุ (169.-)", "5. ลาบเต้าหู้อีสานและคีนัว (เจ) (109.-)"]
    selected_mains = st.multiselect("🥗 เมนูหลัก:", mains)
    
    addons = ["เพิ่มอกไก่ย่าง (+40.-)", "เพิ่มแซลมอนย่าง (+89.-)", "เพิ่มไข่ต้ม (+15.-)", "เพิ่มอะโวคาโด (+35.-)", "เพิ่มเส้นบุกคาร์บ 0% (+25.-)"]
    selected_addons = st.multiselect("➕ ท็อปปิ้งเสริม:", addons)
    
    allergy = st.text_input("⚠️ อาหารที่แพ้ / ไม่กิน:")
    slot = st.selectbox("📦 รอบจัดส่ง:", ["รอบเช้า (11:00 น.)", "รอบบ่าย (14:00 น.)", "รอบเย็น (17:00 น.)"])
    address = st.text_area("📍 ที่อยู่จัดส่งแบบละเอียด:")

    if st.button("🛒 ยืนยันการสั่งซื้อ"):
        if not customer_name or not customer_phone or not selected_mains or not address:
            st.warning("กรุณากรอกชื่อ เบอร์โทร เมนู และที่อยู่ให้ครบถ้วนค่ะบอส!")
        else:
            prompt = f"ลูกค้า: {customer_name}\nเบอร์: {customer_phone}\nเมนู: {', '.join(selected_mains)}\nท็อปปิ้ง: {', '.join(selected_addons)}\nแพ้: {allergy}\nรอบส่ง: {slot}\nที่อยู่: {address}"
            st.session_state.chat_history = [{"role": "user", "text": prompt}]

# ==================== AI PROCESSING ====================
st.markdown("---")
api_key = os.environ.get("GOOGLE_API_KEY")

def get_kb():
    try:
        with open("fitbite_kb.txt", "r", encoding="utf-8") as f: return f.read()
    except: return "ไม่พบข้อมูลฐานความรู้"

if st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        if msg["role"] == "model":
            st.subheader("🧾 ใบเสร็จรับเงินและโภชนาการ")
            with st.chat_message("model"): st.markdown(msg["text"])

    if st.session_state.chat_history[-1]["role"] == "user":
        if api_key:
            client = genai.Client(api_key=api_key)
            sys_inst = f"คุณคือ FitBite AI สรุปบิลคำนวณราคารวม แคลอรี่รวม และตรวจสอบของแพ้\nคลังข้อมูล:\n{get_kb()}"
            with st.spinner("AI กำลังวิเคราะห์ข้อมูลและสรุปยอด..."):
                try:
                    res = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=st.session_state.chat_history[-1]["text"], 
                        config=types.GenerateContentConfig(system_instruction=sys_inst, temperature=0.2)
                    )
                    st.session_state.chat_history.append({"role": "model", "text": res.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {e}")
        else:
            st.error("กรุณาใส่ GOOGLE_API_KEY ในระบบหลังบ้านก่อนใช้งานครับ")

if user_chat := st.chat_input("พิมพ์สอบถามข้อมูลโภชนาการเพิ่มเติมตรงนี้ได้เลยค่ะ..."):
    st.session_state.chat_history.append({"role": "user", "text": user_chat})
    st.rerun()
