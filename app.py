from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import session
import mysql.connector
import json
app = Flask(__name__)
app.secret_key = "abcdefghijk"

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="mydatabase"
)
# mycursor.execute("CREATE DATABASE mydatabase")
# mycursor.execute("SHOW DATABASES")
# mycursor.execute("USE mydatabase")
# mycursor.execute("CREATE TABLE registers (name VARCHAR(255), account VARCHAR(255),password VARCHAR(255))")
# mycursor.execute("ALTER TABLE registers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")
# mycursor.execute("SELECT * FROM registers")
# for x in mycursor:
#     print(x)


@app.route("/")
def index():
    state = session.get("signin")
    if state != None:
        return redirect("/member")
    return render_template("index.html")


@app.route("/signup", methods=["POST"])
def signup():
    signup_name = request.form["signup_name"]
    signup_account = request.form["signup_account"]
    signup_password = request.form["signup_password"]
    sql = "SELECT account FROM registers WHERE account = %s"
    acc = (signup_account,)
    mycursor = mydb.cursor()
    mycursor.execute(sql, acc)
    myresult = mycursor.fetchone()
    if myresult != None:
        return redirect("/error?message=帳號已經被註冊")
    if myresult == None:
        ins = "INSERT INTO registers (name, account, password) VALUES (%s, %s, %s)"
        val = (signup_name, signup_account, signup_password)
        mycursor.execute(ins, val)
        mydb.commit()
        # print(signup_account + "was added")
        return redirect("/")


@app.route("/signin", methods=["POST"])
def signin():
    signin_account = request.form["signin_account"]
    signin_password = request.form["signin_password"]
    usercheck = "SELECT name,account,password FROM registers WHERE account = %s"
    signinacc = (signin_account,)
    mycursor = mydb.cursor()
    mycursor.execute(usercheck, signinacc)
    myresult = mycursor.fetchone()
    if myresult != None and myresult[2] == signin_password:
        session["signin"] = myresult[0]
        session.permanent = True
        return redirect("/member")
    else:
        return redirect("/error?message=帳號或密碼輸入錯誤")


@app.route("/member")
def member():
    state = session.get("signin")
    if state == None:
        return redirect("/")
    return render_template("member.html", name=state)


@app.route("/error")
def error():
    message = request.args.get("message", "")
    return render_template("error.html", wrongMessage=message)


@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")


@app.route("/api/users")
def api():
    username = request.args.get("username", "")
    sql = "SELECT id,name,account FROM registers WHERE account = %s"
    acc = (username,)
    mycursor = mydb.cursor()
    mycursor.execute(sql, acc)
    myresult = mycursor.fetchone()
    if myresult != None:
        return json.dumps({
            "data": {
                "id": myresult[0],
                "name": myresult[1],
                "username": myresult[2]
            }
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "data": myresult
        }, ensure_ascii=False)


@app.route("/api/user", methods=["POST"])
def apiUser():
    data = request.get_json()
    name = data["name"]
    oldname = session.get("signin")
    sql = "UPDATE registers SET name = %s WHERE name = %s"
    val = (name, oldname)
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    mydb.commit()
    print(oldname+" is updated to "+name)
    try:
        return json.dumps({
            "ok": True
        })
    except:
        return json.dumps({
            "error": True
        })


app.run(port="3000")
