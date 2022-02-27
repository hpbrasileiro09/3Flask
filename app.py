import os
import sqlite3
import json

from datetime import datetime, timedelta
from datetime import date

from random import choice
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify, after_this_request
from werkzeug.exceptions import abort

app = Flask(__name__)

app.secret_key = "manbearpig_MUDMAN888"

def get_db_connection():
    conn = sqlite3.connect('2Flask.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tickets/json')
def tickets_json():
    kind = request.args.get('k', default = 0, type = int)
    _tmp = get_status_sql()
    _sql = f"SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo, {_tmp} FROM tickets ORDER BY id"
    if kind != 0:
        _sql = f"SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo, {_tmp} FROM tickets WHERE status = {kind} ORDER BY id"
    conn = get_db_connection()
    regs = conn.execute(_sql).fetchall()
    conn.close()
    #results = [list(row) for row in tickets]
    #result_dict = {'tickets': results}
    #return jsonify(result_dict)
    data = []
    for row in regs:
        data.append({
            "id": row['id'],
            "number": row['number'],
            "dt_ticket": row['dt_ticket'],
            "subject": row['subject'],
            "client": row['client'],
            "description": row['description'],
            "link": row['link'],
            "notes": row['notes'],
            "actions": row['actions'],
            "resume": row['resume'],
            "manager": row['manager'],
            "hours": row['hours'],
            "published": row['published'],
            "status": row['status'],
            "status_lbl": row['status_lbl'],
            "complexity": row['complexity'],
            "production_time": row['production_time'],
            "completion_deadline": row['completion_deadline'],
            "dt_solution": row['dt_solution'],
            "created_at": row['created_at']
        })    
    return jsonify(data)

@app.route('/resources/json')
def resources_json():
    roles = [ 'Guest', 'Scrum Master', 'Product Owner', 'Dev Backend', 'Dev Frontend' ]    
    conn = get_db_connection()
    regs = conn.execute('SELECT * FROM resources').fetchall()
    conn.close()
    data = []    
    for row in regs:
        data.append({
            "id": row['id'],
            "name": row['name'],
            "role": row['role'],
            "role_desc": roles[row['role']],
            "published": row['published'],
            "created_at": row['created_at']
        })    
    return jsonify(data)

def f_create_from_M1(number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM moviedesk1A WHERE number = ?", (number.strip(), )).fetchone()
    if ticket is None:
        abort(404)
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )")
    conn.execute(_sql, 
        (number, ticket['dt_ticket'], ticket['subject'], ticket['client'], ticket['link'], 
        ticket['notes'], ticket['actions'], ticket['resume'], ticket['published'], 
        ticket['status'], ticket['complexity'], ticket['production_time'], ticket['completion_deadline'], 
        ticket['manager'], ticket['hours'], ticket['dt_solution'] ))
    conn.commit()
    conn.close()
    return ticket    

def get_ticket(ticket_id):
    conn = get_db_connection()
    ticket = conn.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    conn.close()
    if ticket is None:
        abort(404)
    return ticket

def get_ticketN(ticket_number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE number = ?", (ticket_number,)).fetchone()
    conn.close()
    if ticket is None:
        abort(404)
    return ticket

def get_ticket2N(ticket_number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM moviedesk2A WHERE number = ?", (ticket_number,)).fetchone()
    conn.close()
    if ticket is None:
        abort(404)
    return ticket

def get_ticket4N(ticket_number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM moviedesk2A WHERE number = ?", (ticket_number,)).fetchone()
    conn.close()
    if ticket is None:
        abort(404)
    return ticket

def get_number(number):
    conn = get_db_connection()
    ticket = conn.execute('SELECT * FROM tickets WHERE number = ?', (number,)).fetchone()
    conn.close()
    if ticket is None:
        return 0
    return 1

@app.route('/tickets/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    ticket = get_ticket(id)

    if request.method == 'POST':

        salvar = True

        save_continue = request.form.get('save_continue')

        if save_continue:
            salvar = False

        if salvar == True:
            sedit(
                id,
                request.form['number'],
                request.form['dt_ticket'],
                request.form['subject'],
                request.form['client'],
                request.form['link'],
                request.form['notes'],
                request.form['actions'],
                request.form['resume'],
                request.form['published'],
                request.form['status'],
                request.form['complexity'],
                request.form['production_time'],
                request.form['completion_deadline'],
                request.form['dt_solution'],
                request.form['manager'],
                request.form['effort'],
                request.form['jira'],
                request.form['hours'])
            return redirect(url_for('tickets'))
        else:
            sedit(
                id,
                request.form['number'],
                request.form['dt_ticket'],
                request.form['subject'],
                request.form['client'],
                request.form['link'],
                request.form['notes'],
                request.form['actions'],
                request.form['resume'],
                request.form['published'],
                request.form['status'],
                request.form['complexity'],
                request.form['production_time'],
                request.form['completion_deadline'],
                request.form['dt_solution'],
                request.form['manager'],
                request.form['effort'],
                request.form['jira'],
                request.form['hours'])
            ticket = get_ticket(id)
            return render_template('edit.html', ticket=ticket, published=get_published(), status=get_status(), complexities=get_complexity(), effort=get_effort())

    return render_template('edit.html', ticket=ticket, published=get_published(), status=get_status(), complexities=get_complexity(), effort=get_effort())

@app.route('/busca', methods=('GET', 'POST'))
def busca():
    if request.method == 'POST':
        try:
            number = request.form['number']
            ticket = get_ticketN(number.strip())
            return redirect(url_for('edit', id=ticket['id']))
        except:
            try:
                f_create_from_M1(number.strip())
                ticket = get_ticketN(number.strip())
                return redirect(url_for('edit', id=ticket['id']))
            except:
                flash('Number \'{}\' not found!'.format(number), 'danger')
                return redirect(url_for('tickets'))    

@app.route('/tickets/<string:number>/newm1OLD', methods=('GET', 'POST'))
def create_from_M1OLD(number):
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) "
    "SELECT "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution "
    "FROM moviedesk1A WHERE number = ?")
    conn = get_db_connection()
    conn.execute(_sql, (number,))
    conn.commit()
    conn.close()
    ticket = get_ticketN(number.strip())
    return redirect(url_for('edit', id=ticket['id']))

@app.route('/tickets/<string:number>/newm1', methods=('GET', 'POST'))
def create_from_M1(number):
    try:
        f_create_from_M1(number.strip())
        ticket = get_ticketN(number.strip())
        return redirect(url_for('edit', id=ticket['id']))
    except:
        flash('Number \'{}\' not found!'.format(number), 'danger')
        return redirect(url_for('movie2'))    

@app.route('/tickets/<string:number>/newm2OLD', methods=('GET', 'POST'))
def create_from_M2OLD(number):
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) "
    "SELECT "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution "
    "FROM moviedesk2A WHERE number = ?")
    conn = get_db_connection()
    conn.execute(_sql, number,)
    conn.commit()
    conn.close()
    ticket = get_ticketN(number.strip())
    return redirect(url_for('edit', id=ticket['id']))

