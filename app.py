import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import searchDB, delete_ledger_data, login_required,  pkr,  get_ledger_totals, create_db, querry_table, extract_date_info, current_month_totals,order_data_for_chart,filterTransaction

# global variables
ledger_list = []
ledger_totals = ()


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
    if session.get("uid") is None:
        return redirect("/welcome")
    else:
        return redirect("/dashboard")
    

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")
    
@app.route("/dashboard")
@login_required
def dashboard():
    message = request.args.get("message")
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    income,expense = order_data_for_chart("../Database/user-databases",session["uid"],session["username"])
    chart_data = [months,income,expense]
    monthly_totals = current_month_totals("../Database/user-databases",session["uid"],session["username"])
    ledger_list = querry_table("../Database/user-databases",session["uid"],session["username"],"ledger")
    return render_template("index.html",ledger_list = ledger_list ,ledger_totals = ledger_totals , monthly_totals = monthly_totals, chart_data= chart_data, message=message)



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
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows_pass = cursor.fetchall()
        if len(rows_pass) != 0:
            return render_template("register.html", message="Username already exists")  
        
        # Inserting data into database
        cursor.execute("INSERT INTO users (name, username, email, hash) VALUES (?,?,?,?)",(name, username, email, generate_password_hash(password),))
        auth_conn.commit()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()
        auth_conn.close()

        # Remember which user has logged in
        session["uid"] = rows[0][0] #(id, Name, username, email, hash)
        session["username"] = username
        session["name"] = rows[0][1]

        # Creating user-specific database
        id = session["uid"]
        if create_db("../Database/user-databases",id, username):
            user_conn = sqlite3.connect(f"../Database/user-databases/{id}/{username}.db")
            u_cursor = user_conn.cursor()
            u_cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, day INTEGER NOT NULL, month INTEGER NOT NULL, year INTEGER NOT NULL, description TEXT NOT NULL, received NUMERIC NOT NULL DEFAULT 0.00, paid NUMERIC NOT NULL DEFAULT 0.00, category TEXT NOT NULL)")
            u_cursor.execute("CREATE TABLE IF NOT EXISTS ledger (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name TEXT NOT NULL)")
            user_conn.commit()
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

        #save username and password in a variable
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        auth_conn = sqlite3.connect("../Database/users/Authentication/CoinTrack.db")
        cursor = auth_conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cursor.fetchall()
        auth_conn.close()
        
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][4], password):
            return render_template("login.html", message="Invalid username and/or password")

        # Remember which user has logged in
        session["uid"] = rows[0][0]
        session["username"] = username
        session["name"] = rows[0][1]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")


@app.route("/table", methods=["GET", "POST"])
@login_required
def table():
    if request.method == "POST":
        return render_template("table.html")
    else:
        transaction = []
        filter = False
        message = request.args.get("message")
        month = request.args.get("month")
        year = request.args.get("year")
        paymentType = request.args.get("paymentType")
        ledgerName = request.args.get("ledgerName")
        if month != None or year != None or paymentType != None or ledgerName != None:
            if month == None:
                month = "all"
            if year == None:
                year = "all"
            if paymentType == None:
                paymentType = "all"
            if ledgerName == None:
                ledgerName = "all"
            filter = True
            transaction = filterTransaction("../Database/user-databases",session["uid"],session["username"],month,year,paymentType,ledgerName)
           
        
        
        else:
            transaction = querry_table("../Database/user-databases",session["uid"],session["username"],"transactions")
            print(transaction)
        # Find unique years and month list from transactions
        calcYandM = querry_table("../Database/user-databases",session["uid"],session["username"],"transactions")
        yearsList=[]
        monthList=[]
        for t in calcYandM:
            if t[3] not in yearsList:
                yearsList.append(t[3])
            if t[2] not in monthList:
                monthList.append(t[2])
        transaction.reverse()
        # print(transaction)

        ledger_list = querry_table("../Database/user-databases",session["uid"],session["username"],"ledger")
        return render_template("table.html",transactions = transaction , ledger_list = ledger_list, years=yearsList, months=monthList, message=message,filter=filter)
    


@app.route("/addLedger", methods=["GET", "POST"])
@login_required
def addLedger():
    if request.method == "POST":
        ledger_name = request.form.get("ledger_name")
        user_conn = sqlite3.connect(f"../Database/user-databases/{session['uid']}/{session['username']}.db")
        u_cursor = user_conn.cursor()
        u_cursor.execute("INSERT INTO ledger (name) VALUES (?)",(ledger_name,))
        user_conn.commit()
        user_conn.close()
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("dashboard",message="Something wen't wrong! Can't add ledger."))
    

