from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('myReports.html')

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/signin")
def login():

    return render_template('sign_in.html')