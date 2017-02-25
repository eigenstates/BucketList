from flask import Flask, render_template, request, json, session, redirect
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
#WSGI stuff.
#flask_app = Flask('flaskapp')
#app = flask_app.wsgi_app
app = Flask(__name__)
app.secrect_key = 'loggins messina'

#MySQL conf
mySql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'taskClient'
app.config['MYSQL_DATABASE_PASSWORD'] = 'solids'
app.config['MYSQL_DATABASE_DB'] = 'taskapp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mySql.init_app(app)

conn = mySql.connect()
cursor = conn.cursor()

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

        con = mySql.connect()
        cursor = con.cursor()
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
        con.close()

    
@app.route('/showSignup')
def showSignup():
    return render_template('signup.html')
    
@app.route('/signUp', methods=['POST'])
def signUp():
    #get values from UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _hashedPassword = generate_password_hash(_password)

    if _name and _email and _password:
        cursor.callproc('sp_createUser', (_name, _email, _hashedPassword))
        data = cursor.fetchall()
        if len(data) is 0:
            conn.commit()
            return json.dumps({'html': '<span> All Good </span>'})
    else:
        return json.dumps({'html': '<span> Please fill in all fields </span>'})

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', gurgle = "Access DENIED!")

@app.route('/showAddBabble')
def addDrop():
    return render_template('addBabble.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run()
