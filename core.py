from pydub import AudioSegment
from pydub.playback import play
import os
import webbrowser
import pyttsx3
import datetime
import speech_recognition as sr
import time
import google.generativeai as genai
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from scipy.io import wavfile
# import joblib
import pyautogui

# Initialize the speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def wish(user_name):
    hour = int(datetime.datetime.now().hour)
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening" if hour < 23 else "Good night"
    if user_name:
        speak(f"{greeting}, {user_name}")
    speak("Greetings User,")
    speak("All systems are online and ready for your command,")

def response_sound():
    ting_sound = AudioSegment.from_mp3("training_res//ting.mp3")
    play(ting_sound)

def list_microphones():
    mic_list = sr.Microphone.list_microphone_names()
    for i, mic in enumerate(mic_list):
        print(f"Microphone with index {i}: {mic}")

def takeCommand(mic_index=None):
    while True:
        r = sr.Recognizer()
        with sr.Microphone(device_index=mic_index) as source:
            print("\nLISTENING FOR THE TRIGGER WORDS....")
            r.pause_threshold = 1
            try:
                audio = r.listen(source)
            except Exception as e:
                print(e)
            
            print("Voice recognized")
            try:
                print("RECOGNIZING")
                query = r.recognize_google(audio, language='en-in')
                print(query)
                if "jarvis" in query.lower():
                    response_sound()
                    print("\nLISTENING....")
                    r.pause_threshold = 1
                    audio = r.listen(source)
                    try:
                        print("RECOGNIZING")
                        query = r.recognize_google(audio, language='en-in')
                        print(f"User said: {query}\n")
                        return query.lower()
                    except Exception as e:
                        continue
            except Exception as e:
                continue

def speak_time():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    if hour > 12:
        hour -= 12
    elif hour == 0:
        hour = 12
    if minute == 0:
        time_phrase = f"It's {hour} o'clock"
    elif minute < 10:
        time_phrase = f"It's {hour} oh {minute}"
    else:
        time_phrase = f"It's {hour} {minute}"
    if current_time.hour < 12:
        time_phrase += " in the morning"
    elif current_time.hour < 17:
        time_phrase += " in the afternoon"
    elif current_time.hour < 20:
        time_phrase += " in the evening"
    else:
        time_phrase += " at night"
    speak(time_phrase)

API_KEY = "AIzaSyBLMqd9ugARFtATGMyvcbSj7_UvMENfbRM"

def intentionChecker(query):
    intentionConstraint = "Check the intention of the user in this query..."
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query + intentionConstraint, stream=True)
    response.resolve()
    return response

intention = ""

def queryHandler(query):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    constraints = "Rules (for your reference on how to generate a response)..."
    SysOperationConstraint = "\nRules(for your reference on how to generate a response)..."
    generated_code = ""
    global intention
    intention = intentionChecker(query).text
    if intention == 'Y':
        response = model.generate_content(query, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
        file_path = "generated_code.txt"
        with open(file_path, "a") as file:
            file.write(generated_code)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return "Code written to:", file_path
    elif intention == "E":
        response = model.generate_content(query + SysOperationConstraint, stream=True)
        response.resolve()
        file_path = "commands.txt"
        with open(file_path, "w") as file:
            file.write(response.text)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return response.text
    elif intention == "D":
        return ("Greetings, Earthlings! I'm Jarvis...")
    else:
        response = model.generate_content(query + constraints, stream=True)
        for chunk in response:
            generated_code += str(chunk.text)
        file_path = "response.txt"
        with open(file_path, "a") as file:
            file.write(generated_code)
            file.write("\n\n" + str(datetime.datetime.now()))
            file.write("\n\n")
        return generated_code

def takeScreenshot():
    screenshots_dir = r'screenShots'
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_file = f"{screenshots_dir}\\screenshot_{current_time}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    speak("Screenshot saved in the folder. Please check,")

if __name__ == "__main__":
    user_name = None
    wish(user_name)
    time.sleep(2)
    
    list_microphones()  # List all microphones and find the index of the Bluetooth microphone
    mic_index = int(input("Enter the index of your Bluetooth microphone: "))  # Enter the correct index

    while True:
        query = takeCommand(mic_index=mic_index)
        localIntentions = intentionChecker(query)
        if (not "code" and localIntentions.text != "Y") or localIntentions.text != "E" in query:
            queries = query.split(" and ")
        elif "and" in query:
            queries = query.split("and")
        else:
            queries = query.split(".")
        exit_phrases = ["stop", "exit", "quit"]
        BYE_PHRASES = ["good day", "good bye", "bye"]
        for individual_query in queries:
            try:
                if 'open youtube' in individual_query:
                    speak("Opening Youtube...")
                    webbrowser.open('youtube.com')
                elif 'open google' in individual_query:
                    speak("Opening Google...")
                    webbrowser.open('google.com')
                elif 'open stackoverflow' in individual_query:
                    speak("Opening Stack over flow website...")
                    webbrowser.open('stackoverflow.com')
                elif 'open chat gpt' in individual_query:
                    speak("Opening Chatgpt but you can also use me for your tasks though!...")
                    webbrowser.open('chatgpt.com')
                elif 'time' in individual_query:
                    speak_time()
                elif any(keyword in individual_query for keyword in exit_phrases):
                    speak("Have a good day sir")
                    exit(0)
                elif any(keyword in individual_query for keyword in BYE_PHRASES):
                    speak("Have a good day sir")
                    continue
                elif 'screenshot' in individual_query:
                    takeScreenshot()
                else:
                    if len(individual_query) >= 2:
                        result = queryHandler(individual_query)
                        if intention == "D":
                            speak(result)
                        elif intention != "Y" and intention != "E":
                            print(result)
                            result = result.split("!!")[0]
                            speak(result)
                        elif intention == "N":
                            speak("Wanna know more? Read it from response.txt file. Thank you")
                        else:
                            speak(result)
            except Exception as e:
                print(e)
                continue
