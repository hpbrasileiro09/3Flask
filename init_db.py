import sqlite3

connection = sqlite3.connect('2Flask.db')

arquivo = "Sql/schema.sql"

arquivo = "Sql/20211224_tickets.sql"

with open(arquivo) as f:
    connection.executescript(f.read())

# cur = connection.cursor()

# cur.execute("INSERT INTO tickets (number, subject, description, notes) VALUES (?, ?, ?, ?)", ('337520', 'Orçamento1', '', ''))
# cur.execute("INSERT INTO tickets (number, subject, description, notes) VALUES (?, ?, ?, ?)", ('337531', 'Orçamento2', '', ''))

"""
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Andre Bis2bis', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Christian Lima', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Fabio Eidi', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Gabriel', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Gilberto Silva', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Leonardo Morita', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Rodrigo Salinet', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Selton Miguel', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Wellington Borba Cordeiro', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'William Gerenutti', 3 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'João Cotrim', 1 )")
cur.execute("INSERT INTO resources ( name, role ) VALUES ( 'Hernando Brasileiro', 2 )")
"""

connection.commit()
connection.close()