import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required,  pkr,  get_time_stamp, create_db


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["pkr"] = pkr

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Creating user credentials database and initilizing tables
create_db("../Database/users","Authentication","CoinTrack")
auth_conn = sqlite3.connect("../Database/users/Authentication/CoinTrack.db")
cursor = auth_conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(uid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL, username TEXT NOT NULL, email TEXT NOT NULL, hash TEXT NOT NULL)")
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username)")
auth_conn.commit()
auth_conn.close()




@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    return response


@app.route("/")
# @login_required
def index():
    return render_template("welcome.html")
    

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Getting data into variables
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # connect 
        auth_conn = sqlite3.connect("../Database/users/Authentication/CoinTrack.db")
        cursor = auth_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", username)
        rows_pass = cursor.fetchall()
        if len(rows_pass) != 0:
            return render_template("register.html", message="Username already exists")  
        
        # Inserting data into database
        cursor.execute("INSERT INTO users (name, username, email, hash) VALUES (?,?,?,?)",name, username, email, generate_password_hash(password))
        auth_conn.commit()
        cursor.execute("SELECT * FROM users WHERE username = ?", username)
        rows = cursor.fetchall()
        auth_conn.close()

        # Remember which user has logged in
        session["uid"] = rows[0]["id"]
        session["username"] = username

        # Creating user-specific database
        id = session["uid"]
        if create_db("../Database/user-databases",id, username):
            user_conn = sqlite3.connect(f"../Database/user-databases/{id}/{username}.db")
            u_cursor = user_conn.cursor()
            u_cursor.execute("CREATE TABLE IF NOT EXISTS dashboard (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, date TEXT NOT NULL, description TEXT NOT NULL, received NUMERIC NOT NULL DEFAULT 0.00, paid NUMERIC NOT NULL DEFAULT 0.00, category TEXT NOT NULL)")
            u_cursor.commit()
            user_conn.close()
        else:
            return render_template("register.html", message="Something went wrong. Please try again later.")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        #save username and password in a variable
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        
        (
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["uid"] = rows[0]["id"]
        username = rows[0]["username"]

        id = session["uid"]
        global userdbcon
        userdbcon = SQL(f"sqlite:///user-databases/{id}/{username}.db")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route ("/home")
@login_required
def home():
    """Show portfolio of stocks"""
    # Connection to user-specific database
    id = session["uid"]
    rows = db.execute("SELECT * FROM users WHERE id = ?", id)
    if len(rows) != 1:
        session.clear()
        return redirect("/login")
    username = rows[0]["username"]
    userdbcon = SQL(f"sqlite:///user-databases/{id}/{username}.db")
    # //////////////////////////////////////////////////////////////
    dashboard = userdbcon.execute("SELECT * FROM dashboard")
    availablecash = rows[0]["cash"]
    # print(dashboard)
    sum_in_stocks = 0

    for row in dashboard:
        row["price"] = lookup(row["symbol"])["price"]
        row["total"] = row["price"] * row["shares"]
        sum_in_stocks += row["total"]
    # print(sum_in_stocks)
    return render_template(
        "index.html",
        dashdata=dashboard,
        currentCash=availablecash,
        total=availablecash + sum_in_stocks,
    )




@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # return apology("TODO")
    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("data missing")
        noFShares = request.form.get("shares")
        if not noFShares.isdigit():
            return apology("You cannot purchase partial shares.")
        noFShares = int(noFShares)
        quoted = lookup(request.form.get("symbol"))
        if quoted == None:
            return apology("Incorrect Symbol")
        elif noFShares <= 0:
            return apology("Incorrect Incorrect No of Shares")

        # Connection to user-specific database
        id = session["uid"]
        rows = db.execute("SELECT * FROM users WHERE id = ?", id)
        username = rows[0]["username"]
        userdbcon = SQL(f"sqlite:///user-databases/{id}/{username}.db")
        # //////////////////////////////////////////////////////////////
        availablecash = rows[0]["cash"]
        total = noFShares * quoted["price"]
        if total > availablecash:
            return apology("SORRY you're out of money")

        already_purchased = userdbcon.execute("SELECT symbol FROM dashboard")
        print(already_purchased)
        # print(already_purchased.values())
        for dict in already_purchased:
            if (
                "symbol" in dict
                and dict["symbol"] == request.form.get("symbol").upper()
            ):
                userdbcon.execute(
                    "UPDATE dashboard SET shares = shares + ? WHERE symbol = ?",
                    noFShares,
                    request.form.get("symbol").upper(),
                )
                print("WOrked")
                break
        else:
            userdbcon.execute(
                "INSERT INTO dashboard (symbol, name, shares) VALUES (?,?,?)",
                quoted["symbol"],
                quoted["name"],
                noFShares,
            )
            print("ISSUE")

        userdbcon.execute(
            "INSERT INTO history (symbol, name, shares, price, date) VALUES (?,?,?,?,?)",
            quoted["symbol"],
            quoted["name"],
            noFShares,
            quoted["price"],
            get_time_stamp(),
        )

        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total, id)
        return redirect("/")
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # return apology("TODO")
    # Connection to user-specific database
    id = session["uid"]
    rows = db.execute("SELECT * FROM users WHERE id = ?", id)
    username = rows[0]["username"]
    userdbcon = SQL(f"sqlite:///user-databases/{id}/{username}.db")
    # //////////////////////////////////////////////////////////////

    htable = userdbcon.execute("SELECT * FROM history")
    print(htable)
    return render_template("history.html", history=htable)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("data missing")
        quoted = lookup(request.form.get("symbol"))
        # print(lookup(request.form.get("symbol"))["price"])
        if quoted == None:
            return apology("Incorrect Symbol")
        return render_template("quote.html", quote=quoted)
    return render_template("quote.html")





