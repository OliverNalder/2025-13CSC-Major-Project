from flask import Flask, render_template, request, redirect, session, make_response, send_file
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
import datetime
import json
import tempfile
import bcrypt
import re
import random
import random


UPLOAD_FOLDER = 'temporary files'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'This is your secret key to utilize session in Flask'



@app.route("/", methods=["GET", "POST"])
def main():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    if request.method == 'POST' and request.form.get("select"):
        team = request.form.get("select")
        current_year = str(datetime.datetime.now().year)[2:]
        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_team", team)
        resp.set_cookie("selected_year", current_year)
        return resp

    selected_team = request.cookies.get("selected_team", 0)
    if selected_team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)
    
    

    team = request.cookies.get('selected_team', 0)
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute(f"SELECT members FROM '{team}'")
    team_members = [t[0] for t in c.fetchall()]
    c.close()
    

    

    if username not in checker:
        return redirect('/signout')
    if request.method == 'POST' and request.form.get("select"):
        team = request.form.get("select")

        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_team", team)
        return resp

    
    

        
    user_teams = request.cookies.get("teams")
    user_teams = json.loads(user_teams)

    
        
    return redirect('/report')

@app.route("/report")
def team_report():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    team = request.cookies.get("selected_team", 0)
    if team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)
    
    user_teams = request.cookies.get("teams")
    user_teams = json.loads(user_teams)

    year = request.cookies.get('selected_year')



    targets = []
    actuals = []
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    for i in range(1,13):
        column_name = f"{i}_{year}_Tar"
        c.execute(f'SELECT "{column_name}" FROM "{team}"')
        column = [col[0] for col in c.fetchall()]
        num = 0
        for col in column:
            if col == '':
                col = 0
            else:
                col = int(col)
            num += col
        if num == 0:
            num = None
        targets.append(num)
        column_name = f"{i}_{year}_Act"
        c.execute(f'SELECT "{column_name}" FROM "{team}"')
        column = [col[0] for col in c.fetchall()]
        num = 0
        for col in column:
            if col == '':
                col = 0
            else:
                col = int(col)
            num += col
        if num == 0:
            num = None
        actuals.append(num)
    
    

    c.close()

    cumulative_targets = []
    num = 0
    for target in targets:
        if target == None:
            target = 0
        num += target
        cumulative_targets.append(num)

    cumulative_actuals = []
    num = 0
    for actual in actuals:
        if actual == None:
            actual = 0
        num += actual
        cumulative_actuals.append(num)
    
    

    conn = sqlite3.connect('csv.db')
    c = conn.cursor()
    c.execute(f"SELECT members FROM '{team}'")
    team_members = [t[0] for t in c.fetchall()]

    stacked_members = {}

    for member in team_members:
        actual_list = []
        for i in range(1, 13):
            column_name = f"{i}_{year}_Act"
            c.execute(f'SELECT "{column_name}" FROM "{team}" WHERE members LIKE ?', (member,))
            result = c.fetchall()[0][0]
            if result == '':
                result = None
            else:
                result = int(result)
            actual_list.append(result)
        stacked_members[member] = actual_list

    
    current_month_cumulative_tar = 0
    for i in range(len(cumulative_actuals)):
        if actuals[i] == None:
            current_month_cumulative_tar = cumulative_targets[i-1]
            break
    if current_month_cumulative_tar == 0:
        current_month_cumulative_tar = cumulative_targets[-1]

    
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    colours = [("#{:06x}".format(random.randint(0, 0xFFFFFF))) for _ in team_members]
    

    return render_template("team_report.html", labels=labels, target_data=targets, actual_data=actuals, cumulative_target=cumulative_targets, cumulative_actual=cumulative_actuals, stacked_data=stacked_members, team_members=team_members, colours=colours, current_month_cumulative_tar=current_month_cumulative_tar, username=username)

