"""
vulnerable_test.py
------------------
INTENTIONALLY VULNERABLE CODE — for security scanner testing only.
DO NOT deploy or run in production.
"""

import os
import sqlite3
import subprocess
import pickle
import hashlib
import random
import yaml
import xml.etree.ElementTree as ET
from flask import Flask, request, render_template_string

app = Flask(__name__)

# -----------------------------------------------------------------------
# 1. HARDCODED CREDENTIALS
# -----------------------------------------------------------------------
SECRET_KEY = "supersecret123"
DB_PASSWORD = "admin123"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
API_TOKEN = "ghp_exampleHardcodedGitHubToken12345"


# -----------------------------------------------------------------------
# 2. SQL INJECTION
# -----------------------------------------------------------------------
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable: user input concatenated directly into SQL query
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchall()


def login(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable: f-string SQL injection
    cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
    return cursor.fetchone()


# -----------------------------------------------------------------------
# 3. COMMAND INJECTION
# -----------------------------------------------------------------------
def ping_host(host):
    # Vulnerable: user-controlled input passed to shell
    os.system("ping -c 1 " + host)


def get_file_info(filename):
    # Vulnerable: shell=True with user input
    result = subprocess.run("ls -la " + filename, shell=True, capture_output=True)
    return result.stdout


def compress_file(filepath):
    # Vulnerable: another shell injection vector
    subprocess.call(f"tar -czf archive.tar.gz {filepath}", shell=True)


# -----------------------------------------------------------------------
# 4. PATH TRAVERSAL
# -----------------------------------------------------------------------
def read_user_file(filename):
    # Vulnerable: no sanitization, allows ../../etc/passwd style paths
    base_dir = "/var/app/uploads/"
    with open(base_dir + filename, "r") as f:
        return f.read()


@app.route("/download")
def download():
    # Vulnerable: user controls file path
    filename = request.args.get("file")
    with open(filename, "r") as f:
        return f.read()


# -----------------------------------------------------------------------
# 5. CROSS-SITE SCRIPTING (XSS)
# -----------------------------------------------------------------------
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    # Vulnerable: user input rendered directly into HTML without escaping
    return render_template_string("<h1>Hello, " + name + "!</h1>")


@app.route("/search")
def search():
    query = request.args.get("q", "")
    # Vulnerable: reflected XSS
    return f"<p>Search results for: {query}</p>"


# -----------------------------------------------------------------------
# 6. INSECURE DESERIALIZATION
# -----------------------------------------------------------------------
def load_user_session(data):
    # Vulnerable: pickle.loads on untrusted data allows arbitrary code execution
    return pickle.loads(data)


def load_config(data):
    # Vulnerable: yaml.load without Loader allows code execution
    return yaml.load(data)


# -----------------------------------------------------------------------
# 7. WEAK CRYPTOGRAPHY
# -----------------------------------------------------------------------
def hash_password_weak(password):
    # Vulnerable: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_sha1(password):
    # Vulnerable: SHA1 without salt
    return hashlib.sha1(password.encode()).hexdigest()


def generate_token():
    # Vulnerable: random is not cryptographically secure
    return str(random.randint(100000, 999999))


# -----------------------------------------------------------------------
# 8. XML EXTERNAL ENTITY (XXE)
# -----------------------------------------------------------------------
def parse_xml(xml_data):
    # Vulnerable: default ET parser can be exploited via malicious XML input
    tree = ET.fromstring(xml_data)
    return tree


# -----------------------------------------------------------------------
# 9. OPEN REDIRECT
# -----------------------------------------------------------------------
@app.route("/redirect")
def unsafe_redirect():
    from flask import redirect
    url = request.args.get("url")
    # Vulnerable: no validation of redirect destination
    return redirect(url)


# -----------------------------------------------------------------------
# 10. SENSITIVE DATA EXPOSURE
# -----------------------------------------------------------------------
@app.route("/debug")
def debug_info():
    # Vulnerable: leaks environment variables and internal state
    env_vars = dict(os.environ)
    return str(env_vars)


@app.route("/user/<int:user_id>")
def get_user_data(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    # Vulnerable: returns full user record including password hash
    return str(user)


# -----------------------------------------------------------------------
# 11. INSECURE DIRECT OBJECT REFERENCE (IDOR)
# -----------------------------------------------------------------------
@app.route("/invoice/<invoice_id>")
def get_invoice(invoice_id):
    # Vulnerable: no authorization check — any user can access any invoice
    conn = sqlite3.connect("billing.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM invoices WHERE id = {invoice_id}")
    return str(cursor.fetchone())


# -----------------------------------------------------------------------
# 12. EXEC / EVAL INJECTION
# -----------------------------------------------------------------------
def run_user_code(code):
    # Vulnerable: executes arbitrary user-supplied Python code
    exec(code)


def evaluate_expression(expr):
    # Vulnerable: evaluates arbitrary expressions
    return eval(expr)


# -----------------------------------------------------------------------
# 13. DIRECTORY LISTING / DEBUG MODE
# -----------------------------------------------------------------------
if __name__ == "__main__":
    # Vulnerable: debug=True exposes interactive debugger in production
    app.run(debug=True, host="0.0.0.0", port=5000)