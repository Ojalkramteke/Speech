import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')       
engine.setProperty('voice', voices[0].id)  # Select the first available voice
engine.setProperty("rate", 175)  # Set speech speed

def speak(audio):
    """Speak out the given text."""
    engine.say(audio)
    engine.runAndWait()

def command():
    """Capture voice command from user."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        r.adjust_for_ambient_noise(source)  # Adjust for background noise
        try:
            audio = r.listen(source, timeout=3)  # Add timeout
            content = r.recognize_google(audio, language='en-in')
            print("You said: " + content)
            return content.lower()
            
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected, try again.")
            return ""

def main_process():
    """Main function to process commands."""
    while True:
        request = command()
        if "hello" in request:
            speak("Welcome, how can I help you?")
        elif "play music" in request:
            speak("Playing Music!")
            songs = [
                "https://www.youtube.com/watch?v=FZLadzn5i6Q",
                "https://www.youtube.com/watch?v=pElk1ShPrcE",
                "https://www.youtube.com/watch?v=1cDoRqPnCXU"
            ]
            webbrowser.open(random.choice(songs))
            break
        elif "exit" in request or "stop" in request or "bye" in request or "ok" in request:
            speak("Goodbye!")
            break
        elif "say time" in request:
            now_time = datetime.datetime.now().strftime("%H:%M")
            speak("Current time is " + str(now_time))
        elif "say date" in request:
            now_time = datetime.datetime.now().strftime("%d:%m")
            speak("Current date is " + str(now_time))

main_process()
