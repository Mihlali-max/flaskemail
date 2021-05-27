import sqlite3
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask import render_template
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'flavoursomefreshfood76@gmail.com'
app.config['MAIL_PASSWORD'] = 'Sakheflavoursome'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# Defining the function that opens sqlite database and creates table
def create_users_table():
    connect = sqlite3.connect('food.db')
    print("Databases has opened")

    connect.execute(
        'CREATE TABLE IF NOT EXISTS users (user id INTEGER, fullname TEXT, email_address TEXT, phone INTEGER, Adults INTEGER, Children INTEGER,  Checkin TEXT ,Checkout TEXT, DISH TEXT, ANYTHINGELSE TEXT )')
    print("Users Table was created successfully")
    # print(connect.execute("PRAGMA table_info('users')"))
    #
    # print("Users Table was created successfully")
    # print(connect.execute("PRAGMA foreign_keys=off"))
    # print(connect.execute("BEGIN TRANSACTION"))
    # print(connect.execute("ALTER TABLE users RENAME TO back_up_users_2"))
    # print(connect.execute("PRAGMA table_info('back_up_users')").fetchall())
    # print(connect.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, email_address TEXT, phone INTEGER, Adults INTEGER, Children INTEGER,  Checkin TEXT ,Checkout TEXT, DISH TEXT, ANYTHINGELSE TEXT)"))
    # print(connect.execute('INSERT INTO users SELECT * FROM back_up_users'))
    # print(connect.execute("PRAGMA foreign_keys=on"))
    # print(connect.execute("PRAGMA table_info('users')").fetchall())
    print(connect.commit())

    connect.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


create_users_table()


# Route for opening the registration form


# Fetching form info and adding users to database
@app.route('/')
@app.route('/add/', methods=['POST', 'GET'])
def add_users():
    if request.method == 'POST':
        try:

            fullname = request.form['customer_name']
            email_address = request.form['customers_email']
            phone = request.form['visitor_phone']
            Adults = request.form['total_adults']
            Children = request.form['total_children']
            Checkin = request.form['checkin']
            Checkout = request.form['checkout']
            DISH = request.form['dish']
            ANYTHINGELSE = request.form['text']

            # username = request.form['username']
            # password = request.form['password']
            # confirm_password = request.form['confirm']
            # email = request.form['email']

            if fullname == fullname:
                with sqlite3.connect('food.db') as con:
                    cursor = con.cursor()
                    cursor.execute(
                        "INSERT INTO users (fullname, email_address, phone, Adults, Children ,Checkin ,Checkout , DISH ,ANYTHINGELSE) VALUES (?, ?, ?, ?, ?,?,?,?,?)",
                        (fullname, email_address, phone, Adults, Children, Checkin, Checkout, DISH, ANYTHINGELSE))
                    con.commit()
                    msg = fullname + " you have been successfully booked please check your email."
                    row_id = cursor.lastrowid
                    cancelattion_link = "{link}".format(
                        link="http://127.0.0.1:5000/delete/" + str(row_id) + "/")
                    send_mail(fullname, email_address, phone, Adults, Children, Checkin, Checkout, DISH, cancelattion_link)

                    return render_template("return.html")
        except Exception as e:
            # con.rollback()
            msg = "Error occured in insert " + str(e)
        # finally:
        #
        #     # con.close()
        # return jsonify(msg=msg)

        finally:

            con.close()
        return jsonify(msg=msg)
    return render_template('return.html')

@app.route('/show-bookers/', methods=['GET'])
def show_bookers():
    users = []
    try:
        with sqlite3.connect('food.db') as connect:
            connect.row_factory = dict_factory
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
    except Exception as e:
        connect.rollback()
        print("There was an error fetching results from the database: " + str(e))
    finally:
        connect.close()
        return jsonify(users)


@app.route
# message object mapped to a particular URL ‘/’
@app.route('/mail/')
def index():
    msg = Message(
        "Hello Jason",
        sender='flavoursomefreshfood76@gmail.com',
        recipients=['flavoursomefreshfood76@gmail.com']
    )
    msg.body = 'Hello Flask message sent from Flask-Mail'
    mail.send(msg)
    return 'Sent'


def send_mail(fullname, email_address, phone, Adults, Children, Checkin, Checkout, DISH, cancellation_link):
    msg = Message(
        "Confirmation of booking",
        sender=email_address,
        recipients=[email_address]
    )
    msg.body = """

Hi {fullname},
We are glad to hear that you are booking a table at Flavoursome for {no_adults} adults and {children} children 
on {checkin} :{checkout} it is has been confirmed. For any changes please contact our customer service landline at 06670742917 .

                                           Your Reservation:
                                           Name: {fullname}
                                           Phone Number: {phone}
                                           Email: {email}
                                           Booking Date: {checkin}
                                           Meal :{food}

We look forward to serving you, please don’t hesitate to contact us for any questions or
concerns. If you want to cancel your reservation you can click this link {link} or call our reservation team at +276670742917 
or email us back.

You can put any extra information such as events, special offers, and deals as
well as linking to your social media on our website.


                                           Terms and Conditions 
                            
We are putting the following measures in place to ensure the safety of our staff and customers.
You will be required to wear a face covering when not eating or drinking at your table.
Your table may be released if you are running more than 20 minutes late.
Please do not enter the site if you or your guests are experiencing any COVID-19 symptoms.

All the best,
Sakhe Silwana
Customer Service
Manager of Flavoursomefreshfood

    
    """.format(fullname=fullname, phone=phone, email=email_address, no_adults=Adults, children=Children, checkin=Checkin,
               checkout=Checkout, food=DISH, link=cancellation_link)

    with app.open_resource("/home/mihlali/Downloads/lauriam.jpg") as fp:
        msg.attach("lauriam.jpg", "image/jpg", fp.read())

    with app.open_resource("/home/mihlali/Downloads/Flavoursome.jpg") as fp:
        msg.attach("Flavoursome.jpg", "image/jpg", fp.read())

    mail.send(msg)


@app.route('/delete/<int:user_id>/', methods=["GET"])
def delete_user(user_id):
    msg = None
    try:
        with sqlite3.connect('food.db') as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE id=" + str(user_id))
            con.commit()
            msg = "Your reservation has been cancelled."
    except Exception as e:
        con.rollback()
        msg = "Error occurred when deleting the user in the database: " + str(e)
    finally:
        con.close()
        return render_template('delete.html')


if __name__ == '__main__':
    app.run(debug=True)
