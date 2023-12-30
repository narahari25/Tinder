import sqlite3
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute('''SELECT * FROM users''')
data=c.fetchall()
print(data)
conn.commit()
conn.close()