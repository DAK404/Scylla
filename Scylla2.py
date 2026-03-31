from flask import Flask, render_template, redirect, url_for, request, Response, stream_with_context
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import pam
import os
import sys
import re
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Config
# -------------------------
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    print("Error: SECRET_KEY not found")
    sys.exit(1)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

# -------------------------
# Flask setup
# -------------------------
app = Flask(__name__)
app.secret_key = secret_key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


# -------------------------
# User model
# -------------------------
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# -------------------------
# Login (PAM)
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        p = pam.pam()
        if p.authenticate(username, password):
            user = User(username)
            login_user(user, remember=remember)
            return redirect(url_for('index'))

    return render_template('login.html')


# -------------------------
# Chat (Ollama streaming)
# -------------------------
@app.route("/chat", methods=["POST"])
@login_required
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return Response("Empty input", status=400)

    def generate():
        try:
            with requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": user_input,
                    "stream": True
                },
                stream=True
            ) as r:

                for line in r.iter_lines():
                    if line:
                        chunk = line.decode("utf-8")

                        try:
                            data = eval(chunk) if chunk.startswith("{") else None
                            token = data.get("response", "") if data else ""

                            token = re.sub(r"<think>.*?</think>", "", token, flags=re.DOTALL)

                            if token.strip():
                                yield token

                        except:
                            continue

        except Exception as e:
            print(f"Error: {e}")
            yield "\n[Error during inference]"

    return Response(stream_with_context(generate()), mimetype='text/plain')


# -------------------------
# Protected routes
# -------------------------
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
