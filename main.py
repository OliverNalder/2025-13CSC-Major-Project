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
        print(data_filename)

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))

        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)

        with open(f'temporary files/{data_filename}', mode='r') as infile:
            reader = csv.reader(infile)
            with open(data_filename, mode='w') as outfile:
                writer = csv.writer(outfile)
                
                mydict = {rows[0]:rows[1] for rows in reader}
                print(mydict)

        
    return render_template('data_input.html')


if __name__ == "__main__":
    app.run(debug=True)


