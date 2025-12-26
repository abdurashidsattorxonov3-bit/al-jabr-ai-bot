import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- SAHIFA SOZLAMALARI ---
st.set_page_config(page_title="Al-Jabr AI", page_icon="🎓")

# --- API SOZLAMALARI ---
API_KEY = "AIzaSyBOYwk2h1DUVClbXFDn4RVA_ZDmcxzMMgU"
genai.configure(api_key=API_KEY)


# --- MODELNI ANIQLASH ---
@st.cache_resource
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if "1.5-flash" in m: return genai.GenerativeModel(m)
        return genai.GenerativeModel(models[0])
    except:
        return None


model = get_working_model()

# --- YON PANEL (SIDEBAR) ---
# Rasm yuklash tugmasini shu yerga qo'yamiz, shunda u chat xalaqit bermaydi
with st.sidebar:
    st.title("⚙️ Boshqaruv")

    if st.button("ℹ️ Muallif haqida"):
        st.info("Salom, men Al-Jabr o'quvchisi Sattorxonov Abdurashid tomonidan yaratilganman ✔")

    st.divider()

    st.write("📸 **Rasm yuklash:**")
    uploaded_file = st.file_uploader("Rasmni tanlang", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Yuklangan rasm")

    if st.button("🗑 Chatni tozalash"):
        st.session_state.messages = []
        st.rerun()

# --- ASOSIY INTERFEYS ---
st.title("🤖 Al-Jabr Intellekti")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Xabarlarni ko'rsatish (Ular doim tepada bo'ladi)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"], width=300)

# --- YOZISH JOYI (CHINNI PASTDA) ---
# st.chat_input hech qanday column ichida emas, shuning uchun u eng pastga yopishadi
if prompt := st.chat_input("Savol yozing yoki rasm haqida so'rang..."):

    # 1. Foydalanuvchi xabarini ko'rsatish
    user_msg = {"role": "user", "content": prompt}
    img_data = None
    if uploaded_file:
        img_data = Image.open(uploaded_file)
        user_msg["image"] = img_data

    st.session_state.messages.append(user_msg)

    # Ekranda darhol ko'rsatish
    with st.chat_message("user"):
        st.markdown(prompt)
        if img_data: st.image(img_data, width=300)

    # 2. Bot javobi
    with st.chat_message("assistant"):
        try:
            # Internetdan rasm qidirish
            if any(s in prompt.lower() for s in ["rasmini ko'rsat", "rasm ber", "rasmini ber"]):
                q = prompt.lower().replace("rasmini ko'rsat", "").replace("rasm ber", "").replace("rasmini ber",
                                                                                                  "").strip()
                if not q: q = "lion"
                img_url = f"https://loremflickr.com/800/600/{q}"
                st.image(img_url, caption=f"{q} rasmi")
                res_text = f"Siz uchun {q} rasmini topdim!"

            # Rasm tahlili
            elif uploaded_file:
                response = model.generate_content([prompt, img_data])
                res_text = response.text

            # Matnli javob
            else:
                response = model.generate_content(prompt)
                res_text = response.text

            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})

        except Exception as e:
            st.error(f"Xatolik: {e}")

    # Sahifani yangilash shart emas, chat_input o'zi ishlaydi
