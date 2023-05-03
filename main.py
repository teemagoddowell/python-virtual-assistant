import speech_recognition as sr
import pyttsx3
import time
import openai
import os
import requests
from bs4 import BeautifulSoup
import pytube
import datetime
from pytube.exceptions import RegexMatchError

# OPENAI API KEYS
openai.api_key = os.environ["OPENAI_APIKEYS"]

NEWS_URL = "https://www.engadget.com"

# Initialize Speech Recogntion and Text to Speech Engine
recognizer = sr.Recognizer()
microphone = sr.Microphone()
engine = pyttsx3.init()
engine.setProperty("rate", 160)

# Set Voice of TTS
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)


# Run Speech
def engine_speech(speech):
    engine.say(speech)
    engine.runAndWait()


# Add a time delay before starting
time.sleep(1)


# Chat GPT Function
def chat_gpt(gpt_query):
    print("Processing Your Request")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": gpt_query}
        ]
    )

    result = ""
    for choice in response.choices:
        result += choice.message.content
    engine_speech(result)


# Get Jokes
def get_jokes1(category):
    response1 = requests.get(url=f"https://official-joke-api.appspot.com/jokes/{category}/random")
    if response1.status_code == 200:
        joke = response1.json()[0]
        engine_speech(f"{joke['setup']}")
        engine_speech(f"{joke['punchline']}")


def get_jokes2(category):
    response2 = requests.get(url=f"https://v2.jokeapi.dev/joke/{category}")
    if response2.status_code == 200:
        joke = response2.json()
        engine_speech(f"{joke['setup']}")
        engine_speech(f"{joke['delivery']}")


# TECH NEWS
def tech_news():
    news_response = requests.get(NEWS_URL)
    news_data = news_response.text
    news_soup = BeautifulSoup(news_data, "html.parser")
    latest_tech_news = news_soup.find(name="h2", class_="My(0)")
    news_title = latest_tech_news.getText()
    engine_speech(news_title)

    with microphone as techsource:
        engine_speech("Do you need the full news? ")
        new_query = recognizer.listen(techsource)
        news_query = recognizer.recognize_google(new_query)

    if news_query == "yes":
        news_url = NEWS_URL + latest_tech_news.find("a").get("href")
        news_response = requests.get(news_url)
        news_data = news_response.text
        news_soup = BeautifulSoup(news_data, "html.parser")
        news_description = news_soup.find(name="div", class_="article-text").getText()
        engine_speech(news_description)


# CURRENT CRYPTO PRICE
def crypto_price(currency):
    crypto = currency.replace(" current price", "")
    crypto_url = f"https://coinmarketcap.com/currencies/{crypto}"
    crypto_response = requests.get(crypto_url)
    data = crypto_response.text
    soup = BeautifulSoup(data, "html.parser")
    current_price = soup.find(name="div", class_="priceValue")
    if current_price is not None:
        engine_speech(f"One {crypto} is currently worth {current_price.getText()}")
    else:
        engine_speech(f"Sorry, I could not find the current price for {crypto}")


# Download Youtube Video
def download_video(video_url):
    try:
        youtube = pytube.YouTube(video_url, use_oauth=True, allow_oauth_cache=True)
    except RegexMatchError:
        engine_speech(f"Sorry, the video link is invalid")
    else:
        engine_speech("Be patient. I am now downloading your video.")
        video = youtube.streams.get_highest_resolution()
        video.download(output_path="../Downloads")
        engine_speech("Video Downloaded Successfully")


# Current Time
def current_time():
    time_now = datetime.datetime.now().strftime("%I:%M %p")
    engine_speech(time_now)


# WELCOME
# Use speech recognition to listen for voice input
with microphone as source:
    engine_speech("Welcome to Python Virtual Assistant")
    engine_speech("What is your name?")
    name = recognizer.listen(source)
    username = recognizer.recognize_google(name)
    engine_speech(f"Please say your secret key {username}")
    audio = recognizer.listen(source)
    secret_key = recognizer.recognize_google(audio).lower()
    message = f"Welcome {username}, how can I help you today?"


while secret_key == os.environ["SECRET_KEY"]:
    try:
        with microphone as source:
            engine_speech(message)
            message = f"Anything else I can help you with {username}?"
            query = recognizer.listen(source)
            my_query = recognizer.recognize_google(query).lower()

        # STOP PROGRAM
        if my_query == "stop":
            break
        if my_query == "tell me a joke":
            joke_cat = "general"
            get_jokes1(joke_cat)
        elif "programming joke" in my_query:
            joke_cat = "programming"
            get_jokes1(joke_cat)
        elif "knock knock" in my_query:
            joke_cat = "knock-knock"
            get_jokes1(joke_cat)
        elif "dark joke" in my_query:
            joke_cat = "Dark"
            get_jokes2(joke_cat)
        elif "spooky joke" in my_query:
            joke_cat = "Spooky"
            get_jokes2(joke_cat)
        elif "download a video" in my_query:
            engine_speech("Give me the link")
            video_link = input("Paste Video Link: ")
            download_video(video_link)
        elif "tech news" in my_query:
            tech_news()
        elif "current price" in my_query:
            crypto_price(my_query)
        elif "time now" in my_query:
            current_time()
        else:
            chat_gpt(my_query)

    except sr.UnknownValueError:
        # Handle unrecognised Speech
        engine_speech("Sorry, I couldn't recognise your voice. Please speak louder.")

    except requests.exceptions.RequestException:
        # Handle error fetching joke
        engine_speech("Sorry, there was an error fetching the joke. Please try again later.")


if secret_key != os.environ["SECRET_KEY"]:
    engine_speech("Sorry, you don't have access to this program.")
else:
    engine_speech(f"Have a nice day {username}.")
