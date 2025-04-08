import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, font
from PIL import Image, ImageTk
import threading
from dotenv import load_dotenv
import os
import pyttsx3
import speech_recognition as sr
import random
import webbrowser
import datetime
import subprocess
import smtplib
import ctypes
import requests
import pyautogui
import whisper
import tempfile
import sounddevice as sd
import scipy.io.wavfile

# Load the variables from .env
load_dotenv()

class ModernVoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("NOVA - AI Voice Assistant")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg='#121212')
        
        # Custom theme colors
        self.bg_color = '#121212'
        self.card_color = '#1E1E1E'
        self.accent_color = '#BB86FC'
        self.secondary_color = '#03DAC6'
        self.text_color = '#FFFFFF'
        self.highlight_color = '#3700B3'
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)
        self.engine.setProperty("rate", 175)
        
        # API keys and configurations
        self.API_KEY = os.getenv("API_KEY")
        self.BASE_URL = os.getenv("BASE_URL")
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        
        # Email contacts
        self.email_contacts = {
            "keshav": "prajapatikeshav497@gmail.com",
            "ojal": "odinson454@gmail.com",
            "cyril": "323keshav0012@dbit.in",
            "sandhya": "prajapatisandhya619@gmail.com",
        }
        
        # Configure styles
        self.configure_styles()
        
        # GUI elements
        self.create_widgets()
        
        # Start the assistant in a separate thread
        self.listening = False
        self.assistant_thread = None
        
    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        self.style.configure('TButton', 
                           background=self.accent_color, 
                           foreground='black',
                           borderwidth=0,
                           focuscolor=self.accent_color)
        self.style.map('TButton',
                      background=[('active', self.highlight_color)],
                      foreground=[('active', 'white')])
        
        self.style.configure('TCombobox', 
                           fieldbackground=self.card_color,
                           background=self.card_color,
                           foreground=self.text_color)
        
        # Custom card style
        self.style.configure('Card.TFrame', background=self.card_color, borderwidth=2, relief='flat')
        
    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header frame
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Logo and title
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)
        
        try:
            logo_img = Image.open("assistant_icon.png").resize((50, 50))
            self.logo = ImageTk.PhotoImage(logo_img)
            logo_label = ttk.Label(logo_frame, image=self.logo, background=self.bg_color)
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            logo_label = ttk.Label(logo_frame, text="🤖", font=('Arial', 24), background=self.bg_color)
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = ttk.Label(logo_frame, 
                              text="NOVA", 
                              font=('Helvetica', 24, 'bold'), 
                              foreground=self.accent_color,
                              background=self.bg_color)
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(logo_frame, 
                                 text="AI Voice Assistant", 
                                 font=('Helvetica', 12), 
                                 foreground=self.text_color,
                                 background=self.bg_color)
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Control buttons
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)
        
        # Conversation display card
        conversation_card = ttk.Frame(main_container, style='Card.TFrame')
        conversation_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.conversation_text = scrolledtext.ScrolledText(
            conversation_card, 
            wrap=tk.WORD, 
            width=70, 
            height=20,
            font=('Helvetica', 10), 
            bg=self.card_color, 
            fg=self.text_color,
            insertbackground=self.text_color,
            padx=15,
            pady=15,
            relief='flat'
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.insert(tk.END, "NOVA: Welcome! I'm your AI assistant. How can I help you today?\n")
        self.conversation_text.configure(state='disabled')
        
        # Add tag configurations for different speakers
        self.conversation_text.tag_config('assistant', foreground=self.accent_color)
        self.conversation_text.tag_config('user', foreground=self.secondary_color)
        self.conversation_text.tag_config('system', foreground='#CF6679')
        self.conversation_text.tag_config('news', foreground='#018786')
        
        # Input controls card
        input_card = ttk.Frame(main_container, style='Card.TFrame')
        input_card.pack(fill=tk.X, pady=(0, 10))
        
        # Microphone button
        self.mic_button = ttk.Button(
            input_card,
            text="🎤", 
            style='TButton',
            command=self.toggle_listening,
            width=3
        )
        self.mic_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Quick actions dropdown
        self.quick_actions = ttk.Combobox(
            input_card,
            values=[
                "Get Time", "Get Date", "Get Weather", 
                "Get News", "Open Notepad", "Open Calculator",
                "Set Alarm", "Set Reminder", "Play Music"
            ],
            state="readonly",
            font=('Helvetica', 10),
            width=25
        )
        self.quick_actions.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.quick_actions.bind("<<ComboboxSelected>>", self.handle_quick_action)
        
        # Exit button
        exit_button = ttk.Button(
            input_card,
            text="Exit", 
            command=self.exit_app,
            style='TButton'
        )
        exit_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_container, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Helvetica', 9),
            foreground=self.text_color,
            background=self.highlight_color
        )
        status_bar.pack(fill=tk.X)
        
        # Configure grid weights for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.status_var.set("Listening...")
            self.mic_button.config(style='Active.TButton')
            self.assistant_thread = threading.Thread(target=self.main_process)
            self.assistant_thread.daemon = True
            self.assistant_thread.start()
        else:
            self.listening = False
            self.status_var.set("Ready")
            self.mic_button.config(style='TButton')
    
    def handle_quick_action(self, event):
        action = self.quick_actions.get()
        self.quick_actions.set('')
        
        if action == "Get Time":
            self.get_time()
        elif action == "Get Date":
            self.get_date()
        elif action == "Get Weather":
            self.get_weather_gui()
        elif action == "Get News":
            self.get_news()
        elif action == "Open Notepad":
            self.open_application("notepad")
        elif action == "Open Calculator":
            self.open_application("calculator")
        elif action == "Set Alarm":
            self.set_alarm()
        elif action == "Set Reminder":
            self.set_reminder()
        elif action == "Play Music":
            self.play_music()
    
    def get_weather_gui(self):
        def on_submit():
            city = city_entry.get()
            if city:
                self.get_weather(city)
                weather_window.destroy()
        
        weather_window = tk.Toplevel(self.root)
        weather_window.title("Weather Check")
        weather_window.geometry("300x180")
        weather_window.configure(bg=self.bg_color)
        weather_window.resizable(False, False)
        
        # Make the window appear centered
        window_width = weather_window.winfo_reqwidth()
        window_height = weather_window.winfo_reqheight()
        position_right = int(weather_window.winfo_screenwidth()/2 - window_width/2)
        position_down = int(weather_window.winfo_screenheight()/2 - window_height/2)
        weather_window.geometry(f"+{position_right}+{position_down}")
        
        card = ttk.Frame(weather_window, style='Card.TFrame')
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(card, text="Enter city name:", font=('Helvetica', 11)).pack(pady=(10, 5))
        
        city_entry = ttk.Entry(card, width=25, font=('Helvetica', 11))
        city_entry.pack(pady=5, padx=20, ipady=5)
        
        submit_btn = ttk.Button(card, text="Get Weather", command=on_submit)
        submit_btn.pack(pady=10, ipadx=10, ipady=5)
        
        city_entry.focus_set()
    
    def update_conversation(self, speaker, text):
        self.conversation_text.configure(state='normal')
        
        # Determine tag based on speaker
        if speaker.lower() == "assistant" or speaker.lower() == "nova":
            tag = 'assistant'
        elif speaker.lower() == "user" or speaker.lower() == "you":
            tag = 'user'
        elif speaker.lower() == "system":
            tag = 'system'
        elif speaker.lower() == "news":
            tag = 'news'
        else:
            tag = ''
        
        self.conversation_text.insert(tk.END, f"{speaker}: {text}\n", tag)
        self.conversation_text.see(tk.END)
        self.conversation_text.configure(state='disabled')
    
    def speak(self, audio):
        """Speak out the given text and update the conversation display."""
        self.update_conversation("NOVA", audio)
        self.engine.say(audio)
        self.engine.runAndWait()
    
    def command(self):
        """Capture voice command from user."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.update_conversation("System", "Listening...")
            r.adjust_for_ambient_noise(source)
            try:
                audio = r.listen(source, timeout=5)
                content = r.recognize_google(audio, language="en-in")
                self.update_conversation("You", content)
                return content.lower()
            except sr.UnknownValueError:
                self.update_conversation("System", "Sorry, I couldn't understand that.")
                return ""
            except sr.WaitTimeoutError:
                self.update_conversation("System", "No speech detected, try again.")
                return ""
    
    def search_web(self, query, platform):
        """Searches Google, YouTube, or Maps based on the platform specified."""
        search_engines = {
            "google": f"https://www.google.com/search?q={query}",
            "youtube": f"https://www.youtube.com/results?search_query={query}",
            "maps": f"https://www.google.com/maps/search/{query}",
        }

        if platform in search_engines:
            webbrowser.open(search_engines[platform])
            self.speak(f"Searching {platform} for {query}")
    
    def open_application(self, app_name):
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
                self.speak(f"Opening {app_name}")
            except Exception as e:
                self.update_conversation("System", f"Error opening {app_name}: {str(e)}")
                self.speak(f"Sorry, I couldn't open {app_name}")
        else:
            self.speak("Sorry, I couldn't find that application.")
    
    def change_volume(self, action):
        """Control system volume."""
        if action == "increase":
            for _ in range(5):  # Increase volume by 5 steps
                ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume up
            self.speak("Volume increased")
        elif action == "decrease":
            for _ in range(5):  # Decrease volume by 5 steps
                ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # Volume down
            self.speak("Volume decreased")
        elif action == "mute":
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # Mute
            self.speak("Volume muted")
        elif action == "unmute":
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # Unmute (same key as mute)
            self.speak("Volume unmuted")
    
    def get_weather(self, city):
        """Fetches weather data for a given city."""
        try:
            params = {"q": city, "appid": self.API_KEY, "units": "metric"}
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            if data["cod"] != 200:
                self.speak(
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
            self.speak(weather_info)

        except Exception as e:
            self.update_conversation("System", f"Error fetching weather: {str(e)}")
            self.speak("There was an error retrieving the weather.")
    
    def send_email(self, to_email, subject, message):
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
            self.speak("Email has been sent successfully.")
        except Exception as e:
            self.update_conversation("System", f"Failed to send email: {str(e)}")
            self.speak("Sorry, I couldn't send the email.")
    
    def dictate_to_file(self, filename="dictation.txt"):
        """Dictates spoken words and writes them into a text file."""
        self.speak(
            "Start speaking. I will write everything you say into a file. Say 'stop dictation' to finish."
        )

        with open(filename, "a", encoding="utf-8") as file:
            while self.listening:
                spoken_text = self.command()
                if "stop dictation" in spoken_text:
                    self.speak("Dictation stopped. Your words have been saved.")
                    break
                elif spoken_text:
                    file.write(spoken_text + "\n")
    
    def set_alarm(self):
        """Open the Clock app to set an alarm."""
        self.speak("I'll open the Clock app where you can set your alarm.")
        self.open_application("alarms")
    
    def set_reminder(self):
        """Open the Clock app to set a reminder."""
        self.speak("I'll open the Clock app where you can set your reminder.")
        self.open_application("clock")
    
    def play_music(self):
        """Play random music from predefined list."""
        self.speak("Playing Music!")
        songs = [
            "https://www.youtube.com/watch?v=1G4isv_Fylg",
            "https://www.youtube.com/watch?v=pElk1ShPrcE",
            "https://www.youtube.com/watch?v=1cDoRqPnCXU",
        ]
        webbrowser.open(random.choice(songs))
    
    def get_news(self):
        """Fetch top news headlines using News API."""
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.NEWS_API_KEY}"
            response = requests.get(url)
            data = response.json()

            if data["status"] != "ok":
                self.speak("Sorry, I couldn't fetch the news at the moment.")
                return

            articles = data.get("articles", [])[:5]
            if not articles:
                self.speak("No news articles were found.")
                return

            self.speak("Here are the top news headlines:")

            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title available")
                self.update_conversation("News", f"{i}. {title}")
                self.speak(title)

        except Exception as e:
            self.update_conversation("System", f"Error fetching news: {str(e)}")
            self.speak("There was an error getting the news.")
    
    def get_time(self):
        now_time = datetime.datetime.now().strftime("%H:%M")
        self.speak("Current time is " + now_time)
    
    def get_date(self):
        now_date = datetime.datetime.now().strftime("%d-%m-%Y")
        self.speak("Today's date is " + now_date)
    
    def main_process(self):
        """Main function to process commands."""
        while self.listening:
            request = self.command()

            if not request:
                continue  # Skip empty commands

            if "hello" in request or "hi" in request or "hey" in request:
                self.speak("Welcome! How can I assist you?")

            elif "play music" in request or "play song" in request or "play a song" in request:
                self.play_music()

            elif "time" in request:
                self.get_time()

            elif "date" in request:
                self.get_date()

            elif "search google for" in request:
                search_query = request.replace("search google for", "").strip()
                if search_query:
                    self.search_web(search_query, "google")

            elif "search youtube for" in request:
                search_query = request.replace("search youtube for", "").strip()
                if search_query:
                    self.search_web(search_query, "youtube")

            elif "search maps for" in request or "search google maps for" in request:
                search_query = (
                    request.replace("search maps for", "")
                    .replace("search google maps for", "")
                    .strip()
                )
                if search_query:
                    self.search_web(search_query, "maps")

            elif "open" in request:
                app_name = request.replace("open", "").strip()
                self.open_application(app_name)

            elif "increase volume" in request:
                self.change_volume("increase")

            elif "decrease volume" in request:
                self.change_volume("decrease")

            elif "mute volume" in request:
                self.change_volume("mute")

            elif "unmute volume" in request:
                self.change_volume("unmute")

            elif "weather" in request or "what's the weather" in request:
                self.speak("Which city's weather would you like to know?")
                city = self.command()
                if city:
                    self.get_weather(city)
                else:
                    self.speak("I couldn't get the city name.")

            elif "send email" in request:
                self.speak("To whom should I send the email?")
                recipient_name = self.command()

                to_email = self.email_contacts.get(recipient_name)
                if not to_email:
                    self.speak("I couldn't find that contact. Please try again.")
                    continue

                self.speak("What should be the subject?")
                subject = self.command()
                if not subject:
                    self.speak("Subject not recognized.")
                    continue

                self.speak("What is the message?")
                message = self.command()
                if not message:
                    self.speak("Message not recognized.")
                    continue

                self.send_email(to_email, subject, message)

            elif "start dictation" in request or "dictate" in request:
                self.dictate_to_file()

            elif "set alarm" in request or "create alarm" in request:
                self.set_alarm()

            elif "set reminder" in request or "create reminder" in request:
                self.set_reminder()

            elif "news" in request or "headlines" in request or "what's the news" in request:
                self.get_news()

            elif "exit" in request or "stop" in request or "bye" in request:
                self.speak("Goodbye! See you soon.")
                self.listening = False
                self.toggle_listening()  # Update button state
    
    def exit_app(self):
        """Clean exit from the application."""
        self.listening = False
        if self.assistant_thread and self.assistant_thread.is_alive():
            self.assistant_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set window icon
    try:
        img = Image.open("assistant_icon.png")
        photo = ImageTk.PhotoImage(img)
        root.iconphoto(False, photo)
    except:
        pass
    
    # Configure the active button style
    style = ttk.Style()
    style.configure('Active.TButton', 
                  background='#CF6679', 
                  foreground='white',
                  borderwidth=0)
    
    app = ModernVoiceAssistant(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()