from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
import requests
import casparser
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'


with open('data.json', 'r') as openfile: 
    temporary_cas_data = json.load(openfile)["data"]
 

@app.route("/")
@app.route("/main")
def main():
    return render_template('index.html')

def fetch_cas(email, pan_no, from_date, to_date, password):
    url = "https://kfintech-cas-mailback-automation.p.rapidapi.com/request_ecas"
    payload = {
        "email": email,
        "pan_no": pan_no,
        "from_date": from_date,
        "to_date": to_date,
        "password": password
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "eb8b8c3737msh83982885850bb0ap1569c6jsn5bc1266dfe30",
        "X-RapidAPI-Host": "kfintech-cas-mailback-automation.p.rapidapi.com"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Response: ", response.text)
        return response.text
    except:
        print("Error generating CAS")
        return "Error"

@app.route('/parse_cas', methods=['GET', 'POST'])
def parse_cas():
    if request.method == 'POST':
        cas_file = request.files['cas_file']
        password = request.form['password']
        cas_file.save("cas.pdf")
        cas_data = casparser.read_cas_pdf("cas.pdf", password)
        return cas_data
    return render_template('parse_cas.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/view', methods=['GET', 'POST'])
def view():
    if request.method == 'POST':
        email = request.form['email']
        pan_no = request.form['pan_no']
        password = request.form['password']
        fetch_cas(email, pan_no, "31/09/2023", "31/10/2023", password)

    return render_template('view.html', data=temporary_cas_data)

if __name__ == "__main__":
    app.run(debug=True)
    app.run()
