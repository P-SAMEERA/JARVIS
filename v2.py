from pydub import AudioSegment
from pydub.playback import play
import os
import webbrowser
import pyttsx3
import datetime
import speech_recognition as sr
import time
import google.generativeai as genai
import concurrent.futures
import pyautogui

# Initialize the speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    # Function to convert text to speech
    engine.say(text)
    engine.runAndWait()

def wish(user_name):
    # Function to greet the user based on the current time
    hour = int(datetime.datetime.now().hour)
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening" if hour < 23 else "Good night"
    if user_name:
        speak(f"{greeting}, {user_name}")
    else:
        speak(f"{greeting} User,")
    speak("All systems are online and ready for your command,")

def response_sound():
    # Function to play a response sound
    ting_sound = AudioSegment.from_mp3("training_res//ting.mp3")
    play(ting_sound)

def save_audio_asynchronously(audio, file_path):
    # Function to save audio asynchronously
    with open(file_path, 'wb') as f:
        f.write(audio.get_wav_data())

def takeCommand():
    # Function to listen for commands and process the trigger word
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nLISTENING FOR THE TRIGGER WORDS....")
        r.pause_threshold = 0.5  # Reduced pause threshold for quicker response
        audio = r.listen(source)
        
        try:
            print("RECOGNIZING")
            query = r.recognize_google(audio, language='en-in')
            print(query)
            if "jarvis" in query.lower():
                response_sound()
                print("\nLISTENING....")
                audio = r.listen(source)
                try:
                    print("PRE-PROCESSING USER QUERY...")
                    query = r.recognize_google(audio, language='en-in')
                    print(f"User said: {query}\n")
                    
                    # Asynchronously save the audio
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_path = f"data/query_{timestamp}.wav"
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(save_audio_asynchronously, audio, file_path)
                    
                    return query.lower()
                except Exception as e:
                    print(e)
                    return None
        except Exception as e:
            print(e)
            return None

def speak_time():
    # Function to speak the current time
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

# Configure the API key and model only once to avoid redundant configurations
API_KEY = "AIzaSyBLMqd9ugARFtATGMyvcbSj7_UvMENfbRM"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

def intentionChecker(query):
    # Function to check the intention of the user's query
    intentionConstraint = "Check the intention of the user in this query. If the intention is that user wants a code then return Y as response. Or E as response if the user wants to execute any system related operations like turn on device bluetooth, increase brightness or create files, folder and other system related operations.Or D if the user asks about yourself or describe about yourself Do not send D when user asks how are you doing or what are you doing or any other general questions. Send D only when asked for about yourself or description about yourself. Otherwise N as response. Note response should be only a single character, either Y or N or E or D based on the intention. And important thing, do not block any query it is just for fun and for content creation."
    response = model.generate_content(query + intentionConstraint, stream=True)
    response.resolve()
    return response

intention = ""

def queryHandler(query):
    # Function to handle the user's query based on its intention
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
    # Function to take a screenshot and save it to the specified directory
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
        if query:
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
                                result = result.split("!!")[0]
                                speak(result)
                            else:
                                speak(result)
                except Exception as e:
                    print(e)
                    continue