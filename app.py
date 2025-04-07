from flask import Flask, render_template, request
from datetime import datetime
from assistant import (
    speak, search_web, open_application, change_volume,
    get_weather, set_alarm, set_reminder
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    response = ""
    if request.method == "POST":
        user_input = request.form.get("command").lower()

        if "hello" in user_input or "hi" in user_input:
            response = "Welcome! How can I assist you?"
            speak(response)

        elif "play music" in user_input:
            response = "Playing music!"
            speak(response)

        elif "time" in user_input:
            now = datetime.now().strftime("%H:%M")
            response = f"The current time is {now}"
            speak(response)

        elif "date" in user_input:
            today = datetime.now().strftime("%d-%m-%Y")
            response = f"Today's date is {today}"
            speak(response)

        elif "search google for" in user_input:
            query = user_input.replace("search google for", "").strip()
            search_web(query, "google")
            response = f"Searching Google for {query}"

        elif "search youtube for" in user_input:
            query = user_input.replace("search youtube for", "").strip()
            search_web(query, "youtube")
            response = f"Searching YouTube for {query}"

        elif "search maps for" in user_input:
            query = user_input.replace("search maps for", "").strip()
            search_web(query, "maps")
            response = f"Searching Maps for {query}"

        elif "open" in user_input:
            app_name = user_input.replace("open", "").strip()
            open_application(app_name)
            response = f"Opening {app_name}"

        elif "increase volume" in user_input:
            change_volume("increase")
            response = "Volume increased"

        elif "decrease volume" in user_input:
            change_volume("decrease")
            response = "Volume decreased"

        elif "mute volume" in user_input:
            change_volume("mute")
            response = "Volume muted"

        elif "unmute volume" in user_input:
            change_volume("unmute")
            response = "Volume unmuted"

        elif "weather" in user_input or "what's the weather" in user_input:
            response = get_weather("Mumbai")  # Default city or extract from input if needed

        elif "set alarm" in user_input:
            set_alarm()
            response = "Opening clock to set alarm"

        elif "set reminder" in user_input:
            set_reminder()
            response = "Opening clock to set reminder"

        elif "exit" in user_input or "stop" in user_input:
            response = "Goodbye!"
            speak(response)

        else:
            response = "Sorry, I couldn't understand that."
            speak(response)

    return render_template("index.html", response=response)
