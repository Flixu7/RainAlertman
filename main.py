# -*- coding: utf-8 -*-
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Załaduj zmienne z pliku .env

# Dane z ENV
ACCOUNT_SID = os.environ["ACCOUNT_SID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
FROM = os.environ["FROM"]
TO = os.environ["TO"]
API_KEY = os.environ["API_KEY"]
CITY = os.environ["CITY"]

def get_weather():
    WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=pl"
    r = requests.get(WEATHER_URL)
    data = r.json()

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    wind = data["wind"]["speed"]
    humidity = data["main"]["humidity"]
    
    # Sprawdź czy pada deszcz (kod pogody 200-531 oznacza różne rodzaje deszczu)
    weather_id = data["weather"][0]["id"]
    is_rainy = 200 <= weather_id <= 531
    
    if is_rainy:
        # Pobierz informacje o opadach jeśli są dostępne
        rain_info = ""
        if "rain" in data:
            if "1h" in data["rain"]:
                rain_info = f"☔ Intensywność opadów: {data['rain']['1h']} mm/h"
            elif "3h" in data["rain"]:
                rain_info = f"☔ Intensywność opadów: {data['rain']['3h']} mm/3h"
        
        return {
            "is_rainy": True,
            "message": f"🌧️ ALERT DESZCZOWY dla {CITY}!\n\n🌡️ Temperatura: {temp}°C\n💧 Wilgotność: {humidity}%\n🌬️ Wiatr: {wind} m/s\n🌧️ {desc.capitalize()}\n{rain_info}\n\n☂️ Pamiętaj o parasolu!"
        }
    else:
        return {
            "is_rainy": False,
            "message": f"🌤️ Pogoda w {CITY}:\n🌡️ {temp}°C\n🌬️ Wiatr: {wind} m/s\n🌥️ {desc.capitalize()}"
        }

def send_whatsapp(message):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=FROM,
        to=TO
    )

if __name__ == "__main__":
    weather_data = get_weather()
    
    # Wysyłaj wiadomość tylko jeśli pada deszcz
    if weather_data["is_rainy"]:
        print("🌧️ Wykryto deszcz - wysyłam alert!")
        send_whatsapp(weather_data["message"])
    else:
        print("☀️ Brak deszczu - nie wysyłam powiadomienia")
        print(f"Obecna pogoda: {weather_data['message']}")
