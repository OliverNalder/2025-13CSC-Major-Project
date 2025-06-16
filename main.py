from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('myReports.html')


@app.route("/signin", methods=["GET"])
def signin():
    error_message = ''
    if 'save' in request.args:
        username = request.args.get('username', '').strip()
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username = {username}")
            checker = c.fetchall()
            c.close()
            print(checker)
        except sqlite3.OperationalError:
            error_message = 'Couldn\'t find your account, Please try again'
        


    return render_template('sign_in_username.html', error_message=error_message)

@app.route("/signup", methods=["GET"])
def signup():
    error_message = ''
    if 'save' in request.args:
            username = request.args.get('username', '').strip()
        
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT acc_id FROM acc_info WHERE username LIKE {username}")
            checker = c.fetchall()
            c.close()
            print(checker)
            if checker:
                error_message = 'Couldn\'t find your account, Please try again'
            return render_template('sign_up_username.html', error_message=error_message)
        
        
    return render_template('sign_up_username.html', error_message=error_message)


    

@app.route("/signup/username=<username>", methods=["GET"])
def signup_2(username):
    error_message = ''
    if 'save' in request.args:
        password = request.args.get('password', '').strip()
        conn = sqlite3.connect(f'csv.db')
        c = conn.cursor()
        c.execute("INSERT INTO acc_info (username, password, manager) VALUES (?, ?, ?)", (username, password, 1))
        conn.commit()
        c.close()
        return redirect('/')
    else:
        return render_template('sign_up_password.html', error_message=error_message, username=username)


if __name__ == "__main__":
    app.run(debug=True)


