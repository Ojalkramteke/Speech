from dotenv import load_dotenv
import os
import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import os
import subprocess
import smtplib
import ctypes
import requests
import pyautogui  # For simulating keyboard typing
import whisper
import tempfile
import sounddevice as sd
import scipy.io.wavfile



# Load the variables from .env
load_dotenv()

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)

API_KEY = os.getenv("API_KEY")  # Weather api key
BASE_URL = os.getenv("BASE_URL")  # Weather base url
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def speak(audio):
    """Speak out the given text."""
    engine.say(audio)
    engine.runAndWait()


def command():
    """Capture voice command from user."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            content = r.recognize_google(audio, language="en-in")
            print("You said:", content)
            return content.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected, try again.")
            return ""


def search_web(query, platform):
    """Searches Google, YouTube, or Maps based on the platform specified."""
    search_engines = {
        "google": f"https://www.google.com/search?q={query}",
        "youtube": f"https://www.youtube.com/results?search_query={query}",
        "maps": f"https://www.google.com/maps/search/{query}",
    }

    if platform in search_engines:
        webbrowser.open(search_engines[platform])
        speak(f"Searching {platform} for {query}")


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
            speak(f"Opening {app_name}")
        except Exception as e:
            print(f"Error opening {app_name}:", e)
            speak(f"Sorry, I couldn't open {app_name}")
    else:
        speak("Sorry, I couldn't find that application.")


def change_volume(action):
    """Control system volume."""
    if action == "increase":
        for _ in range(5):  # Increase volume by 5 steps
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume up
        speak("Volume increased")
    elif action == "decrease":
        for _ in range(5):  # Decrease volume by 5 steps
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # Volume down
        speak("Volume decreased")
    elif action == "mute":
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # Mute
        speak("Volume muted")
    elif action == "unmute":
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # Unmute (same key as mute)
        speak("Volume unmuted")


def get_weather(city):
    """Fetches weather data for a given city."""
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric"}
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        print("API Response:", data)  # Debugging line to check API response

        if data["cod"] != 200:
            speak(
                f"Sorry, I couldn't fetch the weather. Error: {data.get('message', 'Unknown error')}"
            )
            return

        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        weather_info = (
            f"The current temperature in {city} is {temp} degrees Celsius, "
            f"with {weather_desc}. The humidity is {humidity} percent, "
            f"and the wind speed is {wind_speed} meters per second."
        )
        print(weather_info)
        speak(weather_info)

    except Exception as e:
        print("Error fetching weather:", e)
        speak("There was an error retrieving the weather.")


# Nickname to email mapping
email_contacts = {
    "keshav": "prajapatikeshav497@gmail.com",
    "ojal": "odinson454@gmail.com",
    "cyril": "323keshav0012@dbit.in",
    "sandhya": "prajapatisandhya619@gmail.com",
    # Add more as needed
}


def send_email(to_email, subject, message):
    """Sends an email using SMTP."""
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    email_message = f"Subject: {subject}\n\n{message}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, email_message)
        server.quit()
        speak("Email has been sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)
        speak("Sorry, I couldn't send the email.")


def dictate_to_file(filename="dictation.txt"):
    """Dictates spoken words and writes them into a text file."""
    speak(
        "Start speaking. I will write everything you say into a file. Say 'stop dictation' to finish."
    )

    with open(filename, "a", encoding="utf-8") as file:
        while True:
            spoken_text = command()
            if "stop dictation" in spoken_text:
                speak("Dictation stopped. Your words have been saved.")
                break
            elif spoken_text:
                file.write(spoken_text + "\n")

# def dictate_with_whisper(filename="whisper_dictation.txt", duration=30):
#     """Records audio for a given duration and transcribes using Whisper."""
#     speak(f"Start speaking. I will record your voice for {duration} seconds.")
    
#     # Record audio
#     fs = 16000  # Sample rate
#     speak("Recording now...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#     sd.wait()
#     speak("Recording complete. Transcribing now...")

#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
#         scipy.io.wavfile.write(tmpfile.name, fs, recording)
#         audio_path = tmpfile.name

#     try:
#         model = whisper.load_model("medium")
#         result = model.transcribe(audio_path)
#         text = result["text"]

#         with open(filename, "a", encoding="utf-8") as f:
#             f.write(text + "\n")

#         print("Transcribed Text:", text)
#         speak("Transcription complete. The text has been saved.")
#     except Exception as e:
#         print("Error with Whisper transcription:", e)
#         speak("Sorry, there was a problem with transcription.")

# # LibreTranslate base URL
# LIBRETRANSLATE_URL = "https://libretranslate.com/translate"

# def translate_text(text, source_lang="en", target_lang="hi"):
#     try:
#         payload = {
#             "q": text,
#             "source": source_lang,
#             "target": target_lang,
#             "format": "text"
#         }
#         response = requests.post(LIBRETRANSLATE_URL, json=payload)  # Use json instead of data
#         print("Raw response text:", response.text)
#         response.raise_for_status()
#         return response.json()["translatedText"]
#     except Exception as e:
#         print("Translation error:", e)
#         return "Sorry, I couldn't translate that."

# # Example usage (optional)
# # translated = translate_text("Hello, how are you?", source_lang="en", target_lang="hi")
# # print("Translated:", translated)
# # speak(translated)

def set_alarm():
    """Open the Clock app to set an alarm."""
    speak("I'll open the Clock app where you can set your alarm.")
    open_application("alarms")


def set_reminder():
    """Open the Clock app to set a reminder."""
    speak("I'll open the Clock app where you can set your reminder.")
    open_application("clock")


def get_news():
    """Fetch top news headlines using News API."""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        print("Fetching news from:", url)  # Debug line
        response = requests.get(url)
        data = response.json()

        print("API Response Status:", data.get("status"))  # Debug
        if data["status"] != "ok":
            speak("Sorry, I couldn't fetch the news at the moment.")
            return

        articles = data.get("articles", [])[:5]
        if not articles:
            speak("No news articles were found.")
            return

        print("Top 5 Headlines:")  # Terminal output
        speak("Here are the top news headlines:")

        for i, article in enumerate(articles, 1):
            title = article.get("title", "No title available")
            print(f"{i}. {title}")  # This should now print
            speak(title)

    except Exception as e:
        print("Error fetching news:", e)
        speak("There was an error getting the news.")


def main_process():
    """Main function to process commands."""
    while True:
        request = command()

        if not request:
            continue  # Skip empty commands

        if "hello" in request or "hi" in request or "hey" in request:
            speak("Welcome! How can I assist you?")

        elif (
            "play music" in request
            or "play song" in request
            or "play a song" in request
        ):
            speak("Playing Music!")
            songs = [
                "https://www.youtube.com/watch?v=1G4isv_Fylg",
                "https://www.youtube.com/watch?v=pElk1ShPrcE",
                "https://www.youtube.com/watch?v=1cDoRqPnCXU",
            ]
            webbrowser.open(random.choice(songs))

        elif "time" in request:
            now_time = datetime.datetime.now().strftime("%H:%M")
            speak("Current time is " + now_time)

        elif "date" in request:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            speak("Today's date is " + now_date)

        elif "search google for" in request:
            search_query = request.replace("search google for", "").strip()
            if search_query:
                search_web(search_query, "google")

        elif "search youtube for" in request:
            search_query = request.replace("search youtube for", "").strip()
            if search_query:
                search_web(search_query, "youtube")

        elif "search maps for" in request or "search google maps for" in request:
            search_query = (
                request.replace("search maps for", "")
                .replace("search google maps for", "")
                .strip()
            )
            if search_query:
                search_web(search_query, "maps")

        elif "open" in request:
            app_name = request.replace("open", "").strip()
            open_application(app_name)

        elif "increase volume" in request:
            change_volume("increase")

        elif "decrease volume" in request:
            change_volume("decrease")

        elif "mute volume" in request:
            change_volume("mute")

        elif "unmute volume" in request:
            change_volume("unmute")

        elif "weather" in request or "what's the weather" in request:
            speak("Which city's weather would you like to know?")
            city = command()
            if city:
                get_weather(city)
            else:
                speak("I couldn't get the city name.")

        elif "send email" in request:
            speak("To whom should I send the email?")
            recipient_name = command()

            to_email = email_contacts.get(recipient_name)
            if not to_email:
                speak("I couldn't find that contact. Please try again.")
                continue

            speak("What should be the subject?")
            subject = command()
            if not subject:
                speak("Subject not recognized.")
                continue

            speak("What is the message?")
            message = command()
            if not message:
                speak("Message not recognized.")
                continue

            send_email(to_email, subject, message)

        elif "start dictation" in request or "dictate" in request:
            dictate_to_file()

        # elif "translate" in request:
        #     speak("What do you want to translate?")
        #     sentence = command()
        #     if not sentence:
        #         speak("I didn't catch that.")
        #         return

        #     speak("Which language do you want to translate to?")
        #     target_lang = command()

        #     lang_map = {
        #         "hindi": "hi",
        #         "marathi": "mr",
        #         "gujarati": "gu",
        #         "tamil": "ta",
        #         "telugu": "te",
        #         "bengali": "bn",
        #         "kannada": "kn",
        #         "english": "en",
        #         "urdu": "ur",
        #         "malayalam": "ml",
        #     }

        #     lang_code = lang_map.get(target_lang.lower())
        #     if not lang_code:
        #         speak("Sorry, I don't support that language yet.")
        #     else:
        #         translated = translate_text(sentence, source_lang="en", target_lang=lang_code)
        #         print("Translation:", translated)
        #         speak(f"The translated sentence is: {translated}")
        elif "set alarm" in request or "create alarm" in request:
            set_alarm()

        elif "set reminder" in request or "create reminder" in request:
            set_reminder()

        elif (
            "news" in request or "headlines" in request or "what's the news" in request
        ):
            get_news()

        elif "exit" in request or "stop" in request or "bye" in request:
            speak("Goodbye! See you soon.")
            break


if __name__ == "__main__":
    main_process()
