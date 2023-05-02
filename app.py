import json
import os
import pathlib
import requests
from flask import Flask, session, abort, redirect, request, render_template, flash, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from AES_GCM import decryptFromDriveFile, decryptFromFile, encryptDriveFile, encryptToFile
from GoogleDr_api import authenticate_google_drive, change_permissions, create_file, create_folder
# For secret sharing
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir

# app = Flask(__name__)
app = Flask(__name__)

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


@app.route("/")
def login():
    return render_template('login.html')


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper


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
        return redirect("/home")
    except Exception as e:
        print("Error in callback function:", e)
        return "An error occurred: {}".format(str(e))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/home_net_id', methods=['GET', 'POST'])
def home_net_id():
    if request.method == 'POST':
        net_id = request.form['net_id']
        session["net_id"] = net_id
        print("XXX")
        print(session["net_id"])
        return render_template('dash_board.html')
    else:
        return render_template('dash_board.html')


@app.route('/dash_board', methods=['GET', 'POST'])
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


@app.route('/password_change', methods = ['GET', 'POST'])
def password_change():
    if request.method == 'POST':
        pwd = request.form['old_password']
        session['pwd_user'] = pwd
        # fname = session["net_id"] + ".encrypted"
        fname = "jxk10000.encrypted"
        text = decryptFromFile(pwd, fname)
        data = json.loads(text)
        print(data)
        bank = data['Bank-Acc']
        ssn = data['Social-Security']
        return redirect(url_for('new_password', bank = bank, ssn = ssn))
    else:
        try:
            return render_template('password_change.html')
        except Exception as e:
            print("Error in callback function:", e)
            return "An error occurred: {}".format(str(e))


@app.route('/new_password', methods = ['GET', 'POST'])
def new_password():
    bank = request.args.get('bank')
    ssn = request.args.get('ssn')
    print("I'm here " +  bank + ", "+ ssn)
    if request.method == 'POST':
        pwd = request.form['new_password']
        session['pwd_user'] = pwd
        # fname = session['net_id'] + ".encrypted"
        fname = "jxk10000.encrypted"
        ptext = json.dumps({'Social-Security': ssn, 'Bank-Acc': bank})
        encryptToFile(ptext, pwd, fname, tags = ['Social-Security', 'Bank-Acc'])
        return redirect('/dash_board')
    else:
        try:
            return render_template('new_password.html')
        except Exception as e:
            print("Error in callback function:", e)
            return "An error occurred: {}".format(str(e))

# @app.route('/password_change')
# def password_change():
#     # todo
#     return render_template('password_change.html')

@app.route('/modify')
def modify():
    return render_template('enter_password_edit.html')


@app.route('/pwd_edit_file',methods=['GET', 'POST'])
def pwd_edit_file():
    if request.method == "POST":
        pwd = request.form['pwd']
        session["pwd_user"] = pwd
    return redirect('/edit')

@app.route('/edit')
def edit():
    return render_template('edit.html')


@app.route('/edit_bank')
def edit_bank():
    pwd = session["pwd_user"]
    folder_name = session["net_id"]
    fname = session["net_id"] + ".encrypted"

    dtext_all = decryptFromDriveFile(pwd, fname, folder_name)

    if dtext_all == -1:
        flash("Decryption failed: The encrypted file has been modified, or the password that you entered is incorrect.","info")            
        return redirect('/dash_board')
    elif dtext_all == -2:
        flash("Tag not found in the decrypted data.","info")           
        return redirect('/dash_board')
    else:
        dtext_all = json.loads(dtext_all)
        session["edit_all_dec_val_bank"] = dtext_all["Bank-Acc"]
        session["edit_all_dec_val_ssn"] = dtext_all["Social-Security"]
        return render_template('edit_bank_details.html')


@app.route('/edit_ssn')
def edit_ssn():
    pwd = session["pwd_user"]
    folder_name = session["net_id"]
    fname = session["net_id"] + ".encrypted"

    dtext_all = decryptFromDriveFile(pwd, fname, folder_name)

    if dtext_all == -1:
        flash("Decryption failed: The encrypted file has been modified, or the password that you entered is incorrect.","info")            
        return redirect('/dash_board')
    elif dtext_all == -2:
        flash("Tag not found in the decrypted data.","info")           
        return redirect('/dash_board')
    else:
        dtext_all = json.loads(dtext_all)
        session["edit_all_dec_val_bank"] = dtext_all["Bank-Acc"]
        session["edit_all_dec_val_ssn"] = dtext_all["Social-Security"]
        return render_template('edit_ssn_details.html')

@app.route('/edit_all')
def edit_all():
    pwd = session["pwd_user"]
    folder_name = session["net_id"]
    fname = session["net_id"] + ".encrypted"

    dtext_all = decryptFromDriveFile(pwd, fname, folder_name)

    if dtext_all == -1:
        flash("Decryption failed: The encrypted file has been modified, or the password that you entered is incorrect.","info")            
        return redirect('/dash_board')
    elif dtext_all == -2:
        flash("Tag not found in the decrypted data.","info")           
        return redirect('/dash_board')
    else:
        dtext_all = json.loads(dtext_all)
        session["edit_all_dec_val_bank"] = dtext_all["Bank-Acc"]
        session["edit_all_dec_val_ssn"] = dtext_all["Social-Security"]
        return render_template('edit_all_details.html')

