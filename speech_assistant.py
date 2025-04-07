from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import subprocess
import requests
import threading
import queue
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 175)
except Exception as e:
    print(f"Error initializing text-to-speech engine: {e}")
    engine = None

# API configurations
API_KEY = os.getenv("API_KEY")  # Weather API key
BASE_URL = os.getenv("BASE_URL")  # Weather base URL
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Queue for command processing
command_queue = queue.Queue()
response_queue = queue.Queue()


def speak(audio):
    """Speak out the given text."""
    if engine:
        try:
            engine.say(audio)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
    return audio


def process_command(request_text):
    """Process the command and return the response."""
    if not request_text:
        return "Sorry, I didn't catch that. Could you please repeat?"

    request_text = request_text.lower()
    response = ""

    try:
        if any(greeting in request_text for greeting in ["hello", "hi", "hey"]):
            response = speak("Welcome! How can I assist you?")

        elif "play music" in request_text or "play song" in request_text:
            response = speak("Playing Music!")
            songs = [
                "https://www.youtube.com/watch?v=1G4isv_Fylg",
                "https://www.youtube.com/watch?v=pElk1ShPrcE",
                "https://www.youtube.com/watch?v=1cDoRqPnCXU",
            ]
            webbrowser.open(random.choice(songs))

        elif "time" in request_text:
            now_time = datetime.datetime.now().strftime("%H:%M")
            response = speak(f"Current time is {now_time}")

        elif "date" in request_text:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            response = speak(f"Today's date is {now_date}")

        elif "search google for" in request_text:
            search_query = request_text.replace("search google for", "").strip()
            if search_query:
                search_web(search_query, "google")
                response = speak(f"Searching Google for {search_query}")

        elif "search youtube for" in request_text:
            search_query = request_text.replace("search youtube for", "").strip()
            if search_query:
                search_web(search_query, "youtube")
                response = speak(f"Searching YouTube for {search_query}")

        elif "search maps for" in request_text or "search google maps for" in request_text:
            search_query = (
                request_text.replace("search maps for", "")
                .replace("search google maps for", "")
                .strip()
            )
            if search_query:
                search_web(search_query, "maps")
                response = speak(f"Searching Maps for {search_query}")

        elif request_text.startswith("open "):
            app_name = request_text[5:].strip()
            response = open_application(app_name)

        elif "weather" in request_text or "what's the weather" in request_text:
            city = request_text.replace("weather", "").replace("what's the", "").strip()
            if city:
                response = get_weather(city)
            else:
                response = speak("I couldn't get the city name.")

        elif "set alarm" in request_text or "create alarm" in request_text:
            response = set_alarm()

        elif "set reminder" in request_text or "create reminder" in request_text:
            response = set_reminder()

        elif "news" in request_text or "headlines" in request_text or "what's the news" in request_text:
            response = get_news()

        else:
            response = speak("I'm not sure how to help with that. Can you try something else?")

    except Exception as e:
        print(f"Error processing command: {e}")
        response = speak("Sorry, I encountered an error processing your request.")

    return response


def search_web(query, platform):
    """Searches Google, YouTube, or Maps based on the platform specified."""
    search_engines = {
        "google": f"https://www.google.com/search?q={query}",
        "youtube": f"https://www.youtube.com/results?search_query={query}",
        "maps": f"https://www.google.com/maps/search/{query}",
    }

    if platform in search_engines:
        webbrowser.open(search_engines[platform])


def open_application(app_name):
    """Opens applications based on user command."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "vs code": "C:\\Users\\praja\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "clock": "ms-clock:",  # Windows Clock app
        "alarms": "ms-clock:alarms",  # Direct to alarms section
    }

    if app_name in apps:
        try:
            if app_name in ["clock", "alarms"]:
                subprocess.Popen(["start", apps[app_name]], shell=True)
            else:
                subprocess.Popen([apps[app_name]])
            return speak(f"Opening {app_name}")
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return speak(f"Sorry, I couldn't open {app_name}")
    return speak("Sorry, I couldn't find that application.")


def get_weather(city):
    """Fetches weather data for a given city."""
    if not API_KEY or not BASE_URL:
        return speak("Weather service is not configured properly.")

    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params, timeout=5)
        data = response.json()

        if data.get("cod") != 200:
            return speak(f"Sorry, I couldn't fetch the weather. Error: {data.get('message', 'Unknown error')}")

        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = (
            f"The current temperature in {city} is {temp} degrees Celsius, "
            f"with {weather_desc}. The humidity is {humidity} percent, "
            f"and the wind speed is {wind_speed} meters per second."
        )
        return speak(weather_info)

    except Exception as e:
        print(f"Error fetching weather: {e}")
        return speak("There was an error retrieving the weather.")


def set_alarm():
    """Open the Clock app to set an alarm."""
    return speak("I'll open the Clock app where you can set your alarm.")


def set_reminder():
    """Open the Clock app to set a reminder."""
    return speak("I'll open the Clock app where you can set your reminder.")


def get_news():
    """Fetch top news headlines using News API."""
    if not NEWS_API_KEY:
        return speak("News service is not configured properly.")

    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("status") != "ok":
            return speak("Sorry, I couldn't fetch the news at the moment.")

        articles = data.get("articles", [])[:5]  # Get top 5 articles
        if not articles:
            return speak("No news headlines available at the moment.")

        news_text = "Here are the top news headlines: "
        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title available")
            news_text += f"{i}. {title}. "

        return speak(news_text)

    except Exception as e:
        print(f"Error fetching news: {e}")
        return speak("There was an error getting the news.")


def recognize_speech():
    """Capture voice command from user."""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
            content = r.recognize_google(audio, language="en-in")
            print("You said:", content)
            return content.lower()
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.WaitTimeoutError:
        return "No speech detected, try again."
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return "There was an error processing your voice command."


def command_processor():
    """Process commands from the queue."""
    while True:
        command = command_queue.get()
        if command == 'exit':
            break
        response = process_command(command)
        response_queue.put(response)
        command_queue.task_done()


# Start the command processor thread
processor_thread = threading.Thread(target=command_processor)
processor_thread.daemon = True
processor_thread.start()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/process_command', methods=['POST'])
def handle_command():
    command_type = request.form.get('type', 'text')
    command_text = request.form.get('command', '').strip()

    if command_type == 'voice':
        command_text = recognize_speech()

    if command_text:
        command_queue.put(command_text)
        try:
            # Wait for response with timeout
            response = response_queue.get(timeout=10)
            return jsonify({'response': response})
        except queue.Empty:
            return jsonify({'response': "The assistant is taking too long to respond."})

    return jsonify({'response': "No command received"})


@app.route('/exit')
def exit_app():
    command_queue.put('exit')
    return "Assistant is shutting down..."


if __name__ == '__main__':
    app.run(debug=True, threaded=True)