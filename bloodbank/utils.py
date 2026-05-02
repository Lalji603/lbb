from django.core.mail import send_mail
from django.conf import settings
import logging
import ssl

# Bypass local SSL certificate verification issues common on Windows dev environments
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
    ssl.create_default_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)

import threading

def _send_email_thread(subject, message, valid_recipients):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=valid_recipients,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {valid_recipients}. Error: {e}")

def send_notification_email(subject, message, recipient_list):
    """
    Reusable utility function to send emails dynamically in the background.
    :param subject: string, subject of the email
    :param message: string, plain-text message of the email
    :param recipient_list: list of strings, email addresses to send to
    """
    if not recipient_list:
        logger.warning(f"No recipients provided for email: {subject}")
        return False
        
    valid_recipients = [email for email in recipient_list if email]
    if not valid_recipients:
        logger.warning(f"No valid email addresses found for email: {subject}")
        return False

    thread = threading.Thread(target=_send_email_thread, args=(subject, message, valid_recipients))
    thread.daemon = True
    thread.start()
    return True
