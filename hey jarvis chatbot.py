import os
import pyttsx3
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Gemini API config
genai.configure(api_key="AIzaSyA7oGEzmDkkCjB0AEilKqm3xdR-ANtDh7o")

generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

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

# 🗣️ Text-to-Speech Function
def SpeakText(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    for voice in voices:
        if "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    engine.setProperty('rate', 180)  # speaking speed
    engine.say(text)
    engine.runAndWait()

# In-memory chat history (optional: replace with DB later)
chat_sessions = {}

@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_id = request.json.get("user_id", "default_user")
    user_message = request.json.get("message", "")

    try:
        # Create a session if it doesn't exist
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])
        
        chat_session = chat_sessions[user_id]

        # Special phrase trigger
        if user_message.lower() == "i'm home":
            response_text = "Welcome home! Ready to help with your homework or play some fun games?"
        else:
            response = chat_session.send_message(user_message)
            response_text = response.text

        # Soft jogging reminder
        if "6pm" in user_message.lower() or "jog" in user_message.lower():
            response_text += "\n\nRemember, it's good to go jogging at 6pm! It keeps you healthy and strong!"

        # 🔊 Speak the response
        SpeakText(response_text)

        return jsonify({"reply": response_text})
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Oops! Let's try that again. Could you ask me something else?"})

if __name__ == "__main__":
    print("System online and ready to help!")
    app.run(debug=True)
