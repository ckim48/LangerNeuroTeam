# Flask --> Open-source Python library which allows you to make Web-application with Python
# every html goes to folder 'templates'
# every css/js + images files goes to 'static'
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, session # We are going to use Flask for this python code
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from config import firebase_config
import random
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
    istask1_complete =  True
    istask2_complete =  True
    istask3_complete =  True
    task1_scores = None
    task2_scores = None
    task3_scores = None
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

@app.route('/index2')
def index2():
    return render_template('index2.html')
@app.route('/mindful', methods=['GET', 'POST'])
def mindful():
    isLogin = False
    if 'username' in session: # {"username" : "testtest"}
        isLogin = True
    if request.method == 'POST':
        # Handle user responses
        responses = request.form.to_dict()
        print("Mindful Responses:", responses)
        return redirect(url_for('study_process'))  # Redirect after submission
    return render_template('mindful.html',isLogin=isLogin, show_navbar=False)

@app.route('/non-mindful', methods=['GET', 'POST'])
def non_mindful():
    isLogin = False
    if 'username' in session: # {"username" : "testtest"}
        isLogin = True
    if request.method == 'POST':
        # Handle user responses
        responses = request.form.to_dict()
        print("Non-Mindful Responses:", responses)
        return redirect(url_for('index'))  # Redirect after submission
    return render_template('non_mindful.html',isLogin=isLogin, show_navbar=False)

@app.route('/study_process', methods=["GET", "POST"])
def study_process():
    isLogin = False
    if 'username' in session:
        isLogin = True
        user_id = session["username"].replace(".", "_").replace("@", "_")
        progress = db.child("users").child(user_id).child("study_progress").get().val() or {"current_step": 1}

        # Check task completion statuses
        task1_complete = db.child("users").child(user_id).child("game_result_task1").get().val() is not None
        task2_complete = db.child("users").child(user_id).child("game_result_task2").get().val() is not None
        task3_complete = db.child("users").child(user_id).child("game_result_task3").get().val() is not None





        if request.method == "POST":
            next_step = request.json.get("next_step")
            if next_step == 4:
                group = random.choice(["mindful", "non_mindful"])
                db.child("users").child(user_id).child("warmup_group").set(group)  # Save chosen group to Firebase
                db.child("users").child(user_id).child("study_progress").set({"current_step": int(next_step)})

                return jsonify({"status": "redirect", "url": url_for(group)})

            if next_step == 5:  # Step 4: Main Tasks
                # Redirect to the first incomplete task
                if not task1_complete:
                    return jsonify({"status": "redirect", "url": url_for("task")})
                elif not task2_complete:
                    return jsonify({"status": "redirect", "url": url_for("task2")})
                elif not task3_complete:
                    return jsonify({"status": "redirect", "url": url_for("task3")})
            elif next_step and int(next_step) > progress["current_step"]:
                db.child("users").child(user_id).child("study_progress").set({"current_step": int(next_step)})
            return jsonify({"status": "success", "current_step": int(next_step)})

    else:
        return redirect(url_for('login'))

    total_steps = 6  # Total number of steps in the process
    return render_template(
        "index2.html",
        isLogin=isLogin,
        current_step=progress["current_step"],
        total_steps=total_steps,
        steps=[
            {"step_number": 1, "title": "Informed Consent", "description": "Please review and provide consent.", "link": "#", "button_text": "Proceed"},
            {"step_number": 2, "title": "Pre-task Survey", "description": "Complete the pre-task survey.", "link": "https://www.jotform.com/build/243310688876063?iak=e9cfc2fe8d6c64782a898247fc0dc840-9725265b79d1c3af", "button_text": "Take Survey"},
            {"step_number": 3, "title": "Warm-up Activities", "description": "Engage in warm-up activities.", "link": "#", "button_text": "Start Warm-up"},
            {"step_number": 4, "title": "Main Tasks", "description": "Participate in the main study tasks.", "link": "#", "button_text": "Start Task"},
            {"step_number": 5, "title": "Post-task Surveys", "description": "Complete the post-task surveys.", "link": "https://www.jotform.com/build/243311500343440?iak=70ed55bf4126b2266b381045be46b770-70687ed665837d65", "button_text": "Take Survey"},
            {"step_number": 6, "title": "Debriefing", "description": "Read the debriefing information.", "link": "#", "button_text": "Finish"},
        ]
    )




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


@app.route('/survey_pre_task', methods=["GET", "POST"])
def survey_pre_task():
    if request.method == "POST":

        demographic_data = {
            "age": request.form.get("age"),
            "sex": request.form.get("sex"),
            "other_sex": request.form.get("other_sex", ""),
        }

        lms_responses = {f"lms_{i}": request.form.get(f"lms_{i}") for i in range(1, 22)}
        panas_responses = {f"panas_{i}": request.form.get(f"panas_{i}") for i in range(1, 21)}
        stai_responses = {f"stai_{i}": request.form.get(f"stai_{i}") for i in range(1, 21)}
        pss_responses = {f"pss_{i}": request.form.get(f"pss_{i}") for i in range(1, 11)}

        # Save responses to Firebase
        user_id = session.get("username", "anonymous").replace(".", "_").replace("@", "_")
        db.child("users").child(user_id).child("survey_pre_task").set({
            "demographic": demographic_data,
            "LMS": lms_responses,
            "PANAS": panas_responses,
            "STAI": stai_responses,
            "PSS": pss_responses,
        })

        flash("Survey submitted successfully!")
        return redirect(url_for("index"))

    return render_template("survey_pre_task.html")

@app.route('/survey_pre_task_2_neuro', methods=["GET", "POST"])
def survey_pre_task_2_neuro():
    if request.method == "POST":
        # Retrieve survey responses
        ses_responses = {
            "income": request.form.get("income"),
            "education": request.form.get("education"),
            "employment_status": request.form.get("employment_status"),
            "occupation": request.form.get("occupation"),
            "social_class": request.form.get("social_class"),
        }


        user_id = session.get("username", "anonymous").replace(".", "_").replace("@", "_")
        db.child("users").child(user_id).child("survey_pre_task_2_neuro").set(ses_responses)

        flash("Neuro Pre-Task Survey submitted successfully!")
        return redirect(url_for("index"))

    return render_template("survey_neuro.html")


if __name__ == '__main__':
    app.run(debug=True, port=8080) # run our web application