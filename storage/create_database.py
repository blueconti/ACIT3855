import mysql.connector

db_conn = mysql.connector.connect(host="lab6-service.canadacentral.cloudapp.azure.com", user="user", password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
        CREATE TABLE book_campsites
        (id INT NOT NULL AUTO_INCREMENT,
        book_id VARCHAR(250) NOT NULL,
        client_id VARCHAR(250) NOT NULL,
        campsite VARCHAR(250) NOT NULL,
        number_of_guests INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        CONSTRAINT book_campsites_pk PRIMARY KEY (id) )
        ''')
db_cursor.execute('''
        CREATE TABLE payments
        (id INT NOT NULL AUTO_INCREMENT,
        payment_id VARCHAR(250) NOT NULL,
        client_id VARCHAR(250) NOT NULL,
        campsite VARCHAR(250) NOT NULL,
        number_of_guests INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        CONSTRAINT payments_pk PRIMARY KEY (id) )
        ''')
db_conn.commit()
db_conn.close()