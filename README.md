# Messaging System Setup Guide

This guide will walk you through setting up a messaging system that sends emails and logs time using RabbitMQ, Celery, Flask, and Nginx, with port exposure using ngrok.

## Prerequisites

- Python 3.10+
- pip
- RabbitMQ
- Nginx
- ngrok
- Git

## Clone the Repository

First, clone the repository to your local machine:

```sh
git clone https://github.com/alexindevs/HNG11_DevOps_Stage3.git
cd messaging-system
```

## Set Up Python Environment and Install Dependencies

Create a virtual environment and install the necessary Python dependencies:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```text
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

## Set Up RabbitMQ

Install RabbitMQ and start the RabbitMQ server:

```sh
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

## Configure Celery

Celery is already configured in the `app.py` file. Here is a brief look at the configuration:

```python
app.config['CELERY_BROKER_URL'] = 'amqp://guest@localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
```

## Configure Nginx

Create an Nginx configuration file for your application:

```sh
sudo nano /etc/nginx/sites-available/messaging-system
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and restart Nginx:

```sh
sudo ln -s /etc/nginx/sites-available/messaging-system /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## Expose the Port with ngrok

Install ngrok if you haven't already:

```sh
sudo snap install ngrok
```

Run ngrok to expose port 5000:

```sh
nohup ngrok http --domain=your-subdomain.ngrok-free.app 5000 &
```

## Running the Application

Start the Flask application:

```sh
source venv/bin/activate
python app.py
```

Start the Celery worker:

```sh
source venv/bin/activate
celery -A app.celery worker --loglevel=info
```

## Testing the Application

To test the email sending and time logging functionalities, you can use the following endpoints:

1. **Send Email**: Visit `http://your-domain.com/api?sendmail=recipient@example.com` to send an email.
2. **Log Time**: Visit `http://your-domain.com/api?talktome` to log the current time.

You can also download the logs:

1. **Get Logs**: Visit `http://your-domain.com/logs` to download the log file.

## Conclusion

You have successfully set up a messaging system using RabbitMQ, Celery, Flask, Nginx, and ngrok. This system can send emails, log time, and expose the service to the internet via ngrok. Happy coding!