@app.route("/report/<individual>")
def individual_report(individual):
    
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    team = request.cookies.get("selected_team", 0)
    if team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)
    
    user_teams = request.cookies.get("teams")
    user_teams = json.loads(user_teams)

    year = request.cookies.get('selected_year')



    targets = []
    cumulative_targets = []
    actuals = []
    cumulative_actuals = []
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    act_num = 0
    tar_num = 0
    for i in range(1,13):
        column_name = f"{i}_{year}_Tar"
        c.execute(f'SELECT "{column_name}" FROM "{team}" WHERE members LIKE ?', (individual, ))
        column = c.fetchall()[0][0]
        
        if column == '':
            column = 0
        else:
            tar_num += column
        
        targets.append(column)
        cumulative_targets.append(tar_num)

        column_name = f"{i}_{year}_Act"
        c.execute(f'SELECT "{column_name}" FROM "{team}" WHERE members LIKE ?', (individual, ))
        column = c.fetchall()[0][0]

        
        if column == '':
            column = 0
        else:
            act_num += column
        
        actuals.append(column)
        cumulative_actuals.append(act_num)
    

    c.close()

    cumulative_targets = []
    num = 0
    for target in targets:
        if target == None:
            target = 0
        num += target
        cumulative_targets.append(num)

    cumulative_actuals = []
    num = 0
    for actual in actuals:
        if actual == None:
            actual = 0
        num += actual
        cumulative_actuals.append(num)
    
    current_month_cumulative_tar = 0
    for i in range(len(cumulative_actuals)):
        if actuals[i] == 0:
            current_month_cumulative_tar = cumulative_targets[i-1]
            break
    if current_month_cumulative_tar == 0:
        current_month_cumulative_tar = cumulative_targets[-1]

    
    

    conn = sqlite3.connect('csv.db')
    c = conn.cursor()
    c.execute(f"SELECT members FROM '{team}'")
    team_members = [t[0] for t in c.fetchall()]

    
    labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    colours = [("#{:06x}".format(random.randint(0, 0xFFFFFF))) for _ in team_members]
    

    return render_template("individual_report.html", labels=labels, target_data=targets, actual_data=actuals, cumulative_target=cumulative_targets, cumulative_actual=cumulative_actuals, team_members=team_members, colours=colours, current_month_cumulative_tar=current_month_cumulative_tar, username=username, individual=individual)


@app.route("/signin", methods=["GET"])
def signin():
    error_message = ''
    error_message = request.args.get("error_message", '')
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
        password_bytes = password.encode('utf-8') 
    
        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        c.execute("SELECT username, password FROM acc_info WHERE username = ?", (username,))
        result = c.fetchone()
        c.close()
        if result:
            db_username, db_hashed_password = result
            
            if bcrypt.checkpw(password_bytes, db_hashed_password):
                
                logged_in_user = make_response(redirect("/get_team"))
                logged_in_user.set_cookie("username", db_username, max_age=3600)
                logged_in_user.set_cookie('teams', '', max_age=0)
                logged_in_user.set_cookie('selected_year', '', max_age=0)
                return logged_in_user
            else:
                error_message = 'Incorrect Username or Password'
                return redirect(f'/signin?error_message={error_message}')


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
            c.execute("INSERT INTO acc_info (username, password, manager) VALUES (?, ?, ?)", (username, bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), manager))
            conn.commit()
            c.close()
            logged_in_user = make_response(redirect("/get_team"))
            logged_in_user.set_cookie("username", username, max_age=3600)
            logged_in_user.set_cookie('teams', '', max_age=0)
            logged_in_user.set_cookie('selected_year', '', max_age=0)
            return logged_in_user
    else:
        return render_template('sign_up_password.html', error_message=error_message, username=username, manager=manager)

