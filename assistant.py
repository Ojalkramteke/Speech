from dotenv import load_dotenv
import os
import pyttsx3
import webbrowser
import subprocess
import ctypes
import requests

# Load .env variables
load_dotenv()

# Text-to-speech engine setup
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

def speak(text):
    """Use text-to-speech to speak text"""
    engine.say(text)
    engine.runAndWait()

def search_web(query, platform):
    """Searches Google, YouTube, or Maps"""
    search_engines = {
        "google": f"https://www.google.com/search?q={query}",
        "youtube": f"https://www.youtube.com/results?search_query={query}",
        "maps": f"https://www.google.com/maps/search/{query}",
    }
    if platform in search_engines:
        webbrowser.open(search_engines[platform])
        speak(f"Searching {platform} for {query}")

def open_application(app_name):
    """Opens an application based on name"""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "vs code": "C:\\Users\\praja\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "clock": "ms-clock:",
        "alarms": "ms-clock:alarms",
    }

    if app_name in apps:
        try:
            if app_name in ["clock", "alarms"]:
                subprocess.Popen(["start", apps[app_name]], shell=True)
            else:
                subprocess.Popen([apps[app_name]])
            speak(f"Opening {app_name}")
        except Exception as e:
            speak(f"Sorry, I couldn't open {app_name}. Error: {e}")
    else:
        speak("Sorry, I couldn't find that application.")

def change_volume(action):
    """Control volume: increase, decrease, mute, unmute"""
    if action == "increase":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        speak("Volume increased")
    elif action == "decrease":
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
        speak("Volume decreased")
    elif action == "mute":
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        speak("Volume muted")
    elif action == "unmute":
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        speak("Volume unmuted")

def get_weather(city):
    """Get weather for a given city"""
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data["cod"] != 200:
            message = f"Couldn't fetch weather. Error: {data.get('message', 'Unknown error')}"
            speak(message)
            return message

        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = (
            f"The current temperature in {city} is {temp}°C, "
            f"with {weather_desc}. Humidity is {humidity}%, "
            f"and wind speed is {wind_speed} m/s."
        )
        speak(weather_info)
        return weather_info
    except Exception as e:
        error_message = f"There was an error retrieving the weather: {e}"
        speak(error_message)
        return error_message

def set_alarm():
    """Opens the alarm section in the clock app"""
    speak("Opening alarms")
    open_application("alarms")

def set_reminder():
    """Opens the reminder/clock app"""
    speak("Opening clock for reminder")
    open_application("clock")
