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

# Storing the result of task1
@app.route('/save_score', methods=['POST'])
def save_score():
    user_id = session.get('username', None)
    score_data = request.get_json()

    if not user_id or not score_data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    store_user_data(user_id.replace('.', '_').replace('@', '_'), score_data)

    return jsonify({'status': 'success', 'message': 'Score data saved successfully'})
db = firebase.database()
@app.route('/')
def index():
    isLogin = False
    istask1_complete = True
    istask2_complete = True
    istask3_complete = True
    if 'username' in session: # {"username" : "testtest"}
        isLogin = True
        search_user = session["username"].replace('.', '_').replace('@', '_')  # testing_gmail_com
        task1_scores = db.child("users").child(search_user).child("game_result_task1").get().val()
        task2_scores = db.child("users").child(search_user).child("game_result_task2").get().val()
        task3_scores = db.child("users").child(search_user).child("game_result_task3").get().val()
    if task1_scores == None:
        istask1_complete = False
    if task2_scores == None:
        istask2_complete = False
    if task3_scores == None:
        istask3_complete = False

    return render_template('index.html', isLogin = isLogin, istask1_complete=istask1_complete,istask2_complete=istask2_complete,istask3_complete=istask3_complete)




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
        users = db.child("users_auth").order_by_child("username").equal_to(username).get()
        if users.each():
            for user in users.each():
                if user.val().get("password") == password:
                    session["username"] = username
                    return redirect(url_for('index'))

        flash("Username or password is wrong")
        return render_template('login.html')
    else:
        return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = db.child("users_auth").order_by_child("username").equal_to(username).get()
        if existing_user.each():
            flash("This email is already registered or an error occurred")
            return render_template('register.html')
        db.child("users_auth").push({"username":username, "password":password})
        return redirect(url_for('login'))

    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/task')
def task():
    isLogin = False
    istask1_complete = True
    istask2_complete = True
    istask3_complete = True
    if 'username' in session:
        isLogin = True
        search_user = session["username"].replace('.', '_').replace('@', '_')  # testing_gmail_com
        task1_scores = db.child("users").child(search_user).child("game_result_task1").get().val()
        task2_scores = db.child("users").child(search_user).child("game_result_task2").get().val()
        task3_scores = db.child("users").child(search_user).child("game_result_task3").get().val()
    if isLogin == False:
        return redirect(url_for('login'))
    if task1_scores == None:
        istask1_complete = False
    if task2_scores == None:
        istask2_complete = False
    if task3_scores == None:
        istask3_complete = False
    return render_template('task1.html', isLogin = isLogin,istask1_complete=istask1_complete,istask2_complete=istask2_complete,istask3_complete=istask3_complete)

@app.route('/task2')
def task2():
    isLogin = False
    istask1_complete = True
    istask2_complete = True
    istask3_complete = True
    if 'username' in session:
        isLogin = True
    if isLogin == False:
        return redirect(url_for('login'))
    search_user = session["username"].replace('.', '_').replace('@', '_')  # testing_gmail_com
    task1_scores = db.child("users").child(search_user).child("game_result_task1").get().val()
    task2_scores = db.child("users").child(search_user).child("game_result_task2").get().val()
    task3_scores = db.child("users").child(search_user).child("game_result_task3").get().val()
    if task1_scores == None:
        istask1_complete = False
    if task2_scores == None:
        istask2_complete = False
    if task3_scores == None:
        istask3_complete = False
    return render_template('task2.html', isLogin = isLogin,istask1_complete=istask1_complete,istask2_complete=istask2_complete,istask3_complete=istask3_complete)

@app.route('/task3')
def task3():
    isLogin = False
    istask1_complete = True
    istask2_complete = True
    istask3_complete = True
    if 'username' in session: #
        isLogin = True
    if isLogin == False:
        return redirect(url_for('login'))
    search_user = session["username"].replace('.', '_').replace('@', '_')  # testing_gmail_com
    task1_scores = db.child("users").child(search_user).child("game_result_task1").get().val()
    task2_scores = db.child("users").child(search_user).child("game_result_task2").get().val()
    task3_scores = db.child("users").child(search_user).child("game_result_task3").get().val()
    if task1_scores == None:
        istask1_complete = False
    if task2_scores == None:
        istask2_complete = False
    if task3_scores == None:
        istask3_complete = False
    return render_template('task3.html', isLogin = isLogin,istask1_complete=istask1_complete,istask2_complete=istask2_complete,istask3_complete=istask3_complete)


@app.route('/profile')
def profile():
    if 'username' not in session: # {"username": "test@gmail.com"}
        return redirect(url_for('login'))

    # Getting the score data for the logged-in user
    user_id = session["username"].replace('.', '_').replace('@', '_')
    task1_scores = db.child("users").child(user_id).child("game_result_task1").get().val()
    task2_scores = db.child("users").child(user_id).child("game_result_task2").get().val()
    task3_scores = db.child("users").child(user_id).child("game_result_task3").get().val()

    if task1_scores is not None:
        last_task1, task1_scores = next(reversed(task1_scores.items())) # last item of task 1

    if task2_scores is not None: # when user completed task2
        last_task2, task2_scores = next(reversed(task2_scores.items())) # last item of task 2
        total_task2 = task2_scores["total_score"] / 120 * 100 # percentage
        avgtime_task2 = round(task2_scores["avg_response_time"],1)
    else: # when user did not complete task2
        total_task2 = None
        avgtime_task2 = None

    return render_template('profile.html', task1 = task1_scores, task2 = task2_scores, task3 = task3_scores, total_task2 = total_task2,avgtime_task2=avgtime_task2)


if __name__ == '__main__':
    app.run(debug=True, port=8080) # run our web application