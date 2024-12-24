

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import timedelta, datetime
from loguru import logger


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# import datetime
import time

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'pratapdangeti@gmail.com'
SENDER_PASSWORD = 'ogmw jsco ytaq jfuv'
RECIPIENT_EMAIL = 'pratapdangeti@gmail.com'



def send_email(subject, body):
    try:
        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Compose email message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print('Email notification sent successfully!')

        # Close connection
        server.quit()
    except Exception as e:
        print('Error sending email notification:', e)


def calc_index(symbl,_start):
    _index_dict = {'^NSEI':'Nifty','^GSPC':'SnP500','CL=F':'Curde_Oil',
                'GC=F':'Gold_Spot_Price','NG=F':'Natural_Gas',
                'SI=F':'Silver_Spot_Price','^N225':'Nikkei',
                '^FTSE':'FTSE','^DJI':'DJIA','^IXIC':'NASDAQ'}
    

    nifty_df = yf.download(symbl,start=_start)
    nifty_df = nifty_df.loc[:, [ ('Close', symbl),('Volume', symbl) ]]
    nifty_df.reset_index(inplace=True)
    nifty_df.columns=['Date',_index_dict[symbl],'Volume']

    nifty_df['ema_9_period'] = nifty_df[_index_dict[symbl]].ewm(span=9,adjust=False).mean()
    nifty_df['nifty_ema_diff'] = nifty_df[_index_dict[symbl]]-nifty_df['ema_9_period']
    nifty_df['indicator'] = np.nan

    for _i in range(1,len(nifty_df),1):
        _prev_sign = np.sign(nifty_df.loc[_i-1,'nifty_ema_diff'])
        _curr_sign = np.sign(nifty_df.loc[_i,'nifty_ema_diff'])

        if _prev_sign < 0 and _curr_sign > 0:
            nifty_df.loc[_i,'indicator']= 1.0
        elif _prev_sign > 0 and _curr_sign < 0:
            nifty_df.loc[_i,'indicator']= -1.0
    _latest_ind = float(nifty_df['indicator'].iloc[-1])

    
    _signal_ind = 'No Action'

    if (_latest_ind ==1):
        _signal_ind = 'Buy'

    elif (_latest_ind==-1):
        _signal_ind = 'Sell'
    else:
        print("no action")
    
    subject = 'Nifty :'+_signal_ind +' ,Notification: '+str(datetime.now())
    body = 'This is Nifty :'+ _signal_ind +' ,Notification. ' +str(datetime.now()) +' Have a great day!'
    send_email(subject, body)


def main():
    subject = 'Trading day start Notification: '+str(datetime.now())
    body = 'Trading day start notification. ' +str(datetime.now()) +' Have a great day!'
    send_email(subject, body)

    _symbol = '^NSEI'
    _start_date = '2023-01-01'

    _valid_days = ['Monday','Tuesday','Wednesday','Thursday','Friday']
    _cnt =0
    
    while True and (datetime.now().strftime("%A") in _valid_days):
        calc_index(symbl=_symbol,_start=_start_date)
        _cnt += 1
        if _cnt>2:
            break
        time.sleep(60)
    
    print("Completed")



if __name__ == '__main__':
    main()

datetime.now().strftime("%A")