@app.route("/data-input", methods=["GET", "POST"])
def data_input():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    if request.method == 'POST' and request.form.get("select"):
        team = request.form.get("select")
        current_year = str(datetime.datetime.now().year)[2:]
        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_team", team)
        resp.set_cookie("selected_year", current_year)
        return resp

    selected_team = request.cookies.get("selected_team", 0)
    if selected_team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)
    
    if request.method == 'POST' and request.form.get("year"):
        selected_year = request.form.get("year")
        selected_year = selected_year[2] + selected_year[3]
        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_year", selected_year, max_age=3600)
        return resp

    
    
    teams = json.loads(request.cookies.get('teams'))
    team = request.cookies.get('selected_team')

    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute(f"SELECT members FROM '{team}'")
    team_members = [t[0] for t in c.fetchall()]
    c.close()

    error_message = ''


    year = request.cookies.get('selected_year')

    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    column_names = ['members']
    stats = []
    for i in range(1, 13):
        column_names.append(f"{i}_{year}_Tar")
        column_names.append(f"{i}_{year}_Act")
    
    quoted_columns = ', '.join([f'"{col}"' for col in column_names])

    c.execute(f'SELECT {quoted_columns} FROM "{team}"')
    rows = c.fetchall()

    
    stats = [list(row) for row in rows]
    
    c.execute(f"SELECT * FROM '{team}'")
    all_column_names = [name[0] for name in c.description]

    c.close()
    column_names[0] = column_names[0].capitalize()
    


    years = []
    for col in all_column_names:
        match = re.match(r"\d+_(\d+)_\w+", col)
        if match:
            y = (2000 + int(match.group(1)))
            if y not in years:   
                years.append(y)
        
    years = sorted(years)

    
    
    year = int(year)

    if request.method == 'POST':

        f = request.files.get('file')
        if f == None:
            error_message = 'No file selected'
            return render_template('data_input.html', column_names=column_names, stats=stats, team=team, user_teams=teams, team_members=team_members, error_message=error_message, years=years, selected_year=(2000+year), username=username)
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
        c.execute(f"SELECT members FROM '{team}'")
        checker = c.fetchall()
        c.execute(f"SELECT * FROM '{team}'")
        date_checker = [i[0] for i in c.description]
        c.close()
        members_list = [r[0] for r in checker]

        for d in data_list[0]:
            if d not in date_checker:
                error_message = 'CSV File Error: Incorrect Format'
                os.remove(f"temporary files/{data_filename}")
                return render_template('data_input.html', column_names=column_names, stats=stats, team=team, user_teams=teams, team_members=team_members, error_message=error_message, years=years, selected_year=(2000+year), username=username)

        dates = []
        for rows in data_list:
            if rows[0] == 'members':
                dates = rows[1:] 
            elif rows[0] not in members_list and rows[0] != '':
                c = conn.cursor()
                c.execute(f"INSERT INTO '{team}' (members) VALUES (?)", (rows[0],))
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
                query = f'UPDATE "{team}" SET "{column}" = ? WHERE members = ?'
                c.execute(query, (value, member_name))
                conn.commit()
                c.close()

        conn.close()
        os.remove(f"temporary files/{data_filename}")
        

    return render_template('data_input.html', column_names=column_names, stats=stats, team=team, user_teams=teams, team_members=team_members, error_message=error_message, years=years, selected_year=(2000+year), username=username)

@app.route("/data-input-manual", methods=["GET", "POST"])
def manual_input():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    if request.method == 'POST' and request.form.get("select"):
        team = request.form.get("select")

        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_team", team)
        return resp

    selected_team = request.cookies.get("selected_team", 0)
    if selected_team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)

    team = request.cookies.get('selected_team')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute(f"SELECT members FROM '{team}'")
    checker = c.fetchall()
    c.execute(f"SELECT * FROM '{team}'")
    date_checker = [i for i in c.description]
    c.close()
    members_list = [r[0] for r in checker]

    selected_year = request.cookies.get("selected_year")
    dates = []
    for i in range(1,13):
        dates.append(f'{i}_{selected_year}_Tar')
        dates.append(f'{i}_{selected_year}_Act')

    if request.method == 'POST':
        
        stats_list = request.form.getlist('stats')
        num_cols = int(len(stats_list)/len(members_list))
        rows_of_values = [stats_list[i:i+num_cols] for i in range(0, len(stats_list), num_cols)]
        data_list = [[member] + row for member, row in zip(members_list, rows_of_values)]
        

        
        

        for row in data_list:
            if row[0] == 'members' or row[0] == '':
                continue

            member_name = row[0]
            values = row[1:]

            for column, value in zip(dates, values):
                c = conn.cursor()
                query = f'UPDATE "{team}" SET "{column}" = ? WHERE members = ?'
                c.execute(query, (value, member_name))
                conn.commit()
                c.close()

    
    return redirect('/data-input')


@app.route("/team_manager", methods=["GET", "POST"])
def team_manager():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    teams = request.cookies.get("teams")
    teams = json.loads(teams)

    team = request.cookies.get('selected_team')
    if team != None:
        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        c.execute(f"SELECT members FROM '{team}'")
        team_members = [t[0] for t in c.fetchall()]
        c.close()
    else:
        team_members = []
    return render_template("team_manager.html", teams=teams, team_members=team_members, username=username)

