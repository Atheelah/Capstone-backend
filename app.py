import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('bookstore.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


def init_user_table():
    conn = sqlite3.connect('bookstore.db')
    print("Opened database successfully")
    # THE APPROPRIATE FIELDS ARE ADDED HERE IN THE TABLE
    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_books_table():
    with sqlite3.connect('bookstore.db') as conn:
        # THE APPROPRIATE FIELDS ARE ADDED HERE IN THE TABLE
        conn.execute("CREATE TABLE IF NOT EXISTS books(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "book_title TEXT NOT NULL,"
                     "author TEXT NOT NULL,"
                     "category TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "date_listed TEXT NOT NULL)")
    print("books table created successfully.")


init_user_table()  # CALLING THE FUNCTION FOR THE USER TABLE
init_books_table()  # CALLING THE FUNCTION FOR THE PRODUCT TABLE
users = fetch_users()  # CALLING  THE FUNCTION TO FETCH THE USERS

# THIS DISPLAYS THE USERS AND THE ID OF THE USERNAME
username_table = {u.username: u for u in users}
userid_table = {u.id: u for
                u in users}


# CREATING A FUNCTION TO CHECK THE USERNAME AND PASSWORD. TO CHECK IF IT CORRESPONDS
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# THIS CHECKS THE IDENTITY FIT THE ABOVE
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=4000)
CORS(app)

jwt = JWT(app, authenticate, identity)


# THIS PROTECTS THE SIGHT AND CHECKS THE IDENTITY
@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# THIS IS MY FUNCTION  TO REGISTER A USER.
@app.route('/registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("bookstore.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
            return response