@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # Connection to user-specific database
    id = session["uid"]
    rows = db.execute("SELECT * FROM users WHERE id = ?", id)
    username = rows[0]["username"]
    userdbcon = SQL(f"sqlite:///user-databases/{id}/{username}.db")
    # //////////////////////////////////////////////////////////////

    symbols = userdbcon.execute("SELECT symbol FROM dashboard")
    if request.method == "POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("data missing")
        noFShares = int(request.form.get("shares"))
        symbol = request.form.get("symbol")
        quoted = lookup(symbol)
        if quoted == None:
            return apology("Incorrect Symbol")
        elif noFShares <= 0:
            return apology("Incorrect No of Shares")

        oldShares = userdbcon.execute(
            "SELECT shares FROM dashboard WHERE symbol=?", symbol
        )
        # print(oldShares[0]["shares"])
        if noFShares > oldShares[0]["shares"]:
            return apology("Too Many Shares Selected")
        elif noFShares == oldShares[0]["shares"]:
            # print("")
            userdbcon.execute("DELETE FROM dashboard WHERE symbol = ?", symbol)
        elif noFShares < oldShares[0]["shares"]:
            # print("A")
            userdbcon.execute(
                "UPDATE dashboard SET shares = shares - ? WHERE symbol = ?",
                noFShares,
                symbol,
            )
        # availablecash = rows[0]["cash"]
        total = noFShares * quoted["price"]
        # if total>availablecash:
        #     return apology("SORRY you're out of money")
        # userdbcon.execute("INSERT INTO dashboard (symbol, name, shares) VALUES (?,?,?)", quoted["symbol"], quoted["name"], noFShares)
        userdbcon.execute(
            "INSERT INTO history (symbol, name, shares, price, date) VALUES (?,?,?,?,?)",
            quoted["symbol"],
            quoted["name"],
            -noFShares,
            quoted["price"],
            get_time_stamp(),
        )

        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total, id)
        return redirect("/")

    return render_template("sell.html", symbols=symbols)
    # return apology("TODO")

if __name__ == "__main__":
    app.run(debug=True)