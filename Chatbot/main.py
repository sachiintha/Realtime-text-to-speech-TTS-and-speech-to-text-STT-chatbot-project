from flask import Flask
from flask import render_template
from flask import request
import time
import requests
import speech_recognition as sr
import pyttsx3
from flask import Flask, render_template, request, jsonify

# Init first message
current_messages = {
    "users": ["James", "You"],
    "chats": [{
        "from": 'James',
        "msg": 'Hi, what do you want to chat about?',
        "action": ''
    }]
}
current_messages['chats'][0]['time'] = str(round(time.time() * 1000))
print(str(round(time.time() * 1000)), flush = True)
API_TOKEN = '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'  # Retrieve own API token to make this work


def query(payload, model_id, api_token):
    headers = {"Authorization": f"Bearer {api_token}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    response = requests.post(API_URL, headers = headers, json = payload)
    return response.json()


def speech_to_text():


    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)

    try:
        msg = r.recognize_google(audio)
    except sr.UnknownValueError:
        msg = "I couldn't understand what you said."

    return msg


def text_to_speech(text):

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


## Create app

app = Flask(__name__, template_folder = 'templates')


@app.route('/', methods = ['GET', 'POST'])
def page():
    global current_messages
    global API_TOKEN

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    if request.method == 'GET':
        return render_template('chat.html', chat = current_messages)
    if request.method == 'POST':
        current_messages = request.json
        msg = current_messages['chats'][-1]['msg']

        # Convert speech to text, if the user has selected the speech-to-text option.
        if request.form.get('speech_to_text'):
            msg = speech_to_text()

        responses = query(msg, 'facebook/blenderbot_small-90M', API_TOKEN)['conversation']['generated_responses']
        response = responses[-1]

        # Convert text to speech, if the user has selected the text-to-speech option.
        if request.form.get('text_to_speech'):
            text_to_speech(engine)  # Pass the engine to the function

            # Modify to return the TTS audio file instead of speaking it directly
            audio_file = 'tts_output.mp3'
            engine.save_to_file(response, audio_file)
            engine.runAndWait()

            return jsonify({'audio_file': audio_file, 'response': response})

        current_messages['chats'].append(
            {'from': 'James', 'msg': response, 'time': str(round(time.time() * 1000)), 'action': ''})

        return current_messages, text_to_speech(response)


if __name__ == '__main__':
    app.run(debug = True, port = 5001)
