from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename
import sqlite3
from fileinput import filename
import os
import csv


UPLOAD_FOLDER = 'temporary files'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'

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
            c.execute(f"SELECT acc_id FROM acc_info WHERE username = '{username}'")
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
            manager = request.args.get('manager', '')
            if manager == 'true':
                manager = 1
            else:
                manager = 0
            
            try:
                conn = sqlite3.connect("csv.db")
                c = conn.cursor()
                c.execute(f"SELECT username FROM acc_info WHERE username LIKE '{username}'")
                checker = c.fetchall()
                c.close()
                if checker[0][0] == username:
                    error_message = 'This Name is Already in Use'
                    return render_template('sign_up_username.html', error_message=error_message)
            except IndexError:
                return redirect(f'/signup/username={username}/type={manager}')
        
        
    return render_template('sign_up_username.html', error_message=error_message)


    

@app.route("/signup/username=<username>/type=<manager>", methods=["GET"])
def signup_2(username, manager):
    error_message = ''
    if 'save' in request.args:
        password = request.args.get('password', '').strip()
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username LIKE '{username}'")
            checker = c.fetchall()
            c.close()
            if checker[0][0] == username:
                error_message = 'This Name is Already in Use'
                return render_template('sign_up_username.html', error_message=error_message)
        except IndexError:
            conn = sqlite3.connect(f'csv.db')
            c = conn.cursor()
            c.execute("INSERT INTO acc_info (username, password, manager) VALUES (?, ?, ?)", (username, password, manager))
            conn.commit()
            c.close()
            return redirect('/')
    else:
        return render_template('sign_up_password.html', error_message=error_message, username=username, manager=manager)

@app.route("/data-input", methods=["GET", "POST"])
def data_input():
    if request.method == 'POST':
        f = request.files.get('file')

        data_filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

 
        data_list = []
        with open(f'temporary files/{data_filename}', 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                data_list.append(row)

        conn = sqlite3.connect("csv.db")

    
        c = conn.cursor()
        c.execute("SELECT members FROM team_1")
        checker = c.fetchall()
        c.close()

        members_list = [r[0] for r in checker]

        dates = []
        for rows in data_list:
            if rows[0] == 'members':
                dates = rows[1:] 
            elif rows[0] not in members_list and rows[0] != '':
                c = conn.cursor()
                c.execute("INSERT INTO team_1 (members) VALUES (?)", (rows[0],))
                conn.commit()
                c.close()

        for rows in data_list:
            if rows[0] == 'members' or rows[0] == '':
                continue

            member_name = rows[0]

            for num in range(len(dates)):
                column = dates[num]
                value = rows[num + 1]

                

                c = conn.cursor()
                query = f'UPDATE team_1 SET "{column}" = ? WHERE members = ?'
                c.execute(query, (value, member_name))
                conn.commit()
                c.close()

        conn.close()
        os.remove(f"temporary files/{data_filename}")

    return render_template('data_input.html')

@app.route("/team_manager")
def team_manager():
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT team_name FROM _teams")
    teams = c.fetchall()
    c.close()
    print(teams)

    return render_template("team_manager.html", teams=teams)



if __name__ == "__main__":
    app.run(debug=True)


