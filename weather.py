from flask import Flask, render_template, request
import requests
from datetime import datetime  # Anlık tarih ve saat için ekledik

app = Flask(__name__)

# Hava durumu simgeleri için URL'yi belirleyen fonksiyon
def get_icon_url(description):
    icon_map = {
        "açık hava": "01d",  # Güneşli
        "güneşli": "01d",  # Güneşli (alternatif açıklama)
        "az bulutlu": "02d",  # Hafif bulut
        "parçalı bulutlu": "03d",  # Orta bulut
        "çok bulutlu": "04d",  # Kapalı hava
        "hafif yağmurlu": "10d",  # Hafif yağmur
        "sağanak yağmurlu": "09d",  # Şiddetli yağmur
        "yağmurlu": "10d",  # Genel yağmurlu
        "fırtınalı": "11d",  # Fırtına
        "karlı": "13d",  # Karlı hava
        "sisli": "50d"  # Sisli
    }
    
    desc_lower = description.lower()  # Açıklamayı küçük harfe çevir
    icon_code = None

    # Açıklamanın içinde hangi kelime varsa ona göre simge seç
    for key in icon_map:
        if key in desc_lower:
            icon_code = icon_map[key]
            break

    if not icon_code:
        icon_code = "01d"  # Varsayılan olarak güneşli simgeyi yap

    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

# Hava durumu verisini OpenWeatherMap'ten almak için fonksiyon
def get_weather(city, district):
    try:
        location = f"{district},{city}" if district else city  # İlçe varsa ekle
        url = f"https://wttr.in/{location}?lang=tr&format=%C|%t|%w|%h|%P"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text.strip()
            parts = data.split("|")
            if len(parts) < 5:
                return None
            description = parts[0].strip()
            temperature = parts[1].strip()
            wind = parts[2].strip()
            humidity = parts[3].strip()  # Nem oranı
            precipitation = parts[4].strip()  # Yağış oranı
            icon_url = get_icon_url(description)
            return {
                "city": city,
                "district": district,
                "description": description,
                "temperature": temperature,
                "wind": wind,
                "humidity": humidity,  # Nem oranı
                "precipitation": precipitation,  # Yağış oranı
                "icon_url": icon_url
            }
        else:
            return None
    except Exception as e:
        print("Hata:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error_message = None
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Anlık tarih ve saat al

    if request.method == "POST":
        city = request.form["city"].strip()
        district = request.form["district"].strip()  # İlçe alanını al
        if not city:
            error_message = "Lütfen geçerli bir şehir adı girin."
        else:
            weather_data = get_weather(city, district)
            if not weather_data:
                error_message = "Şehir veya ilçe bulunamadı ya da hava durumu verisi alınamadı."
    
    return render_template("index.html", weather=weather_data, error=error_message, current_time=current_time)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
