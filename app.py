from dotenv import load_dotenv
import logging
from flask import Flask, request, jsonify, send_file
from celery import Celery
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'amqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configure email settings
MAIL_SERVER = 'smtp-relay.brevo.com'
MAIL_PORT = 587
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

log_file = '/var/log/messaging_system.log'

# Ensure the log directory exists and has the appropriate permissions
log_dir = os.path.dirname(log_file)
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)
if not os.path.exists(log_file):
    open(log_file, 'a').close()
    os.chmod(log_file, 0o666)  # Set permissions to allow read and write

@celery.task
def send_email(recipient_email):
    msg = MIMEText('This is a test email.')
    msg['Subject'] = 'Test Email'
    msg['From'] = MAIL_USERNAME
    msg['To'] = recipient_email

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, recipient_email, msg.as_string())
    except Exception as e:
        app.logger.error(f'Error sending email: {str(e)}')

@celery.task
def log_time():
    with open(log_file, 'a') as f:
        f.write(f"Current time: {datetime.now()}\n")

@app.route('/api', methods=['GET'])
def handle_request():
    sendmail = request.args.get('sendmail')
    talktome = request.args.get('talktome')

    if sendmail:
        send_email.delay(sendmail)
        return jsonify({'status': 'Email is being sent.'})
    
    if talktome:
        log_time.delay()
        return jsonify({'status': 'Logged current time.'})
    
    return jsonify({'error': 'Invalid parameters.'})

@app.route('/logs', methods=['GET'])
def get_logs():
    if os.path.exists(log_file):
        return send_file(log_file, as_attachment=True)
    else:
        return jsonify({'error': 'Log file not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
