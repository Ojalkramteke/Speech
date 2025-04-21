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
                # "Set Alarm",
                # "Manage Alarms",
                "Tell a Joke",
                "Set Reminder",
                "Manage Reminders",
                # "Play Music",
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
        # elif action == "Set Alarm":
        #     self.show_manual_alarm_input()
        # elif action == "Manage Alarms":
        #     self.manage_alarms()
        elif action == "Set Reminder":
            self.show_manual_reminder_input()
        elif action == "Manage Reminders":
            self.manage_reminders()
        elif action == "Tell a Joke":
            self.get_joke()
        # elif action == "Play Music":
        #     self.play_music()

    # def show_manual_alarm_input(self):
    #     """Show manual alarm input form"""
    #     alarm_window = tk.Toplevel(self.root)
    #     alarm_window.title("Set Alarm")
    #     alarm_window.geometry("400x500")
    #     alarm_window.configure(bg=self.bg_color)
    #     alarm_window.resizable(False, False)

    #     # Center the window
    #     window_width = alarm_window.winfo_reqwidth()
    #     window_height = alarm_window.winfo_reqheight()
    #     position_right = int(alarm_window.winfo_screenwidth() / 2 - window_width / 2)
    #     position_down = int(alarm_window.winfo_screenheight() / 2 - window_height / 2)
    #     alarm_window.geometry(f"+{position_right}+{position_down}")

    #     card = ttk.Frame(alarm_window, style="Card.TFrame")
    #     card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    #     # Time entry
    #     ttk.Label(card, text="Time (HH:MM):", font=("Helvetica", 11)).pack(pady=(10, 5))
    #     time_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
    #     time_entry.pack(pady=5, padx=20, ipady=5)
    #     time_entry.insert(0, "00:00")  # Default time

    #     # Days selection
    #     ttk.Label(card, text="Days:", font=("Helvetica", 11)).pack(pady=(10, 5))
    #     days_frame = ttk.Frame(card)
    #     days_frame.pack(pady=5, padx=20)
        
    #     day_vars = {}
    #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #     for day in days:
    #         var = tk.BooleanVar()
    #         day_vars[day] = var
    #         ttk.Checkbutton(days_frame, text=day, variable=var).pack(anchor=tk.W)

    #     # Label entry
    #     ttk.Label(card, text="Label:", font=("Helvetica", 11)).pack(pady=(10, 5))
    #     label_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
    #     label_entry.pack(pady=5, padx=20, ipady=5)

    #     # Buttons frame
    #     buttons_frame = ttk.Frame(card)
    #     buttons_frame.pack(pady=20)

    #     # Voice input button
    #     voice_btn = ttk.Button(buttons_frame, text="🎤 Voice Input", command=lambda: [alarm_window.destroy(), self.set_alarm()])
    #     voice_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    #     # Submit button
    #     submit_btn = ttk.Button(buttons_frame, text="Set Alarm", command=lambda: self.on_submit_alarm(time_entry.get(), day_vars, label_entry.get(), alarm_window))
    #     submit_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

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

    # def on_submit_alarm(self, time_str, day_vars, label, window):
    #     """Handle alarm submission from manual input"""
    #     try:
    #         days = [day for day, var in day_vars.items() if var.get()]
            
    #         if not time_str or not days or not label:
    #             messagebox.showerror("Error", "Please fill in all fields")
    #             return
            
    #         # Validate time format
    #         try:
    #             datetime.datetime.strptime(time_str, "%H:%M")
    #         except ValueError:
    #             messagebox.showerror("Error", "Time must be in HH:MM format (e.g., 14:30)")
    #             return
            
    #         self.alarm_manager.create_alarm(time_str, days, label)
    #         self.speak(f"Alarm set for {time_str} on {', '.join(days)}")
    #         window.destroy()
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to set alarm: {str(e)}")

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

    # def set_alarm(self):
    #     """Create a new alarm through GUI"""
    #     def show_manual_input():
    #         alarm_window = tk.Toplevel(self.root)
    #         alarm_window.title("Set Alarm")
    #         alarm_window.geometry("400x500")
    #         alarm_window.configure(bg=self.bg_color)
    #         alarm_window.resizable(False, False)

    #         # Center the window
    #         window_width = alarm_window.winfo_reqwidth()
    #         window_height = alarm_window.winfo_reqheight()
    #         position_right = int(alarm_window.winfo_screenwidth() / 2 - window_width / 2)
    #         position_down = int(alarm_window.winfo_screenheight() / 2 - window_height / 2)
    #         alarm_window.geometry(f"+{position_right}+{position_down}")

    #         card = ttk.Frame(alarm_window, style="Card.TFrame")
    #         card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    #         # Time entry
    #         ttk.Label(card, text="Time (HH:MM):", font=("Helvetica", 11)).pack(pady=(10, 5))
    #         time_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
    #         time_entry.pack(pady=5, padx=20, ipady=5)
    #         time_entry.insert(0, "00:00")  # Default time

    #         # Days selection
    #         ttk.Label(card, text="Days:", font=("Helvetica", 11)).pack(pady=(10, 5))
    #         days_frame = ttk.Frame(card)
    #         days_frame.pack(pady=5, padx=20)
            
    #         day_vars = {}
    #         days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #         for day in days:
    #             var = tk.BooleanVar()
    #             day_vars[day] = var
    #             ttk.Checkbutton(days_frame, text=day, variable=var).pack(anchor=tk.W)

    #         # Label entry
    #         ttk.Label(card, text="Label:", font=("Helvetica", 11)).pack(pady=(10, 5))
    #         label_entry = ttk.Entry(card, width=25, font=("Helvetica", 11))
    #         label_entry.pack(pady=5, padx=20, ipady=5)

    #         # Buttons frame
    #         buttons_frame = ttk.Frame(card)
    #         buttons_frame.pack(pady=20)

    #         # Voice input button
    #         voice_btn = ttk.Button(buttons_frame, text="🎤 Voice Input", command=lambda: [alarm_window.destroy(), self.set_alarm()])
    #         voice_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    #         # Submit button
    #         submit_btn = ttk.Button(buttons_frame, text="Set Alarm", command=lambda: self.on_submit_alarm(time_entry.get(), day_vars, label_entry.get(), alarm_window))
    #         submit_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)

    #     def on_submit(time_str, day_vars, label, window):
    #         try:
    #             days = [day for day, var in day_vars.items() if var.get()]
                
    #             if not time_str or not days or not label:
    #                 messagebox.showerror("Error", "Please fill in all fields")
    #                 return
                
    #             # Validate time format
    #             try:
    #                 datetime.datetime.strptime(time_str, "%H:%M")
    #             except ValueError:
    #                 messagebox.showerror("Error", "Time must be in HH:MM format (e.g., 14:30)")
    #                 return
                
    #             self.alarm_manager.create_alarm(time_str, days, label)
    #             self.speak(f"Alarm set for {time_str} on {', '.join(days)}")
    #             window.destroy()
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to set alarm: {str(e)}")

    #     def voice_input():
    #         self.speak("What time would you like to set the alarm for?")
    #         spoken_time = self.command()
    #         if not spoken_time:
    #             self.speak("I couldn't hear the time. Would you like to enter it manually?")
    #             if "yes" in self.command().lower():
    #                 show_manual_input()
    #             return

    #         time_str = self.parse_spoken_time(spoken_time)
    #         if not time_str:
    #             self.speak("I couldn't understand the time. Would you like to enter it manually?")
    #             if "yes" in self.command().lower():
    #                 show_manual_input()
    #             return

    #         self.speak("Which days would you like the alarm to repeat? Say 'every day' for all days, or list specific days.")
    #         days_input = self.command().lower()
    #         if not days_input:
    #             self.speak("I couldn't hear the days. Would you like to enter them manually?")
    #             if "yes" in self.command().lower():
    #                 show_manual_input()
    #             return

    #         days = []
    #         if "every day" in days_input:
    #             days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #         else:
    #             for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
    #                 if day in days_input:
    #                     days.append(day.capitalize())
    #             if not days:
    #                 self.speak("I couldn't understand the days. Would you like to enter them manually?")
    #                 if "yes" in self.command().lower():
    #                     show_manual_input()
    #                 return

    #         self.speak("What would you like to label this alarm?")
    #         label = self.command()
    #         if not label:
    #             self.speak("I couldn't hear the label. Would you like to enter it manually?")
    #             if "yes" in self.command().lower():
    #                 show_manual_input()
    #             return

    #         try:
    #             self.alarm_manager.create_alarm(time_str, days, label)
    #             self.speak(f"Alarm set for {time_str} on {', '.join(days)}")
    #         except Exception as e:
    #             self.speak(f"Sorry, I couldn't set the alarm. Error: {str(e)}")
    #             self.speak("Would you like to try entering it manually?")
    #             if "yes" in self.command().lower():
    #                 show_manual_input()

    #     # Start with voice input by default
    #     voice_input()

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

    # def manage_alarms(self):
    #     """Show and manage existing alarms"""
    #     def delete_alarm(alarm_id):
    #         try:
    #             if self.alarm_manager.delete_alarm(alarm_id):
    #                 self.speak("Alarm deleted")
    #                 refresh_alarms()
    #             else:
    #                 self.speak("Failed to delete alarm")
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to delete alarm: {str(e)}")

        # def toggle_alarm(alarm_id):
        #     try:
        #         alarm = next((a for a in self.alarm_manager.alarms if a.id == alarm_id), None)
        #         if alarm:
        #             alarm = self.alarm_manager.edit_alarm(alarm_id, is_active=not alarm.is_active)
        #             if alarm:
        #                 status = "activated" if alarm.is_active else "deactivated"
        #                 self.speak(f"Alarm {status}")
        #                 refresh_alarms()
        #     except Exception as e:
        #         messagebox.showerror("Error", f"Failed to toggle alarm: {str(e)}")

        # def refresh_alarms():
        #     # Clear existing items
        #     for widget in alarms_frame.winfo_children():
        #         widget.destroy()

        #     # Add alarms
        #     for alarm in self.alarm_manager.alarms:
        #         alarm_frame = ttk.Frame(alarms_frame, style="Card.TFrame")
        #         alarm_frame.pack(fill=tk.X, pady=5, padx=5)

        #         ttk.Label(
        #             alarm_frame,
        #             text=f"{alarm.time} - {alarm.label} ({', '.join(alarm.days)})",
        #             font=("Helvetica", 10)
        #         ).pack(side=tk.LEFT, padx=5)

        #         status = "Active" if alarm.is_active else "Inactive"
        #         ttk.Button(
        #             alarm_frame,
        #             text=status,
        #             command=lambda id=alarm.id: toggle_alarm(id)
        #         ).pack(side=tk.LEFT, padx=5)

        #         ttk.Button(
        #             alarm_frame,
        #             text="Delete",
        #             command=lambda id=alarm.id: delete_alarm(id)
        #         ).pack(side=tk.RIGHT, padx=5)

        # manage_window = tk.Toplevel(self.root)
        # manage_window.title("Manage Alarms")
        # manage_window.geometry("500x400")
        # manage_window.configure(bg=self.bg_color)

        # # Center the window
        # window_width = manage_window.winfo_reqwidth()
        # window_height = manage_window.winfo_reqheight()
        # position_right = int(manage_window.winfo_screenwidth() / 2 - window_width / 2)
        # position_down = int(manage_window.winfo_screenheight() / 2 - window_height / 2)
        # manage_window.geometry(f"+{position_right}+{position_down}")

        # # Add new alarm button
        # ttk.Button(
        #     manage_window,
        #     text="Add New Alarm",
        #     command=self.set_alarm
        # ).pack(pady=10)

        # # Alarms list
        # alarms_frame = ttk.Frame(manage_window)
        # alarms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # refresh_alarms()

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
