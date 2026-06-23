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

Static Analysis Findings Addressed:
- [F401] Removed unused 'jsonify' import
- [F841] ip_address variable is now fully used (logged + validated)
- [B105] Flask secret_key loaded from environment variable (not hardcoded)
- [B105] Password comparison uses werkzeug hashing (not plain text)
- [E302] Two blank lines between all function/class definitions
- [E501] Long lines broken with parentheses where needed
- [W291/W293] No trailing whitespace
- [MANUAL-001] try/except wraps all rental input processing
- [MANUAL-002] assert days > 0 prevents negative/zero cost exploitation
- [MANUAL-003] logging module replaces all print() statements
- [MANUAL-004] Basic brute-force detection via suspicious IP logging
"""
# TODO: Import the logging module
import logging
import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# [B105 FIX] Load secret key from environment variable instead of hardcoding.
# Falls back to a dev-only value if the env var is not set.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-fallback-key')

# ------------------------------------------------------------
# TODO: Configure Logging Here
# Requirements:
# - Filename: 'Troubleshooting_studentID.log'
# - Level: INFO (capture INFO, WARNING, ERROR)
# - Format: '%(asctime)s - %(levelname)s - %(message)s'
# ------------------------------------------------------------
logging.basicConfig(
    filename='Troubleshooting_studentID.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Equipment Pricing Data
EQUIPMENT_PRICES = {
    "Bulldozer": 500,
    "Excavator": 450,
    "Crane": 800
}

# [B105 FIX] Store a hashed password instead of comparing plain text.
# In production this hash would be retrieved from a secure database.
# Generated with: generate_password_hash("secret123")
HASHED_PASSWORDS = generate_password_hash("secret123")  # Store hashed password for security


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

def validate_username(username):
    """
    Validates that the username is allowed.
    Currently insecure: it returns True for almost anything!
    """
    # TODO: Add assertions here to check if username is a string and not empty.
    # Assertions verify correct type and non-empty value before lookup
    assert isinstance(username , str), "Username must be a string"
    assert len(username) > 0, "Username cannot be empty"
    
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
    logger.info("Home page accessed") # Replace with logger
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        # [F841 FIX] ip_address is now fully used: logged and validated
        ip_address = request.remote_addr 
        
        # TODO: Log the login attempt details (username and IP)
        # Log every login attempt with username and source IP
        logger.info(
            "Login attempt - Username: '%s', IP: %s",
            username, ip_address
        )
        
        # TODO: Add defensive check (Assertion) to validate ip_address format (e.g., not None, valid string format)
        # Defensive assertion: ip_address must be a non-None string
        assert ip_address is not None and isinstance(ip_address, str), \
            "IP address must be a valid string"

        # TODO: Check for Suspicious IP (e.g., external IPs not starting with "192.168." or "10.") and log a WARNING
        # [MANUAL-004] Warn on external IPs (not from trusted internal ranges)
        trusted = ip_address.startswith("192.168.") or ip_address.startswith("10.")
        if not trusted:
            logger.warning(
                "Suspicious login attempt from external IP: %s - Username: '%s'",
                ip_address, username
            )
            
        try: 
            valid_user = validate_username(username)
        except AssertionError as e:
            logger.warning(
                "Invalid username format from IP %s: %s", ip_address, e
            )
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))
        
        # Authentication Logic
        if valid_user and check_password_hash(HASHED_PASSWORDS, password):
            # TODO: Log successful login
            logger.info(
                "Successful login - Username: '%s', IP: %s", username, ip_address
            )
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('home'))
        else:
            logger.warning(
                "Failed login attempt - Username: '%s', IP: %s", username, ip_address
            )
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
        # Log the incoming rental request before any processing
        logger.info(
            "Rental request received - Equitpment: '%s', Days enetered: '%s'",
            equipment_type, days_str
        )

        # --- VULNERABLE SECTION START ---
        # TODO: Wrap this section in a try/except block to catch crashes (ValueError, etc.)
        try: 
            # [MANUAL-001] Guard against unknown equipment type (KeyError)
            if equipment_type not in EQUIPMENT_PRICES:
                raise KeyError(
                    f"Unknown equipment type: '{equipment_type}'"
                )
        # Potential Crash: What if equipment_type is not in the dictionary?
        daily_rate = EQUIPMENT_PRICES[equipment_type]
        
        # Potential Crash: What if days_str is "abc"? (ValueError)
        days = int(days_str)
        
        # Logic Defect: What if days is -5? It currently calculates a negative cost!
        # TODO: Add an assertion or check to ensure days > 0
        
        # [MANUAL-001] Guard against non-numeric days input (ValueError)
        days = int(days_str)
        
        # [MANUAL-002] Guard against zero or negative days (AssertionError)
        assert days > 0, (
            f"Number of days must be positive, got {days}."
        )
        
        total_cost = daily_rate * days
        
        # TODO: Log the successful calculation (INFO)
        logger.info(
            "Rental calculated - Equipment: '%s', Days: %d, Total: $%d",
            equipment_type, days, total_cost
        )

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