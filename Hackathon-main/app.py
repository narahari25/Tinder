from flask import Flask, render_template, request,  redirect, url_for, jsonify
import sqlite3
import base64
app = Flask(__name__)


def create_table():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (name TEXT,
                 age INTEGER,
                 bio TEXT,
                 username TEXT,
                 password TEXT,
                 photo BLOB)''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    age = request.form['age']
    bio = request.form['bio']
    photo = request.files['photo'].read()

    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name, age, bio, photo) VALUES (?, ?, ?, ?)',
              (name, age, bio, photo))
    conn.commit()
    conn.close()

    return 'Data submitted successfully!'


@app.route('/view')
def view():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    users = [dict(zip(('id', 'name', 'age', 'bio', 'photo'), row))
             for row in rows]
    conn.close()
    return render_template('view.html', users=users)


@app.route('/view2')
def view2():
    user_dict= []
    conn = sqlite3.connect('user_data.db')
    name = "kr$"  # replace with the name of the currently logged-in user
    c = conn.cursor()
    # c.execute('SELECT * FROM details WHERE name=? ', (name))
    # name = c.fetchone()
    c.execute('SELECT * FROM users WHERE name <> ? AND name NOT IN (SELECT DISTINCT name FROM swipes WHERE user = ?)', (name, name))
    rows = c.fetchall()
    if rows:
            for row in rows:
                user_dict.append(
                    {
                    'id': row[0],
                    'name': row[1],
                    'age': row[2],
                    'bio': row[3],
                    'photo': base64.b64encode(row[4]).decode('utf-8')
                    }
                
                )
            
    conn.close()
    return render_template('view2.html', users= user_dict)


@app.route('/match')
def matched():
    user_dict=[]
    conn = sqlite3.connect('user_data.db')

    name = "kr$"  # replace with the name of the currently logged-in user
    c = conn.cursor()
    # c.execute('SELECT * FROM details WHERE name=? ', (name))
    # name = c.fetchone()
    c.execute('SELECT u.* FROM users u INNER JOIN matched m ON u.name = m.user OR u.name = m.name WHERE m.name = ? OR m.user = ? ', (name, name))

    rows = c.fetchall()
    
    if rows:
            for row in rows:
                user_dict.append(
                    {
                    'id': row[0],
                    'name': row[1],
                    'age': row[2],
                    'bio': row[3],
                    'photo': base64.b64encode(row[4]).decode('utf-8')
                    }
                
                )
            
    conn.close()
    return render_template('match.html', users= user_dict)

# app = Flask(__name__)v
def get_user(id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (id,))
    user = c.fetchone()
    conn.close()
    return user


@app.route('/users/<int:id>')
def user_profile(id):
    user = get_user(id)
    if user:
        return render_template('profile.html', user=user)
    else:
        return 'User not found'


def create_table2():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS swipes
                (id INTEGER PRIMARY KEY,
                 name TEXT,
                 swipe_direction TEXT,
              user TEXT)''')
    conn.commit()
    conn.close()


def create_table3():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS matched
                (
                 name TEXT,
                 user TEXT)''')
    conn.commit()
    conn.close()


@app.route('/swipe_left', methods=['POST'])
def swipe_left():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    name1 = request.args.get('name')
    name2 = request.args.get('user')
    c.execute('INSERT INTO swipes (name, user, swipe_direction) VALUES (?, ?, ?)',
              (name1, name2, "left"))
    conn.commit()
    conn.close
    return "swiped left"


@app.route('/swipe_right', methods=['POST'])
def swipe_right():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()

    name1 = request.args.get('name')
    name2 = request.args.get('user')
    # conn.commit()
    # check for match
    c.execute('SELECT * FROM swipes WHERE name = ? AND user = ? AND swipe_direction = ?',
              (name2, name1, "right"))
    match = c.fetchone()
    if match:
        # delete matching swipes from table
        c.execute('INSERT INTO matched (name, user) VALUES (?, ?)',
                  (name1, name2))

        c.execute('DELETE FROM swipes WHERE name = ? AND user = ? AND swipe_direction = ?',
                  (name2, name1, "right"))
        c.execute('DELETE FROM swipes WHERE name = ? AND user = ? AND swipe_direction = ?',
                  (name1, name2, "right"))
        conn.commit()
        conn.close()

        return "Match found!"
    else:
        c.execute('INSERT INTO swipes (name, user, swipe_direction) VALUES (?, ?, ?)',
                  (name1, name2, "right"))
        conn.commit()
        conn.close()
        return "swipe right"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute('SELECT * FROM details WHERE email=? AND password=?',
                  (email, password))
        data = c.fetchone()

        if data is not None:
            return redirect(url_for('get_user', name=email))

        conn.close()
        return redirect(url_for('register'))

    return render_template('login.html')


@app.route('/sign', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute('INSERT INTO details (name, email, password) VALUES (?, ?, ?)',
                  (name, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('get_user', name=email))

    return render_template('signup.html')


@app.route('/user/<email>')
def user_details(email):
    if request.method == 'POST':
        return redirect(url_for(view2))
    # Read user data from the "details" table and display on user details page

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute('SELECT * FROM details WHERE email=?', (email,))
    data = c.fetchone()

    if data is not None:
        return f"Name: {data[0]}<br>Email: {data[1]}<br>Password: {data[2]}"

    conn.close()
    return "User not found"


if __name__ == '__main__':
    create_table()
    create_table2()
    create_table3()
    app.run(port=3004, debug=True)
