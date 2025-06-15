from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('myReports.html')


@app.route("/signin", methods=["GET"])
def login():
    error_message = ''
    if 'save' in request.args:
        username = request.args.get('username', '').strip()
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username LIKE {username}")
            checker = c.fetchall()
            c.close()
            print(checker)
        except sqlite3.OperationalError:
            error_message = 'Couldn\'t find your account, Please try again'
        


    return render_template('sign_in_username.html', error_message=error_message)

@app.route("/signup", methods=["GET"])
def login():
    error_message = ''
    if 'save' in request.args:
        username = request.args.get('username', '').strip()
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username LIKE {username}")
            checker = c.fetchall()
            c.close()
            error_message = 'Couldn\'t find your account, Please try again'
        except sqlite3.OperationalError:
            print(checker)
        


    return render_template('sign_up_username.html', error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)


