from flask import Flask, render_template, request, redirect, session, make_response
from werkzeug.utils import secure_filename
import sqlite3
from fileinput import filename
import os
import csv
import datetime


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
            c.execute(f"SELECT username FROM acc_info WHERE username = '{username}'")
            checker = c.fetchall()
            print(checker)
            c.close()
            return redirect(f"/signin/username={checker}")
        except IndexError:
            error_message = 'Couldn\'t find your account, Please try again'
        
            print(error_message)

    return render_template('sign_in_username.html', error_message=error_message)

@app.route("/signin/username=<username>", methods=["GET", "POST"])
def signin_2(username):
    
    if request.method == 'POST':
        password = request.args.get('password', '').strip()
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username LIKE '{username}' AND password LIKE '{password}'")
            checker = c.fetchall()
            c.close()
            logged_in_user = make_response(redirect("/"))
            logged_in_user.set_cookie("username", checker, max_age=3600)
            return redirect('/')
        except IndexError:
            error_message = 'Incorrect Username or Password'
            return redirect('/signin', error_message=error_message)
    return render_template('sign_in_password.html')
        
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
        print(data_list)
        

        conn = sqlite3.connect("csv.db")

    
        c = conn.cursor()
        c.execute("SELECT members FROM team_1")
        checker = c.fetchall()
        c.execute("SELECT * FROM team_1")
        date_checker = [i for i in c.description]
        c.close()
        members_list = [r[0] for r in checker]

        print(data_list)

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
        
        

    
            
    
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT * FROM team_1")
    stats = c.fetchall()
    column_names = [name[0] for name in c.description]
    c.close()
    column_names[0] = column_names[0].capitalize()
    
    
    

    return render_template('data_input.html', column_names=column_names, stats=stats)

@app.route("/data-input-manual", methods=["GET", "POST"])
def manual_input():
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT members FROM team_1")
    checker = c.fetchall()
    c.execute("SELECT * FROM team_1")
    date_checker = [i for i in c.description]
    c.close()
    members_list = [r[0] for r in checker]
    if request.method == 'POST':
        
        stats_list = request.form.getlist('stats')
        num_cols = int(len(stats_list)/len(members_list))
        rows_of_values = [stats_list[i:i+num_cols] for i in range(0, len(stats_list), num_cols)]
        data_list = [[member] + row for member, row in zip(members_list, rows_of_values)]
        

        dates = []
        for rows in date_checker:
            if rows[0] != 'members':
                dates.append(rows[0])
        print(dates)

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

    
    return redirect('/data-input')


@app.route("/team_manager", methods=["GET", "POST"])
def team_manager():
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT team_name FROM _teams")
    teams = c.fetchall()
    c.close()

    return render_template("team_manager.html", teams=teams)

@app.route("/team_manager/create", methods=["GET", "POST"])
def create_team():
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    user_list = c.fetchall()
    c.close()
    if request.method == 'POST':
        team_name = request.form['team_name'].replace(" ", "_")
        members = request.form.getlist('members')
        print(team_name)
        print(members)
        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        c.execute("INSERT INTO _teams (team_name) VALUES (?)", (team_name,))
        c.execute(f"CREATE TABLE {team_name} (members)")

        for member in members:
            c.execute(f"INSERT INTO '{team_name}' (members) VALUES (?)", (member,))
        
        current_year = str(datetime.datetime.now().year)[2:]
        for i in range(1, 13):
            c.execute(f"ALTER TABLE {team_name} ADD COLUMN '{i}_{current_year}_Tar' INTEGER")
            c.execute(f"ALTER TABLE {team_name} ADD COLUMN '{i}_{current_year}_Act' INTEGER")
            
        conn.commit()
        c.close()

        
        
    return render_template("create_team.html", user_list=user_list)



if __name__ == "__main__":
    app.run(debug=True)


