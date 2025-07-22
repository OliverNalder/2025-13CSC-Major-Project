from flask import Flask, render_template, request, redirect, session, make_response, url_for
from werkzeug.utils import secure_filename
import sqlite3
from fileinput import filename
import os
import csv
import datetime
import json


UPLOAD_FOLDER = 'temporary files'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'

@app.route("/")
def main():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
        
    user_teams = request.cookies.get("teams")
    user_teams = json.loads(user_teams)

    
        
    return render_template('myReports.html', user_teams=user_teams)


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
            
            c.close()
            return redirect(f"/signin/username={checker[0][0]}")
        except IndexError:
            error_message = 'Couldn\'t find your account, Please try again'
        
            

    return render_template('sign_in_username.html', error_message=error_message)

@app.route("/signin/username=<username>", methods=["GET", "POST"])
def signin_2(username):
    
    if 'save' in request.args:
        password = request.args.get('password', '')
        
        try:
            conn = sqlite3.connect("csv.db")
            c = conn.cursor()
            c.execute(f"SELECT username FROM acc_info WHERE username LIKE '{username}' AND password LIKE '{password}'")
            checker = c.fetchall()
            c.close()
            logged_in_user = make_response(redirect("/get_team"))
            logged_in_user.set_cookie("username", checker[0][0], max_age=3600)
            return logged_in_user
        except IndexError:
            error_message = 'Incorrect Username or Password'
            return redirect('/signin', error_message=error_message)
    return render_template('sign_in_password.html', username=username)
        
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
            logged_in_user = make_response(redirect("/get_team"))
            logged_in_user.set_cookie("username", checker[0][0], max_age=3600)
            return logged_in_user
    else:
        return render_template('sign_up_password.html', error_message=error_message, username=username, manager=manager)

@app.route("/data-input", methods=["GET", "POST"])
def data_input():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
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
        c.execute("SELECT members FROM Green_Team")
        checker = c.fetchall()
        c.execute("SELECT * FROM Green_Team")
        date_checker = [i for i in c.description]
        c.close()
        members_list = [r[0] for r in checker]

        

        dates = []
        for rows in data_list:
            if rows[0] == 'members':
                dates = rows[1:] 
            elif rows[0] not in members_list and rows[0] != '':
                c = conn.cursor()
                c.execute("INSERT INTO Green_Team (members) VALUES (?)", (rows[0],))
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
                query = f'UPDATE Green_Team SET "{column}" = ? WHERE members = ?'
                c.execute(query, (value, member_name))
                conn.commit()
                c.close()

        conn.close()
        os.remove(f"temporary files/{data_filename}")
        
        

    
            
    
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT * FROM Green_Team")
    stats = c.fetchall()
    column_names = [name[0] for name in c.description]
    c.close()
    column_names[0] = column_names[0].capitalize()
    
    
    

    return render_template('data_input.html', column_names=column_names, stats=stats)

@app.route("/data-input-manual", methods=["GET", "POST"])
def manual_input():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT members FROM Green_Team")
    checker = c.fetchall()
    c.execute("SELECT * FROM Green_Team")
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
        

        for rows in data_list:
            if rows[0] == 'members' or rows[0] == '':
                continue

            member_name = rows[0]

            for num in range(len(dates)):
                column = dates[num]
                value = rows[num + 1]

                

                c = conn.cursor()
                query = f'UPDATE Green_Team SET "{column}" = ? WHERE members = ?'
                c.execute(query, (value, member_name))
                conn.commit()
                c.close()

    
    return redirect('/data-input')


@app.route("/team_manager", methods=["GET", "POST"])
def team_manager():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    
    teams = request.cookies.get("teams")
    teams = json.loads(teams)

    return render_template("team_manager.html", teams=teams)

@app.route("/team_manager/create", methods=["GET", "POST"])
def create_team():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    error_message = ''
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    user_list = c.fetchall()
    c.close()
    if request.method == 'POST':
        team_name = request.form['team_name'].replace(" ", "_")
        members = request.form.getlist('members')
        
        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        try:
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
            return redirect("/team_manager")
        except sqlite3.OperationalError:
            error_message = 'This team name is taken'
            return render_template("create_team.html", user_list=user_list, error_message=error_message)
            
    
        
    return render_template("create_team.html", user_list=user_list, error_message=error_message)

@app.route("/team_manager/edit/<team_name>", methods=["GET", "POST"])
def edit_team(team_name):
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    
    teams = request.cookies.get("teams")
    teams = json.loads(teams)
    if team_name not in teams:
        return redirect('/team_manager')

    conn = sqlite3.connect("csv.db")
    c = conn.cursor()

    c.execute("SELECT username FROM acc_info")
    all_users = [row[0] for row in c.fetchall()]

    
    c.execute(f"SELECT members FROM '{team_name}'")
    current_members = [row[0] for row in c.fetchall()]

    conn.close()

    if request.method == 'POST':
        updated_members = request.form.getlist("members")

        conn = sqlite3.connect("csv.db")
        c = conn.cursor()

        for new in updated_members:
            if new not in current_members:
                
                c.execute(f"INSERT INTO '{team_name}' (members) VALUES '?'", (new,))

        for old in current_members:
            if old not in updated_members:
                
                c.execute(f"DELETE FROM '{team_name}' WHERE (members) VALUES '?'", (old,))

        conn.commit()
        c.close()

        
        return redirect('/team_manager')

    return render_template("edit_team.html", team_name=team_name, all_users=all_users, current_members=current_members)

@app.route('/get_team')
def get_team():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    teams = []
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT team_name FROM _teams")
    checker = [a[0] for a in c.fetchall()]
    for check in checker:
        c.execute(f"SELECT members FROM {check}")
        members = [member[0] for member in c.fetchall()]
        if username in members:
            teams.append(check)
    
    c.close()

    teams = json.dumps(teams)
    user_teams = make_response(redirect("/"))
    user_teams.set_cookie("teams", teams, max_age=3600)
    return user_teams
    

    
    

@app.route('/signout')
def signout():
    response = make_response(redirect('/'))
    response.set_cookie('username', '', max_age=0)
    return response

if __name__ == "__main__":
    app.run(debug=True)


