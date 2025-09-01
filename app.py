import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Ambil API Key dari st.secrets untuk keamanan.
# Anda perlu menaruh API Key di file .streamlit/secrets.toml
# Contoh:
# [secrets]
# gemini_api_key = "AIzaSy..."
try:
    API_KEY = st.secrets["gemini_api_key"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Harap pastikan Anda telah menempatkan 'gemini_api_key' di file `.streamlit/secrets.toml` Anda.")
    st.stop()

MODEL_NAME = 'gemini-1.5-flash'
genai.configure(api_key=API_KEY)

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah ahli Hukum. Konsultasikan apapun tentang hukum. Jawaban singkat dan Jelas. Tolak pertanyaan non-Hukum."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan Kasus Yang ingin dikonsultasikan."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

st.title("⚖️ Chatbot Ahli Hukum")
st.caption("Aplikasi ini dibuat menggunakan Google Gemini API dan Streamlit.")

# Inisialisasi sesi chat
if "chat" not in st.session_state:
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        st.session_state.chat = model.start_chat(history=INITIAL_CHATBOT_CONTEXT)
        st.session_state.messages = INITIAL_CHATBOT_CONTEXT.copy()
    except Exception as e:
        st.error(f"Kesalahan saat menginisialisasi model atau chat: {e}")
        st.stop()

# Tampilkan riwayat chat dari session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Tangani input pengguna
if prompt := st.chat_input("Apa kasus yang ingin Anda konsultasikan?"):
    # Tambahkan pesan pengguna ke riwayat dan tampilkan
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim pesan ke model Gemini
    with st.chat_message("model"):
        try:
            response = st.session_state.chat.send_message(prompt)
            if response and response.text:
                st.markdown(response.text)
                # Tambahkan balasan model ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
            else:
                st.markdown("Maaf, saya tidak bisa memberikan balasan.")
        except Exception as e:
            st.error(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
            st.warning("Penyebab: Masalah koneksi, API Key tidak valid, atau batas kuota terlampaui.")
