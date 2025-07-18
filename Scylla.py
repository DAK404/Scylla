from flask import Flask, render_template, redirect, url_for, request, Response, stream_with_context
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pam
import os
import sys
import re
from llama_cpp import Llama
from dotenv import load_dotenv

load_dotenv()  # Loads from .env into os.environ

# Check for secret key
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    print("Error: SECRET_KEY environment variable not found. Exiting.")
    sys.exit(1)

#####################################
# ONLY GGUF MODELS CAN BE USED HERE #
#####################################
#
# Using the following model:
# bartowski/Mistral-Small-Instruct-2409-GGUF
# bartowski/uncensoredai_UncensoredLM-DeepSeek-R1-Distill-Qwen-14B-GGUF
# TheBloke/Llama-2-7B-Chat-GGUF

# Load the model using llama_cpp
llm = Llama.from_pretrained(
    repo_id="TheBloke/Llama-2-7B-Chat-GGUF",
    filename="llama-2-7b-chat.Q6_K.gguf"
)

app = Flask(__name__)
app.secret_key = secret_key  # Use the environment variable for the secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

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

# @app.route('/chat', methods=['POST'])
# @login_required
# def chat():
#     user_input = request.json.get('message')
#     print("Received input:", user_input)  # Debug print statement
#
#     try:
#         # Generate a response using the model
#         response = llm.create_chat_completion(
#             messages=[
#                 {
#                     "role": "user",
#                     "content": user_input
#                 }
#             ]
#         )
#         response_text =f"Scylla> {response["choices"][0]["message"]["content"]}"
#         print("Response:", response_text)  # Debug print statement
#     except Exception as e:
#         print(f"Error during model inference: {e}")  # Print any errors during inference
#         return {'response': "Error during model inference"}
#
#     return {'response': response_text}

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return Response("Empty input", status=400)

    # def generate():
    #     try:
    #         yield "Scylla> "
    #         for output in llm.create_chat_completion(
    #             messages=[{"role": "user", "content": user_input}],
    #             stream=True
    #         ):
    #             delta = output["choices"][0]["delta"]
    #             token = delta.get("content", "")
    #             # Strip <think> tags inline
    #             token = re.sub(r"<think>.*?</think>", "", token, flags=re.DOTALL)
    #             yield token
    #     except Exception as e:
    #         print(f"Error during model inference: {e}")
    #         yield "\n[Error during model inference]"
    def generate():
        try:
            yield ""
            for output in llm.create_chat_completion(
                messages=[{"role": "user", "content": user_input}],
                stream=True
            ):
                delta = output["choices"][0]["delta"]
                token = delta.get("content", "")
                token = re.sub(r"<think>.*?</think>", "", token, flags=re.DOTALL)
                if token.strip():
                    yield token
        except Exception as e:
            print(f"Error during model inference: {e}")
            yield "\n[Error during model inference]"

    return Response(stream_with_context(generate()), mimetype='text/plain')


@app.route('/')
@login_required
def index():
    return render_template('index.html', username=current_user.id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    #app.run(debug=False)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
