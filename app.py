from flask import Flask, request, flash, url_for, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy
import lxml.html
from urllib.request import urlopen
import ssl
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(24) #for user sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)

class posts_(db.Model): #creating the tables in SQLAlchemy
   id = db.Column('student_id', db.Integer, primary_key = True)
   user = db.Column(db.String(25))
   url = db.Column(db.String(65))
   title = db.Column(db.String(200))
   review = db.Column(db.String(3000))

   def __init__(self, user, url, title, review):
       self.user = user
       self.url = url
       self.title = title
       self.review = review

class users_(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))

    def __init__(self,username,password):
        self.username = username
        self.password = password

class follows_(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    user = db.Column(db.String(25))
    followed = db.Column(db.String(25))

    def __init__(self,user,followed):
        self.user = user
        self.followed = followed

db.create_all() #commented this out after the first run since the tables only need to be created once


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/',methods=['POST'])
def homepage_options(): #users have two options on the homepage: log in or sign up.
    if request.form['btn'] == 'LogIn':
        return redirect(url_for('login'))
    elif request.form['btn'] == 'SignUp':
        return redirect(url_for('signup'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def check_credentials():
    username = str(request.form['username'])
    password = request.form['password']
    for i in users_.query.all(): #check if user exists
        if username == i.username:
            if password == i.password:
                session['user'] = useit #create user session
                return redirect(url_for('profile'))
            else:
                return 'Incorrect password!'
    return 'User does not exist!'

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/profile')
def profile():
    if 'user' in session:
        return render_template('profile_page.html',data=reversed([i for i in posts_.query.filter_by(user=session['user'])])) #find all posts from user. Not sure how this scales
    else:
        return 'not logged in!'

@app.route('/profile',methods=['POST'])
def profile_options(): #users have 5 options from their profile in addition to viewing their posts and the accompanying hyperlinks. They can check their timeline, follow a user, log a new article, delete and article they've already logged, or view their followers
    if request.form['btn'] == 'timeline':
        return redirect(url_for('tl'))
    elif request.form['btn'] == 'search':
        return redirect(url_for('search_friend'))
    elif request.form['btn'] == 'log':
        return redirect(url_for('log_new'))
    elif request.form['btn'] == 'delete':
        return redirect(url_for('delete'))
    elif request.form['btn'] == 'view_followers':
        return redirect(url_for('followers'))

@app.route('/followers')
def followers():
    if 'user' in session:
        followers_ = [i.user for i in follows_.query.filter_by(followed=session['user'])]
        return f'your follower(s) are {followers_}!'

@app.route('/timeline')
def tl():
    if 'user' in session:
        follows__ = [i.followed for i in follows_.query.filter_by(user=session['user'])] #find all users the current user follows and put them in a list
        data = [i for i in posts_.query.all() if str(i.user).lower() in follows__] #search through all posts to find posts by those users. Again, not sure how it scales.
        return render_template('user_timeline.html',data=reversed(data))
    else:
        return 'not logged in!'

@app.route('/timeline',methods=['POST'])
def tl_options(): #in addition to viewing their friends' posts and their accompanying hyperlinks, users can log a new article, follow a new user, or return to their profile
    if request.form['btn'] == 'log':
        return redirect(url_for('log_new'))
    elif request.form['btn'] == 'search':
        return redirect(url_for('search_friend'))
    elif request.form['btn'] == 'profile':
        return redirect(url_for('profile'))

@app.route('/search')
def search_friend():
    return render_template('search_for_friends.html')

@app.route('/log')
def log_new():
    return render_template('button.html')

@app.route('/log',methods=['POST'])
def log():
    ssl._create_default_https_context = ssl._create_unverified_context
    url = request.form['url'].lower()
    review = request.form['review']
    url_ = str(url)
    tree = (lxml.html.parse(urlopen(url_))) #parse site's HTML/XML with lxml
    title =str((tree.find('//title').text.replace('â','\'').replace('\x80\x99',''))) #find the title
    if 'user' in session:
        new_article = posts_(session['user'],url,title,review)
        db.session.add(new_article)
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        return 'not logged in!'


@app.route('/search',methods=['POST'])
def add_friend():
    searched = request.form['username']
    exists = False
    for j in users_.query.all(): #check to see if user exists
        if j.username == searched:
            exists = True
            break
    if exists == True:
        if 'user' in session:
            new_follow = follows_(session['user'],searched)
            db.session.add(new_follow)
            db.session.commit()
            return redirect(url_for('tl'))
        else:
            return 'Not Logged In!'
    else:
        return 'User doesn\'t exist!'


@app.route('/signup',methods=['POST'])
def create_credentials():
    username_attempt = request.form['username']
    password_attempt = request.form['password']
    for i in users_.query.all():
        if i.username == username_attempt:
            return 'Username Taken!'
    new_user = users_(request.form['username'], request.form['password'])
    db.session.add(new_user) #add the new credentials to the correct table
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/delete',methods=['POST'])
def deletion():
    url = request.form['username']
    if 'user' in session:
        posts_.query.filter_by(user=session['user'],url=url).delete()
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        return 'Not Logged In!'

if __name__ == "__main__":
   #db.create_all()
   app.run(debug=True)
