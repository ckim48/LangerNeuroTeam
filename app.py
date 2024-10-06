# Flask --> Open-source Python library which allows you to make Web-application with Python
# every html goes to folder 'templates'
# every css/js + images files goes to 'static'
from flask import Flask, render_template, request, url_for, redirect, flash, session # We are going to use Flask for this python code
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
            db.child("users").child(user_id).child("game_result_task2").push(data)
            return {"status": "success"}, 200
        else:
            return {"error":"No data received"}
    else:
        return {"error":"User not logged in"}

# We added the login page to our web application
@app.route('/login' , methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user = auth.get_user_by_email(username)
            session["username"] = username
            return redirect(url_for('index'))
        except firebase_admin._auth_utils.UserNotFoundError:
            flash("Username or password is wrong")
            return render_template('login.html')
        except Exception as e:
            flash(str(e))
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/register' , methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            user = auth.create_user(
                email = username,
                password=password
            )
            return redirect(url_for('login'))
        except firebase_admin._auth_utils.EmailAlreadyExistsError:
            flash("This email is already registered")
            return render_template('register.html')
        except Exception as e:
            flash(str(e))
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