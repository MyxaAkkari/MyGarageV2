import sqlite3
from flask import Flask, render_template, redirect, url_for, request

# Connect to SQLite database
con = sqlite3.connect('garage.db', check_same_thread=False)
cur = con.cursor()

# Create Flask app
app = Flask(__name__)

try:
    # Create 'Cars' and 'FinishedCars' tables if they don't exist
    cur.execute("CREATE TABLE IF NOT EXISTS Cars (OwnerName, OwnerNumber TEXT, Brand, Model, ModelYear, Color)")
    cur.execute("CREATE TABLE IF NOT EXISTS FinishedCars (OwnerName, OwnerNumber TEXT, Brand, Model, ModelYear, Color)")
    con.commit()
except Exception as e:
    print(f"Error creating tables: {e}")

# Define route for the home page
@app.route('/')
def home():
    # Retrieve all cars from the 'Cars' table
    cur.execute("SELECT rowid,* FROM Cars")
    cars = cur.fetchall()
    # Render the home page template with the list of cars
    return render_template('index.html', cars=cars)

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
    # Retrieve all fixed cars from the 'FinishedCars' table
    cur.execute("SELECT rowid,* FROM FinishedCars")
    cars = cur.fetchall()
    # Render the fixed cars page template with the list of fixed cars
    return render_template('fixed.html', cars=cars)

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

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=8000)
