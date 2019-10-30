from flask import Flask, request, flash, url_for, redirect, render_template,session
from flask_sqlalchemy import SQLAlchemy
import lxml.html
from urllib.request import urlopen
import flask_avatars
from flask_avatars import Avatars
import ssl
import hashlib
import os
import time


app = Flask(__name__)
avatars = Avatars(app)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'

db = SQLAlchemy(app)

class posts_(db.Model):
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


class follows(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    user = db.Column(db.String(25))
    followed = db.Column(db.String(25))

    def __init__(self,user,followed):
        self.user = user
        self.followed = followed



class users(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    db.Column(db.String(25))
    password = db.Column(db.String(25))
    email = db.Column(db.String(75))

    def __init__(self,username,password,email):
        self.username = username
        self.password = password
        self.email = email


db.create_all() 


@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/',methods=['POST'])
def homepage_options():
    if request.form['btn'] == 'LogIn':
        return redirect(url_for('login'))
    elif request.form['btn'] == 'SignUp':
        return redirect(url_for('signup'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def check_credentials():
    username = request.form['username']
    password = request.form['password']
    for i in users.query.all():
        if username == i.username:
            if password == i.password:
                session['user'] = username
                session['email'] = str(i.email)
                return redirect(url_for('profile'))
            else:
                return 'Incorrect password!'
    return 'User does not exist!'

@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/profile')
def profile(current_user=username):
    if 'user' in session:
        return render_template('profile_page.html', data=reversed([i for i in posts_.query.filter_by(user=session['user'])]),email_hash = hashlib.md5(session['email'].lower().encode('utf-8')).hexdigest(),articles=str(len([i for i in posts_.query.filter_by(user=session['user'])])),following=str(len([i for i in follows_.query.filter_by(user=session['user'])])),follows = str(len([i for i in follows_.query.filter_by(followed=session['user'])])),user=session['user'])
    else:
        return 'Not logged in!'

@app.route('/profile',methods=['POST'])
def profile_options():
    if request.form['btn'] == 'timeline':
        return redirect(url_for('tl',current_user=username))
    elif request.form['btn'] == 'search':
        return redirect(url_for('search_friend'))
    elif request.form['btn'] == 'log':
        return redirect(url_for('log_new'))
    elif request.form['btn'] == 'delete':
        return redirect(url_for('delete'))
    elif request.form['btn'] == 'followers':
        return redirect(url_for('followers'))
    elif request.form['btn'] == 'following':
        return redirect(url_for('following'))
    elif request.form['btn'] == 'articles':
        return render_template('profile_page.html', data=reversed([i for i in posts_.query.filter_by(user=session['user'])]),email_hash = hashlib.md5(session['email'].lower().encode('utf-8')).hexdigest(),articles=str(len([i for i in posts_.query.filter_by(user=session['user'])])),following=str(len([i for i in follows_.query.filter_by(user=session['user'])])),follows = str(len([i for i in follows_.query.filter_by(followed=session['user'])])),user=session['user'])


@app.route('/followers')
def followers():
    if 'user' in session:
        followers_ = [i.user for i in follows.query.filter_by(followed=session['user'])]
        return f'your follower(s) are {followers_}!'

@app.route('/following')
def following():
    if 'user' in session:
        following_ = [i.user for i in follows.query.filter_by(user=session['user'])]
        return f'you\'re following {following_}!'


@app.route('/timeline')
def tl(current_user=username):
    if 'user' in session:
        follows__ = [i.followed for i in follows_.query.filter_by(user=session['user'])]
        data = [i for i in posts_.query.all() if str(i.user).lower() in follows__]
        return render_template('test.html',data=reversed(data))
    else:
        return 'not logged in!'

@app.route('/timeline',methods=['POST'])
def tl_options():
    if request.form['btn'] == 'log':
        return redirect(url_for('log_new'))
    elif request.form['btn'] == 'search':
        return redirect(url_for('search_friend'))
    elif request.form['btn'] == 'profile':
        return redirect(url_for('profile'))

@app.route('/search')
def search_friend():
    return render_template('testing.html')

@app.route('/log')
def log_new():
    return render_template('button.html')

@app.route('/log',methods=['POST'])
def log():
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        url = request.form['title'].lower()
        review = request.form['review']
        url_ = str(url)
        tree = (lxml.html.parse(urlopen(url_)))
        title =str((tree.find('//title').text.replace('â','\'').replace('\x80\x99','')))
        if 'user' in session:
            new_article = posts_(session['user'],url,title,review)
            db.session.add(new_article)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            return 'not logged in!'
    except ValueError:
        return 'Invalid URL! Make sure that it starts with https://'


@app.route('/search',methods=['POST'])
def add_friend():
    searched = request.form['username']
    exists = False
    for j in users__.query.all():
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
    for i in users__.query.all():
        if i.username == username_attempt:
            return 'Username Taken!'
    new_user = users__(request.form['username'], request.form['password'], request.form['email'])
    db.session.add(new_user)
    db.session.commit()
    session['user'] = username_attempt
    session['email'] = request.form['email']
    return redirect(url_for('profile'))

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/delete',methods=['POST'])
def deletion():
    url = request.form['url']
    if 'user' in session:
        posts_.query.filter_by(user=session['user'],url=url).delete()
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        return 'Not Logged In!'


if __name__ == "__main__":
   app.run(debug=True)
