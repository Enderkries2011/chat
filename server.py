from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import os
import json
import time
import threading

# Google Sheets configuration
JSON_KEY_FILE = 'cgat-437117-9c8acbec337e.json'
SPREADSHEET_NAME = 'Chat user data'
WORKSHEET_NAME = 'Sheet1'

# Set up credentials and client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scope)
client = gspread.authorize(creds)

app = Flask(__name__)
app.secret_key = 'unk090vo5555id909nown'  # Needed for session management

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg', 'pdf'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

MESSAGES_FILE = 'messages.txt'
email_to_userinfo = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_messages():
    """Load messages from the messages file."""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []  # Return empty if there's a decoding error
    return []

def save_messages(messages):
    """Save messages to the messages file."""
    with open(MESSAGES_FILE, 'w') as file:
        json.dump(messages, file)

def load_users_from_sheet():
    """Load users and their colors from the Google Spreadsheet."""
    global email_to_userinfo
    worksheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    data = worksheet.get_all_records()

    email_to_userinfo = {
        entry['Email'].strip(): {
            'username': entry['Username'].strip(),
            'password': str(entry['Password']).strip(),
            'color': entry['Color'].strip(),  # HEX Color code
            'authcode': str(entry['Authcode']).strip()  # Added authcode
        }
        for entry in data
    }

def background_user_loader():
    """Thread function to reload users from sheet every 5 seconds."""
    while True:
        load_users_from_sheet()
        time.sleep(5)

# Start the background thread for loading users
threading.Thread(target=background_user_loader, daemon=True).start()

@app.route('/auth', methods=['POST'])
def authenticate():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    userinfo = email_to_userinfo.get(email)
    if userinfo and userinfo['password'] == password:
        response = make_response(jsonify({"message": "Authenticated", "username": userinfo['username']}))
        response.set_cookie('username', email)  # Set cookie for user
        return response, 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/login', methods=['GET'])
def login():
    email = request.args.get('email')
    authcode = request.args.get('authcode')
    
    # Validate the authcode
    userinfo = email_to_userinfo.get(email)
    if userinfo and userinfo['authcode'] == authcode:
        response = make_response(redirect(url_for('home')))
        response.set_cookie('username', email)  # Set a cookie to remember the user
        return response
    else:
        return jsonify({"error": "Invalid authcode or email"}), 401

@app.route('/')
def home():
    username = request.cookies.get('username')
    if username and username in email_to_userinfo:
        return render_template('index.html', username=email_to_userinfo[username]['username'])
    return render_template('index.html')

@app.route('/get_messages', methods=['GET'])
def get_messages():
    messages = load_messages()
    return jsonify(messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    email = data.get('email') or request.cookies.get('username')  # Try to get email from cookies
    message = data.get('message')
    
    if not email or not message:
        return jsonify({"error": "Missing email or message"}), 400

    userinfo = email_to_userinfo.get(email)
    if not userinfo:
        return jsonify({"error": "Invalid email"}), 400

    username = userinfo['username']
    color = f"#{userinfo['color']}"

    messages = load_messages()
    new_message = {
        'username': username,
        'message': message,
        'timestamp': time.time(),
        'color': color
    }
    messages.append(new_message)
    save_messages(messages)
    
    return jsonify({"message": "Message sent"}), 200

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'email' not in request.form:
        return jsonify({"error": "Missing file or email"}), 400

    file = request.files['file']
    email = request.form['email']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        userinfo = email_to_userinfo.get(email)
        if not userinfo:
            return jsonify({"error": "Invalid email"}), 400

        username = userinfo['username']

        messages = load_messages()
        messages.append({
            'username': username,
            'message': f'FILE: {filename}',
            'timestamp': time.time(),
            'color': userinfo['color']
        })
        save_messages(messages)

        return jsonify({"message": "File uploaded"}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
