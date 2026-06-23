import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. Konfigurasi Tampilan Halaman (UI mirip Gemini)
st.set_page_config(page_title="AI Kinerja Region 5", page_icon="✨", layout="wide")

st.title("✨ AI Assistant: Kinerja Region 5 Bandar Lampung")
st.markdown("Tanyakan apa saja terkait pencapaian, target, atau performa cabang (Kanca) berdasarkan data keragaan.")

# 2. Setup API Key Gemini
# API Key bisa diinput oleh user dari sidebar web
API_KEY = st.sidebar.text_input("Masukkan Google Gemini API Key Anda", type="password")

if API_KEY:
    # Inisialisasi koneksi ke Gemini
    genai.configure(api_key=API_KEY)
    
    # Menggunakan Gemini 1.5 Flash (Cocok untuk membaca jutaan teks/data Excel besar)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # 3. Membaca Data dari Excel
    @st.cache_data
    def load_data():
        # Membaca file excel keragaan
        df = pd.read_excel("Keragaan_Kanca_B_v29 21jun26.xlsx")
        return df

    try:
        df = load_data()
        st.sidebar.success("✅ File Data Keragaan berhasil dimuat!")
        
        # Mengubah data ke teks/CSV agar bisa dianalisis oleh AI
        data_text = df.to_csv(index=False)
        
    except FileNotFoundError:
        st.error("Gagal memuat file Excel. Pastikan file 'Keragaan_Kanca_B_v29 21jun26.xlsx' ada di folder yang sama.")
        st.stop()

    # 4. Inisialisasi Riwayat Percakapan (Memory)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Menampilkan riwayat chat sebelumnya di layar
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 5. Kotak Input Chat (UI Input)
    if prompt := st.chat_input("Ketik pertanyaan Anda di sini... (Contoh: Siapa Kanca dengan performa terbaik?)"):
        # Tampilkan pesan dari user
        st.chat_message("user").markdown(prompt)
        # Simpan ke riwayat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 6. Menyusun prompt untuk Gemini beserta konteks datanya
        system_prompt = f"""
        Anda adalah AI Assistant profesional untuk menganalisis performa kinerja perbankan/perusahaan di Region 5 Bandar Lampung.
        Gunakan data berikut (dalam format CSV) untuk menjawab pertanyaan pengguna secara akurat.
        Gunakan bahasa Indonesia yang profesional. Buatlah tabel, list, atau poin-poin jika itu membantu memperjelas data.
        Jika pengguna bertanya sesuatu yang datanya tidak ada di dokumen, katakan bahwa data tidak tersedia.
        
        DATA KINERJA REGION 5:
        {data_text}
        
        Pertanyaan Pengguna: {prompt}
        """

        # 7. Meminta Gemini menjawab & menampilkannya secara interaktif
        with st.chat_message("assistant"):
            try:
                # Membuat animasi loading saat AI berpikir
                with st.spinner("Menganalisis data kinerja..."):
                    response = model.generate_content(system_prompt)
                
                # Tampilkan hasil
                st.markdown(response.text)
                # Simpan jawaban AI ke riwayat
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses dari AI: {e}")
else:
    st.info("👈 Silakan masukkan API Key Gemini di sidebar sebelah kiri untuk mulai menggunakan chat box.")
