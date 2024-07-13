import logging
from flask import Flask, request, jsonify
from celery import Celery
from datetime import datetime
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'amqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'alexindevs@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbpr ywwq lfvc wgqp'

# Initialize Flask-Mail
mail = Mail(app)

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
    with app.app_context():
        msg = Message('Test Email', sender=app.config['MAIL_USERNAME'], recipients=[recipient_email])
        msg.body = 'This is a test email.'
        mail.send(msg)

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

if __name__ == '__main__':
    app.run(debug=True)
