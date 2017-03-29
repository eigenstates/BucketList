from flask import Flask, render_template, request, json, session, redirect, jsonify
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
#WSGI stuff.
#flask_app = Flask('flaskapp')
#app = flask_app.wsgi_app
app = Flask(__name__)
app.secret_key = 'loggins messina'

#MySQL conf
mySql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'liarsClient'
app.config['MYSQL_DATABASE_PASSWORD'] = 'solids'
app.config['MYSQL_DATABASE_DB'] = 'liars'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mySql.init_app(app)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin', methods = ['POST'])
def validateLogin():
    try:
        _userName = request.form['inputEmail']
        _password = request.form['inputPassword']

        conn = mySql.connect()
        cursor = conn.cursor()
        cursor.callproc('sp_validateLogin',(_userName,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error = "Wrong email address or password")
        else:
            return render_template('error.html', error = "Wrong email address or password")
    except Exception as e:
        return render_template('error.html', error = str(e))
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
    _password = request.form['inputPassword']

    if _name and _password:
        conn = mySql.connect()
        cursor = conn.cursor()
        hashedPassword = generate_password_hash(_password)
        cursor.callproc('sp_createUser', (_name, hashedPassword))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return redirect('/userHome')
    else:
        return render_template('error.html', error = "Please fill in all fields")

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error = "Access DENIED!")

@app.route('/showAddBabble')
def addDrop():
    return render_template('addBabble.html')

@app.route('/addBabble', methods=['POST'])
def addBabble():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')
            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addBabble',(_title, _description, _user))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html', error = "A vague error occured")
        else:
            return render_template('error.html', error = "Who do you think you are? I don't know.")
    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/getBabbles')
def getBabbles():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = mySql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_getBabblesByUser',(_user,))
            babbles = cursor.fetchall()
            print("ERE")
            
            babble_dict = []
            for babble in babbles:
                babble_item = {
                    'Id': babble[0],
                    'Title':babble[1],
                    'Description':babble[2],
                    'Date':babble[3]
                }
                babble_dict.append(babble_item)
            print (babble_dict)
            return jsonify({'babbles': babble_dict})
        else:
            return render_template('error.html', error = "Who do you think you are? I don't know.")
    except Exception as e:
        return render_template('error.html', error = str(e))
    finally:
        cursor.close()
        conn.close()      


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run()
