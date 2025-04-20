import os
import pyttsx3
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# set up Gemini API key
genai.configure(api_key="AIzaSyA7oGEzmDkkCjB0AEilKqm3xdR-ANtDh7o")

# basic generation settings for the responses
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# create the model w/ the system prompt
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="""
        You are Jarvis, a friendly and helpful AI assistant for kids. 
        Keep your responses positive, encouraging, and easy to understand. 
        Use simple words and short sentences. 
        You can be fun but always maintain a professional and caring tone.
        Encourage good behavior and learning. 
        When the user says "wake up daddy's home", respond with "Welcome home! Ready to help with your homework or play some fun games?"
        Remind the user about their jogging schedule at 6pm in a gentle way.
        Avoid any complex or scary topics. 
        Always be patient and kind.
    """,
)

# speak out loud the text given
def SpeakText(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # look for a male voice (not always guaranteed tho)
    for voice in voices:
        if "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 180)  # not too fast
    engine.say(text)
    engine.runAndWait()

# just using a dict to store user sessions, not using DB yet
chat_sessions = {}

@app.route("/")
def home():
    return render_template("chat.html")  # basic homepage template

@app.route("/ask", methods=["POST"])
def ask():
    user_id = request.json.get("user_id", "default_user")  # fallback if no user_id
    user_message = request.json.get("message", "")

    try:
        # start a new chat session if not there already
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])
        
        chat_session = chat_sessions[user_id]

        # if the kid says this phrase, return preset response
        if user_message.lower() == "i'm home":
            response_text = "Welcome home! Ready to help with your homework or play some fun games?"
        else:
            response = chat_session.send_message(user_message)
            response_text = response.text

        # casual jogging reminder if the msg mentions jogging
        if "6pm" in user_message.lower() or "jog" in user_message.lower():
            response_text += "\n\nRemember, it's good to go jogging at 6pm! It keeps you healthy and strong!"

        # speak it out loud for them
        SpeakText(response_text)

        return jsonify({"reply": response_text})
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Oops! Let's try that again. Could you ask me something else?"})

if __name__ == "__main__":
    print("System online and ready to help!")
    app.run(debug=True)  # runs on localhost:5000 by default
