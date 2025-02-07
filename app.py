import os
import uuid
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from googlecloud_tts import text_to_speech  # Opsiyonel: Sesli çıktı için kullanılabilir
import io

# PDF'den metin çıkarımı için (opsiyonel)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# .env dosyasından API anahtarını yükleyelim
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Gemini modeli – model adı ortamınıza göre uyarlanabilir
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Yanıt üretimi için ayarlar
generation_config = {
    "candidate_count": 1,
    "max_output_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.85,
    "top_k": 40,
}

# Güvenlik ayarları
safety_settings = {
    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

# Şirket tarafından oluşturulan mülakat oturumlarını saklamak için
if "company_sessions" not in st.session_state:
    st.session_state.company_sessions = {}

# URL'den query parametreleri alalım
query_params = st.query_params

# Eğer session_id varsa, otomatik olarak "Aday" arayüzünü gösterelim; yoksa kullanıcıya seçim şansı sunalım.
if query_params.get("session_id", [None])[0] is not None:
    user_type = "Aday"
else:
    user_type = st.sidebar.selectbox("Kullanıcı Tipi", ["Şirket", "Aday"])

#############################
# ŞİRKET (İnsan Kaynakları) Arayüzü
#############################
if user_type == "Şirket":
    st.header("Şirket (İnsan Kaynakları) Arayüzü")
    st.write("Aşağıdaki formu doldurarak bir mülakat oturumu oluşturabilirsiniz.")

    with st.form("company_form"):
        job_position = st.text_input("İş Pozisyonu")
        interview_duration = st.number_input("Mülakat Süresi (dakika)", min_value=1, value=30)
        num_sections = st.number_input("Mülakat Bölüm Sayısı", min_value=1, value=3)

        st.write("Her bölüm için detayları giriniz:")
        sections = []
        for i in range(int(num_sections)):
            st.markdown(f"**Bölüm {i+1}**")
            section_title = st.text_input(f"{i+1}. Bölüm Başlığı", key=f"sec_title_{i}")
            section_duration = st.number_input(f"{i+1}. Bölüm Süresi (dakika)", min_value=1, value=10, key=f"sec_duration_{i}")
            section_questions = st.text_area(f"{i+1}. Bölüme Özel Sorular", key=f"sec_questions_{i}")
            sections.append({
                "title": section_title,
                "duration": section_duration,
                "questions": section_questions,
            })

        interview_questions = st.text_area("Genel Röportaj Soruları (opsiyonel)")
        required_experience = st.number_input("Gerekli İş Deneyimi (yıl)", min_value=0, value=2)
        submitted = st.form_submit_button("Mülakatı Oluştur")

    if submitted:
        session_id = str(uuid.uuid4())
        st.session_state.company_sessions[session_id] = {
            "job_position": job_position,
            "interview_duration": interview_duration,
            "num_sections": int(num_sections),
            "sections": sections,
            "interview_questions": interview_questions,
            "required_experience": required_experience,
        }
        interview_link = f"http://localhost:8513/?session_id={session_id}"
        st.success("Mülakat oturumu oluşturuldu!")
        st.write("Adaylara gönderilecek link:")
        port = st.get_option("server.port")  # Streamlit'in çalıştığı portu alır
        st.markdown(f"[Mülakata Git](http://localhost:{port}/?session_id={session_id})", unsafe_allow_html=True)


#############################
# ADAY Arayüzü
#############################
elif user_type == "Aday":
    st.header("Aday Arayüzü")

    # Oturum ID'sini URL query parametresi üzerinden alalım
    query_params = st.query_params
    session_id = query_params.get("session_id", [None])[0]
    if session_id is None:
        session_id = st.text_input("Mülakat Oturum Numarası (session_id)", value="")

    candidate_name = st.text_input("Adınız ve Soyadınız")
    st.write("Lütfen CV'nizi yükleyiniz (PDF veya TXT formatında):")
    cv_file = st.file_uploader("CV Yükle", type=["pdf", "txt"])

    if cv_file is not None and candidate_name:
        # CV içeriğini metin olarak çıkaralım
        if cv_file.type == "text/plain":
            cv_text = cv_file.read().decode("utf-8")
        elif cv_file.type == "application/pdf":
            if PyPDF2 is not None:
                pdf_reader = PyPDF2.PdfReader(cv_file)
                cv_text = ""
                for page in pdf_reader.pages:
                    cv_text += page.extract_text()
            else:
                st.error("PDF dosyalarını işleyebilmek için PyPDF2 kütüphanesi kurulmalı.")
                cv_text = ""
        else:
            cv_text = ""
        
        st.subheader("CV Analizi ve Mülakat Hazırlığı")
        st.write("CV'niz analiz ediliyor...")

        if session_id and session_id in st.session_state.company_sessions:
            sections_info = ""
            for idx, sec in enumerate(st.session_state.company_sessions[session_id]["sections"]):
                sections_info += f"\nBölüm {idx+1} - Başlık: {sec['title']}\n"
                sections_info += f"Süre: {sec['duration']} dakika\n"
                sections_info += f"Özel Sorular: {sec['questions']}\n"
            
            company_info = f"""
            **Şirket Tarafından Belirlenen Mülakat Kriterleri:**
            - İş Pozisyonu: {st.session_state.company_sessions[session_id]['job_position']}
            - Toplam Mülakat Süresi: {st.session_state.company_sessions[session_id]['interview_duration']} dakika
            - Genel Röportaj Soruları: {st.session_state.company_sessions[session_id]['interview_questions']}
            - Gerekli İş Deneyimi: {st.session_state.company_sessions[session_id]['required_experience']} yıl
            - Bölüm Bilgileri: {sections_info}
            """
        else:
            company_info = "Şirket kriterleri bulunamadı. Genel bir mülakat hazırlanacaktır."
        
        # ÖNEMLİ: Pre Prompt'ı adayın CV'si ve şirket bilgilerine göre ayarlıyoruz.
        candidate_pre_prompt = f"""
        Adayın adı: {candidate_name}
        Adayın CV'si:{cv_text}

        Şirket bilgileri: {company_info}

        Bu mülakatta, insan kaynakları rolünü üstlenerek adayın yetkinliklerini, deneyimlerini ve pozisyona uygunluğunu değerlendireceksin.
        Lütfen adayın cevabını inceledikten sonra yalnızca **tek bir soru** sorarak devam et. 
        Adayın yanıtına göre bir sonraki soruyu belirle ve ek soru sormadan önce adayın cevabını bekle.
        Yanıtlarını verirken profesyonel ve dostane bir ton kullan. Adayın verdiği yanıtlara göre ek sorularla mülakatı derinleştir ve uygunluğunu değerlendir.
        Mülakat dışına çıkılmamasına dikkat et, aday bunu denediğinde mülakata geri dönmesini sağla.
        """
        st.write("Mülakat başlatılıyor...")

        # Eğer henüz bir chat oturumu başlatılmadıysa, pre prompt ile sohbeti başlatıyoruz.
        if candidate_name and "chat_candidate" not in st.session_state:
            st.session_state.chat_candidate = model.start_chat()
            st.session_state.chat_candidate.send_message(
                content=candidate_pre_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            # İlk mesajı insan kaynakları rolüyle gönderiyoruz.
            initial_message = f"Merhaba {candidate_name}, mülakata hoş geldiniz. Lütfen kendinizi tanıtarak başlayın."
            st.write("### Mülakat Başlangıç Mesajı (İK Tarafından)")
            st.write(initial_message)
        
        # Aday yanıtını alıp sohbeti güncelliyoruz.
        candidate_input = st.text_input("Cevabınızı yazınız:")
        if st.button("Gönder") and candidate_input:
            response = st.session_state.chat_candidate.send_message(
                content=candidate_input,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            st.write("### İK'nın Sorusu:")
            st.write(response.text)
            # Opsiyonel: Yanıtı sesli dinlemek için
            # audio_stream = text_to_speech(response.text)
            # st.audio(audio_stream, format="audio/mp3")
