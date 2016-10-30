#!/usr/bin/env python
import getpass
import smtplib
from email.mime.text import MIMEText

class Mailer(object):
    def __init__(self, host):
        self.host = host
        self.sender = 'assassins-umpire@srcf.ucam.org'

    def send_message(self, address):
        msg = MIMEText('meep')
        msg['Subject'] = '[Assassins] Targets'
        msg['From'] = self.sender
        msg['To'] = address
        s = smtplib.SMTP(self.host, port=587)
        s.starttls()
        crsid = raw_input('Enter CRSID (excluding @cam section): ')
        pwd = getpass.getpass('Enter Hermes password for {} (password will not be visible when typed): '.format(crsid))
        s.login(crsid, pwd)
        s.sendmail(self.sender, address, msg.as_string())
        s.quit()



    
