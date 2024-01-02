import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

# Connect to SQLite database
con = sqlite3.connect('garage.db', check_same_thread=False)
cur = con.cursor()

# Create Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Create 'Cars' and 'FinishedCars' tables if they don't exist
cur.execute("CREATE TABLE IF NOT EXISTS Cars (OwnerName, OwnerNumber TEXT, Brand, Model, ModelYear, Color)")
cur.execute("CREATE TABLE IF NOT EXISTS FinishedCars (OwnerName, OwnerNumber TEXT, Brand, Model, ModelYear, Color)")
# Create 'Users' table for authentication
cur.execute("CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT, profile_photo TEXT)")
con.commit()

UPLOAD_FOLDER = 'static/uploads'  # Change this to your desired upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Add more if needed

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Define route for the home page
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur.execute("SELECT username, profile_photo FROM Users WHERE id=?", (session['user_id'],))
    user_data = cur.fetchone()

    if user_data:
        user_name, user_profile_photo = user_data
        if user_profile_photo is None:
            user_profile_photo = 'default.png'  # Set to your default photo filename
        cur.execute("SELECT rowid,* FROM Cars")
        cars = cur.fetchall()

        return render_template('index.html', cars=cars, user_name=user_name, user_profile_photo=user_profile_photo)
    else:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))

# Define route for adding a new car
@app.route('/add', methods=['POST'])
def add():
    # Extract car details from the submitted form
    owner_name = request.form['ownerName']
    phone_number = str(request.form['phoneNumber'])
    brand = request.form['brand']
    model = request.form['model']
    model_year = request.form['year']
    color = request.form['clr']
    # Insert the new car into the 'Cars' table
    cur.execute("INSERT INTO Cars (OwnerName, OwnerNumber, Brand, Model, ModelYear, Color) VALUES (?, ?, ?, ?, ?, ?)",
                (owner_name, phone_number, brand, model, model_year, color))
    con.commit()
    # Redirect to the home page after adding the car
    return redirect(url_for('home'))

# Define route for deleting a car
@app.route('/delete/<int:car_id>', methods=['POST'])
def delete(car_id):
    # Fetch the car information from the 'Cars' table based on its rowid
    cur.execute("SELECT * FROM Cars WHERE rowid=?", (car_id,))
    car_data = cur.fetchone()

    if car_data:
        # Insert the car into the 'FinishedCars' table
        cur.execute("INSERT INTO FinishedCars (OwnerName, OwnerNumber, Brand, Model, ModelYear, Color) VALUES (?, ?, ?, ?, ?, ?)",
                    (car_data[0], car_data[1], car_data[2], car_data[3], car_data[4], car_data[5]))
        con.commit()

        # Delete the car from the 'Cars' table
        cur.execute("DELETE FROM Cars WHERE rowid=?", (car_id,))
        con.commit()

    # Redirect to the home page after deleting the car
    return redirect('/')

# Define route for displaying fixed cars
@app.route('/fixed')
def fixed():
    # Check if user is not logged in
    if 'user_id' not in session:
        # Redirect to the login page
        return redirect(url_for('login'))

    # Retrieve the username and profile photo from the 'Users' table
    cur.execute("SELECT username, profile_photo FROM Users WHERE id=?", (session['user_id'],))
    user_data = cur.fetchone()

    if user_data:
        user_name, user_profile_photo = user_data

        if user_profile_photo is None:
            user_profile_photo = 'default.png'
        # Retrieve all fixed cars from the 'FinishedCars' table
        cur.execute("SELECT rowid,* FROM FinishedCars")
        cars = cur.fetchall()

        # Render the fixed cars page template with the list of fixed cars, user's name, and user's profile photo
        return render_template('fixed.html', cars=cars, user_name=user_name, user_profile_photo=user_profile_photo)
    else:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))


# Define route for editing a car
@app.route('/edit/<int:car_id>', methods=['POST'])
def edit(car_id):
    # Update the car information in the 'Cars' table based on its rowid
    owner_name = request.form['ownerName']
    phone_number = str(request.form['phoneNumber'])
    brand = request.form['brand']
    model = request.form['model']
    model_year = request.form['year']
    color = request.form['clr']

    cur.execute("UPDATE Cars SET OwnerName=?, OwnerNumber=?, Brand=?, Model=?, ModelYear=?, Color=? WHERE rowid=?",
                (owner_name, phone_number, brand, model, model_year, color, car_id))
    con.commit()

    # Redirect to the home page after editing the car
    return redirect('/')

# Define route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Save the uploaded file
        profile_photo = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo = filename

        try:
            # Insert the new user into the 'Users' table
            cur.execute("INSERT INTO Users (username, email, password, profile_photo) VALUES (?, ?, ?, ?)",
                        (username, email, hashed_password, profile_photo))
            con.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose a different username or email.', 'danger')

    return render_template('register.html')


# Define route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_identifier = request.form['identifier']  # This can be either username or email
        password = request.form['password']

        # Retrieve the user from the 'Users' table based on the username or email
        cur.execute("SELECT * FROM Users WHERE username=? OR email=?", (input_identifier, input_identifier))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[3], password):
            # User authentication successful
            session['user_id'] = user[0]
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username, email, or password. Please try again.', 'danger')

    return render_template('login.html')

# Define route for password reset
@app.route('/passreset', methods=['GET', 'POST'])
def passreset():
    if request.method == 'POST':
        # Get the user's email from the form
        email = request.form['email']

        # TODO: Add logic to send an email to the user's email address with a password reset link
        # This typically involves generating a unique token, creating a password reset link,
        # and sending it to the user's email.

        # For now, just display a message indicating that the email has been sent
        email_sent_message = f"A password reset link has been sent to {email}. Check your email."
        return render_template('passreset.html', email_sent=email_sent_message)
    email_sent_message = "Type your Email address, We will send you a link to reset your password."
    return render_template('passreset.html', email_sent=email_sent_message)



# Define route for user logout
@app.route('/logout')
def logout():

    session.clear()  # Clear the entire session
    flash('You have been logged out.', 'info')

    # Clear browser cache
    response = redirect(url_for('home'))  
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'


    return response



# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8000)
