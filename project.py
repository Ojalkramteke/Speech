import re
import json
import time
from datetime import datetime
import requests
from typing import Dict, List, Tuple, Callable, Union, Optional, Any
from dataclasses import dataclass
import speech_recognition as sr
import pyttsx3
import random
import os

# Type aliases
CommandHandler = Callable[[str, str], Union[str, Awaitable[str]]]

@dataclass
class CommandRule:
    patterns: Dict[str, List[re.Pattern]]
    handler: CommandHandler

# Global variables
reminders = []
jokes = {
    'en': [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't eggs tell jokes? They'd crack each other up!",
        "What do you call a fake noodle? An impasta!",
        "How does a penguin build its house? Igloos it together!"
    ],
    'es': [
        "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter!",
        "¿Qué le dice un pez a otro? Nada!",
        "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
        "¿Cómo se llama un boomerang que no vuelve? Palo!",
        "¿Por qué las focas miran hacia arriba? ¡Porque ahí están los focos!"
    ],
    'fr': [
        "Que fait une fraise sur un cheval? Elle monte à la crème!",
        "Pourquoi les poissons n'aiment pas les ordinateurs? Ils ont peur du net!",
        "C'est l'histoire d'un pingouin qui respire par les fesses. Un jour il s'assoit et il meurt!",
        "Qu'est-ce qui est jaune et qui attend? Jonathan!",
        "Qu'est-ce qu'un crocodile qui surveille la pharmacie? Un pharmaguard!"
    ]
}

# Function to get API keys from environment variables
def get_api_keys() -> Dict[str, str]:
    return {
        'weatherApi': os.getenv('WEATHER_API_KEY', ''),
        'newsApi': os.getenv('NEWS_API_KEY', ''),
        'translationApi': os.getenv('TRANSLATION_API_KEY', '')
    }

# Helper function to get language code
def get_base_language(lang_code: str) -> str:
    return lang_code.split('-')[0] if '-' in lang_code else lang_code

# Weather API functionality
async def get_weather(location: str, language: str) -> str:
    api_keys = get_api_keys()
    weather_api_key = api_keys['weatherApi']
    base_language = get_base_language(language)
    
    if not weather_api_key:
        if base_language == 'en':
            return "To get weather information, please set up your Weather API key first."
        else:
            return await translate_text("To get weather information, please set up your Weather API key first.", "en", base_language)
    
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid={weather_api_key}&lang={base_language}"
        )
        response.raise_for_status()
        
        data = response.json()
        temp = round(data['main']['temp'])
        condition = data['weather'][0]['description']
        city_name = data['name']
        
        if base_language == 'en':
            return f"The weather in {city_name} is currently {condition} with a temperature of {temp}°C."
        else:
            english_text = f"The weather in {city_name} is currently {condition} with a temperature of {temp}°C."
            return await translate_text(english_text, "en", base_language)
    except Exception as error:
        print(f"Weather API error: {error}")
        if base_language == 'en':
            return f"Sorry, I couldn't get the weather for {location}. Please try again later."
        else:
            error_msg = f"Sorry, I couldn't get the weather for {location}. Please try again later."
            return await translate_text(error_msg, "en", base_language)

# News API functionality
async def get_news(topic: Optional[str], language: str) -> str:
    api_keys = get_api_keys()
    news_api_key = api_keys['newsApi']
    base_language = get_base_language(language)
    
    if not news_api_key:
        if base_language == 'en':
            return "To get news updates, please set up your News API key first."
        else:
            return await translate_text("To get news updates, please set up your News API key first.", "en", base_language)
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?language={base_language}&apiKey={news_api_key}"
        if topic:
            url += f"&q={topic}"
        
        response = requests.get(url)
        
        if not response.ok:
            # Fallback to English if language not supported
            url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={news_api_key}"
            if topic:
                url += f"&q={topic}"
            fallback_response = requests.get(url)
            fallback_response.raise_for_status()
            data = fallback_response.json()
            return await process_news_results(data, topic, language)
        
        data = response.json()
        return await process_news_results(data, topic, language)
    except Exception as error:
        print(f"News API error: {error}")
        error_msg = "Sorry, I couldn't fetch the latest news. Please try again later."
        return error_msg if base_language == 'en' else await translate_text(error_msg, "en", base_language)

