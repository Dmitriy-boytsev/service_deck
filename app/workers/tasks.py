import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logging

from app.workers.celery_config import celery_app
from app.core.config import settings


smtp_server = settings.SMTP_SERVER
smtp_port = settings.SMTP_PORT
sender_email = settings.SMTP_EMAIL
sender_password = settings.SMTP_PASSWORD


@celery_app.task
def send_email(to_email: str, subject: str, body: str):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password) 
            server.sendmail(sender_email, to_email, message.as_string())
        logging.info(f"Email sent to {to_email}")
        return f"Email sent to {to_email}"
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return f"Failed to send email: {str(e)}"

@celery_app.task
def send_auto_reply(to_email: str):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = "Ваше обращение принято"
        body = "Спасибо за ваше обращение. Мы начали обработку вашего тикета. Ожидайте ответа."
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        logging.info(f"Auto-reply sent to {to_email}")
        return f"Auto-reply sent to {to_email}"
    except Exception as e:
        logging.error(f"Failed to send auto-reply: {str(e)}")
        return f"Failed to send auto-reply: {str(e)}"

@celery_app.task
def send_close_notification(to_email: str):
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to_email
        message["Subject"] = "Ваше обращение закрыто"
        body = "Ваше обращение успешно закрыто. Спасибо, что обратились к нам!"
        message.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        logging.info(f"Close notification sent to {to_email}")
        return f"Close notification sent to {to_email}"
    except Exception as e:
        logging.error(f"Failed to send close notification: {str(e)}")
        return f"Failed to send close notification: {str(e)}"
