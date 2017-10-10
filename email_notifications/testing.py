# coding: utf-8
from quickstart import get_credentials
import httplib2
from apiclient import discovery
cred = get_credentials()
http = cred.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)
users = service.users()
msgs = users.messages()
from email.mime.text import MIMEText
msg = MIMEText('This is a test')
msg['From'] = 'Test Python'
msg['To'] = 'test1@example.com, test2@example.com'
msg['Subject'] = 'Please stay calm, this is a test'
import base64
body={'raw':base64.urlsafe_b64encode(msg.as_bytes()).decode()}
msgs.send(userId='me', body=body).execute()
