# Email Notifier

For when you need scripts to send someone an email instead of merely logging what happens. This library uses Google's Gmail API to send someone an email. Note that the Gmail API does not work behind the corporate firewall.

## Set up

1. Install this submodule with `pipenv install -e 'git+https://github.com/CityofToronto/bdit_python_utilities.git#egg=email_notifications&subdirectory=email_notifications'`
2. Run `python -m quickstart` to create secrets local to your account/machine, your `client_secret.json` must be in the same folder and it must be named that. Because we could only run this on our server we're sending the `noauth_local_webserver` flag through `oauth2client.tools.argparser.parse_args()`.
3. The command-line will print a URL that you have to visit in a web browser where you can sign into your gmail account to authorize this application. Copy the code and paste it into the command-line. Your validated API credentials should now be stored in `~/.credentials/gmail-python-quickstart.json`.
4. Add `from email_notifications import send_mail` to import the `sendmail` function into your code.