@app.route('/tickets/<string:number>/newm2', methods=('GET', 'POST'))
def create_from_M2(number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM moviedesk2A WHERE number = ?", (number.strip(), )).fetchone()
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )")
    conn.execute(_sql, 
        (number, ticket['dt_ticket'], ticket['subject'], ticket['client'], ticket['link'], 
        ticket['notes'], ticket['actions'], ticket['resume'], ticket['published'], 
        ticket['status'], ticket['complexity'], ticket['production_time'], ticket['completion_deadline'], 
        ticket['manager'], ticket['hours'], ticket['dt_solution'] ))
    conn.commit()
    conn.close()
    ticket = get_ticketN(number.strip())
    return redirect(url_for('edit', id=ticket['id']))

@app.route('/tickets/<string:number>/newm4OLD', methods=('GET', 'POST'))
def create_from_M4OLD(number):
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) "
    "SELECT "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution "
    "FROM moviedesk4A WHERE number = ?")
    conn = get_db_connection()
    conn.execute(_sql, (number,))
    conn.commit()
    conn.close()
    ticket = get_ticketN(number.strip())
    return redirect(url_for('edit', id=ticket['id']))

@app.route('/tickets/<string:number>/newm4', methods=('GET', 'POST'))
def create_from_M4(number):
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM moviedesk4A WHERE number = ?", (number.strip(), )).fetchone()
    _sql = ("INSERT INTO tickets ( "
    "number, dt_ticket, subject, client, link, "
    "notes, actions, resume, published, "
    "status, complexity, production_time, completion_deadline, "
    "manager, hours, dt_solution ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )")
    conn.execute(_sql, 
        (number, ticket['dt_ticket'], ticket['subject'], ticket['client'], ticket['link'], 
        ticket['notes'], ticket['actions'], ticket['resume'], ticket['published'], 
        ticket['status'], ticket['complexity'], ticket['production_time'], ticket['completion_deadline'], 
        ticket['manager'], ticket['hours'], ticket['dt_solution'] ))
    conn.commit()
    conn.close()
    ticket = get_ticketN(number.strip())
    return redirect(url_for('edit', id=ticket['id']))

@app.route('/tickets/<string:number>/nedit', methods=('GET', 'POST'))
def nedit(number):

    ticket = get_ticketN(number)

    id = ticket['id']

    if request.method == 'POST':

        salvar = True

        save_continue = request.form.get('save_continue')

        if save_continue:
            salvar = False

        if salvar == True:
            sedit(
                id,
                request.form['number'],
                request.form['dt_ticket'],
                request.form['subject'],
                request.form['client'],
                request.form['link'],
                request.form['notes'],
                request.form['actions'],
                request.form['resume'],
                request.form['published'],
                request.form['status'],
                request.form['complexity'],
                request.form['production_time'],
                request.form['completion_deadline'],
                request.form['dt_solution'],
                request.form['manager'],
                request.form['effort'],
                request.form['jira'],
                request.form['hours'])
            return redirect(url_for('tickets'))
        else:
            sedit(
                id,
                request.form['number'],
                request.form['dt_ticket'],
                request.form['subject'],
                request.form['client'],
                request.form['link'],
                request.form['notes'],
                request.form['actions'],
                request.form['resume'],
                request.form['published'],
                request.form['status'],
                request.form['complexity'],
                request.form['production_time'],
                request.form['completion_deadline'],
                request.form['dt_solution'],
                request.form['manager'],
                request.form['effort'],
                request.form['jira'],
                request.form['hours'])
            ticket = get_ticket(id)
            return render_template('edit.html', ticket=ticket, published=get_published(), status=get_status(), complexities=get_complexity(), effort=get_effort())

    return render_template('edit.html', ticket=ticket, published=get_published(), status=get_status(), complexities=get_complexity(), effort=get_effort())

def sedit(
    id,
    number,
    dt_ticket,
    subject,
    client,
    link,
    notes,
    actions,
    resume,
    published,
    status,
    complexity,
    production_time,
    completion_deadline,
    dt_solution,
    manager,
    effort,
    jira,
    hours
    ):

    # production_time = 0
    # completion_deadline = 0
    if float(complexity) != 0:
        complexities = get_complexity()
        for x in complexities:
            if float(complexity) == float(x['complexity']):
                #if int(production_time) == 0:
                production_time = x['hours']
                #if int(completion_deadline) == 0:
                completion_deadline = x['days']
                break

    _sql = ("UPDATE tickets SET "
    "number = ?, "
    "dt_ticket = ?, "
    "subject = ?, "
    "client = ?, "
    "link = ?, "
    "notes = ?, "
    "actions = ?, "
    "resume = ?, "
    "published = ?, "
    "status = ?, "
    "complexity = ?, "
    "production_time = ?, "
    "completion_deadline = ?, "
    "manager = ?, "
    "effort = ?, "
    "jira = ?, "
    "hours = ?, "
    "dt_solution = ? "
    "WHERE id = ?")

    if not number:
        flash('Number is required!', 'danger')
    else:
        conn = get_db_connection()
        conn.execute(_sql,
                    (number, dt_ticket, subject, client, link,
                    notes, actions, resume, published, 
                    status, complexity, production_time, completion_deadline, 
                    manager, effort, jira, hours, dt_solution, id))
        conn.commit()
        conn.close()
        upd_movie2(number, effort, jira)
        upd_movie4(number, effort, jira)
        flash('Ticket \'{}\' updated!'.format(number), 'success')

