import requests

def hava_durumu_getir(sehir):
    API_KEY = "YOUR_API_KEY_HERE"  # 🔑 Buraya kendi OpenWeather API anahtarını yaz
    url = f"https://api.openweathermap.org/data/2.5/weather?q={sehir}&appid={API_KEY}&units=metric&lang=tr"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            print(f"\n🌆 Şehir: {data['name']}")
            print(f"🌡️ Sıcaklık: {data['main']['temp']}°C")
            print(f"☁️ Hava Durumu: {data['weather'][0]['description'].capitalize()}")
            print(f"💨 Rüzgar Hızı: {data['wind']['speed']} m/s")
            print(f"💧 Nem Oranı: {data['main']['humidity']}%")
        elif response.status_code == 404:
            print("⚠️ Şehir bulunamadı. Lütfen doğru bir şehir adı girin.")
        else:
            print("❌ Bir hata oluştu:", data)
    except requests.exceptions.RequestException as e:
        print("🌐 Bağlantı hatası:", e)


def main():
    print("=== 🌦️ HAVA DURUMU UYGULAMASI ===")
    while True:
        sehir = input("\nŞehir adı girin (Çıkmak için 'q'): ").strip()
        if sehir.lower() == "q":
            print("Görüşürüz 👋")
            break
        hava_durumu_getir(sehir)


if __name__ == "__main__":
    main()
