from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
import requests
import casparser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'

app.config['MONGO_dbname'] = 'users'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

temporary_cas_data = [
    {"name": "Stock A", "symbol": "STK-A", "price": 100.00},
    {"name": "Stock B", "symbol": "STK-B", "price": 150.50}
]

mongo = PyMongo(app)

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
    if 'username' in session:
        return render_template('index.html', username=session['username'])

    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        pan_no = request.form['pan_no']
        password = request.form['password']
        fetch_cas(email, pan_no, "31/09/2023", "31/10/2023", password)
        users = mongo.db.users
        signin_user = users.find_one({'username': request.form['email']})

        if signin_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), signin_user['password'].encode('utf-8')) == \
                    signin_user['password'].encode('utf-8'):
                session['username'] = request.form['username']
                return redirect(url_for('index'))

        flash('Username and password combination is wrong')
        return render_template('signin.html')

    return render_template('signin.html')

@app.route('/view')
def view():
    username = request.args.get("user")
    user = mongo.db.users.find_one({'username': username})
    return render_template('view.html', data=temporary_cas_data)

if __name__ == "__main__":
    app.run(debug=True)
    app.run()
