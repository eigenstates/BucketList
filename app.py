"""
This specific server is for the Daily Bucket List
"""

import os, uuid
from flask import Flask, render_template, request, json, session, redirect, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
#WSGI stuff.
#flask_app = Flask('flaskapp')
#app = flask_app.wsgi_app

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static/Uploads")

app = Flask(__name__)
app.secret_key = 'loggins messina'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOADS_FOLDER"] = UPLOAD_FOLDER

#MySQL conf
mySql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'taskClient'
app.config['MYSQL_DATABASE_PASSWORD'] = 'solids'
app.config['MYSQL_DATABASE_DB'] = 'taskapp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mySql.init_app(app)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        conn = mySql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error="Wrong email address or password")
        else:
            return render_template('error.html', error="Wrong email address or password")
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/showSignup')
def showSignup():
    return render_template('signup.html')

@app.route('/signUp', methods=['POST'])
def signUp():
    #get values from UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    if _name and _email and _password:
        conn = mySql.connect()
        cursor = conn.cursor()
        hashedpassword = generate_password_hash(_password)
        cursor.callproc('sp_createUser', (_name, _email, hashedpassword))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return redirect('/userHome')
    else:
        return render_template('error.html', error="Please fill in all fields")

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error="Access DENIED!")

@app.route('/showAddBabble')
def addDrop():
    return render_template('addBabble.html')

@app.route('/getBabbles')
def getBabbles():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_getBabblesByUser', (_user,))
            babbles = cursor.fetchall()

            babble_dict = []
            for babble in babbles:
                babble_item = {
                    'Id': babble[0],
                    'Title':babble[1],
                    'Description':babble[2],
                    'Date':babble[3]
                }
                babble_dict.append(babble_item)
            return jsonify({'babbles': babble_dict})
        else:
            return render_template('error.html', error="Who do you think you are? I don't know.")
    except StandardError as ex:
        return render_template('error.html', error=str(ex))
    finally:
        cursor.close()
        conn.close()

'''@app.route("/getBabbleById", methods=['POST'])
def getBabbleById():
    try:
        if session.get('user'):
            _id = request.form['id']
            _user = session.get('user')

            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_getBabblesById',(_id,_user,))
            result = cursor.fetchall()

            babble = []
            babble.append({'Id':result[0][0], 'Title':result[0][1], 'Description':[0][2]})
            return json.dumps(babble)
        else:
            return render_template('error.html', error='Do you need to log in? Yes. Yes you do. UNAUTHORIZED!')
    except Exception as e:
        return render_template('error.html', error = str(e))'''

@app.route('/addBabble', methods=['POST'])
def addBabble():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')

            if request.form.get('filePath') is None:
                _filepath = ''
            else:
                _filepath = request.form.get('filePath')
            if request.form.get('private') is None:
                _private = 0
            else:
                _private = 1
            if request.form.get('done') is None:
                _done = 0
            else:
                _done = 1

            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addBabble', (_title, _description, _user, _filepath, _private, _done))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html', error="A vague error occured")
        else:
            return render_template('error.html', error="Who do you think you are? I don't know.")
    except StandardError as ex:
        return render_template('error.html', error=str(ex))
    finally:
        cursor.close()
        conn.close()

@app.route("/updateBabble", methods=['POST'])
def updateBabble():
    try:
        if session.get('user'):
            _id = request.form['id']
            _title = request.form['title']
            _description = request.form['description']
            _user = session.get('user')
            _file = request.form['filePath']
            _is_private = request.form['private']
            _is_done = request.form['done']

            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_updateBabble', (_title, _description, _id, _user, _file, _is_private, _is_done))
            result = cursor.fetchall()
            if len(result) is 0:
                conn.commit()
                return json.dumps({"status":"OK"})
            else:
                return json.dumps({"status":"The data is messed up"})
    except StandardError as ex:
        return json.dumps({"status":"Do you need to log in? Yes. Yes you do. UNAUTHORIZED!"})
    finally:
        cursor.close()
        conn.close()

@app.route("/deleteBabble", methods=['POST'])
def deleteBabble():
    try:
        _id = request.form['id']
        _user = session.get('user')

        conn = mySql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_deleteBabble', (_id, _user))
        result = cursor.fetchall()
        if len(result) is 0:
            conn.commit()
            return json.dumps({"status":"OK"})
        else:
            return json.dumps({"status":"The data is messed up"})
    except StandardError as ex:
        return json.dumps({"status":"Do you need to log in? Yes. Yes you do. UNAUTHORIZED!"})
    finally:
        cursor.close()
        conn.close()

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        f_name = str(uuid.uuid4()) + extension
        file.save(os.path.join(app.config["UPLOADS_PATH"], f_name))
        return json.dumps({"filename": f_name})



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run()
