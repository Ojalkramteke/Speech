import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()
voices = engine.getProperty('voices')       #getting details of current voice
for voice in voices:
    engine.setProperty('voice', voice.id)
    engine.setProperty("rate", 175)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def command():
    content = " "
    while content == " ":
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        # recognize speech using Google Speech Recognition
        try:
            content = r.recognize_google(audio, language='en-in')
            print("You said ........." + content)
        except Exception as e:
            print("Please try again...")

    return content

request = command()
print(request)
#speak("How are you?")