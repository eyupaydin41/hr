import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

from googlecloud_tts import text_to_speech 

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

pre_prompt = (
    """
    Bu konuşmada insan kaynakları rolünü üstleneceksin. Adayın yetkinliklerini, deneyimlerini ve işe uygunluğunu değerlendirmek için mülakat yapar gibi sorular soracaksın. İşe alım sürecinde olduğunuzu düşünerek adayın başvurduğu pozisyona uygun olup olmadığını anlamaya çalış.
    İlk olarak, adayın genel iş deneyimi, teknik becerileri ve projeleri hakkında sorular sor. 
    Adayın takım çalışması, problem çözme yetenekleri ve zorlayıcı durumlarla başa çıkma becerileri ile ilgili detaylı sorular yönelt. 
    Pozisyona uygunluğu konusunda daha fazla bilgi edinmek için adayın kariyer hedeflerini ve uzun vadeli planlarını sorgula. 
    Özellikle adayın bu pozisyona ve şirket kültürüne uygunluğunu değerlendirmeye yönelik davranışsal sorular sorarak cevaplarını analiz et.
    Yanıtlarını verirken profesyonel ve dostane bir ton kullan. Adayın verdiği yanıtlara göre ek sorularla mülakatı derinleştir ve uygunluğunu değerlendir.
    """
)

generation_config = {
    "candidate_count": 1,                      # Üretilen yanıt sayısı
    "max_output_tokens": 2048,                 # Maksimum çıktı token sayısı
    "temperature": 0.7,                        # Çıktının rastgeleliğini kontrol eder
    "top_p": 0.85,                             # Nucleus sampling için maksimum kümülatif olasılık
    "top_k": 40,                               # Sampling için maksimum token sayısı
}

safety_settings = {
    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

if "chat" not in st.session_state:
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    user_role = st.text_input("Lütfen rolünüzü giriniz:")
    user_name = st.text_input("Adayın adını giriniz:")

    if user_role and user_name:
        custom_pre_prompt = pre_prompt + f"\nAdayın başvurduğu pozisyon: {user_role}\nAdayın adı: {user_name}"
        st.session_state.chat = model.start_chat()
        response = st.session_state.chat.send_message(
            content=custom_pre_prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

input_prompt = st.text_input("Mülakat sorusu girin:")

if st.button("Generate") and input_prompt:
    response = st.session_state.chat.send_message(
        content=input_prompt,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
        
    st.write(response.text)
    st.write(st.session_state.chat.history)

    audio_stream = text_to_speech(response.text)
    st.audio(audio_stream, format="audio/mp3")
