import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Select voice
engine.setProperty("rate", 175)  # Adjust speech rate


def speak(audio):
    """Speak out the given text."""
    engine.say(audio)
    engine.runAndWait()


def command():
    """Capture voice command from user."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = r.listen(source, timeout=5)  # Increased timeout
            content = r.recognize_google(audio, language="en-in")
            print("You said:", content)
            return content.lower()
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected, try again.")
            return ""


def search_google(query):
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)


def search_youtube(query):
    search_url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(search_url)


def search_google_maps(query):
    search_url = f"https://www.google.com/maps/search/{query}"
    webbrowser.open(search_url)


def main_process():
    """Main function to process commands."""
    while True:
        request = command()

        if "hello" in request:
            speak("Welcome, how can I help you?")

        elif "play music" in request:
            speak("Playing Music!")
            songs = [
                "https://www.youtube.com/watch?v=1G4isv_Fylg",
                "https://www.youtube.com/watch?v=pElk1ShPrcE",
                "https://www.youtube.com/watch?v=1cDoRqPnCXU",
            ]
            webbrowser.open(random.choice(songs))

        elif "say time" in request:
            now_time = datetime.datetime.now().strftime("%H:%M")
            speak("Current time is " + now_time)

        elif "say date" in request:
            now_date = datetime.datetime.now().strftime("%d-%m-%Y")
            speak("Today's date is " + now_date)

        elif "open google and search" in request:
            if "search" in request:
                search_query = request.split("open google and search")[-1].strip()
                search_google(search_query)
                speak(f"Searching Google for {search_query}")

        elif "open youtube and search" in request:
            if "search" in request:
                search_query = request.split("open youtube and search")[-1].strip()
                search_youtube(search_query)
                speak(f"Searching Youtube for {search_query}")

        elif "open google maps and search" in request:
            if "search" in request:
                search_query = request.split("open google maps and search")[-1].strip()
                search_google_maps(search_query)
                speak(f"Searching Google Maps for {search_query}")

        elif "open notepad" in request:
            speak("Opening Notepad")
            import os

            os.system("notepad.exe")

        elif "exit" in request or "stop" in request or "bye" in request:
            speak("Goodbye! See you soon.")
            break


main_process()
