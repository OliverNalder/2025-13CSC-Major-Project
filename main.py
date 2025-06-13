from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('myReports.html')

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/signin", method="GET")
def login():
    if request.GET.save:
        username = request.GET.username.strip()

        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        c.execute(f"SELECT username FROM acc_info WHERE username LIKE {username}")


    return render_template('sign_in.html')