import json
from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def home():
    #return "Login Page"
    return render_template('edit.html')

@app.route('/edit_bank')
def edit_bank():
    #todo
    #access file -> decrypt data
    bank_data = "123456"
    
    return render_template('edit_bank_details.html')

@app.route('/edit_ssn')
def edit_ssn():
    #todo
    return render_template('edit_ssn_details.html')

@app.route('/edit_all')
def edit_all():
    #todo
    return render_template('edit_all_details.html')
