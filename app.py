```python
import streamlit as st
import pandas as pd
from google import genai # Menggunakan pustaka Google yang baru

# 1. Konfigurasi Tampilan Halaman
st.set_page_config(page_title="AI Kinerja Region 5", page_icon="✨", layout="wide")

st.title("✨ AI Assistant: Kinerja Region 5 Bandar Lampung")
st.markdown("Tanyakan apa saja terkait pencapaian, target, atau performa cabang (Kanca) berdasarkan data keragaan.")

# 2. Setup API Key Gemini
API_KEY = st.sidebar.text_input("Masukkan Google Gemini API Key Anda", type="password")

if API_KEY:
    # Inisialisasi client menggunakan format google-genai terbaru
    client = genai.Client(api_key=API_KEY)

    # 3. Membaca Data dari Excel
    @st.cache_data
    def load_data():
        df = pd.read_excel("Keragaan_Kanca_B_v29 21jun26.xlsx")
        return df

    try:
        df = load_data()
        st.sidebar.success("✅ File Data Keragaan berhasil dimuat!")
        data_text = df.to_csv(index=False)
    except FileNotFoundError:
        st.error("Gagal memuat file Excel. Pastikan file 'Keragaan_Kanca_B_v29 21jun26.xlsx' ada di folder yang sama.")
        st.stop()

    # 4. Inisialisasi Riwayat Percakapan
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. Kotak Input Chat
    if prompt := st.chat_input("Ketik pertanyaan Anda di sini... (Contoh: Siapa Kanca dengan performa terbaik?)"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Menyusun prompt dengan konteks data
        system_prompt = f"""
        Anda adalah AI Assistant profesional untuk menganalisis performa kinerja perbankan di Region 5 Bandar Lampung.
        Gunakan data berikut (dalam format CSV) untuk menjawab pertanyaan pengguna secara akurat.
        Gunakan bahasa Indonesia yang profesional. Buatlah tabel, list, atau poin-poin jika itu membantu memperjelas data.
        
        DATA KINERJA REGION 5:
        {data_text}
        
        Pertanyaan Pengguna: {prompt}
        """

        # 6. Meminta Gemini menjawab (Format Baru)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Menganalisis data kinerja..."):
                    # Cara pemanggilan model versi terbaru
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=system_prompt,
                    )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses dari AI: {e}")
else:
    st.info("👈 Silakan masukkan API Key Gemini di sidebar sebelah kiri untuk mulai menggunakan chat box.")