def upd_ticket(id, effort, jira):
    _sql = "UPDATE tickets SET effort = ?, jira = ? WHERE id = ?"
    conn = get_db_connection()
    conn.execute(_sql, (effort, jira, id))
    conn.commit()
    conn.close()

def upd_movie2(number, effort, jira):
    _sql = "UPDATE moviedesk2A SET effort = ?, jira = ? WHERE number = ?"
    conn = get_db_connection()
    conn.execute(_sql, (effort, jira, number))
    conn.commit()
    conn.close()

def upd_movie4(number, effort, jira):
    _sql = "UPDATE moviedesk4A SET effort = ?, jira = ? WHERE number = ?"
    conn = get_db_connection()
    conn.execute(_sql, (effort, jira, number))
    conn.commit()
    conn.close()

def get_published():
    regs = []
    regs.append({ "id": 0, "name": "Não"}) 
    regs.append({ "id": 1, "name": "Sim"}) 
    return regs

def get_status():
    regs = []
    regs.append({ "id": 0, "name": "Opened"}) 
    regs.append({ "id": 1, "name": "Poker ready"}) 
    regs.append({ "id": 2, "name": "Pending"}) 
    regs.append({ "id": 3, "name": "Budget Done"}) 
    regs.append({ "id": 4, "name": "Resolved"}) 
    regs.append({ "id": 5, "name": "Jira"}) 
    regs.append({ "id": 6, "name": "Orçamento"}) 
    return regs

def get_effort():
    regs = []
    regs.append({ "id": 0, "name": "-"}) 
    regs.append({ "id": 1, "name": "Front"}) 
    regs.append({ "id": 2, "name": "Back"}) 
    regs.append({ "id": 3, "name": "Back/Front"}) 
    regs.append({ "id": 4, "name": "Suporte"}) 
    regs.append({ "id": 5, "name": "Infra"}) 
    regs.append({ "id": 6, "name": "Integrado"}) 
    return regs

def get_effort_sql():
    _sql = ("""CASE effort
    WHEN 1 THEN 'Front'
    WHEN 2 THEN 'Back'
    WHEN 3 THEN 'Back/Front'
    WHEN 4 THEN 'Suporte'
    WHEN 5 THEN 'Infra'
    WHEN 6 THEN 'Integrado'
    ELSE '-'
    END effort_lbl """)
    return _sql

def get_status_sql():
    _sql = ("CASE status "
    "WHEN 1 THEN 'Poker ready' "
    "WHEN 2 THEN 'Pending' "
    "WHEN 3 THEN 'Budget Done' "
    "WHEN 4 THEN 'Resolved' "
    "WHEN 5 THEN 'Jira' "
    "WHEN 6 THEN 'Orçamento' "
    "ELSE 'Opened' "
    "END status_lbl ")
    return _sql

def get_status_all():
    status = []
    status.append("Opened") 
    status.append("Poker ready") 
    status.append("Pending") 
    status.append("Budget Done") 
    status.append("Resolved") 
    status.append("Jira") 
    status.append("Orçamento") 
    return status

