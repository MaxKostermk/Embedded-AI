from flask import Flask, request, render_template, jsonify
from datetime import datetime, timedelta
import sqlite3
import os

app = Flask(__name__)

# SQLite database setup - modified to point to the 'database' folder
DB_FILE = os.path.join(os.path.dirname(__file__), 'database', 'feedback.db')

def init_db():
    """Create the feedback table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        feedback_type TEXT NOT NULL,
        device_identifier TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def store_feedback(client_ip, feedback):
    """Store feedback in the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO feedback (timestamp, feedback_type, device_identifier)
    VALUES (?, ?, ?)
    """, (datetime.now().replace(second=0, microsecond=0), feedback, client_ip))
    conn.commit()
    conn.close()

def has_submitted_recently(client_ip):
    """Check if the client has submitted feedback in the last hour."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT timestamp FROM feedback
    WHERE device_identifier = ?
    ORDER BY timestamp DESC LIMIT 1
    """, (client_ip,))
    last_submission = cursor.fetchone()
    conn.close()

    if last_submission:
        last_feedback_time = datetime.strptime(last_submission[0], '%Y-%m-%d %H:%M:%S')
        if datetime.now() - last_feedback_time < timedelta(hours=1):
            return True  # Already submitted within the last hour
    return False  # No recent submission

@app.route('/too-hot', methods=['GET'])
def too_hot():
    client_ip = request.remote_addr

    # Check if the client has already submitted feedback recently
    if has_submitted_recently(client_ip):
        return render_template(
            'index_hot.html', 
            message="Thank you for training our AI, but you have already submitted feedback within the last hour.",
            img_url='/static/images/hot_person.jpg',
            title="Too Hot"
        )

    # Store the feedback if it hasn't been submitted recently
    store_feedback(client_ip, "too hot")
    return render_template(
        'index_hot.html', 
        message="Thank you for helping train our AI!",
        img_url='/static/images/hot_person.jpg',
        title="Too Hot"
    )

@app.route('/too-cold', methods=['GET'])
def too_cold():
    client_ip = request.remote_addr

    # Check if the client has already submitted feedback recently
    if has_submitted_recently(client_ip):
        return render_template(
            'index_cold.html', 
            message="Thank you for training our AI, but you have already submitted feedback within the last hour.",
            img_url='/static/images/cold_person.jpg',
            title="Too Cold"
        )

    # Store the feedback if it hasn't been submitted recently
    store_feedback(client_ip, "too cold")
    return render_template(
        'index_cold.html', 
        message="Thank you for helping train our AI!",
        img_url='/static/images/cold_person.jpg',
        title="Too Cold"
    )

@app.route('/feedback-log', methods=['GET'])
def feedback_log():
    """Route to retrieve the logged feedback data (for debugging or monitoring)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY timestamp DESC")
    feedback_entries = cursor.fetchall()
    conn.close()
    
    return jsonify(feedback_entries)

if __name__ == '__main__':
    init_db()  # Initialize the database and create the table if it doesn't exist
    app.run(debug=True, host='192.168.178.21', port=5000)