@app.route('/write_to_file',methods=['GET', 'POST'])
def write_to_file():
    if request.method == "POST":

        bank_acc = request.form['bankacc']
        ssn = request.form['ssn']

        pwd = session["pwd_user"]
        folder_name = session["net_id"]
        fname = session["net_id"] + ".encrypted"

        ptext = json.dumps({"Social-Security": ssn, "Bank-Acc": bank_acc})
        encryptDriveFile(ptext, pwd, fname, folder_name, tags=["Social-Security", "Bank-Acc"])
        
        flash("File edited!", "info")

    return redirect('/dash_board')


@app.route('/write_to_file_ssn', methods=['GET', 'POST'])
def write_to_file_ssn():
    if request.method == "POST":

        bank_acc = session["edit_all_dec_val_bank"]
        ssn = request.form['ssn']

        pwd = session["pwd_user"]
        folder_name = session["net_id"]
        fname = session["net_id"] + ".encrypted"

        ptext = json.dumps({"Social-Security": ssn, "Bank-Acc": bank_acc})
        encryptDriveFile(ptext, pwd, fname, folder_name, tags=["Social-Security", "Bank-Acc"])
        
        flash("File edited!", "info")

    return redirect('/dash_board')


@app.route('/write_to_file_bank', methods=['GET', 'POST'])
def write_to_file_bank():
    if request.method == "POST":

        bank_acc = request.form['bankacc']
        ssn = session["edit_all_dec_val_ssn"]

        pwd = session["pwd_user"]
        folder_name = session["net_id"]
        fname = session["net_id"] + ".encrypted"

        ptext = json.dumps({"Social-Security": ssn, "Bank-Acc": bank_acc})
        encryptDriveFile(ptext, pwd, fname, folder_name, tags=["Social-Security", "Bank-Acc"])
        
        flash("File edited!", "info")
    return redirect('/dash_board')


@app.route('/create_new_file', methods=['GET', 'POST'])
def create_new_file():
    if request.method == 'POST':
        bank_acc = request.form['bank_acc']
        ssn = request.form['ssn']
        pwd = request.form['pwd']
        
        bdetails = [bank_acc, ssn]
        net_id = session["net_id"]

        ptext = json.dumps(
            {"Social-Security": bdetails[1], "Bank-Acc": bdetails[0]})
        fname = net_id + ".encrypted"
        print(fname)

        encryptToFile(ptext, pwd, fname, tags=["Social-Security", "Bank-Acc"])

        drive_service = authenticate_google_drive()
        folder_name = net_id

        folder_id = create_folder(drive_service, folder_name)

        local_file_name = fname
        script_directory = os.path.dirname(os.path.abspath(__file__))
        local_file_path = os.path.join(script_directory, local_file_name)

        with open(local_file_path, 'r') as f:
            file_content = f.read()

        file_id = create_file(drive_service, os.path.basename(
            local_file_path), file_content, folder_id)
        user_email = '6348projectutd2023@gmail.com'
        change_permissions(drive_service, file_id, user_email)

        return render_template('dash_board.html')

@app.route('/decrypt', methods = ['POST', 'GET'])
def decrypt():
    pwd = session['pwd_user']
    fname = session['net_id']

    if request.method == 'POST':
        selection = request.form['decrypt']
        if selection == "ssn":
            data = decryptFromFile(pwd, fname, tag = 'Social-Security')
        elif selection == "bank":
            data = decryptFromFile(pwd, fname, tag = 'Bank')
        else:
            data = decryptFromFile(pwd, fname)
            data = "Social-Security: " + str(data[0]) + "Bank Acc: " + str(data[1])
        return redirect(url_for('decrypted', data = data))
    else:
        return render_template('decrypt.html')

@app.route('/decrypted', methods = ['POST', 'GET'])
def decrypted():
    data = request.args.get('data')
    print(data)
    return render_template('decrypted.html', data = data)

@app.route('/secret_sharing')
def secret_sharing():
    return render_template('secret_sharing.html')

@app.route('/enter')
def enter():
    return render_template('enter.html')

@app.route('/decryptshare', methods=['POST','GET'])
def decryptshare():
    # Get the shares from the HTML form
    idx1 = int(request.form['share1_idx'])
    share1 = bytes.fromhex(request.form['share1_share'])
    idx2 = int(request.form['share2_idx'])
    share2 = bytes.fromhex(request.form['share2_share'])

    # Combine the shares to reconstruct the key
    shares = [(idx1, share1), (idx2, share2)]
    key = Shamir.combine(shares)

    # Decrypt the file using the key
    with open("sdec.txt", "rb") as fi:
        nonce, tag = [fi.read(16) for x in range(2)]
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        try:
            result = cipher.decrypt(fi.read())
            cipher.verify(tag)
            with open("output1.txt", "wb") as fo:
                fo.write(result)
            return send_file("output1.txt", as_attachment=True)
        except Exception as e:
            flash("An error occured", "error")
            return redirect('/dash_board')
        
@app.route('/generate', methods=['POST','GET'])
def generate():
    # Generate a random key
    key = get_random_bytes(16)

    # Split the key into 3 shares, requiring at least 2 to reconstruct
    shares = Shamir.split(2, 3, key)

    # Store the shares in a list of dictionaries to be passed to the HTML template
    share_list = []
    for idx, share in shares:
        share_dict = {'idx': idx, 'value': share.hex()}
        share_list.append(share_dict)

    # Encrypt the file using the key
    encrypted_file_name = session["net_id"] + ".encrypted"
    with open(encrypted_file_name, "rb") as fi, open("sdec.txt", "wb") as fo:
        cipher = AES.new(key, AES.MODE_EAX)
        ct, tag = cipher.encrypt(fi.read()), cipher.digest()
        fo.write(cipher.nonce + tag + ct)

    # Pass the shares to the HTML template and render it
    return render_template('generate.html', shares=share_list)



if __name__ == '__main__':
    app.run(debug=True)
