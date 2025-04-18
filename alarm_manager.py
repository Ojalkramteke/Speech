import datetime
import threading
import time
import json
import os
import winsound
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import tkinter as tk
from tkinter import messagebox

@dataclass
class Alarm:
    id: str
    time: str  # HH:MM format
    days: List[str]  # List of days: ["Monday", "Tuesday", etc.]
    label: str
    sound_file: str
    is_active: bool = True

@dataclass
class Reminder:
    id: str
    datetime: str  # ISO format
    label: str
    sound_file: str
    is_active: bool = True

class AlarmManager:
    def __init__(self):
        self.alarms: List[Alarm] = []
        self.reminders: List[Reminder] = []
        self.checker_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.load_data()
        
        # Default sound file path - you can change this
        self.default_sound = "alarm.wav"
        
        # Start the checker thread
        self.start_checker()

    def load_data(self):
        """Load alarms and reminders from JSON file"""
        try:
            if os.path.exists('alarms.json'):
                with open('alarms.json', 'r') as f:
                    data = json.load(f)
                    self.alarms = [Alarm(**alarm) for alarm in data.get('alarms', [])]
                    self.reminders = [Reminder(**reminder) for reminder in data.get('reminders', [])]
        except Exception as e:
            print(f"Error loading alarms data: {e}")

    def save_data(self):
        """Save alarms and reminders to JSON file"""
        try:
            data = {
                'alarms': [asdict(alarm) for alarm in self.alarms],
                'reminders': [asdict(reminder) for reminder in self.reminders]
            }
            with open('alarms.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving alarms data: {e}")

    def create_alarm(self, time: str, days: List[str], label: str, sound_file: Optional[str] = None) -> Alarm:
        """Create a new alarm"""
        try:
            # Validate time format (HH:MM)
            datetime.datetime.strptime(time, "%H:%M")
            
            # Generate a unique ID using timestamp
            alarm_id = str(int(time.time()))
            
            alarm = Alarm(
                id=alarm_id,
                time=time,
                days=days,
                label=label,
                sound_file=sound_file or self.default_sound
            )
            self.alarms.append(alarm)
            self.save_data()
            return alarm
        except ValueError as e:
            print(f"Invalid time format: {e}")
            raise ValueError("Time must be in HH:MM format")
        except Exception as e:
            print(f"Error creating alarm: {e}")
            raise

    def create_reminder(self, datetime_str: str, label: str, sound_file: Optional[str] = None) -> Reminder:
        """Create a new reminder"""
        try:
            # Validate datetime format
            datetime.datetime.fromisoformat(datetime_str)
            
            # Generate a unique ID using timestamp
            reminder_id = str(int(time.time()))
            
            reminder = Reminder(
                id=reminder_id,
                datetime=datetime_str,
                label=label,
                sound_file=sound_file or self.default_sound
            )
            self.reminders.append(reminder)
            self.save_data()
            return reminder
        except ValueError as e:
            print(f"Invalid datetime format: {e}")
            raise ValueError("Datetime must be in ISO format (YYYY-MM-DDTHH:MM:00)")
        except Exception as e:
            print(f"Error creating reminder: {e}")
            raise

    def edit_alarm(self, alarm_id: str, **kwargs) -> Optional[Alarm]:
        """Edit an existing alarm"""
        for alarm in self.alarms:
            if alarm.id == alarm_id:
                for key, value in kwargs.items():
                    if hasattr(alarm, key):
                        setattr(alarm, key, value)
                self.save_data()
                return alarm
        return None

    def edit_reminder(self, reminder_id: str, **kwargs) -> Optional[Reminder]:
        """Edit an existing reminder"""
        for reminder in self.reminders:
            if reminder.id == reminder_id:
                for key, value in kwargs.items():
                    if hasattr(reminder, key):
                        setattr(reminder, key, value)
                self.save_data()
                return reminder
        return None

    def delete_alarm(self, alarm_id: str) -> bool:
        """Delete an alarm"""
        try:
            for i, alarm in enumerate(self.alarms):
                if alarm.id == alarm_id:
                    self.alarms.pop(i)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting alarm: {e}")
            return False

    def delete_reminder(self, reminder_id: str) -> bool:
        """Delete a reminder"""
        try:
            for i, reminder in enumerate(self.reminders):
                if reminder.id == reminder_id:
                    self.reminders.pop(i)
                    self.save_data()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting reminder: {e}")
            return False

    def play_sound(self, sound_file: str):
        """Play the alarm/reminder sound"""
        try:
            # Check if sound file exists
            if not os.path.exists(sound_file):
                print(f"Sound file not found: {sound_file}")
                # Fallback to system beep
                winsound.Beep(1000, 1000)
                return
                
            winsound.PlaySound(sound_file, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Error playing sound: {e}")
            # Fallback to system beep
            winsound.Beep(1000, 1000)

    def show_notification(self, title: str, message: str):
        """Show a notification window"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo(title, message)
        root.destroy()

    def check_alarms(self):
        """Check if any alarms should trigger"""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")

        for alarm in self.alarms:
            if not alarm.is_active:
                continue

            if alarm.time == current_time and current_day in alarm.days:
                self.play_sound(alarm.sound_file)
                self.show_notification("Alarm", f"Alarm: {alarm.label}")

    def check_reminders(self):
        """Check if any reminders should trigger"""
        now = datetime.datetime.now()

        for reminder in self.reminders:
            if not reminder.is_active:
                continue

            reminder_time = datetime.datetime.fromisoformat(reminder.datetime)
            if now >= reminder_time:
                self.play_sound(reminder.sound_file)
                self.show_notification("Reminder", f"Reminder: {reminder.label}")
                # Remove one-time reminders after triggering
                self.delete_reminder(reminder.id)

    def checker_loop(self):
        """Main loop to check for alarms and reminders"""
        while self.is_running:
            self.check_alarms()
            self.check_reminders()
            time.sleep(30)  # Check every 30 seconds

    def start_checker(self):
        """Start the alarm/reminder checker thread"""
        if not self.checker_thread or not self.checker_thread.is_alive():
            self.is_running = True
            self.checker_thread = threading.Thread(target=self.checker_loop)
            self.checker_thread.daemon = True
            self.checker_thread.start()

    def stop_checker(self):
        """Stop the alarm/reminder checker thread"""
        self.is_running = False
        if self.checker_thread:
            self.checker_thread.join() 