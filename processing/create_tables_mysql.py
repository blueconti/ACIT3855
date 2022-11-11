import sqlite3
conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()
c.execute('''
        CREATE TABLE stats
        (id INTEGER PRIMARY KEY ASC,
        num_book INTEGER NOT NULL,
        num_payment INTEGER NOT NULL,
        sum_book_total INTEGER,
        avg_book_total INTEGER,
        last_updated VARCHAR(100) NOT NULL)
        ''')
conn.commit()
conn.close()