@app.route('/tickets/new', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

        number = request.form['number']
        dt_ticket = request.form['dt_ticket']
        subject = request.form['subject']
        client = request.form['client']
        # description = request.form['description']
        link = request.form['link']
        notes = request.form['notes']
        actions = request.form['actions']
        resume = request.form['resume']
        published = request.form['published']
        status = request.form['status']
        complexity = request.form['complexity']
        production_time = request.form['production_time']
        completion_deadline = request.form['completion_deadline']
        dt_solution = request.form['dt_solution']

        manager = request.form['manager']
        hours = request.form['hours']

        _sql = ("INSERT INTO tickets ( "
        "number, dt_ticket, subject, client, link, "
        "notes, actions, resume, published, "
        "status, complexity, production_time, completion_deadline, "
        "manager, hours, dt_solution ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )")

        if not number:
            flash('Number is required!', 'danger')
        else:
            if get_number(number) == 0:
                conn = get_db_connection()
                conn.execute(_sql, 
                        (number, dt_ticket, subject, client, link, 
                        notes, actions, resume, published, 
                        status, complexity, production_time, completion_deadline, 
                        manager, hours, dt_solution ))
                conn.commit()
                conn.close()
                ticket = get_ticketN(number)
                return redirect(url_for('edit', id=ticket['id']))
            else:
                flash('Number already in use!', 'warning')

    return render_template('create.html', published=get_published(), status=get_status())

@app.route('/tickets', methods=('GET', 'POST'))
def tickets():
    if request.method == 'POST':
        dt_ini = request.form['dt_ini']
        dt_fim = request.form['dt_fim']
        busca = request.form['busca']
        data = {
            "dt_ini": dt_ini,
            "dt_fim": dt_fim,
            "busca": busca,
        }    
        # return jsonify(data)
        _where = ""
        if len(dt_ini) > 0 and len(dt_fim):
            _where = "WHERE dt_ticket BETWEEN '{}' AND '{}'".format(dt_ini, dt_fim)
            if len(busca) > 0:
                _where += " AND subject LIKE '%{}%'".format(busca)
        else:
            _where += "WHERE subject LIKE '%{}%'".format(busca)
        _sql = "SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets {} ORDER BY dt_ticket DESC".format(_where)
        conn = get_db_connection()
        tickets = conn.execute(_sql).fetchall()
        conn.close()
        return render_template('tickets.html', tickets=tickets, status=get_status_all(), 
            effort=get_effort(), dt_ini=dt_ini, dt_fim=dt_fim, busca=busca)
    else:
        dias = 7
        hoje = date.today()
        days_to_subtract = dias
        dt_ini = hoje - timedelta(days=days_to_subtract)
        dt_fim = hoje         
        # dt_ini = date.today()
        # dt_fim = date.today()
        busca = ""
        _where = "WHERE dt_ticket BETWEEN '{}' AND '{}'".format(dt_ini, dt_fim)
        _sql = "SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets {} ORDER BY dt_ticket DESC".format(_where)
        conn = get_db_connection()
        tickets = conn.execute(_sql).fetchall()
        conn.close()
    return render_template('tickets.html', tickets=tickets, status=get_status_all(), 
        effort=get_effort(), dt_ini=dt_ini, dt_fim=dt_fim, busca=busca)

@app.route('/poker')
def poker():
    names = os.listdir(os.path.join(app.static_folder, 'images'))
    conn = get_db_connection()
    tickets = conn.execute("SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets WHERE status = 1 ORDER BY dt_ticket DESC").fetchall()
    conn.close()
    return render_template('poker.html', tickets=tickets, status=get_status_all(), complexities=get_complexity(), names=names)

@app.route('/lpoker', methods=('GET',))
def lpoker():
    _tags = " AND tags LIKE '%amento%' "
    _tags = " AND tags LIKE '%melhoria%' "
    #_tags = ""
    _sql = ("SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo "
    "FROM tickets WHERE status = 1 {} ORDER BY Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) DESC".format(_tags))
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    conn.close()
    return render_template('lpoker.html', tickets=tickets, status=get_status_all())

@app.route('/lorca', methods=('GET',))
def lorca():
    _sql = ("SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo "
    "FROM tickets WHERE status = 6 AND complexity <> 0 AND complexity < 13 ORDER BY Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) ASC")
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    conn.close()
    return render_template('lorca.html', tickets=tickets, status=get_status_all())

@app.route('/lpoker', methods=('POST',))
def lpokerP():
    if request.method == 'POST':
        dataX = []
        action = request.form['action']
        bag = request.form['bag']
        x = bag.split(",")
        itens = []
        if len(bag) > 0:
            for z in x:
                itens.append(int(z))
            itens.sort()
            conn = get_db_connection()
            for y in itens:
                status = 1 # Poker ready=1 | Pending=2
                chave = "comp_"+str(y)
                complexity = request.form.get(chave)
                if len(complexity) > 0:
                    _sql = ("UPDATE tickets SET status = ?, complexity = ? WHERE id = ?")
                    conn.execute(_sql,( status, complexity, y))
                    dataX.append({
                        "key": chave,
                        "value": complexity
                    }) 
            conn.commit()
            conn.close()
        data = {
            "bag": bag,
            "x": x,
            "action": action,
            "itens": itens,
            "dataX": dataX
        }    
    return jsonify(data)
    # return redirect(url_for('lpoker'))

@app.route('/tickets/<int:id>/delete', methods=('POST',))
def delete(id):
    ticket = get_ticket(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM tickets WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(ticket['number']), 'success')
    return redirect(url_for('tickets'))

def get_complexity():
    regs = []
    regs.append({ "id":  0, "complexity": .5, "hours": 1,  "days": 5 }) 
    regs.append({ "id":  1, "complexity": 1,  "hours": 2,  "days": 10 }) 
    regs.append({ "id":  2, "complexity": 2,  "hours": 4,  "days": 15 }) 
    regs.append({ "id":  3, "complexity": 3,  "hours": 6,  "days": 20 }) 
    regs.append({ "id":  4, "complexity": 4,  "hours": 8,  "days": 22 }) 
    regs.append({ "id":  5, "complexity": 5,  "hours": 10, "days": 25 }) 
    regs.append({ "id":  6, "complexity": 8,  "hours": 16, "days": 40 }) 
    regs.append({ "id":  7, "complexity": 13, "hours": 26, "days": 50 }) 
    regs.append({ "id":  8, "complexity": 21, "hours": 42, "days": 60 }) 
    regs.append({ "id":  9, "complexity": 23, "hours": 46, "days": 65 }) 
    regs.append({ "id": 10, "complexity": 29, "hours": 58, "days": 70 }) 
    regs.append({ "id": 11, "complexity": 31, "hours": 62, "days": 75 }) 
    regs.append({ "id": 12, "complexity": 37, "hours": 74, "days": 80 }) 
    regs.append({ "id": 13, "complexity": 41, "hours": 82, "days": 85 }) 
    regs.append({ "id": 14, "complexity": 43, "hours": 86, "days": 90 }) 
    regs.append({ "id": 15, "complexity": 47, "hours": 94, "days": 95 }) 
    regs.append({ "id": 16, "complexity": 53, "hours": 106, "days": 100 }) 
    regs.append({ "id": 17, "complexity": 59, "hours": 118, "days": 105 }) 
    return regs

def get_complexity_poker():
    regs = []
    regs.append({ "id":  0, "complexity": 0,  "hours": 0,  "days": 0 }) 
    regs.append({ "id":  1, "complexity": .5, "hours": 1,  "days": 5 }) 
    regs.append({ "id":  2, "complexity": 1,  "hours": 2,  "days": 10 }) 
    regs.append({ "id":  3, "complexity": 2,  "hours": 4,  "days": 15 }) 
    regs.append({ "id":  4, "complexity": 3,  "hours": 6,  "days": 20 }) 
    regs.append({ "id":  5, "complexity": 4,  "hours": 8,  "days": 22 }) 
    regs.append({ "id":  6, "complexity": 5,  "hours": 10, "days": 25 }) 
    regs.append({ "id":  7, "complexity": 8,  "hours": 16, "days": 40 }) 
    regs.append({ "id":  8, "complexity": 13, "hours": 26, "days": 50 }) 
    regs.append({ "id":  9, "complexity": 21, "hours": 42, "days": 60 }) 
    regs.append({ "id": 10, "complexity": 23, "hours": 46, "days": 65 }) 
    regs.append({ "id": 11, "complexity": 29, "hours": 58, "days": 70 }) 
    regs.append({ "id": 12, "complexity": 31, "hours": 62, "days": 75 }) 
    regs.append({ "id": 13, "complexity": 37, "hours": 74, "days": 80 }) 
    regs.append({ "id": 14, "complexity": 41, "hours": 82, "days": 85 }) 
    regs.append({ "id": 15, "complexity": 43, "hours": 86, "days": 90 }) 
    regs.append({ "id": 16, "complexity": 47, "hours": 94, "days": 95 }) 
    regs.append({ "id": 17, "complexity": 53, "hours": 106, "days": 100 }) 
    regs.append({ "id": 18, "complexity": 59, "hours": 118, "days": 105 }) 
    return regs

@app.route('/tickets/<int:id>/budget', methods=('GET',))
def budget(id):

    ticket = get_ticket(id)

    complexity = ticket['complexity']
    production_time = ticket['production_time']
    completion_deadline = ticket['completion_deadline']

    if int(complexity) != 0:
        complexities = get_complexity()
        for x in complexities:
            if int(complexity) == int(x['complexity']):
                if int(production_time) == 0:
                    production_time = x['hours']
                if int(completion_deadline) == 0:
                    completion_deadline = x['days']
                break

    return render_template('budget.html', ticket=ticket, tempo=production_time, dias=completion_deadline)

@app.route('/triagem')
def triagem():
    pdate = request.args.get('d', default = '202112')
    qregs = request.args.get('q', default = 0)
    _sql = ("SELECT "
    "*, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo "
    "FROM "
    "tickets "
    "WHERE "
    f"status = 0 AND jira = '' AND strftime('%Y%m', dt_ticket) = '{pdate}' "
    "ORDER BY dt_ticket DESC")
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    conn.close()
    return render_template('triagem.html', tickets=tickets, status=get_status_all(), pdate=pdate, qregs=qregs)

@app.route('/triagemo')
def triagemo():
    pdate = request.args.get('d', default = '202112')
    qregs = request.args.get('q', default = 0)
    _sql = ("SELECT "
    "*, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo "
    "FROM "
    "tickets "
    "WHERE "
    f"status = 0 AND jira = '' AND tags LIKE '%amento%' AND strftime('%Y%m', dt_ticket) = '{pdate}' "
    "ORDER BY dt_ticket DESC")
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    conn.close()
    return render_template('triagemo.html', tickets=tickets, status=get_status_all(), pdate=pdate, qregs=qregs)

@app.route('/resume')
def resume():

    conn = get_db_connection()

    _sql = ("SELECT "
    "strftime('%Y', dt_ticket) AS year, "
    "strftime('%m', dt_ticket) AS month, "
    "count(*) AS regs "
    "FROM "
    "tickets " 
    "WHERE "
    "status = 0 AND jira = '' "
    "GROUP BY "
    "strftime('%Y', dt_ticket), "
    "strftime('%m', dt_ticket) ")
    resume = conn.execute(_sql).fetchall()

    _sql = ("SELECT " 
    "  status_lbl, "
    "  registers "
    "FROM ( "
    "  SELECT "
    "  CASE status "
    "  WHEN 1 THEN 'Poker ready' "
    "  WHEN 2 THEN 'Pending' "
    "  WHEN 3 THEN 'Budget Done' "
    "  WHEN 4 THEN 'Resolved' "
    "  WHEN 5 THEN 'Jira' "
    "  WHEN 6 THEN 'Orçamento' "
    "  ELSE 'Opened' "
    "  END status_lbl, "
    "  count(*) AS registers " 
    "  FROM tickets " 
    "  WHERE "
    "  jira = '' "
    "  GROUP BY status " 
    
    "  UNION " 

    "  SELECT "
    "  'Total' AS status_lbl, "
    "  count(*) "
    "  FROM "
    "  tickets "
    "  WHERE "
    "  jira = '' "
    ") AS Temp")
    resume1 = conn.execute(_sql).fetchall()

    conn.close()
    return render_template('resume.html', resume=resume, resume1=resume1)

@app.route('/resumeo')
def resumeo():

    conn = get_db_connection()

    _sql = ("SELECT "
    "strftime('%Y', dt_ticket) AS year, "
    "strftime('%m', dt_ticket) AS month, "
    "count(*) AS regs "
    "FROM "
    "tickets " 
    "WHERE "
    "status = 0 AND jira = '' AND tags LIKE '%amento%' "
    "GROUP BY "
    "strftime('%Y', dt_ticket), "
    "strftime('%m', dt_ticket) ")
    resume = conn.execute(_sql).fetchall()

    _sql = ("SELECT " 
    "  status_lbl, "
    "  registers "
    "FROM ( "
    "  SELECT "
    "  CASE status "
    "  WHEN 1 THEN 'Poker ready' "
    "  WHEN 2 THEN 'Pending' "
    "  WHEN 3 THEN 'Budget Done' "
    "  WHEN 4 THEN 'Resolved' "
    "  WHEN 5 THEN 'Jira' "
    "  WHEN 6 THEN 'Orçamento' "
    "  ELSE 'Opened' "
    "  END status_lbl, "
    "  count(*) AS registers " 
    "  FROM tickets " 
    "  WHERE "
    "  status = 0 AND jira = '' AND tags LIKE '%amento%' "
    "  GROUP BY status " 
    
    "  UNION " 

    "  SELECT "
    "  'Total' AS status_lbl, "
    "  count(*) "
    "  FROM "
    "  tickets "
    "  WHERE "
    "  status = 0 AND jira = '' AND tags LIKE '%amento%' "
    ") AS Temp")
    resume1 = conn.execute(_sql).fetchall()

    conn.close()
    return render_template('resumeo.html', resume=resume, resume1=resume1)

@app.route('/fpoker')
def fpoker():
    kind = request.args.get('k', default = 0, type = int)
    _sql = "SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets WHERE status = 1 ORDER BY effort, dt_ticket DESC"
    if kind == 1:
        _sql = f"SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets WHERE tags LIKE '%mento%' AND complexity = 0 AND status = 1 ORDER BY effort, dt_ticket DESC"
    if kind == 2:
        _sql = f"SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets WHERE tags LIKE '%melhoria%' complexity = 0 AND  AND status = 1 ORDER BY effort, dt_ticket DESC"
    names = os.listdir(os.path.join(app.static_folder, 'images'))
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    conn.close()
    return render_template('fpoker.html', tickets=tickets, status=get_status_all(), complexities=get_complexity_poker(), names=names, effort=get_effort())

@app.route('/rpoker')
def rpoker():
    _complex = "complexity <> 0 AND"
    #_complex = ""
    _sql = "SELECT *, Cast ((JulianDay('now') - JulianDay(dt_ticket)) As Integer) AS Tempo FROM tickets WHERE {} status = 1 ORDER BY effort, dt_ticket DESC".format(_complex)
    names = os.listdir(os.path.join(app.static_folder, 'images'))
    conn = get_db_connection()
    tickets = conn.execute(_sql).fetchall()
    status=get_status_all()
    effort=get_effort()    
    _resp = ""
    _linha = ("{};{};{};{};{};{};{};{};{}\n".format(
        "ticket",
        "assunto",
        "cliente",
        "tipo",
        "tags",
        "complexidade",
        "production_time",
        "completion_deadline",
        "status"))
    _icont = 0
    _resp += _linha
    for ticket in tickets:
        _effort = effort[ticket['effort']]["name"]
        _linha = ("{};{};{};{};{};{};{};{};{}\n".format(
            ticket['number'],
            ticket['subject'],
            ticket['client'],
            _effort,
            ticket['tags'],
            ticket['complexity'],
            ticket['production_time'],
            ticket['completion_deadline'],
            ticket['status']))
        _icont += 1
        _resp += _linha
    conn.close()
    _resp += "{} registro(s)".format(_icont)
    return render_template('rpoker.html', resp=_resp, icont=_icont)

@app.route('/lesma/<int:id>/edit', methods=('GET', 'POST'))
def lesma(id):
    ticket = get_ticket(id)
    if request.method == 'POST':
        complexity = request.form['complexity']
        effort = request.form['effort']
        _sql = "UPDATE tickets SET complexity = ?, effort = ? WHERE id = ?"
        conn = get_db_connection()
        conn.execute(_sql, (complexity, effort, id))
        conn.commit()
        conn.close()
    return redirect(url_for('fpoker'))

@app.route('/movie1')
def moviedesk_resume():

    conn = get_db_connection()

    where = ""

    _sql = f"""SELECT visao, tabela, registros FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, count(*) AS registros FROM moviedesk1A {where} UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, count(*) AS registros FROM moviedesk2A {where} UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, count(*) AS registros FROM moviedesk3A {where} UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, count(*) AS registros FROM moviedesk4A {where} UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, count(*) AS registros FROM moviedesk5A {where} 
) AS Temp ORDER BY tabela """
    resume1 = conn.execute(_sql).fetchall()

    where = "WHERE jira = '' AND tags LIKE '%to ap%' "

    _sql = f"""SELECT visao, tabela, registros FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, count(*) AS registros FROM moviedesk1A {where} UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, count(*) AS registros FROM moviedesk2A {where} UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, count(*) AS registros FROM moviedesk3A {where} UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, count(*) AS registros FROM moviedesk4A {where} UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, count(*) AS registros FROM moviedesk5A {where} 
) AS Temp ORDER BY tabela """
    resume2 = conn.execute(_sql).fetchall()

    _sql = f"""SELECT *, (SELECT count(*) FROM tickets AS T1 WHERE T1.number = Temp.number) AS net FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, * FROM moviedesk1A UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, * FROM moviedesk2A UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, * FROM moviedesk3A UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, * FROM moviedesk4A UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, * FROM moviedesk5A 
) AS Temp WHERE jira = '' AND tags LIKE '%to ap%' AND tabela = 'moviedesk2A' 
ORDER BY number """
    resume3 = conn.execute(_sql).fetchall()

    _sql = f"""SELECT *, (SELECT count(*) FROM tickets AS T1 WHERE T1.number = Temp.number) AS net FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, * FROM moviedesk1A UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, * FROM moviedesk2A UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, * FROM moviedesk3A UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, * FROM moviedesk4A UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, * FROM moviedesk5A 
) AS Temp WHERE jira = '' AND tags LIKE '%to ap%' AND tabela = 'moviedesk4A' 
AND number NOT IN ( SELECT number FROM moviedesk2A WHERE jira = '' AND tags LIKE '%to ap%' )
ORDER BY number """
    resume4 = conn.execute(_sql).fetchall()

    conn.close()
    return render_template('movie1.html', 
        resume1=resume1,
        resume2=resume2,
        resume3=resume3,
        resume4=resume4,
    )

@app.route('/movie2')
def moviedesk_resume2():

    conn = get_db_connection()

    _sql = """SELECT *, strftime('%d-%m',created_at) AS created_at_br FROM resume ORDER BY created_at DESC LIMIT 10"""
    resume1 = conn.execute(_sql).fetchall()

    _sql = f"""SELECT ordem, visao, registros FROM ( 
SELECT 0 AS  ordem, 'Tickets sem Jira' AS visao, count(*) AS registros FROM moviedesk1A WHERE jira = '' UNION 
SELECT 2 AS  ordem, 'Tickets de Orçamento' AS visao, count(*) AS registros FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' UNION
SELECT 1 AS  ordem, 'Tickets de Melhoria' AS visao, count(*) AS registros FROM moviedesk1A WHERE jira = '' AND number NOT IN ( SELECT number FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' )
) AS Temp ORDER BY ordem """
    resume2 = conn.execute(_sql).fetchall()

    _sql = f"""SELECT *, (SELECT count(*) FROM tickets AS T1 WHERE T1.number = Temp.number) AS net FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, * FROM moviedesk1A UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, * FROM moviedesk2A UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, * FROM moviedesk3A UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, * FROM moviedesk4A UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, * FROM moviedesk5A 
) AS Temp WHERE jira = '' AND tags LIKE '%orçamento%' AND tabela = 'moviedesk1A' 
ORDER BY dt_ticket DESC """
    resume3 = conn.execute(_sql).fetchall()

    conn.close()
    return render_template('movie2.html', 
        resume1=resume1,
        resume2=resume2,
        resume3=resume3,
    )

@app.route('/handle_data', methods=('POST', ))
def handle_data():
    #result_dict = {'request': request.form}
    #return jsonify(result_dict)
    conn = get_db_connection()
    _sql = ("INSERT INTO resume ( mov1, mov2, mov3, mov4, mov5, aux1, aux2, aux3, aux4, aux5  ) VALUES ( "
            "?, ?, ?, ?, ?, "
            "?, ?, ?, ?, ? )")
    conn.execute(_sql, (
        request.form["mov1_0"], 
        request.form["mov2_0"], 
        request.form["mov3_0"], 
        request.form["mov4_0"], 
        request.form["mov5_0"], 
        request.form["aux1_0"], 
        request.form["aux2_0"], 
        request.form["aux3_0"], 
        request.form["aux4_0"], 
        request.form["aux5_0"]
    ))
    conn.commit()
    conn.close()
    return redirect(url_for('lresume'))  

@app.route('/lresume', methods=('GET', 'POST'))
def lresume():
    if request.method == 'POST':
        mat = request.form['bag'].split(',')
        #lids = []
        conn = get_db_connection()
        for item in mat:
            if len(item) > 0:
                #lids.append(item)
                _sql = ("UPDATE resume SET "
                        "mov1 = ?, mov2 = ?, mov3 = ?, mov4 = ?, mov5 = ?, "
                        "aux1 = ?, aux2 = ?, aux3 = ?, aux4 = ?, aux5 = ?, "
                        "published = ? WHERE id = ?")
                conn.execute(_sql, (
                    request.form["mov1_"+item], 
                    request.form["mov2_"+item], 
                    request.form["mov3_"+item], 
                    request.form["mov4_"+item], 
                    request.form["mov5_"+item], 
                    request.form["aux1_"+item], 
                    request.form["aux2_"+item], 
                    request.form["aux3_"+item], 
                    request.form["aux4_"+item], 
                    request.form["aux5_"+item], 
                    request.form["published_"+item], 
                    item
                ))
                conn.commit()
        conn.close()
        # result_dict = {'request': request.form, 'lids': lids}
        # return jsonify(result_dict)
    conn = get_db_connection()
    where = ""
    _sql = f"""SELECT visao, tabela, registros FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, count(*) AS registros FROM moviedesk1A {where} UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, count(*) AS registros FROM moviedesk2A {where} UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, count(*) AS registros FROM moviedesk3A {where} UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, count(*) AS registros FROM moviedesk4A {where} UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, count(*) AS registros FROM moviedesk5A {where} 
) AS Temp ORDER BY tabela """
    resume1 = conn.execute(_sql).fetchall()
    _sql = "SELECT *, strftime('%d-%m-%Y',created_at) AS created_at_br FROM resume ORDER BY created_at DESC LIMIT 6"
    resume = conn.execute(_sql).fetchall()
    conn.close()
    _tabela = []
    for item in resume1:
        _tabela.append(item['registros'])
    return render_template('lresume.html', resume=resume, resume1=resume1, tabela=_tabela)

@app.route('/movie3')
def moviedesk_resume3():

    conn = get_db_connection()

    where = ""

    _sql = f"""
SELECT visao, tabela, registros FROM (
SELECT 'Todos Abertos nos Grupos Evolução' AS visao, 'moviedesk1A' AS tabela, count(*) AS registros FROM moviedesk1A {where} UNION
SELECT 'Orçamentos Aprovados Abertos -Grupo Evolução' AS visao, 'moviedesk2A' AS tabela, count(*) AS registros FROM moviedesk2A {where} UNION
SELECT 'Orçamentos Pendentes de Orçar Abertos - Grupo Evolução' AS visao, 'moviedesk3A' AS tabela, count(*) AS registros FROM moviedesk3A {where} UNION
SELECT 'Orçamentos Aprovados Abertos - Todas as Equipes' AS visao, 'moviedesk4A' AS tabela, count(*) AS registros FROM moviedesk4A {where} UNION
SELECT 'Orçamentos Abertos ( Pendentes Orçar) - Todas Equipes' AS visao, 'moviedesk5A' AS tabela, count(*) AS registros FROM moviedesk5A {where} 
) AS Temp ORDER BY tabela """
    resume0 = conn.execute(_sql).fetchall()

    _sql = f"""
SELECT 
dt_ticket_br,
registros
FROM (
SELECT
strftime('%Y-%m',dt_ticket) AS dt_ticket_br,
count(*) AS registros
FROM
moviedesk1A 
WHERE
jira = '' AND tags LIKE '%orçamento%' 
GROUP BY
strftime('%Y-%m',dt_ticket)
) AS Temp ORDER BY dt_ticket_br DESC """
    resume1 = conn.execute(_sql).fetchall()

    _sql = f"""
SELECT 
dt_ticket_br,
registros
FROM (
SELECT
strftime('%Y-%m',dt_ticket) AS dt_ticket_br,
count(*) AS registros
FROM
moviedesk1A 
--WHERE
--jira = '' AND tags LIKE '%orçamento%' 
WHERE 
jira = '' AND number NOT IN ( SELECT number FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' )
GROUP BY
strftime('%Y-%m',dt_ticket)
) AS Temp ORDER BY dt_ticket_br DESC """
    resume2 = conn.execute(_sql).fetchall()

    conn.close()
    return render_template('movie3.html', 
        resume0=resume0,
        resume1=resume1,
        resume2=resume2,
    )

@app.route('/orcamentos/json')
def orcamentos_json():
    @after_this_request
    def add_header(response):
        # https://qastack.com.br/programming/11773348/python-flask-how-to-set-content-type
        response.headers['Content-Type'] = 'text/json; charset=utf-8'
        return response
    _sql = f"""
SELECT
number,
'' AS Time,
'' AS Parecer,
'' AS Tag,
'' AS Effort,
'' AS Complexidade,
dt_ticket,
subject,
client,
link,
tags,
category,
responsible,
manager
FROM
moviedesk1A 
WHERE
jira = '' AND tags LIKE '%orçamento%' 
ORDER BY dt_ticket DESC
    """
    conn = get_db_connection()
    regs = conn.execute(_sql).fetchall()
    conn.close()
    data = []
    for row in regs:
        data.append({
            "number": row['number'],
            "Time": "",
            "Parecer": "",
            "Tag": "",
            "Effort": "",
            "Complexidade": "",
            "dt_ticket": row['dt_ticket'],
            "subject": row['subject'],
            "client": row['client'],
            "link": row['link'],
            "tags": row['tags'],
            "category": row['category'],
            "responsible": row['responsible'],
            "manager": row['manager']
        })    
    return jsonify(data)

@app.route('/orcamentos/csv')
def orcamentos_csv():
    _sql = f"""
SELECT
number,
'' AS Time,
'' AS Parecer,
'' AS Tag,
'' AS Effort,
'' AS Complexidade,
dt_ticket,
subject,
client,
link,
tags,
category,
responsible,
manager
FROM
moviedesk1A 
WHERE
jira = '' AND tags LIKE '%orçamento%' 
ORDER BY dt_ticket DESC
    """
    conn = get_db_connection()
    regs = conn.execute(_sql).fetchall()
    conn.close()
    data = []
    for row in regs:
        data.append({
            "number": row['number'],
            "Time": "",
            "Parecer": "",
            "Tag": "",
            "Effort": "",
            "Complexidade": "",
            "dt_ticket": row['dt_ticket'],
            "subject": row['subject'],
            "client": row['client'],
            "link": row['link'],
            "tags": row['tags'],
            "category": row['category'],
            "responsible": row['responsible'],
            "manager": row['manager']
        })    
    return jsonify(data)

@app.route('/melhorias/json')
def melhorias_json():
    _sql = f"""
SELECT
number,
'' AS Time,
'' AS Parecer,
'' AS Tag,
'' AS Effort,
'' AS Complexidade,
dt_ticket,
subject,
client,
link,
tags,
category,
responsible,
manager
FROM
moviedesk1A WHERE jira = '' AND number NOT IN ( SELECT number FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' )
ORDER BY dt_ticket DESC
    """
    conn = get_db_connection()
    regs = conn.execute(_sql).fetchall()
    conn.close()
    data = []
    for row in regs:
        data.append({
            "number": row['number'],
            "Time": "",
            "Parecer": "",
            "Tag": "",
            "Effort": "",
            "Complexidade": "",
            "dt_ticket": row['dt_ticket'],
            "subject": row['subject'],
            "client": row['client'],
            "link": row['link'],
            "tags": row['tags'],
            "category": row['category'],
            "responsible": row['responsible'],
            "manager": row['manager']
        })    
    return jsonify(data)

@app.route('/movie4')
def moviedesk_resume4():

    dias = 10
    hoje = date.today()
    days_to_subtract = dias
    start_dt = hoje - timedelta(days=days_to_subtract)
    end_dt = hoje 
    #start_dt = date(2022, 2, 1)
    #end_dt = date(2022, 2, 10)

    conn = get_db_connection()

    _sql = f"""
SELECT
dt_ticket,
count(*) AS registros
FROM
moviedesk1A 
WHERE
jira = '' AND tags LIKE '%orçamento%' 
GROUP BY dt_ticket
ORDER BY dt_ticket DESC
LIMIT {dias} """
    resumeO = conn.execute(_sql).fetchall()

    _sql = f"""
SELECT count(*) AS registros FROM moviedesk1A WHERE 
jira = '' AND tags LIKE '%orçamento%' AND dt_ticket < '{start_dt}' """
    resumeOT = conn.execute(_sql).fetchall()

    _sql = f"""
SELECT
dt_ticket,
count(*) AS registros
FROM
moviedesk1A 
WHERE
jira = '' AND number NOT IN ( SELECT number FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' )
GROUP BY dt_ticket
ORDER BY dt_ticket DESC
LIMIT {dias} """
    resumeM = conn.execute(_sql).fetchall()

    _sql = f"""
SELECT count(*) AS registros FROM moviedesk1A WHERE 
jira = '' AND number NOT IN ( SELECT number FROM moviedesk1A WHERE jira = '' AND tags LIKE '%orçamento%' )
AND dt_ticket < '{start_dt}' """
    resumeMT = conn.execute(_sql).fetchall()

    days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    data = []

    torca = 0
    for item in resumeOT:
        torca = item['registros']

    tmelh = 0
    for item in resumeMT:
        tmelh = item['registros']

    tsoma = torca + tmelh

    data.append({
        "dt_ticket": "",
        "weekday": "",
        "orcamentos": torca,
        "melhorias": tmelh,
        "total": torca + tmelh,
        "soma": torca + tmelh
    })

    icont = 0
    for dt in daterange(start_dt, end_dt):
            orcamentos = 0
            melhorias = 0
            for item in resumeO:
                if item['dt_ticket'] == dt.strftime("%Y-%m-%d"):
                    orcamentos = item['registros']
                    break;
            for item in resumeM:
                if item['dt_ticket'] == dt.strftime("%Y-%m-%d"):
                    melhorias = item['registros']
                    break;
            tsoma = tsoma + (orcamentos + melhorias)
            data.append({
                "dt_ticket": dt.strftime("%Y-%m-%d"),
                "weekday": days[dt.weekday()],
                "orcamentos": orcamentos,
                "melhorias": melhorias,
                "total": orcamentos + melhorias,
                "soma": tsoma
            })
            icont += 1

    conn.close()
    return render_template('movie4.html', 
        resume1=data
    )

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def date_bwn_two_dates(start_date, end_date):
    date_list = [] # The list where we want to store
    for i in range(int((end_date-start_date).days)+1): # Iterate between the range of dates
        year = (start_date+timedelta(i)).strftime("%Y") # Get the Year
        month = (start_date+timedelta(i)).strftime("%m") # Get the month
        date_a = (start_date+timedelta(i)).strftime("%d") # Get the day
        date_list.append([year, month, date_a]) # Append the Objects accquired
    return date_list # return the list

@app.route('/datesbetween1')
def dates_between1():
    data = []
    for i in date_bwn_two_dates(date(2022, 2, 1), date(2022, 2, 10)):
        data.append(i)
    return jsonify(data)

@app.route('/datesbetween')
def dates_between():
    data = []
    hoje = date.today()
    days_to_subtract = 9
    start_dt = hoje - timedelta(days=days_to_subtract)
    end_dt = hoje 
    days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    #start_dt = date(2022, 2, 1)
    #end_dt = date(2022, 2, 10)
    data.append({
        "start_dt": start_dt.strftime("%Y-%m-%d"),
        "end_dt": end_dt.strftime("%Y-%m-%d"),
        "days_to_subtract": days_to_subtract
    })
    for dt in daterange(start_dt, end_dt):
        data.append({
            "date": dt.strftime("%Y-%m-%d"),
            "weekday": days[dt.weekday()],
            "month": dt.strftime("%m"),
            "year": dt.strftime("%Y")
        })
    return jsonify(data)

