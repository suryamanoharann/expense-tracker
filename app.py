from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'mysql55',   
    'database': 'expense_tracker'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    cfg = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS expense_tracker CHARACTER SET utf8mb4")
    conn.commit(); cur.close(); conn.close()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            title      VARCHAR(255) NOT NULL,
            amount     DECIMAL(12,2) NOT NULL,
            category   ENUM('Food','Transport','Shopping','Bills','Entertainment','Other') NOT NULL,
            date       DATE NOT NULL,
            note       TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit(); cur.close(); conn.close()
    print("✅ Database ready.")

VALID_CATEGORIES = {'Food','Transport','Shopping','Bills','Entertainment','Other'}

def validate(data):
    errors = []
    title    = str(data.get('title','')).strip()
    amount   = data.get('amount')
    category = str(data.get('category','')).strip()
    exp_date = str(data.get('date','')).strip()
    note     = str(data.get('note','')).strip()

    if not title:           errors.append("Title is required.")
    elif len(title) > 255:  errors.append("Title max 255 chars.")
    try:
        amount = float(amount)
        if amount <= 0:     errors.append("Amount must be > 0.")
    except (TypeError, ValueError):
                            errors.append("Amount must be a number.")
    if category not in VALID_CATEGORIES:
                            errors.append("Invalid category.")
    try:
        datetime.strptime(exp_date, '%Y-%m-%d')
    except ValueError:      errors.append("Date must be YYYY-MM-DD.")

    return errors, title, amount, category, exp_date, note

def to_dict(cursor, row):
    d = dict(zip([c[0] for c in cursor.description], row))
    if isinstance(d.get('date'), date):           d['date']       = d['date'].isoformat()
    if isinstance(d.get('created_at'), datetime): d['created_at'] = d['created_at'].isoformat()
    if isinstance(d.get('updated_at'), datetime): d['updated_at'] = d['updated_at'].isoformat()
    if d.get('amount') is not None:               d['amount']     = float(d['amount'])
    return d

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET'])
def list_expenses():
    sql, params = "SELECT * FROM expenses WHERE 1=1", []
    for key, col, op in [('category','category','='),('date_from','date','>='),('date_to','date','<=')]:
        val = request.args.get(key,'').strip()
        if val and (key != 'category' or val in VALID_CATEGORIES):
            sql += f" AND {col} {op} %s"; params.append(val)
    if s := request.args.get('search','').strip():
        sql += " AND title LIKE %s"; params.append(f"%{s}%")
    sql += " ORDER BY date DESC, id DESC"
    conn = get_db(); cur = conn.cursor()
    cur.execute(sql, params)
    result = [to_dict(cur, r) for r in cur.fetchall()]
    cur.close(); conn.close()
    return jsonify(result)

@app.route('/api/expenses', methods=['POST'])
def create_expense():
    data = request.get_json(force=True) or {}
    errors, title, amount, category, exp_date, note = validate(data)
    if errors: return jsonify({'errors': errors}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT INTO expenses (title,amount,category,date,note) VALUES (%s,%s,%s,%s,%s)",
                (title, amount, category, exp_date, note or None))
    conn.commit()
    cur.execute("SELECT * FROM expenses WHERE id=%s", (cur.lastrowid,))
    result = to_dict(cur, cur.fetchone())
    cur.close(); conn.close()
    return jsonify(result), 201

@app.route('/api/expenses/<int:eid>', methods=['PUT'])
def update_expense(eid):
    data = request.get_json(force=True) or {}
    errors, title, amount, category, exp_date, note = validate(data)
    if errors: return jsonify({'errors': errors}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id FROM expenses WHERE id=%s", (eid,))
    if not cur.fetchone(): cur.close(); conn.close(); return jsonify({'error':'Not found.'}), 404
    cur.execute("UPDATE expenses SET title=%s,amount=%s,category=%s,date=%s,note=%s WHERE id=%s",
                (title, amount, category, exp_date, note or None, eid))
    conn.commit()
    cur.execute("SELECT * FROM expenses WHERE id=%s", (eid,))
    result = to_dict(cur, cur.fetchone())
    cur.close(); conn.close()
    return jsonify(result)

@app.route('/api/expenses/<int:eid>', methods=['DELETE'])
def delete_expense(eid):
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id FROM expenses WHERE id=%s", (eid,))
    if not cur.fetchone(): cur.close(); conn.close(); return jsonify({'error':'Not found.'}), 404
    cur.execute("DELETE FROM expenses WHERE id=%s", (eid,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'message': 'Deleted.'})

@app.route('/api/summary')
def summary():
    today = date.today()
    try:
        y = int(request.args.get('year',  today.year))
        m = int(request.args.get('month', today.month))
        if not 1 <= m <= 12: raise ValueError
    except ValueError:
        return jsonify({'error': 'Invalid year/month.'}), 400
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE YEAR(date)=%s AND MONTH(date)=%s", (y,m))
    total = float(cur.fetchone()[0])
    cur.execute("SELECT category, SUM(amount) FROM expenses WHERE YEAR(date)=%s AND MONTH(date)=%s GROUP BY category ORDER BY 2 DESC", (y,m))
    breakdown = {r[0]: float(r[1]) for r in cur.fetchall()}
    cur.close(); conn.close()
    return jsonify({'year':y,'month':m,'total':total,'breakdown':breakdown})

if __name__ == '__main__':
    init_db()
    print("🚀  http://127.0.0.1:5000")
    app.run(debug=True, port=5000)