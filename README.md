# HR Mülakat Asistanı

## Genel Bakış

**HR Mülakat Asistanı**, yapay zeka kullanarak iş görüşmelerini simüle etmek için tasarlanmış bir web uygulamasıdır. Google'ın **Gemini** üretken AI modelini kullanarak kişiselleştirilmiş mülakat soruları oluşturur ve aday yanıtlarını değerlendirerek, çeşitli iş rolleri için adayları etkili bir şekilde değerlendirmek amacıyla etkileşimli bir deneyim sunar.

## Kullanılan Model

Proje, **gemini-1.5-flash** modelini kullanmaktadır. Bu model, doğal dil işleme yetenekleri sayesinde, adayların yetkinliklerini, deneyimlerini ve iş pozisyonuna uygunluklarını değerlendirmek için mülakat soruları üretir. Adayın yanıtlarına dayanarak ek sorular da sorarak mülakat sürecini derinleştirir. Model, kullanıcı dostu bir deneyim sunmak için profesyonel ve dostane bir ton kullanır.

## Özellikler

- **Etkileşimli Sohbet Arayüzü**: Adayla gerçek zamanlı bir mülakat yapar.
- **Özelleştirilebilir İstekler**: Adayın iş rolü ve deneyimine göre mülakat sorularını kişiselleştirir.
- **Davranışsal Değerlendirme**: Kültürel uyum ve problem çözme becerilerini ölçmek için davranış temelli sorular içerir.
- **Oturum Geçmişi**: Sohbet geçmişini takip ederek gözden geçirme imkanı sağlar.

## Kullanılan Teknolojiler

- **Python**: Uygulamanın ana programlama dili.
- **Streamlit**: Python ile web uygulamaları oluşturmak için bir framework.
- **Google Generative AI**: Mülakat soruları ve yanıtları oluşturmak için Google'ın AI modelini kullanır.
- **dotenv**: API anahtarlarının güvenli bir şekilde saklanması için ortam değişkenlerini yönetir.

## Gereksinimler

Bu projeyi çalıştırmak için aşağıdaki araçların yüklü olduğundan emin olun:

- Python 3.7 veya üzeri
- Sanal ortam aracı (isteğe bağlı ama önerilir)

## Kurulum

1. Depoyu klonlayın:

   ```bash
   git clone https://github.com/eyupaydin41/hr.git
   cd hr
2. Bir sanal ortam oluşturun ve etkinleştirin:

    ```bash
    # Sanal ortamı etkinleştirin
    python -m venv .venv
    
    # Windows
    .venv\Scripts\activate
    
    # macOS/Linux
    source .venv/bin/activate
3. Gerekli paketleri yükleyin:

    ```bash
    pip install -r requirements.txt
4. Ana dizinde bir **.env** dosyası oluşturun ve Google API anahtarınızı ekleyin:

    ```bash
    GOOGLE_API_KEY=api_anahtarınız
5. Uygulamayı çalıştırın:

    ```bash
    streamlit run app.py
