import sqlite3
db_conn = sqlite3.connect('stats.sqlite')
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE stats
''')
db_conn.commit()
db_conn.close()