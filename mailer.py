#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

class Mailer(object):
    def __init__(self, crsid, pwd, host):
        self.crsid = crsid
        self.pwd = pwd
        self.host = host
        self.sender = 'assassins-umpire@srcf.ucam.org'
    
    def send_message(self, address):
        msg = MIMEText('meep')
        msg['Subject'] = '[Assassins] Targets'
        msg['From'] = self.sender
        msg['To'] = address
        s = smtplib.SMTP(self.host, port=587)
        s.starttls()
        s.login(self.crsid, self.pwd)
        s.sendmail(self.sender, address, msg.as_string())
        s.quit()

    send_message('fake@address.org')
