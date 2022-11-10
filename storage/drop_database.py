import mysql.connector
db_conn = mysql.connector.connect(host="lab6-service.canadacentral.cloudapp.azure.com", user="user",
password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE book_campsites, payments
''')
db_conn.commit()
db_conn.close()