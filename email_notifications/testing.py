# coding: utf-8
from quickstart import get_credentials
cred = get_credentials
http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)
import httplib2
from apiclient import discovery
http = cred.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)
users = service.users()
msgs = users.messages()
from email.mime.text import MIMEText
msg = MIMEText('This is a test')
msg['From'] = 'Test Python'
msg['To'] = 'raphael.a.dumas@gmail.com'
msg['Subject'] = 'Please stay calm, this is a test'
body={'raw':base64.urlsafe_b64encode(msg.as_bytes())}
msgs.send(userId='me', body=body).execute()
