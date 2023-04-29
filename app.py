import json
from flask import Flask,render_template,session,redirect,request,flash
from decrypt import decryptAll
from encrypt import encryptToFile

app = Flask(__name__)
app.secret_key = "key"

@app.route("/")
def home():

    #todo 
    session["net_id"] = "jxk10000"
    session["user_name"] = "Chase"
   

    #todo - add support for flash msg

    return render_template('edit.html')

@app.route('/edit_bank')
def edit_bank():
    #todo

    # 1. check whether file exists or not? - after steve code

    # 2. if exists - check modification

    # 3. error -> alert show

    # 4. file decrypt - 
        # read values
        # show in ui
        # and on submit click - again call encrypt

    
    if (True):
        print("w")

    else: 
        flash("File has been modified!", "info")



    
  
    
    return render_template('edit_bank_details.html')

@app.route('/edit_ssn')
def edit_ssn():
    #todo
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


        
if __name__ == '__main__':
    app.run(debug=True)

