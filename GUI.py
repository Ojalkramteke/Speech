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
import pywhatkit
from alarm_manager import AlarmManager

# Load the variables from .env
load_dotenv()


class ModernVoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("SAYNTEX - Voice Assistant")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg="#121212")

        # Custom theme colors
        self.bg_color = "#121212"
        self.card_color = "#1E1E1E"
        self.accent_color = "#BB86FC"
        self.secondary_color = "#03DAC6"
        self.text_color = "#FFFFFF"
        self.highlight_color = "#3700B3"

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

        # WhatsApp contacts
        self.whatsapp_contacts = {
            "keshav": "9136669616",
            "ojal": "9876543211",
            "cyril": "9876543212",
            "sandhya": "9876543213",
        }

        # Configure styles
        self.configure_styles()

        # GUI elements
        self.create_widgets()

        # Start the assistant in a separate thread
        self.listening = False
        self.assistant_thread = None

        self.alarm_manager = AlarmManager()

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure colors
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure(
            "TLabel", background=self.bg_color, foreground=self.text_color
        )
        self.style.configure(
            "TButton",
            background=self.accent_color,
            foreground="black",
            borderwidth=0,
            focuscolor=self.accent_color,
        )
        self.style.map(
            "TButton",
            background=[("active", self.highlight_color)],
            foreground=[("active", "white")],
        )

        self.style.configure(
            "TCombobox",
            fieldbackground=self.card_color,
            background=self.card_color,
            foreground=self.text_color,
        )

        # Custom card style
        self.style.configure(
            "Card.TFrame", background=self.card_color, borderwidth=2, relief="flat"
        )

        # Configure Accent button style
        self.style.configure(
            "Accent.TButton",
            background=self.accent_color,
            foreground="black",
            font=("Helvetica", 10, "bold"),
            padding=5
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", self.highlight_color)],
            foreground=[("active", "white")]
        )

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
            logo_label = ttk.Label(
                logo_frame, image=self.logo, background=self.bg_color
            )
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
        except:
            logo_label = ttk.Label(
                logo_frame, text="🤖", font=("Arial", 24), background=self.bg_color
            )
            logo_label.pack(side=tk.LEFT, padx=(0, 10))

        title_label = ttk.Label(
            logo_frame,
            text="SAYNTEX",
            font=("Helvetica", 24, "bold"),
            foreground=self.accent_color,
            background=self.bg_color,
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = ttk.Label(
            logo_frame,
            text="Voice Assistant",
            font=("Helvetica", 12),
            foreground=self.text_color,
            background=self.bg_color,
        )
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Control buttons
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)

        # Conversation display card
        conversation_card = ttk.Frame(main_container, style="Card.TFrame")
        conversation_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.conversation_text = scrolledtext.ScrolledText(
            conversation_card,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Helvetica", 10),
            bg=self.card_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            padx=15,
            pady=15,
            relief="flat",
        )
        self.conversation_text.pack(fill=tk.BOTH, expand=True)
        self.conversation_text.insert(
            tk.END, "SAYNTEX: Welcome! I'm your assistant. How can I help you today?\n"
        )
        self.conversation_text.configure(state="disabled")

        # Add tag configurations for different speakers
        self.conversation_text.tag_config("assistant", foreground=self.accent_color)
        self.conversation_text.tag_config("user", foreground=self.secondary_color)
        self.conversation_text.tag_config("system", foreground="#CF6679")
        self.conversation_text.tag_config("news", foreground="#018786")

        # Input controls card
        input_card = ttk.Frame(main_container, style="Card.TFrame")
        input_card.pack(fill=tk.X, pady=(0, 10))

        # Microphone button
        self.mic_button = ttk.Button(
            input_card,
            text="🎤",
            style="TButton",
            command=self.toggle_listening,
            width=3,
        )
        self.mic_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Quick actions dropdown
        self.quick_actions = ttk.Combobox(
            input_card,
            values=[
                "Get Time",
                "Get Date",
                "Get Weather",
                "Get News",
                "Open Notepad",
                "Open Calculator",
                "Tell a Joke",
                "Set Reminder",
                "Manage Reminders",
                "Manage Contacts",
            ],
            state="readonly",
            font=("Helvetica", 10),
            width=25,
        )
        self.quick_actions.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.quick_actions.bind("<<ComboboxSelected>>", self.handle_quick_action)

        # Exit button
        exit_button = ttk.Button(
            input_card, text="Exit", command=self.exit_app, style="TButton"
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
            font=("Helvetica", 9),
            foreground=self.text_color,
            background=self.highlight_color,
        )
        status_bar.pack(fill=tk.X)

        # Configure grid weights for resizing
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.status_var.set("Listening...")
            self.mic_button.config(style="Active.TButton")
            self.assistant_thread = threading.Thread(target=self.main_process)
            self.assistant_thread.daemon = True
            self.assistant_thread.start()
        else:
            self.listening = False
            self.status_var.set("Ready")
            self.mic_button.config(style="TButton")

    def handle_quick_action(self, event):
        action = self.quick_actions.get()
        self.quick_actions.set("")

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
        elif action == "Set Reminder":
            self.show_manual_reminder_input()
        elif action == "Manage Reminders":
            self.manage_reminders()
        elif action == "Tell a Joke":
            self.get_joke()
        elif action == "Manage Contacts":
            self.manage_contacts()

    def show_manual_reminder_input(self):
        """Show manual reminder input form"""
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Set Reminder")
        reminder_window.geometry("400x400")
        reminder_window.configure(bg=self.bg_color)
        reminder_window.resizable(False, False)

        # Center the window
        window_width = reminder_window.winfo_reqwidth()
        window_height = reminder_window.winfo_reqheight()
        position_right = int(reminder_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(reminder_window.winfo_screenheight() / 2 - window_height / 2)
        reminder_window.geometry(f"+{position_right}+{position_down}")

        card = ttk.Frame(reminder_window, style="Card.TFrame")
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Date entry
        ttk.Label(card, text="Date (YYYY-MM-DD):", font=("Helvetica", 11)).pack(pady=(10, 5))
        date_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
        date_entry.pack(pady=5, padx=20, ipady=5)
        date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))  # Default to today

        # Time entry
        ttk.Label(card, text="Time (HH:MM):", font=("Helvetica", 11)).pack(pady=(10, 5))
        time_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
        time_entry.pack(pady=5, padx=20, ipady=5)
        time_entry.insert(0, "00:00")  # Default time

        # Label entry
        ttk.Label(card, text="Label:", font=("Helvetica", 11)).pack(pady=(10, 5))
        label_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
        label_entry.pack(pady=5, padx=20, ipady=5)

        # Buttons frame
        buttons_frame = ttk.Frame(card)
        buttons_frame.pack(pady=20)

        # Voice input button
        voice_btn = ttk.Button(buttons_frame, text="🎤 Voice Input", command=lambda: [reminder_window.destroy(), self.set_reminder()])
        voice_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        # Submit button
        submit_btn = ttk.Button(buttons_frame, text="Set Reminder", command=lambda: self.on_submit_reminder(date_entry.get(), time_entry.get(), label_entry.get(), reminder_window))
        submit_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    def on_submit_reminder(self, date_str, time_str, label, window):
        """Handle reminder submission from manual input"""
        try:
            if not date_str or not time_str or not label:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            # Validate date format
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Date must be in YYYY-MM-DD format (e.g., 2024-03-20)")
                return
            
            # Validate time format
            try:
                datetime.datetime.strptime(time_str, "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Time must be in HH:MM format (e.g., 14:30)")
                return
            
            # Combine date and time into ISO format
            datetime_str = f"{date_str}T{time_str}:00"
            
            self.alarm_manager.create_reminder(datetime_str, label)
            self.speak(f"Reminder set for {date_str} at {time_str}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set reminder: {str(e)}")

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
        position_right = int(weather_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(weather_window.winfo_screenheight() / 2 - window_height / 2)
        weather_window.geometry(f"+{position_right}+{position_down}")

        card = ttk.Frame(weather_window, style="Card.TFrame")
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(card, text="Enter city name:", font=("Helvetica", 11)).pack(
            pady=(10, 5)
        )

        city_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
        city_entry.pack(pady=5, padx=20, ipady=5)

        submit_btn = ttk.Button(card, text="Get Weather", command=on_submit)
        submit_btn.pack(pady=10, ipadx=10, ipady=5)

        city_entry.focus_set()

    def update_conversation(self, speaker, text):
        self.conversation_text.configure(state="normal")

        # Determine tag based on speaker
        if speaker.lower() == "assistant" or speaker.lower() == "sayntex":
            tag = "assistant"
        elif speaker.lower() == "user" or speaker.lower() == "you":
            tag = "user"
        elif speaker.lower() == "system":
            tag = "system"
        elif speaker.lower() == "news":
            tag = "news"
        else:
            tag = ""

        self.conversation_text.insert(tk.END, f"{speaker}: {text}\n", tag)
        self.conversation_text.see(tk.END)
        self.conversation_text.configure(state="disabled")

    def speak(self, audio):
        """Speak out the given text and update the conversation display."""
        self.update_conversation("SAYNTEX", audio)
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
                self.update_conversation(
                    "System", f"Error opening {app_name}: {str(e)}"
                )
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

    def parse_spoken_time(self, spoken_time: str) -> str:
        """Convert spoken time to HH:MM format"""
        try:
            # Handle "quarter past/to" format
            if "quarter" in spoken_time:
                if "past" in spoken_time:
                    hour = int(spoken_time.split("past")[0].strip())
                    return f"{hour:02d}:15"
                elif "to" in spoken_time:
                    hour = int(spoken_time.split("to")[0].strip()) + 1
                    return f"{hour:02d}:45"
            
            # Handle "half past" format
            if "half past" in spoken_time:
                hour = int(spoken_time.split("half past")[1].strip())
                return f"{hour:02d}:30"
            
            # Handle "o'clock" format
            if "o'clock" in spoken_time:
                hour = int(spoken_time.split("o'clock")[0].strip())
                return f"{hour:02d}:00"
            
            # Handle direct time format (e.g., "2 30" or "2:30")
            time_parts = spoken_time.replace(":", " ").split()
            if len(time_parts) >= 2:
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                return f"{hour:02d}:{minute:02d}"
            
            # If only hour is given, assume :00
            hour = int(spoken_time)
            return f"{hour:02d}:00"
            
        except Exception as e:
            print(f"Error parsing time: {e}")
            return None

    def parse_spoken_date(self, spoken_date: str) -> str:
        """Convert spoken date to YYYY-MM-DD format"""
        try:
            today = datetime.datetime.now()
            
            # Handle relative dates
            if "today" in spoken_date:
                return today.strftime("%Y-%m-%d")
            elif "tomorrow" in spoken_date:
                tomorrow = today + datetime.timedelta(days=1)
                return tomorrow.strftime("%Y-%m-%d")
            elif "next week" in spoken_date:
                next_week = today + datetime.timedelta(days=7)
                return next_week.strftime("%Y-%m-%d")
            
            # Handle "day after tomorrow"
            if "day after tomorrow" in spoken_date:
                day_after = today + datetime.timedelta(days=2)
                return day_after.strftime("%Y-%m-%d")
            
            # Handle specific day names
            days = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            
            for day_name, day_num in days.items():
                if day_name in spoken_date.lower():
                    current_day = today.weekday()
                    days_ahead = day_num - current_day
                    if days_ahead <= 0:
                        days_ahead += 7
                    target_date = today + datetime.timedelta(days=days_ahead)
                    return target_date.strftime("%Y-%m-%d")
            
            # If no special format is detected, try to parse as direct date
            # This is a simple implementation and might need enhancement
            parts = spoken_date.split()
            if len(parts) >= 2:
                month = parts[0]
                day = int(parts[1])
                year = today.year
                if len(parts) >= 3:
                    year = int(parts[2])
                return f"{year}-{month:02d}-{day:02d}"
            
            return None
            
        except Exception as e:
            print(f"Error parsing date: {e}")
            return None

    def set_reminder(self):
        """Create a new reminder through GUI"""
        def show_manual_input():
            reminder_window = tk.Toplevel(self.root)
            reminder_window.title("Set Reminder")
            reminder_window.geometry("400x400")
            reminder_window.configure(bg=self.bg_color)
            reminder_window.resizable(False, False)

            # Center the window
            window_width = reminder_window.winfo_reqwidth()
            window_height = reminder_window.winfo_reqheight()
            position_right = int(reminder_window.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(reminder_window.winfo_screenheight() / 2 - window_height / 2)
            reminder_window.geometry(f"+{position_right}+{position_down}")

            card = ttk.Frame(reminder_window, style="Card.TFrame")
            card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Date entry
            ttk.Label(card, text="Date (YYYY-MM-DD):", font=("Helvetica", 11)).pack(pady=(10, 5))
            date_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
            date_entry.pack(pady=5, padx=20, ipady=5)
            date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))  # Default to today

            # Time entry
            ttk.Label(card, text="Time (HH:MM):", font=("Helvetica", 11)).pack(pady=(10, 5))
            time_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
            time_entry.pack(pady=5, padx=20, ipady=5)
            time_entry.insert(0, "00:00")  # Default time

            # Label entry
            ttk.Label(card, text="Label:", font=("Helvetica", 11)).pack(pady=(10, 5))
            label_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
            label_entry.pack(pady=5, padx=20, ipady=5)

            # Buttons frame
            buttons_frame = ttk.Frame(card)
            buttons_frame.pack(pady=20)

            # Voice input button
            voice_btn = ttk.Button(buttons_frame, text="🎤 Voice Input", command=lambda: [reminder_window.destroy(), self.set_reminder()])
            voice_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

            # Submit button
            submit_btn = ttk.Button(buttons_frame, text="Set Reminder", command=lambda: self.on_submit_reminder(date_entry.get(), time_entry.get(), label_entry.get(), reminder_window))
            submit_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

        def on_submit(date_str, time_str, label, window):
            try:
                if not date_str or not time_str or not label:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return
                
                # Validate date format
                try:
                    datetime.datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Error", "Date must be in YYYY-MM-DD format (e.g., 2024-03-20)")
                    return
                
                # Validate time format
                try:
                    datetime.datetime.strptime(time_str, "%H:%M")
                except ValueError:
                    messagebox.showerror("Error", "Time must be in HH:MM format (e.g., 14:30)")
                    return
                
                # Combine date and time into ISO format
                datetime_str = f"{date_str}T{time_str}:00"
                
                self.alarm_manager.create_reminder(datetime_str, label)
                self.speak(f"Reminder set for {date_str} at {time_str}")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to set reminder: {str(e)}")

        def voice_input():
            self.speak("What date would you like to set the reminder for? You can say 'today', 'tomorrow', or a specific date.")
            spoken_date = self.command()
            if not spoken_date:
                self.speak("I couldn't hear the date. Would you like to enter it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()
                return

            date_str = self.parse_spoken_date(spoken_date)
            if not date_str:
                self.speak("I couldn't understand the date. Would you like to enter it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()
                return

            self.speak("What time would you like to set the reminder for?")
            spoken_time = self.command()
            if not spoken_time:
                self.speak("I couldn't hear the time. Would you like to enter it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()
                return

            time_str = self.parse_spoken_time(spoken_time)
            if not time_str:
                self.speak("I couldn't understand the time. Would you like to enter it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()
                return

            self.speak("What would you like to be reminded about?")
            label = self.command()
            if not label:
                self.speak("I couldn't hear the reminder text. Would you like to enter it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()
                return

            try:
                datetime_str = f"{date_str}T{time_str}:00"
                self.alarm_manager.create_reminder(datetime_str, label)
                self.speak(f"Reminder set for {date_str} at {time_str}")
            except Exception as e:
                self.speak(f"Sorry, I couldn't set the reminder. Error: {str(e)}")
                self.speak("Would you like to try entering it manually?")
                if "yes" in self.command().lower():
                    show_manual_input()

        # Start with voice input by default
        voice_input()

    def manage_reminders(self):
        """Show and manage existing reminders"""
        def delete_reminder(reminder_id):
            try:
                if self.alarm_manager.delete_reminder(reminder_id):
                    self.speak("Reminder deleted")
                    refresh_reminders()
                else:
                    self.speak("Failed to delete reminder")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete reminder: {str(e)}")

        def toggle_reminder(reminder_id):
            try:
                reminder = next((r for r in self.alarm_manager.reminders if r.id == reminder_id), None)
                if reminder:
                    reminder = self.alarm_manager.edit_reminder(reminder_id, is_active=not reminder.is_active)
                    if reminder:
                        status = "activated" if reminder.is_active else "deactivated"
                        self.speak(f"Reminder {status}")
                        refresh_reminders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to toggle reminder: {str(e)}")

        def refresh_reminders():
            # Clear existing items
            for widget in reminders_frame.winfo_children():
                widget.destroy()

            # Add reminders
            for reminder in self.alarm_manager.reminders:
                reminder_frame = ttk.Frame(reminders_frame, style="Card.TFrame")
                reminder_frame.pack(fill=tk.X, pady=5, padx=5)

                reminder_time = datetime.datetime.fromisoformat(reminder.datetime)
                time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
                
                ttk.Label(
                    reminder_frame,
                    text=f"{time_str} - {reminder.label}",
                    font=("Helvetica", 10)
                ).pack(side=tk.LEFT, padx=5)

                status = "Active" if reminder.is_active else "Inactive"
                ttk.Button(
                    reminder_frame,
                    text=status,
                    command=lambda id=reminder.id: toggle_reminder(id)
                ).pack(side=tk.LEFT, padx=5)

                ttk.Button(
                    reminder_frame,
                    text="Delete",
                    command=lambda id=reminder.id: delete_reminder(id)
                ).pack(side=tk.RIGHT, padx=5)

        manage_window = tk.Toplevel(self.root)
        manage_window.title("Manage Reminders")
        manage_window.geometry("500x400")
        manage_window.configure(bg=self.bg_color)

        # Center the window
        window_width = manage_window.winfo_reqwidth()
        window_height = manage_window.winfo_reqheight()
        position_right = int(manage_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(manage_window.winfo_screenheight() / 2 - window_height / 2)
        manage_window.geometry(f"+{position_right}+{position_down}")

        # Add new reminder button
        ttk.Button(
            manage_window,
            text="Add New Reminder",
            command=self.set_reminder
        ).pack(pady=10)

        # Reminders list
        reminders_frame = ttk.Frame(manage_window)
        reminders_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        refresh_reminders()

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

    def get_joke(self):
        """Fetch a random joke from a joke API"""
        try:
            url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
            response = requests.get(url)
            data = response.json()
            
            if data["error"]:
                self.speak("Sorry, I couldn't fetch a joke right now.")
                return
                
            if data["type"] == "single":
                joke = data["joke"]
            else:
                joke = f"{data['setup']} ... {data['delivery']}"
                
            self.speak(joke)
        except Exception as e:
            self.update_conversation("System", f"Error fetching joke: {str(e)}")
            self.speak("There was an error getting a joke.")

    def send_whatsapp_message(self, recipient, message):
        """Send a WhatsApp message to a specified contact."""
        try:
            # Check if recipient is a contact name
            phone_number = self.whatsapp_contacts.get(recipient.lower())
            
            if not phone_number:
                # If not a contact, try to use the input as a phone number
                phone_number = ''.join(filter(str.isdigit, recipient))
                if len(phone_number) != 10:
                    self.speak("Invalid phone number. Please provide a 10-digit number or a contact name.")
                    return False
            
            # Add country code if not present (assuming Indian numbers)
            if len(phone_number) == 10:
                phone_number = "+91" + phone_number
            
            # Send message using pywhatkit
            pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=15)
            self.speak(f"Message sent to {recipient}")
            return True
        except Exception as e:
            self.update_conversation("System", f"Error sending WhatsApp message: {str(e)}")
            self.speak("Sorry, I couldn't send the WhatsApp message.")
            return False

    def manage_contacts(self):
        """Show and manage email and WhatsApp contacts"""
        contacts_window = tk.Toplevel(self.root)
        contacts_window.title("Manage Contacts")
        contacts_window.geometry("800x600")
        contacts_window.configure(bg=self.bg_color)
        contacts_window.resizable(False, False)

        # Center the window
        window_width = contacts_window.winfo_reqwidth()
        window_height = contacts_window.winfo_reqheight()
        position_right = int(contacts_window.winfo_screenwidth() / 2 - window_width / 2)
        position_down = int(contacts_window.winfo_screenheight() / 2 - window_height / 2)
        contacts_window.geometry(f"+{position_right}+{position_down}")

        # Create notebook for tabs
        notebook = ttk.Notebook(contacts_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Email Contacts Tab
        email_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(email_frame, text="Email Contacts")

        # WhatsApp Contacts Tab
        whatsapp_frame = ttk.Frame(notebook, style="Card.TFrame")
        notebook.add(whatsapp_frame, text="WhatsApp Contacts")

        def refresh_email_contacts():
            # Clear existing items
            for widget in email_frame.winfo_children():
                widget.destroy()

            # Add header
            header_frame = ttk.Frame(email_frame)
            header_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(header_frame, text="Name", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
            ttk.Label(header_frame, text="Email", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

            # Add contacts
            for name, email in self.email_contacts.items():
                contact_frame = ttk.Frame(email_frame, style="Card.TFrame")
                contact_frame.pack(fill=tk.X, pady=2, padx=5)

                ttk.Label(contact_frame, text=name, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
                ttk.Label(contact_frame, text=email, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)

                ttk.Button(
                    contact_frame,
                    text="Edit",
                    command=lambda n=name, e=email: edit_email_contact(n, e)
                ).pack(side=tk.RIGHT, padx=2)

                ttk.Button(
                    contact_frame,
                    text="Delete",
                    command=lambda n=name: delete_email_contact(n)
                ).pack(side=tk.RIGHT, padx=2)

            # Add new contact button
            ttk.Button(
                email_frame,
                text="Add New Email Contact",
                command=lambda: edit_email_contact()
            ).pack(pady=10)

        def refresh_whatsapp_contacts():
            # Clear existing items
            for widget in whatsapp_frame.winfo_children():
                widget.destroy()

            # Add header
            header_frame = ttk.Frame(whatsapp_frame)
            header_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(header_frame, text="Name", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
            ttk.Label(header_frame, text="Phone", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

            # Add contacts
            for name, phone in self.whatsapp_contacts.items():
                contact_frame = ttk.Frame(whatsapp_frame, style="Card.TFrame")
                contact_frame.pack(fill=tk.X, pady=2, padx=5)

                ttk.Label(contact_frame, text=name, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
                ttk.Label(contact_frame, text=phone, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)

                ttk.Button(
                    contact_frame,
                    text="Edit",
                    command=lambda n=name, p=phone: edit_whatsapp_contact(n, p)
                ).pack(side=tk.RIGHT, padx=2)

                ttk.Button(
                    contact_frame,
                    text="Delete",
                    command=lambda n=name: delete_whatsapp_contact(n)
                ).pack(side=tk.RIGHT, padx=2)

            # Add new contact button
            ttk.Button(
                whatsapp_frame,
                text="Add New WhatsApp Contact",
                command=lambda: edit_whatsapp_contact()
            ).pack(pady=10)

        def edit_email_contact(name=None, email=None):
            edit_window = tk.Toplevel(contacts_window)
            edit_window.title("Edit Email Contact")
            edit_window.geometry("400x500")
            edit_window.configure(bg=self.bg_color)
            edit_window.resizable(True, True)  # Make window resizable

            # Center the window
            window_width = edit_window.winfo_reqwidth()
            window_height = edit_window.winfo_reqheight()
            position_right = int(edit_window.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(edit_window.winfo_screenheight() / 2 - window_height / 2)
            edit_window.geometry(f"+{position_right}+{position_down}")

            # Set minimum size
            edit_window.minsize(400, 250)

            card = ttk.Frame(edit_window, style="Card.TFrame")
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Increased padding

            # Title label
            title_label = ttk.Label(
                card,
                text="Edit Email Contact",
                font=("Helvetica", 14, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Form frame
            form_frame = ttk.Frame(card)
            form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

            ttk.Label(form_frame, text="Name:", font=("Helvetica", 11)).pack(pady=(10, 5))
            name_entry = ttk.Entry(form_frame, width=35, font=("Helvetica", 11))  # Increased width
            name_entry.pack(pady=5, padx=20, ipady=5)
            if name:
                name_entry.insert(0, name)

            ttk.Label(form_frame, text="Email:", font=("Helvetica", 11)).pack(pady=(10, 5))
            email_entry = ttk.Entry(form_frame, width=35, font=("Helvetica", 11))  # Increased width
            email_entry.pack(pady=5, padx=20, ipady=5)
            if email:
                email_entry.insert(0, email)

            def save_contact():
                new_name = name_entry.get().strip().lower()
                new_email = email_entry.get().strip()
                
                if not new_name or not new_email:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return
                
                if name and name != new_name:
                    del self.email_contacts[name]
                
                self.email_contacts[new_name] = new_email
                refresh_email_contacts()
                edit_window.destroy()

            # Buttons frame with more padding
            buttons_frame = ttk.Frame(card)
            buttons_frame.pack(pady=20, padx=20, fill=tk.X)  # Increased padding

            # Save button with custom style
            save_btn = ttk.Button(
                buttons_frame,
                text="Save (Ctrl+S)",
                command=save_contact,
                style="Accent.TButton"
            )
            save_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)  # Increased padding

            # Cancel button
            cancel_btn = ttk.Button(
                buttons_frame,
                text="Cancel (Esc)",
                command=edit_window.destroy
            )
            cancel_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)  # Increased padding

            # Configure keyboard shortcuts
            edit_window.bind("<Control-s>", lambda e: save_contact())
            edit_window.bind("<Escape>", lambda e: edit_window.destroy())

            # Focus the name entry
            name_entry.focus_set()

        def edit_whatsapp_contact(name=None, phone=None):
            edit_window = tk.Toplevel(contacts_window)
            edit_window.title("Edit WhatsApp Contact")
            edit_window.geometry("400x500")
            edit_window.configure(bg=self.bg_color)
            edit_window.resizable(True, True)  # Make window resizable

            # Center the window
            window_width = edit_window.winfo_reqwidth()
            window_height = edit_window.winfo_reqheight()
            position_right = int(edit_window.winfo_screenwidth() / 2 - window_width / 2)
            position_down = int(edit_window.winfo_screenheight() / 2 - window_height / 2)
            edit_window.geometry(f"+{position_right}+{position_down}")

            # Set minimum size
            edit_window.minsize(400, 250)

            card = ttk.Frame(edit_window, style="Card.TFrame")
            card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Increased padding

            # Title label
            title_label = ttk.Label(
                card,
                text="Edit WhatsApp Contact",
                font=("Helvetica", 14, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Form frame
            form_frame = ttk.Frame(card)
            form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

            ttk.Label(form_frame, text="Name:", font=("Helvetica", 11)).pack(pady=(10, 5))
            name_entry = ttk.Entry(form_frame, width=35, font=("Helvetica", 11))  # Increased width
            name_entry.pack(pady=5, padx=20, ipady=5)
            if name:
                name_entry.insert(0, name)

            ttk.Label(form_frame, text="Phone:", font=("Helvetica", 11)).pack(pady=(10, 5))
            phone_entry = ttk.Entry(form_frame, width=35, font=("Helvetica", 11))  # Increased width
            phone_entry.pack(pady=5, padx=20, ipady=5)
            if phone:
                phone_entry.insert(0, phone)

            def save_contact():
                new_name = name_entry.get().strip().lower()
                new_phone = phone_entry.get().strip()
                
                if not new_name or not new_phone:
                    messagebox.showerror("Error", "Please fill in all fields")
                    return
                
                if not new_phone.isdigit() or len(new_phone) != 10:
                    messagebox.showerror("Error", "Phone number must be 10 digits")
                    return
                
                if name and name != new_name:
                    del self.whatsapp_contacts[name]
                
                self.whatsapp_contacts[new_name] = new_phone
                refresh_whatsapp_contacts()
                edit_window.destroy()

            # Buttons frame with more padding
            buttons_frame = ttk.Frame(card)
            buttons_frame.pack(pady=20, padx=20, fill=tk.X)  # Increased padding

            # Save button with custom style
            save_btn = ttk.Button(
                buttons_frame,
                text="Save (Ctrl+S)",
                command=save_contact,
                style="Accent.TButton"
            )
            save_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)  # Increased padding

            # Cancel button
            cancel_btn = ttk.Button(
                buttons_frame,
                text="Cancel (Esc)",
                command=edit_window.destroy
            )
            cancel_btn.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=5)  # Increased padding

            # Configure keyboard shortcuts
            edit_window.bind("<Control-s>", lambda e: save_contact())
            edit_window.bind("<Escape>", lambda e: edit_window.destroy())

            # Focus the name entry
            name_entry.focus_set()

        def delete_email_contact(name):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
                del self.email_contacts[name]
                refresh_email_contacts()

        def delete_whatsapp_contact(name):
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
                del self.whatsapp_contacts[name]
                refresh_whatsapp_contacts()

        # Initial refresh
        refresh_email_contacts()
        refresh_whatsapp_contacts()

    def main_process(self):
        """Main function to process commands."""
        while self.listening:
            request = self.command()

            if not request:
                continue  # Skip empty commands

            if "hello" in request or "hi" in request or "hey" in request:
                self.speak("Welcome! How can I assist you?")

            elif "play music" in request or "play song" in request:
                self.speak("Playing song for you.")
                songs = [
                    "https://www.youtube.com/watch?v=1G4isv_Fylg",
                    "https://www.youtube.com/watch?v=pElk1ShPrcE",
                    "https://youtube.com/playlist?list=PLzo8U24DZFeqD4f6ndxeioj5GbxI_xM78&si=MG02jqW4ku2Oqw9r",
                    "https://www.youtube.com/watch?v=1cDoRqPnCXU",
                ]
                webbrowser.open(random.choice(songs))

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

            elif "send whatsapp message" in request or "send whatsapp" in request:
                self.speak("To whom should I send the message? You can say a contact name or phone number.")
                recipient = self.command()
                if not recipient:
                    self.speak("I couldn't get the recipient.")
                    continue

                self.speak("What is the message?")
                message = self.command()
                if not message:
                    self.speak("I couldn't get the message.")
                    continue

                self.send_whatsapp_message(recipient, message)

            elif "start dictation" in request or "dictate" in request:
                self.dictate_to_file()

            elif "set reminder" in request or "create reminder" in request:
                self.set_reminder()

            elif "manage reminders" in request or "show reminders" in request or "list reminders" in request:
                self.manage_reminders()

            elif "news" in request or "headlines" in request or "what's the news" in request:
                self.get_news()
            
            elif "tell me a joke" in request or "joke" in request or "tell me another joke" in request:
                self.get_joke()

            elif "manage contacts" in request or "edit contacts" in request:
                self.manage_contacts()

            elif "exit" in request or "stop" in request or "bye" in request:
                self.speak("Goodbye! See you soon.")
                self.listening = False
                self.toggle_listening()  # Update button state

    def exit_app(self):
        """Clean exit from the application."""
        self.listening = False
        if self.assistant_thread and self.assistant_thread.is_alive():
            self.assistant_thread.join(timeout=1)
        self.alarm_manager.stop_checker()  # Stop the alarm checker thread
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
    style.configure(
        "Active.TButton", background="#CF6679", foreground="white", borderwidth=0
    )

    app = ModernVoiceAssistant(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()
