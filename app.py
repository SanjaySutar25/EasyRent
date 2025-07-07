from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        license = request.form['license']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()

        if user:
            return redirect(url_for('browse'))
        else:
            return render_template('login.html', error="Invalid login credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        license = request.form['license']

        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password, license) VALUES (?, ?, ?)', 
                     (email, password, license))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/browse')
def browse():
    conn = get_db_connection()
    vehicles = conn.execute('SELECT * FROM vehicles WHERE availability = 1').fetchall()
    conn.close()
    return render_template('browse.html', vehicles=vehicles)

@app.route('/book/<int:vehicle_id>', methods=['GET', 'POST'])
def book(vehicle_id):
    conn = get_db_connection()
    vehicle = conn.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,)).fetchone()

    if request.method == 'POST':
        duration = int(request.form['duration'])
        total_fare = duration * vehicle['fare']
        conn.execute('UPDATE vehicles SET availability = 0 WHERE id = ?', (vehicle_id,))
        conn.commit()
        conn.close()
        return render_template('confirmation.html', vehicle=vehicle, total_fare=total_fare)
    
    conn.close()
    return render_template('booking.html', vehicle=vehicle)

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    app.run(debug=True)
