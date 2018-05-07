# coding: utf-8
"""Send a notification email from our gmail account

`

"""
import base64
from email.mime.text import MIMEText

import httplib2
from apiclient import discovery

from . import quickstart

CREDENTIALS = quickstart.get_credentials()
HTTP = CREDENTIALS.authorize(httplib2.Http())
SERVICE = discovery.build('gmail', 'v1', http=HTTP, cache_discovery=False)
MESSAGES = SERVICE.users().messages()


def send_mail(to, sender, subject, message):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message."""

    msg = MIMEText(message)
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    body = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    MESSAGES.send(userId='me', body=body).execute()
