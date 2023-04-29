import os
import pathlib
import requests
from flask import Flask, session, abort, redirect, request, render_template, flash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from encrypt import encryptToFile
from decrypt import decryptAll,decryptFromFile

# session = requests.Session()

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates')

app.secret_key = "googleDrive.com"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "18146000347-jpbtnt2mb2o6th6piv70efobm8b47ieu.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback")


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper


@app.route("/")
def login():
    #todo home?
    session["net_id"] = "jxk10000"
    session["user_name"] = "Chase"
   

    return render_template('login.html')


@app.route('/glogin')
def glogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)
    # session["google_id"] = "test"
    # return redirect("/dash_board")


@app.route('/glogout')
def glogout():
    session.clear()
    return redirect("/")


@app.route("/callback")
def callback():
    try:
        flow.fetch_token(authorization_response=request.url)

        if not session["state"] == request.args["state"]:
            abort(500)

        credentials = flow.credentials
        request_session = requests.Session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(
            session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")
        print(id_info.get("sub"))
        print(id_info.get("name"))
        return redirect("/dash_board")
    except Exception as e:
        print("Error in callback function:", e)
        return "An error occurred: {}".format(str(e))


@app.route('/dash_board', methods=['GET', 'POST'])
@login_required
def dash_board():
    # todo
    if request.method == 'POST':
        bank_name = request.form['bank_name']
        account_id = request.form['account_id']
        password = request.form['password']
        social_security = request.form['social_security']
        # new_password = request.form['new_password']
        print(bank_name, account_id, password, social_security)
        return render_template('dash_board.html')
    else:
        return render_template('dash_board.html')


@app.route('/new_details')
def new_details():
    return render_template('new_details.html')


@app.route('/password_change')
def password_change():
    # todo
    try:
        return render_template('password_change.html')
    except Exception as e:
        print("Error in callback function:", e)
        return "An error occurred: {}".format(str(e))


# @app.route('/password_change')
# def password_change():
#     # todo
#     return render_template('password_change.html')


@app.route('/edit_bank')
def edit_bank():
    #todo - pwd check
    pwd = "SuperSecRetPassWord"
    uinfo = [session["user_name"],session["net_id"],pwd]

    decryptedVal = decryptAll(uinfo)
    if decryptedVal == 0 :
        #todo -add flash support
        flash("File is modified", "info")
        return redirect('/')
    else: 
        session["edit_all_dec_val_bank"] = decryptedVal[0]
        session["edit_all_dec_val_ssn"] = decryptedVal[1]
        return render_template('edit_bank_details.html')

@app.route('/edit_ssn')
def edit_ssn():
    #todo - pwd check
    pwd = "SuperSecRetPassWord"
    uinfo = [session["user_name"],session["net_id"],pwd]

    decryptedVal = decryptAll(uinfo)
    if decryptedVal == 0 :
        #todo -add flash support
        flash("File is modified", "info")
        return redirect('/')
    else: 
        session["edit_all_dec_val_bank"] = decryptedVal[0]
        session["edit_all_dec_val_ssn"] = decryptedVal[1]
        return render_template('edit_ssn_details.html')

@app.route('/edit_all')
def edit_all():
    #todo - pwd check
    pwd = "SuperSecRetPassWord"
    uinfo = [session["user_name"],session["net_id"],pwd]

    decryptedVal = decryptAll(uinfo)
    if decryptedVal == 0 :
        #todo -add flash support
        flash("File is modified", "info")
        return redirect('/')
    else: 
        session["edit_all_dec_val_bank"] = decryptedVal[0]
        session["edit_all_dec_val_ssn"] = decryptedVal[1]
        return render_template('edit_all_details.html')

@app.route('/write_to_file',methods=['GET', 'POST'])
def write_to_file():
    if request.method == "POST":

        bank_acc = request.form['bankacc']
        ssn = request.form['ssn']
        bdetails = [bank_acc,ssn]

        pwd = "SuperSecRetPassWord"
        uinfo = [session["user_name"],session["net_id"],pwd]
        encryptToFile(uinfo, bdetails)

        flash("File edited!", "info")


    return redirect('/')

@app.route('/write_to_file_ssn',methods=['GET', 'POST'])
def write_to_file_ssn():
    if request.method == "POST":

        ssn = request.form['ssn']
        bdetails = [ session["edit_all_dec_val_bank"],ssn]

        pwd = "SuperSecRetPassWord"
        uinfo = [session["user_name"],session["net_id"],pwd]
        encryptToFile(uinfo, bdetails)

        flash("File edited!", "info")


    return redirect('/')

@app.route('/write_to_file_bank',methods=['GET', 'POST'])
def write_to_file_bank():
    if request.method == "POST":

        bank_acc = request.form['bankacc']
        bdetails = [ bank_acc, session["edit_all_dec_val_ssn"]]

        pwd = "SuperSecRetPassWord"
        uinfo = [session["user_name"],session["net_id"],pwd]
        encryptToFile(uinfo, bdetails)

        flash("File edited!", "info")


    return redirect('/')


        
if __name__ == '__main__':
    app.run(debug=True)