@app.route("/deleteLedger", methods=["GET", "POST"])
@login_required
def deleteLedger():
    if request.method == "POST":
        Ledgname = request.form.get("ledger_name")
        
        if Ledgname == None:
            return redirect(url_for("dashboard",message="Something wen't wrong! Must Select a ledger to delete."))
        
        user_conn = sqlite3.connect(f"../Database/user-databases/{session['uid']}/{session['username']}.db")
        u_cursor = user_conn.cursor()
        u_cursor.execute("DELETE FROM ledger WHERE name = ?",(Ledgname,))
        user_conn.commit()
        user_conn.close()
        delete_ledger_data("../Database/user-databases",session["uid"],session["username"],Ledgname) #Delete Ledger Data From Transactions Table
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for("dashboard",message="Something wen't wrong! Can't delete ledger.")) 

@app.route("/viewLedgerTotals", methods=["GET", "POST"])
@login_required
def viewLedgerTotals():
    if request.method == "POST":
        
        ledger_name = request.form.get("ledger_name")
        if ledger_name == None:
            return redirect(url_for("dashboard",message="Something wen't wrong! Must Select a ledger to view."))
        
        global ledger_totals
        ledger_totals_values =()
        ledger_totals_values = get_ledger_totals("../Database/user-databases",session["uid"],session["username"],ledger_name)
        ledger_totals = ledger_totals_values[:3] + (ledger_name,)
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("dashboard",message="Something wen't wrong! Can't view ledger.")) 

@app.route("/addTransaction", methods=["GET", "POST"])
@login_required
def addTransaction():
    if request.method == "POST":
        date = request.form.get("date")
        # print(date)
        day, year, month = extract_date_info(date)
        description = request.form.get("description")
        received = request.form.get("received")
        paid = request.form.get("paid")
        category = request.form.get("category")
        if category == None or date == None or description == None or received == None or paid == None:
            return redirect(url_for("table",message="Something wen't wrong! Must fill all fields."))
            
        user_conn = sqlite3.connect(f"../Database/user-databases/{session['uid']}/{session['username']}.db")
        u_cursor = user_conn.cursor()
        u_cursor.execute("INSERT INTO transactions (day, month, year, description, received, paid, category) VALUES (?,?,?,?,?,?,?)",(day, month, year, description, received, paid, category))
        user_conn.commit()
        user_conn.close()
        return redirect(url_for("table"))
    else:
        return redirect(url_for("table",message="Something wen't wrong! Can't add transaction."))

@app.route("/deleteTransaction", methods=["GET", "POST"])
@login_required
def deleteTransaction():
    if request.method == "POST":
        id = request.form.get("tid")
        user_conn = sqlite3.connect(f"../Database/user-databases/{session['uid']}/{session['username']}.db")
        u_cursor = user_conn.cursor()
        u_cursor.execute("DELETE FROM transactions WHERE id = ?",(id,))
        user_conn.commit()
        user_conn.close()
        return redirect(url_for("table"))
    else:
        return redirect(url_for("table",message="Something wen't wrong! Can't delete transaction."))
    


@app.route("/editTransaction", methods=["GET", "POST"])
@login_required
def editTransaction():
    print("Edit transaction called")
    if request.method == "POST":
        id = request.form.get("tid")
        date = request.form.get("date")
        day, year, month = extract_date_info(request.form.get("date"))
        description = request.form.get("description")
        received = request.form.get("received")
        paid = request.form.get("paid")
        category = request.form.get("category")
        # print(id,date,description,received,paid,category)
        user_conn = sqlite3.connect(f"../Database/user-databases/{session['uid']}/{session['username']}.db")
        u_cursor = user_conn.cursor()
        u_cursor.execute("UPDATE transactions SET day = ?, month = ?, year = ?, description = ?, received = ?, paid = ?, category = ? WHERE id = ?",(day, month, year, description, received, paid, category, id))
        user_conn.commit()
        user_conn.close()
        return redirect(url_for("table"))
    else:
        return redirect(url_for("table",message="Something wen't wrong! Can't edit transaction."))


@app.route("/applyFilter", methods=["GET", "POST"])
@login_required
def applyFilter():
    if request.method == "POST":
        month = request.form.get("month")
        year = request.form.get("year")
        paymentType = request.form.get("paymentType")
        ledgerName = request.form.get("ledgerName")
        return redirect(url_for("table",month=month,year=year,paymentType=paymentType,ledgerName=ledgerName))
    else:
        return redirect(url_for("table",message="Something wen't wrong! Can't apply filter."))
    
#Search API

@app.route("/search")
@login_required
def search():
    q= request.args.get("q")
    if q == None:
        return redirect(url_for("table",message="Something wen't wrong! Can't search."))
    else:
        results = searchDB("../Database/user-databases",session["uid"],session["username"],q)
        print(results)
        return render_template("API-Templates/search.html",transactions=results)


if __name__ == "__main__":
    app.run(debug=True)