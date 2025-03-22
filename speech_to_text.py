import speech_recognition as sr

def recognize_speech():
    recognizer = sr.Recognizer()  # Initialize the recognizer
    with sr.Microphone() as source:  # Use microphone as the input source
        print("Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = recognizer.listen(source)  # Capture the audio

    try:
        text = recognizer.recognize_sphinx(audio)  # Convert speech to text using PocketSphinx
        print("You said:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError:
        print("Speech recognition service is not available.")
        return None

# Make sure this part is OUTSIDE the function
if __name__ == "__main__":
    print("Say something and wait for recognition...")
    text = recognize_speech()
    
    if text:
        print("Recognized Text:", text)
    else:
        print("No valid speech detected.")

def test_microphone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak something... Testing microphone.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    with open("test_audio.wav", "wb") as f:
        f.write(audio.get_wav_data())

    print("Audio recorded. Check test_audio.wav")
    print("Hello")

test_microphone()

