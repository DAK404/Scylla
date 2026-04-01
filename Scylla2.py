from flask import Flask, render_template, redirect, url_for, request, Response, stream_with_context
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import pam
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Config
# -------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("Error: SECRET_KEY not set")
    sys.exit(1)

OLLAMA_URL = "http://localhost:11434/api/generate"

# ⚠️ CHANGE THIS AFTER CHECKING `ollama list`
MODEL_NAME = "llama3:8b"   # <-- update if needed


# -------------------------
# Flask setup
# -------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)


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
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        p = pam.pam()
        if p.authenticate(username, password):
            login_user(User(username))
            return redirect(url_for("index"))

        return "Login failed", 401

    return render_template("login.html")


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
                headers={  # ✅ IMPORTANT FIX
                    "Content-Type": "application/json"
                },
                stream=True
            ) as r:

                # ❗ DEBUG: print status
                print("Ollama status:", r.status_code)

                if r.status_code != 200:
                    yield f"[ERROR] Ollama returned {r.status_code}\n"
                    return

                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")

                        # ❗ DEBUG RAW STREAM
                        print("RAW:", decoded)

                        try:
                            data = json.loads(decoded)   # ✅ FIXED
                            token = data.get("response", "")

                            if token:
                                yield token

                        except Exception as e:
                            print("PARSE ERROR:", e)

        except Exception as e:
            print("REQUEST ERROR:", e)
            yield "\n[Error contacting Ollama]"

    return Response(stream_with_context(generate()), mimetype="text/plain")


# -------------------------
# Protected routes
# -------------------------
@app.route("/")
@login_required
def index():
    return render_template("index.html", username=current_user.id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
