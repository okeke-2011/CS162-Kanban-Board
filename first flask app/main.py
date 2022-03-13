from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "kanban board"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/welcome")
def welcome():
    if "user_name" in session:
        user = session["user_name"]
        return render_template("welcome.html", user = user)
    else:
        flash("You need to sign in")
        return redirect(url_for("login"))

@app.route("/", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        user_name = request.form["user_name"]
        session["user_name"] = user_name

        found_user = users.query.filter_by(name = user_name).first()
        if found_user:
            session["email"] = found_user.email
        else:
            new_user = users(user_name, "")
            db.session.add(new_user)
            db.session.commit()
            flash("Added you to the database")

        flash("Logged you in!")
        return redirect(url_for("welcome"))
    else:
        if "user_name" in session:
            flash("You're already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/email", methods = ["POST", "GET"])
def edit_email():
    email = ""
    if "user_name" in session:
        usr = session["user_name"]
        found_user = users.query.filter_by(name = usr)
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email

            found_user.update(dict(email = email))
            db.session.commit()
            flash("Email saved")

        else:
            if "email" in session:
                email = session["email"]
        return render_template("email.html", email = email)
    else:
        flash("You need to be logged in to edit email!")
        return redirect(url_for("login"))


@app.route("/user")
def user():
    if "user_name" in session:
        name = session["user_name"]
        return render_template("user.html", roommates = ["Philip", "Favour", "Aarthi"], name = name)
    else:
        flash("You need to be logged in to see user details!")
        return redirect(url_for("login"))

@app.route("/view")
def view():
    if "user_name" in session:
        user = session["user_name"]
        if user == "Favour":
            all_users = users.query.all()
            return render_template("view.html", all_users = all_users)
        else:
            flash("You are not Favour! You can't view the database")
            return redirect(url_for("user"))
    else:
        flash("You need to be logged in!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user_name" in session:
        flash(f"Logged out {session['user_name']}", "info")
        session.pop("user_name", None)
        session.pop("email", None)
    return redirect(url_for("login"))



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)