async def process_news_results(data: Dict, topic: Optional[str], language: str) -> str:
    base_language = get_base_language(language)
    
    if not data.get('articles'):
        no_news_msg = f"No recent news found about {topic}." if topic else "No recent headlines found."
        return no_news_msg if base_language == 'en' else await translate_text(no_news_msg, "en", base_language)
    
    # Get the top 3 news items
    top_articles = data['articles'][:3]
    news_items = "\n".join([f"{i+1}. {article['title']}" for i, article in enumerate(top_articles)])
    
    news_msg = f"Here are the latest headlines about {topic}:\n{news_items}" if topic else f"Here are today's top headlines:\n{news_items}"
    return news_msg if base_language == 'en' else await translate_text(news_msg, "en", base_language)

# Translation functionality
async def translate_text(text: str, source_language: str = "auto", target_language: str) -> str:
    api_keys = get_api_keys()
    translation_api_key = api_keys['translationApi']
    
    # Convert language code format if needed
    target_language = get_base_language(target_language)
    source_language = get_base_language(source_language)
    
    # Don't translate if source and target are the same
    if source_language == target_language and source_language != "auto":
        return text
    
    # Use LibreTranslate API
    try:
        payload = {
            "q": text,
            "source": source_language,
            "target": target_language,
            "format": "text",
        }
        
        # Add API key if available
        if translation_api_key:
            payload["api_key"] = translation_api_key
        
        response = requests.post("https://libretranslate.de/translate", json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data['translatedText']
    except Exception as error:
        print(f"Translation API error: {error}")
        return text

# Email sending (mock implementation)
async def send_email(to: str, subject: str, body: str, language: str) -> str:
    print(f"Email to: {to}, Subject: {subject}, Body: {body}")
    base_language = get_base_language(language)
    response = f"Email sent to {to} with subject \"{subject}\"."
    return response if base_language == 'en' else await translate_text(response, "en", base_language)

# Reminder system
async def set_reminder(text: str, minutes: int, language: str) -> str:
    reminder_id = int(time.time())
    reminder_time = datetime.now() + timedelta(minutes=minutes)
    base_language = get_base_language(language)
    
    reminders.append({
        "id": reminder_id,
        "text": text,
        "time": reminder_time
    })
    
    # In a real implementation, you'd set up a background task to trigger the reminder
    # This is a simplified version
    print(f"REMINDER SET: Will remind to \"{text}\" at {reminder_time}")
    
    response = f"I'll remind you to \"{text}\" in {minutes} minute{'s' if minutes != 1 else ''}."
    return response if base_language == 'en' else await translate_text(response, "en", base_language)

# Language pattern maps
language_patterns = {
    'en': {
        'greeting': [
            re.compile(r'^(?:hey|hello|hi)(?:.*)$', re.IGNORECASE),
            re.compile(r'^(?:greetings|howdy)(?:.*)$', re.IGNORECASE)
        ],
        # ... (other English patterns)
    },
    'es': {
        'greeting': [
            re.compile(r'^(?:hola|oye|buenos días|buenas tardes)(?:.*)$', re.IGNORECASE)
        ],
        # ... (other Spanish patterns)
    },
    # ... (other languages)
}

def get_patterns_for_language(language: str, pattern_type: str) -> List[re.Pattern]:
    base_language = get_base_language(language)
    lang_patterns = language_patterns.get(base_language, {})
    
    if pattern_type in lang_patterns:
        return lang_patterns[pattern_type]
    
    # Fallback to English patterns
    return language_patterns.get('en', {}).get(pattern_type, [])

async def get_joke(language: str) -> str:
    base_language = get_base_language(language)
    
    if base_language in jokes:
        return random.choice(jokes[base_language])
    
    # Otherwise, get an English joke and translate it
    joke = random.choice(jokes['en'])
    return await translate_text(joke, "en", base_language)

def create_command_rules() -> List[CommandRule]:
    return [
        # Basic greeting patterns
        CommandRule(
            patterns={
                'en': get_patterns_for_language('en', 'greeting'),
                'es': get_patterns_for_language('es', 'greeting'),
                'fr': get_patterns_for_language('fr', 'greeting'),
                'default': get_patterns_for_language('default', 'greeting')
            },
            handler=async lambda query, language: {
                'en': "Hello! How can I help you today?",
                'es': "¡Hola! ¿Cómo puedo ayudarte hoy?",
                'fr': "Bonjour! Comment puis-je vous aider aujourd'hui?",
                'de': "Hallo! Wie kann ich Ihnen heute helfen?",
                'it': "Ciao! Come posso aiutarti oggi?",
                'pt': "Olá! Como posso ajudá-lo hoje?",
                'hi': "नमस्ते! आज मैं आपकी कैसे मदद कर सकता हूँ?",
                'mr': "नमस्कार! आज मी तुमची कशी मदत करू शकतो?",
                'ml': "ഹലോ! ഞാൻ ഇന്ന് നിങ്ങളെ എങ്ങനെ സഹായിക്കാൻ കഴിയും?",
                'ja': "こんにちは！本日はどのようにお手伝いできますか？",
                'ko': "안녕하세요! 오늘 어떻게 도와드릴까요?",
                'zh': "你好！今天我能帮你什么？",
                'ru': "Здравствуйте! Чем я могу вам помочь сегодня?",
                'ar': "مرحبا! كيف يمكنني مساعدتك اليوم؟"
            }.get(get_base_language(language), 
                await translate_text("Hello! How can I help you today?", "en", get_base_language(language)))
        ),
        # ... (other command rules)
    ]

async def process_user_input(input_text: str, language: str = 'en-US') -> str:
    rules = create_command_rules()
    base_language = get_base_language(language)
    
    for rule in rules:
        # First try with language-specific patterns
        lang_patterns = rule.patterns.get(base_language, rule.patterns.get('default', []))
        
        for pattern in lang_patterns:
            if pattern.match(input_text):
                try:
                    return await rule.handler(input_text, language)
                except Exception as error:
                    print(f"Error processing command: {error}")
                    error_msg = "Sorry, I encountered an error while processing your request."
                    return error_msg if base_language == 'en' else await translate_text(error_msg, "en", base_language)
    
    # If no match in the language-specific patterns, try translating to English
    if base_language != 'en':
        try:
            translated_input = await translate_text(input_text, base_language, 'en')
            
            # Now check with English patterns
            for rule in rules:
                eng_patterns = rule.patterns.get('en', [])
                
                for pattern in eng_patterns:
                    if pattern.match(translated_input):
                        try:
                            return await rule.handler(translated_input, language)
                        except Exception as error:
                            print(f"Error processing translated command: {error}")
                            return await translate_text("Sorry, I encountered an error while processing your request.", "en", base_language)
        except Exception as error:
            print(f"Translation error: {error}")
    
    # Fallback response
    fallback_msg = "I'm not sure how to help with that yet. You can try asking me about the weather, setting a reminder, or searching for something."
    return fallback_msg if base_language == 'en' else await translate_text(fallback_msg, "en", base_language)

def setup_speech_recognition(language: str):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    def recognize_speech():
        with microphone as source:
            print("Listening...")
            audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language=language)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Recognition error: {e}")
            return None
    
    return recognize_speech

def speak_response(text: str, language: str):
    engine = pyttsx3.init()
    
    # Try to set voice for the language
    voices = engine.getProperty('voices')
    for voice in voices:
        if language.split('-')[0] in voice.languages[0].lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.say(text)
    engine.runAndWait()