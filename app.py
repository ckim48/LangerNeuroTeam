# Flask --> Open-source Python library which allows you to make Web-application with Python
# every html goes to folder 'templates'
# every css/js + images files goes to 'static'
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session # We are going to use Flask for this python code
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from config import firebase_config

# Loading the secret key
cred = credentials.Certificate("secret.json")
# Access to the firebase using the loaded key.
firebase_admin.initialize_app(cred)

firebase = pyrebase.initialize_app(firebase_config)

app = Flask(__name__)  # It creates an empty web application
app.secret_key = "abc"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=5)
# Log-out
# Session = {}
# As soon as user login
# Session = {"username" : "test"}
# Added the homepage --> For now we don't html filr for the homepage, but we just have "Hello, World"

# Function to store user data in Firebase
def store_user_data(user_id, score_data):
    db.child("users").child(user_id).child("game_result_task1").push(score_data)

@app.route('/save_score', methods=['POST'])
def save_score():
    user_id = session.get('username', None)
    score_data = request.get_json()

    if not user_id or not score_data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    store_user_data(user_id.replace('.', '_').replace('@', '_'), score_data)

    return jsonify({'status': 'success', 'message': 'Score data saved successfully'})

@app.route('/')
def index():
    isLogin = False
    if 'username' in session:
        isLogin = True
    return render_template('index.html', isLogin = isLogin)

db = firebase.database()
@app.route('/add_task2', methods=["POST"])
def add_task2():
    if 'username' in session:
        user_id = session["username"].replace('.','_').replace('@','_')
        data = request.json
        if data:
            # Save the total score and average response time in the database
            db.child("users").child(user_id).child("game_result_task2").push({
                "total_score": data['totalScore'],
                "avg_response_time": data['avgResponseTime']
            })
            return {"status": "success"}, 200
        else:
            return {"error": "No data received"}
    else:
        return {"error": "User not logged in"}

@app.route('/add_task3', methods=["POST"])
def add_task3():
    if 'username' in session:
        user_id = session["username"].replace('.', '_').replace('@', '_')
        data = request.json
        if data:
            db.child("users").child(user_id).child("game_result_task3").push({
                "task": data['task'],
                "level": data['level'],
                "rounds_completed": data['roundsCompleted'],
                "mistakes": data['mistakes']
            })
            return {"status": "success"}, 200
        else:
            return {"error": "No data received"}, 400
    else:
        return {"error": "User not logged in"}, 403

# We added the login page to our web application
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user = firebase.auth().sign_in_with_email_and_password(username, password)
            session["username"] = username  # Store the email or unique identifier in session
            return redirect(url_for('index'))
        except Exception as e:
            flash("Username or password is wrong")
            return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user = firebase.auth().create_user_with_email_and_password(username, password)
            return redirect(url_for('login'))
        except Exception as e:
            flash("This email is already registered or an error occurred")
            return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/task')
def task():
    return render_template('task1.html')

@app.route('/task2')
def task2():
    return render_template('task2.html')

@app.route('/task3')
def task3():
    return render_template('task3.html')





if __name__ == '__main__':
    app.run(debug=True) # run our web application