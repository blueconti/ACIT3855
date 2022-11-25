import sqlite3
db_conn = sqlite3.connect('health.sqlite')
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE health
''')
db_conn.commit()
db_conn.close()