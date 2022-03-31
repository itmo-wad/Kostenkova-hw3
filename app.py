from flask import Flask, render_template, request, redirect, send_from_directory, flash, session
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import Length, EqualTo, InputRequired, DataRequired
from flask_bootstrap import Bootstrap 
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/wad_hw_02'
bootstrap = Bootstrap(app)
mongo = PyMongo(app)
app.secret_key = 'wad'


class SignUpForm(FlaskForm):
    
    login = StringField('LOGIN', validators=[InputRequired(message='LOGIN REQUIRED'), Length(min=3, max=25, message='LOGIN MUST BE BETWEEN 3 AND 25 CHARACTERS')])
    password = PasswordField('PASSWORD', validators=[InputRequired(message='PASSWORD REQUIRED'), Length(min=8, max=30, message='PASSWORD MUST BE BETWEEN 8 AND 30 CHARACTERS')])
    password_retype = PasswordField('RETYPE PASSWORD', validators=[InputRequired(message='RETYPE OF PASSWORD REQUIRED'), EqualTo('password', message='PASSWORDS MUST BE EQUAL')])
    submit = SubmitField('SIGN UP')

class AuthForm(FlaskForm):
    login = StringField('LOGIN', validators=[InputRequired(message='LOGIN REQUIRED')])
    password = PasswordField('PASSWORD', validators=[InputRequired(message='PASSWORD REQUIRED')])
    submit = SubmitField('LOG IN')

class TimelineForm(FlaskForm):
    title = StringField('TITLE', validators=[InputRequired(message='TITLE REQUIRED')])
    message = StringField('MESSAGE', validators=[InputRequired(message='MSG REQUIRED')])
    submit = SubmitField('POST')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    form = SignUpForm()
    login = form.login.data
    password = form.password.data
    password_retype = form.password_retype.data

    if request.method == 'GET':
        return render_template('signup.html', form=form)

    else:
        
        if mongo.db.users.count_documents({'login':login}) !=0:
            flash('Login already exist')
            return redirect('/signup')
        elif password_retype != password:
            flash('Password doesnt match, try harder')
            return redirect('/signup')    
        else:
            mongo.db.users.insert_one({
                'login':login,
                'password':generate_password_hash(password)
                })
            return redirect('/auth')
    
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    form = AuthForm()
    login = form.login.data
    password = form.password.data

    if 'login' in session:
        return redirect('/profile')

    if request.method == 'GET':
        return render_template('auth.html', form=form)

    else:
        user = mongo.db.users.find_one({'login':login})

        if user and check_password_hash(user['password'], password):
            session['login'] = user.get('login')
            return redirect('/profile')
        else:
            flash('wrong creds! Try again :(')
            return redirect('/auth')

@app.route('/create', methods=(["GET","POST"]))
def create():
    
    form = TimelineForm()
    title = form.title.data
    message = form.message.data
    if 'login' in session:
        if request.method == "GET":
            return render_template("create.html", form = form)
        else:
            mongo.db.timeline.insert_one({'title' : title, 'message' : message})
            timeline = mongo.db.timeline.find()
            return render_template('timeline.html', timeline = timeline, form=form, title = title, message = message)
    else: 
        return redirect('/profile')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'login' in session:
        login = session['login']
        return render_template('profile.html', login = login)
    else:
        return redirect('/auth')

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if 'login' in session:
        session.pop('login', None)
        return render_template('index.html')
    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
    
    