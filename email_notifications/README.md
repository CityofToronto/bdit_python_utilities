# Email Notifier

For when you need scripts to send someone an email instead of merely logging what happens. This library uses Google's Gmail API to send someone an email. Note that the Gmail API does not work behind the corporate firewall.

A virtual environment is required to run the package if the script is on the EC2.

## Set up

1. Install this submodule with `pipenv install -e 'git+https://github.com/CityofToronto/bdit_python_utilities.git#egg=email_notifications&subdirectory=email_notifications'`
2. Run `pipenv run python -m quickstart` to create secrets local to your account/machine.`client_secret.json` must be a pre-existing file in the same directory as the script and must be named `client_secret.json`. Because we could only run this on our server, we're sending the `noauth_local_webserver` flag through `oauth2client.tools.argparser.parse_args()`.
3. The command-line will print a URL that you have to visit in a web browser where you can sign into your gmail account to authorize this application. Copy the resulting authorization code and paste it into the command-line when prompted. Your validated API credentials should now be stored in `~/.credentials/gmail-python-quickstart.json`.
4. Add the following to import the `send_mail` package to the code
```python
from notify_email import send_mail
``` 

### `client_secret.json` 

The general format of the file is this: 

```json
{
    "installed": 
    {"client_id":"_______",
        "project_id":"________",
        "auth_uri":"https://accounts.google.com/o/oauth2/auth",
        "token_uri":"https://www.googleapis.com/oauth2/v3/token",
        "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":"__________",
        "redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]
    }
}
```
For the blank entries, ask the other people on the team.

## Running the Package

It's recommended that you store the destination email in a configuration file.

For example, write out a text file named config.cfg with the following
```
[EMAIL]
to=email@email.com
from=email@email.com
subject=Email Subject
```
Since the email is being sent from the already authorized email, this field is not important and any emails sent will not use the email in the `from` field. However, the `from` field should still be filled.
Then, declare a dictionary to store all of the email variables/keys
```python
    CONFIG = configparser.ConfigParser()
    CONFIG.read(config.cfg)
    email=CONFIG['EMAIL']
```

To send emails, write out this line in your code.
```
send_mail(email['to'], email['from'], 'Subject,  'text for your email in string format')      
```
The third argument is the subject of the email, and the fourth argument is the body of the email. It is also possible to set the subject in the configuration file and replace that argument in the script with `email['subject']`.
