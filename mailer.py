#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

def send_targets(address):
    sender = 'assassins-umpire@srcf.ucam.org'
    msg = MIMEText('meep')
    msg['Subject'] = '[Assassins] Targets'
    msg['From'] = sender
    msg['To'] = address
    s = smtplib.SMTP()
    s.sendmail(sender, address, msg.as_string())
    s.quit()

send_targets('address')
