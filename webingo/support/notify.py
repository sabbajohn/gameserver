import os
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from webingo.support import logger
import json

class Notify():
    def __init__(self,*args, **kwargs):
        path = os.path.abspath("./webingo/support")
        aws_config = path + "/" +"aws_ses_config.json"
        if not os.path.exists(aws_config):
            raise FileNotFoundError(f'File aws_ses_config.json not found at {path}')
        else:
            with open(aws_config, "r") as c:
                data = str(c.read())
        try:
            config = json.loads(data)
        except Exception as e:
            raise AttributeError("Probably not a valid json file!")
        self.__dict__.update(config)
        if not "sender" in config or not self.sender:
            raise AttributeError("Invalid definition for 'sender' in {}".format(aws_config))
        if not "sendername" in config or not self.sendername:
            raise AttributeError("Invalid definition for 'sendername' in {}".format(aws_config))
        if not "username_smtp" in config or not self.username_smtp:
            raise AttributeError("Invalid definition for 'username_smtp' in {}".format(aws_config))
        if not "password_smtp" in config or not self.password_smtp:
            raise AttributeError("Invalid definition for 'password_smtp' in {}".format(aws_config))
        if not "host" in config or not self.host:
            raise AttributeError("Invalid definition for 'host' in {}".format(aws_config))
        if not "port" in config or not self.port:
            raise AttributeError("Invalid definition for 'port' in {}".format(aws_config))
        self.msg = MIMEMultipart('alternative')
        self.msg['Subject'] = kwargs.get('Subject')
        self.msg['From']    = email.utils.formataddr((self.sendername, self.sender))
        self.To             = kwargs.get('To')
        if type(self.To) != list:
            self.msg['To']      = kwargs.get('To')
        body_html = kwargs.get('body_html') if kwargs.get('body_html') != None else "" 
        body_text = kwargs.get('body_text') if kwargs.get('body_text') != None else "" 
        part1 = MIMEText(body_text, 'plain')
        part2 = MIMEText(body_html, 'html')
        self.msg.attach(part1)
        self.msg.attach(part2)


    # def setEmail(self, **kwargs):
    #     # self.__dict__.update(kwargs)
    #     # kwargs.get('field')
    #     self.msg['Subject'] = get.kwargs['Subject']
    #     self.msg['From']    = email.utils.formataddr((self.sendername, self.sender))
    #     self.msg['To']      = get.kwargs['To']
    #     part1 = MIMEText(kwargs['body_text'], 'plain')
    #     part2 = MIMEText(kwargs['body_html'], 'html')
    #     self.msg.attach(part1)
    #     self.msg.attach(part2)


    def sendEmail(self):
        try:
            server = smtplib.SMTP(self.host, self.port)
            server.ehlo()
            server.starttls()
            #stmplib docs recommend calling ehlo() before & after starttls()
            server.ehlo()
            server.login(self.username_smtp, self.password_smtp)
            server.sendmail(self.sender, self.To, self.msg.as_string())
            server.close()
            # Display an error message if something goes wrong.
        except Exception as e:
            raise Exception(e)