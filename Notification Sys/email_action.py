import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type


MSG = 'nice'
SUBJECT = 'sup'
EMAIL = 'ido@fusmobile.com'
CONTACT_LIST = ['ron@fusmobile.com', 'arik@fusmobile.com', 'brians@fusmobile.com', 'niv@fusmobile.com',
                'ericm@fusmobile.com', 'stephen@fusmobile.com']

SCOPES = ['https://mail.google.com/']


def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def build_message(destination, title, body, attachments=[]):
    if not attachments:
        message = MIMEText(body)
    else:
        message = MIMEMultipart()
        message.attach(MIMEText(body))
        for filename in attachments:
            add_attachment(message, filename)
    message['to'] = destination
    message['from'] = EMAIL
    message['subject'] = title
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}


def add_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    fp = open(filename, 'rb')
    if main_type == 'text':
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
    elif main_type == 'image':
        msg = MIMEImage(fp.read(), _subtype=sub_type)
    elif main_type == 'audio':
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
    else:
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
    fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)


def send_message(service, destination, obj, body, attachments=[]):
    msg = build_message(destination, obj, body, attachments)
    return service.users().messages().send(userId="me", body=msg).execute()


service = gmail_authenticate()
send_message(service, 'ericm@fusmobile.com', "This email was sent by FUSmobile notification system",
             "This is a test email with attachment", ['C:/Technion/empty.txt'])