@app.route("/team_manager/create", methods=["GET", "POST"])
def create_team():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    team = request.cookies.get('selected_team')
    
    if team != None:
        conn = sqlite3.connect("csv.db")
        c = conn.cursor()
        c.execute(f"SELECT members FROM '{team}'")
        team_members = [t[0] for t in c.fetchall()]
        c.close()
    else:
        team_members = []

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
            c.execute(f"INSERT INTO _teams (team_name) VALUES ('{team_name}')")
            c.execute(f"CREATE TABLE {team_name} (members)")
            conn.commit()

            for member in members:
                c.execute(f"INSERT INTO '{team_name}' (members) VALUES (?)", (member,))

            current_year = str(datetime.datetime.now().year)[2:]
            for i in range(1, 13):
                c.execute(f"ALTER TABLE {team_name} ADD COLUMN '{i}_{current_year}_Tar' INTEGER DEFAULT ''")
                c.execute(f"ALTER TABLE {team_name} ADD COLUMN '{i}_{current_year}_Act' INTEGER DEFAULT ''")

            conn.commit()
            teams = []
            c.execute("SELECT team_name FROM _teams")
            checker = [a[0] for a in c.fetchall()]
            for check in checker:
                c.execute(f"SELECT members FROM {check}")
                members = [member[0] for member in c.fetchall()]
                if username in members:
                    teams.append(check)

            teams = json.dumps(teams)
            user_teams = make_response(redirect("/team_manager"))
            user_teams.set_cookie("teams", teams, max_age=3600)
            

            c.close()
            return user_teams

        except sqlite3.OperationalError:
            error_message = 'This team name is taken'
            return render_template("create_team.html", user_list=user_list, error_message=error_message, team_members=team_members, username=username)



    return render_template("create_team.html", user_list=user_list, error_message=error_message, username=username)

@app.route("/team_manager/edit/<team_name>", methods=["GET", "POST"])
def edit_team(team_name):
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
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
                
                c.execute(f"INSERT INTO '{team_name}' (members) VALUES (?)", (new,))

        for old in current_members:
            if old not in updated_members:
                
                c.execute(f"DELETE FROM '{team_name}' WHERE members = ?", (old,))

        conn.commit()
        c.close()

        
        return redirect('/team_manager')

    return render_template("edit_team.html", team_name=team_name, all_users=all_users, current_members=current_members, username=username)

@app.route('/get_team')
def get_team():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
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
    user_teams.set_cookie("selected_year", "25", max_age=3600)
    return user_teams
    

    
    

@app.route('/signout')
def signout():
    response = make_response(redirect('/'))
    response.set_cookie('username', '', max_age=0)
    response.set_cookie('selected_team', '', max_age=0)
    response.set_cookie('teams', '', max_age=0)
    response.set_cookie('selected_year', '', max_age=0)
    return response


@app.route('/download_csv')
def download():
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    team = request.cookies.get('selected_team')

    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM '{team}'")
    rows = c.fetchall()
    headers = [description[0] for description in c.description]
    c.close()
    
    temp = tempfile.NamedTemporaryFile(mode='w+', newline='', delete=False, suffix=".csv")
    writer = csv.writer(temp)
    writer.writerow(headers)
    writer.writerows(rows)
    temp.seek(0)

    return send_file(temp.name, as_attachment=True, download_name=f"{team}.csv", mimetype='text/csv')

@app.route('/new_year/<new>', methods=["GET", "POST"])
def add_new_year(new):
    
    username = request.cookies.get("username", 0)
    if username == 0:
        return render_template('not_signed_in.html')
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute("SELECT username FROM acc_info")
    checker = [check[0] for check in c.fetchall()]
    c.close()
    if username not in checker:
        return redirect('/signout')
    
    if request.method == 'POST' and request.form.get("select"):
        team = request.form.get("select")

        resp = make_response(redirect(request.path))
        resp.set_cookie("selected_team", team)
        return resp

    selected_team = request.cookies.get("selected_team", 0)
    if selected_team == 0:
        
        user_teams = json.loads(request.cookies.get("teams", "[]"))
        return render_template('select_team.html', user_teams=user_teams, username=username)
    
    conn = sqlite3.connect("csv.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM '{selected_team}'")
    checker = [col[0] for col in c.description]

    years = []
    for col in checker:
        match = re.match(r"\d+_(\d+)_\w+", col)
        if match:
            years.append(int(match.group(1)))

    if int(new) == 0:
        new_year = min(years) - 1 
    elif int(new) == 1:
        new_year = max(years) + 1  
    else:
        conn.close()
        return redirect('/data-input')

    for i in range(1, 13):
        c.execute(f"ALTER TABLE '{selected_team}' ADD COLUMN '{i}_{new_year}_Tar' INTEGER DEFAULT ''")
        c.execute(f"ALTER TABLE '{selected_team}' ADD COLUMN '{i}_{new_year}_Act' INTEGER DEFAULT ''")
        conn.commit()
    
    conn.commit()
    return redirect('/data-input')


@app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'


@app.errorhandler(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'

if __name__ == "__main__":
    app.run(debug=True)


