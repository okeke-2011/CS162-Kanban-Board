# import necessary libraries
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

# set up the app and database
app = Flask(__name__)
app.secret_key = "kanban board"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# define the users table
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, password):
        self.user_name = name
        self.password = password

# define the tasks table
class Tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    task_type = db.Column(db.String(100))
    task_description = db.Column(db.String(100))

    def __init__(self, id, type, description):
        self.user_id = id
        self.task_type = type
        self.task_description = description

# login page
@app.route("/", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        # get form data
        session["user_name"] = request.form["user_name"]
        session["password"] = request.form["password"]
        # check for existing user from the database
        found_user = Users.query.filter_by(user_name = session["user_name"], password = session["password"]).first()
        if not found_user:
            flash(f"Created profile for {session['user_name']}")
            new_user = Users(session["user_name"], session["password"])
            db.session.add(new_user)
            db.session.commit()
        flash("Signed you in!")
        # send user to the welcome page
        return redirect(url_for("welcome"))

    else:
        if "user_name" in session:
            flash("You're already logged in")
            # if not logged in, go back to the login page
            return redirect(url_for("tasks"))
        else:
            # show login page
            return render_template("login.html")

# welcome page
@app.route("/welcome")
def welcome():
    # check if the user is logged in
    if "user_name" in session:
        # render the welcome page
        return render_template("welcome.html", user_name = session["user_name"])
    else:
        # send the user to the login page
        flash("You need to log in!")
        return redirect(url_for("login"))

@app.route("/tasks", methods = ["POST", "GET"])
def tasks():
    if "user_name" in session:
        # find the users data
        usr = Users.query.filter_by(user_name=session["user_name"], password=session["password"]).first()
        if request.method == "POST":
            if "add_todo" in request.form:
                # get the task description from the user
                task = request.form['add_todo']
                flash(f"Added task '{task}'")
                # update the database
                new_task = Tasks(usr.user_id, "todo", request.form['add_todo'])
                db.session.add(new_task)
                db.session.commit()

            if "add_doing" in request.form:
                # get the task description from the user
                task = request.form['add_doing']
                # check for the task in the database
                found_task = Tasks.query.filter_by(user_id=usr.user_id, task_description=task).first()
                if found_task:
                    # update the database
                    flash(f"Marked '{task}' as doing")
                    found_task.task_type = "doing"
                    db.session.commit()
                else:
                    flash("Task not found! Check your spelling")

            if "add_done" in request.form:
                # get the task description from the user
                task = request.form['add_done']
                # check for the task in the database
                found_task = Tasks.query.filter_by(user_id=usr.user_id, task_description=task).first()
                if found_task:
                    # update the database
                    flash(f"Marked '{task}' as done")
                    found_task.task_type = "done"
                    db.session.commit()
                else:
                    flash("Task not found! Check your spelling")

            if "delete" in request.form:
                task = request.form['delete']
                # look for task in database
                found_task = Tasks.query.filter_by(user_id=usr.user_id, task_description=task).first()
                if found_task:
                    # update the database
                    flash(f"Deleted '{task}'")
                    Tasks.query.filter_by(user_id=usr.user_id, task_description=task).delete()
                    db.session.commit()
                else:
                    flash("Task not found! Check your spelling")
        # database data to populate the tasks page
        usr_todo = Tasks.query.filter_by(user_id=usr.user_id, task_type="todo").all()
        usr_doing = Tasks.query.filter_by(user_id=usr.user_id, task_type="doing").all()
        usr_done = Tasks.query.filter_by(user_id=usr.user_id, task_type="done").all()
        return render_template("tasks.html", todo=usr_todo, doing=usr_doing, done=usr_done)
    else:
        flash("You need to log in!")
        return redirect(url_for("login"))

@app.route("/user_info", methods = ["POST", "GET"])
def user_info():
    if "user_name" in session:
        # find user in the database
        usr = Users.query.filter_by(user_name = session["user_name"], password = session["password"]).first()
        if request.method == "POST":
            if "new_name" in request.form:
                # update name with user input
                flash(f"Changed username from {session['user_name']} to {request.form['new_name']}")
                session['user_name'] = request.form['new_name']
                usr.user_name = session['user_name']
                db.session.commit()

            if "new_password" in request.form:
                # update password with user input
                flash(f"Changed username from {session['password']} to {request.form['new_password']}")
                session['password'] = request.form['new_password']
                usr.password = session['password']
                db.session.commit()
        return render_template("user_info.html", name = usr.user_name, password = usr.password)
    else:
        flash("You need to log in!")
        return redirect(url_for("login"))

@app.route("/view")
def view_db():
    if "user_name" in session:
        # confirm credentials needed to view this page
        if session["user_name"] == "Favour" and session["password"] == "GOAT":
            # get all table data
            all_users = Users.query.all()
            all_tasks = Tasks.query.all()
            return render_template("view.html", all_users = all_users, all_tasks = all_tasks)
        else:
            flash("Only the GOAT can view this page")
            # if credentials are not valid send the user to their tasks page
            return redirect(url_for("tasks"))
    else:
        flash("You need to log in!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    # delete all the session data
    if "user_name" in session:
        flash(f"Signed {session['user_name']} out")
        session.pop("user_name", None)
        session.pop("password", None)
    # send the user to the login page
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)