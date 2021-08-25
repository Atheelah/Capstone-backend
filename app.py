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
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "image TEXT NOT NULL,"
                     "date_listed TEXT NOT NULL)")
    print("books table created successfully.")


init_user_table()  # CALLING THE FUNCTION FOR THE USER TABLE
init_books_table()  # CALLING THE FUNCTION FOR THE BOOKS TABLE
users = fetch_users()  # CALLING  THE FUNCTION TO FETCH THE USERS


def send_email(address):
    sender_password = 'lifechoices1234'
    sender_email = "atheelahlifechoices@gmail.com"
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = sender_email
    app.config['MAIL_PASSWORD'] = sender_password
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    msg = Message('Bookstore registration', sender=sender_email, recipients=[address])
    msg. body = "Welcome to Book Cave." \
                "" \
                "You successfully been registered"
    mail.send(msg)
    return "sent"


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
        email = request.form['email']

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
            send_email(email)

        return response


# THIS IS MY FUNCTION TO ADD AN ITEM
@app.route('/add-book/', methods=["POST"])
@jwt_required()
def add_book():
    response = {}

    if request.method == "POST":
        book_title = request.form['book_title']
        author = request.form['author']
        category = request.form['category']
        price = request.form['price']
        description = request.form['description']
        image = request.form['image']
        date_listed = datetime.datetime.now()

        with sqlite3.connect('bookstore.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books("
                           "book_title,"
                           "author,"
                           "category,"
                           "price,"
                           "description,"
                           "image,"
                           "date_listed) VALUES(?, ?, ?, ?, ?, ?, ?)", (book_title, author, category, price, description,
                                                                        image, date_listed))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "book was added successfully"
        return response


@app.route('/get-books/', methods=["GET"])
def get_books():
    response = {}
    with sqlite3.connect("bookstore.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# THIS IS MY FUNCTION TO GET THE USERS
@app.route('/get-users/', methods=["GET"])
def get_user():
    response = {}
    with sqlite3.connect("bookstore.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


# THIS IS MY FUNCTION TO DELETE A BOOK
@app.route("/delete-book/<int:product_id>/")
@jwt_required()
def delete_book(product_id):
    response = {}
    with sqlite3.connect("bookstore.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "book deleted successfully."
    return jsonify(response)


# THIS IS MY FUNCTION TO EDIT A BOOK
@app.route('/edit-book/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_book(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('bookstore.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("book_title") is not None:
                put_data["book_title"] = incoming_data.get("book_title")
                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET book_title =? WHERE id=?", (put_data["book_title"], product_id))
                    conn.commit()
                    response['message'] = "book title updated successfully"
                    response['status_code'] = 200

            if incoming_data.get("author") is not None:
                put_data['author'] = incoming_data.get('author')
                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET author =? WHERE id=?", (put_data["author"], product_id))
                    conn.commit()
                    response["author"] = "Author updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')
                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET category =? WHERE id=?", (put_data["category"], product_id))
                    conn.commit()
                    response["category"] = "category updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')
                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()
                    response["price"] = "price updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET description =? WHERE id=?", (put_data["description"], product_id))
                    conn.commit()
                    response["description"] = "description updated successfully"
                    response["status_code"] = 200

            if incoming_data.get("image") is not None:
                put_data['image'] = incoming_data.get('image')
                with sqlite3.connect('bookstore.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE books SET image =? WHERE id=?",
                                   (put_data["image"], product_id))
                    conn.commit()
                    response["image"] = "image updated successfully"
                    response["status_code"] = 200
    return response


# THIS RUNS THE APPLICATION
if __name__ == '__main__':
    app.run()
    app.debug = True