"""
WGU Construction Equipment Rental - Flask Application (Student Starter)

Scenario:
You have been provided with this partially operational web application.
While it "works" (the site loads and processes requests), it is fragile and insecure.
Previous logs (`network_security_log.txt`) indicate several issues:
1. Application crashes (Runtime Errors).
2. Security vulnerabilities (Unrestricted inputs, suspicious IPs).
3. Lack of real-time logging (Blind spots).

Your Task:
1. Analyze the `network_security_log.txt` to understand the past issues.
2. Review the `static_analysis_report.txt` to see vulnerabilities detected by
   static analysis tools (Flake8 and Bandit) - supports Rubric Aspect A9.
3. Modify this file (`app_student.py`) to:
   - Configure Python's logging module to write to 'Troubleshooting_studentID.log'.
   - Add defensive coding (Assertions, Try/Except blocks) to prevent crashes.
   - Add proper validation (e.g., check for negative days, invalid users).
   - Log all significant events (INFO) and errors (WARNING/ERROR).

Static Analysis Tools Used:
- Flake8: Code quality and PEP 8 style checking (run: python -m flake8 app_student.py)
- Bandit: Security vulnerability detection (run: python -m bandit app_student.py)
"""

# TODO: Import the logging module
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkeyforflasksessions'

# ------------------------------------------------------------
# TODO: Configure Logging Here
# Requirements:
# - Filename: 'Troubleshooting_studentID.log'
# - Level: INFO (capture INFO, WARNING, ERROR)
# - Format: '%(asctime)s - %(levelname)s - %(message)s'
# ------------------------------------------------------------


# Equipment Pricing Data
EQUIPMENT_PRICES = {
    "Bulldozer": 500,
    "Excavator": 450,
    "Crane": 800
}

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

def validate_username(username):
    """
    Validates that the username is allowed.
    Currently insecure: it returns True for almost anything!
    """
    # TODO: Add assertions here to check if username is a string and not empty.
    
    allowed_users = {"admin", "alice", "bob", "charlie"}
    if username in allowed_users:
        return True
    return False

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------

@app.route('/')
def home():
    # TODO: Log "Home page accessed" at INFO level
    print("Home page accessed") # Replace with logger
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Simulated IP address (In a real app, this would be request.remote_addr)
        ip_address = request.remote_addr 
        
        # TODO: Log the login attempt details (username and IP)

        # TODO: Add defensive check (Assertion) to validate ip_address format (e.g., not None, valid string format)

        # TODO: Check for Suspicious IP (e.g., external IPs not starting with "192.168." or "10.") and log a WARNING
        
        # Authentication Logic
        if validate_username(username) and password == "secret123":
            # TODO: Log successful login
            print(f"User {username} logged in.") 
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('home'))
        else:
            # TODO: Log failed login (WARNING)
            print(f"Login failed for {username}.")
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/rent', methods=['GET', 'POST'])
def rent_equipment():
    rental_result = None
    
    if request.method == 'POST':
        equipment_type = request.form.get("equipment_type")
        days_str = request.form.get("days")

        # TODO: Log the rental request details

        # --- VULNERABLE SECTION START ---
        # TODO: Wrap this section in a try/except block to catch crashes (ValueError, etc.)
        
        # Potential Crash: What if equipment_type is not in the dictionary?
        daily_rate = EQUIPMENT_PRICES[equipment_type]
        
        # Potential Crash: What if days_str is "abc"? (ValueError)
        days = int(days_str)
        
        # Logic Defect: What if days is -5? It currently calculates a negative cost!
        # TODO: Add an assertion or check to ensure days > 0
        
        total_cost = daily_rate * days
        
        # TODO: Log the successful calculation (INFO)
        print(f"Calculated cost: {total_cost}")

        rental_result = {
            "equipment": equipment_type,
            "days": days,
            "total_cost": total_cost
        }
        flash("Rental calculated successfully!", "success")
        
        # --- VULNERABLE SECTION END ---
        
        # TODO: In your except blocks, log the errors (ERROR) and flash a user-friendly message

    return render_template('rent.html', rental_result=rental_result)

if __name__ == '__main__':
    print("Starting application...") # Replace with logger
    app.run(debug=False, port=5000)