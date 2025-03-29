import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import os
import subprocess
import smtplib
import ctypes

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 175)


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
    }

    if app_name in apps:
        subprocess.Popen([apps[app_name]])  # Open app without blocking execution
        speak(f"Opening {app_name}")
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


import smtplib


# def send_email(to_email, subject, message):
#     """Send an email using SMTP with an App Password."""
#     try:
#         sender_email = "323keshav0012@dbit.in"  # Your Gmail
#         sender_password = "xqeb woxj pwnj isvz"  # Use the generated App Password

#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(sender_email, sender_password)

#         email_message = f"Subject: {subject}\n\n{message}"
#         server.sendmail(sender_email, to_email, email_message)
#         server.quit()

#         print("Email has been sent successfully.")
#         speak("Email has been sent successfully.")
#     except Exception as e:
#         print("Error:", e)
#         speak("Sorry, I couldn't send the email.")


def main_process():
    """Main function to process commands."""
    while True:
        request = command()

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

        # elif "send email" in request:
        #     speak("To whom should I send the email?")
        #     recipient = command()

        #     # Manually set recipient email or map to known contacts
        #     email_contacts = {
        #         "keshav": "323keshav0012@dbit.in",  # Replace with actual emails
        #         "ghost": "prajapatikeshav775@gmail.com",
        #         "thor": "odinson454@gmail.com",
        #     }

        #     if recipient in email_contacts:
        #         to_email = email_contacts[recipient]
        #     else:
        #         speak("I couldn't find that contact. Please provide an email address.")
        #         to_email = command()

        #     speak("What is the subject?")
        #     subject = command()
        #     speak("What should I say in the email?")
        #     message = command()

        #     if to_email and subject and message:
        #         send_email(to_email, subject, message)
        #     else:
        #         speak("I couldn't get the email details properly.")

        elif "exit" in request or "stop" in request or "bye" in request:
            speak("Goodbye! See you soon.")
            break


main_process()
