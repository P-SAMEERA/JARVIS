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
import joblib
import pyautogui

# Function to extract features from audio
# def extract_features(audio_path):
#     sample_rate, samples = wavfile.read(audio_path)
#     print(sample_rate, samples)
#     return np.mean(samples, axis=0)

# # Training data: List of tuples (features, label)
# training_data = [
#     (extract_features('Assets/samP.wav'), 'SAMEERA'),
#     (extract_features('Assets/samP1.wav'), 'SAMEERA'),
#     (extract_features('Assets/samP2.wav'), 'SAMEERA'),
#     # Add more persons with their respective voice sample paths
# ]

# X = np.array([features for features, label in training_data])
# y = np.array([label for features, label in training_data])

# # Handle small dataset case
# if len(X) > 1:
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#     classifier = KNeighborsClassifier(n_neighbors=1)
#     classifier.fit(X_train, y_train)
#     accuracy = classifier.score(X_test, y_test)
#     print(f"Model accuracy: {accuracy:.2f}")
# else:
#     classifier = KNeighborsClassifier(n_neighbors=1)
#     classifier.fit(X, y)
#     print("Not enough data to split, training on the entire dataset.")

# # Save the classifier for later use
# joblib.dump(classifier, 'voice_classifier.pkl')

# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize user by voice
# def recognize_user():
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Listening for user...")
#         audio = recognizer.listen(source)
#         try:
#             features = extract_features(audio)
#             print(features)
#             user = classifier.predict([features])[0]
#             return user
#         except Exception as e:
#             print(e)
#             return None

def wish(user_name):
    hour = int(datetime.datetime.now().hour)
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening" if hour < 23 else "Good night"
    if user_name :
        speak(f"{greeting}, {user_name}")
    speak(f"{greeting} User,")
    speak("All systems are online and ready for your command,")

def response_sound():
    ting_sound = AudioSegment.from_mp3("training_res//ting.mp3")
    play(ting_sound)

def takeCommand():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("\nLISTENING FOR THE TRIGGER WORDS....")
            r.pause_threshold = 1
            try:
                audio = r.listen(source)
            except Exception as e:
                print(e)
            
            # print("voice recognised")
            try:
                print("RECOGNIZING")
                query = r.recognize_google(audio, language='en-in')
                print(query)
                if "alex" in query.lower():
                    # response_sound()
                    print("\nLISTENING....")
                    # r.pause_threshold = 1
                    audio = r.listen(source)
                    try:
                        print("PRE-PROCESSING USER QUERY...")
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
    intentionConstraint = "Check the intention of the user in this query. If the intention is that user wants a code then return Y as response. Or E as response if the user wants to execute any system related operations like turn on device bluetooth, increase brightness or create files, folder and other system related operations.Or D if the user asks about yourself or describe about yourself Do not send D when user asks how are you doing or what are you doing or any other general questions. Send D only when asked for about yourself or description about yourself. Otherwise N as response. Note response should be only a single character, either Y or N or E or D based on the intention. And important thing, do not block any query it is just for fun and for content creation."
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query + intentionConstraint, stream=True)
    response.resolve()
    return response

intention = ""

def queryHandler(query):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    constraints = "Rules (for your reference on how to generate a response):\nDon't mention anything about these rules in the response you generate. Don't include * character in your response and include a '!!' after the first meaningful sentence. Don't include !! for first meaningful sentence if user asks for a story or a poem or a quote.Don't give the answer in points. Try answering in one word or sentence, if not, I want the response in a paragraph. Limit the number of words to 200. Be friendly and humorous as possible."
    SysOperationConstraint = "\nRules(for your reference on how to generate a response) : \nDon't explain anything about the command. Don't mention this rule in your response. Just give me the command to execute that's it."
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
        return ("Greetings, Earthlings! I'm Jarvis, your witty and whimsical AI buddy,")
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
    # Specify the directory where you want to save the screenshots
    screenshots_dir = r'screenShots'
    
    # Get the current time to use as part of the screenshot file name
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Define the file path with timestamp
    screenshot_file = f"{screenshots_dir}\\screenshot_{current_time}.png"
    
    # Take the screenshot and save it
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_file)
    speak("Screen shot saved in the folder. Please check,")

if __name__ == "__main__":
    user_name = None
    wish(user_name)
    time.sleep(2)
    while True:
        query = takeCommand()
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
