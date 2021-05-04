print(r"""
                       ______
                     <((((((\\\
                     /      . }\
                     ;--..--._|}
  (\                 '--/\--'  )
   \\                | '-'  :'|
    \\               . -==- .-|
     \\               \.__.'   \--._
     [\\          __.--|       //  _/'--.
     \ \\       .'-._ ('-----'/ __/      \
      \ \\     /   __>|      | '--.       |
       \ \\   |   \   |     /    /       /
        \ '\ /     \  |     |  _/       /
         \  \       \ |     | /        /
          \  \      \        /
 __      __     _____ _____ _____ _   _       _______ ____  _____  
 \ \    / /\   / ____/ ____|_   _| \ | |   /\|__   __/ __ \|  __ \ 
  \ \  / /  \ | |   | |      | | |  \| |  /  \  | | | |  | | |__) |
   \ \/ / /\ \| |   | |      | | | . ` | / /\ \ | | | |  | |  _  / 
    \  / ____ \ |___| |____ _| |_| |\  |/ ____ \| | | |__| | | \ \ 
     \/_/    \_\_____\_____|_____|_| \_/_/    \_\_|  \____/|_|  \_\
                                                                   
                                           Hasta La Vista Corona...

""")

import smtplib
import ssl
import sys
import re
import time
import json
import argparse
from datetime import date
from datetime import datetime

# Not part of standard lib
import requests as r
from pynotifier import Notification

# Global vars
DEBUG = False
SENT_MAIL_QUEUE = set()
SMTP_SERVER = 'danwin1210.me'
PORT = 587
SENDER_EMAIL = 'cowininfo-2021@danwin1210.me'
SENDER_PASS = 'cowininfo-2021'

######### Util functions #########
def debug(data, name):
    if DEBUG:
        print(f"Data: {data}\nFunction name: {name}\n\n")

def error(err, err_type='normal'):
    if err_type == 'critical':
        print(f"Error: {err}\nExiting the program...")
        sys.exit()
    else:
        print(f"Error: {err}")
######### Util functions end #########

######### User input parsing functions #########
def parse():
    global SMTP_SERVER, PORT, SENDER_EMAIL, SENDER_PASS
    parser = argparse.ArgumentParser(prog='vaccinator')

    parser.add_argument('-p', '--pincode', metavar='Pincode1 Pincode2', type=int, nargs='*', required=False, \
    help='Pincode(s) to look for slots.')

    parser.add_argument('-a', '--age', metavar='Age', type=int, required=False, default=18, \
    help='Age of the user(Default=18).')

    parser.add_argument('-d', '--date', metavar='Date', type=str, required=False, default=date.today().strftime('%d-%m-%Y'), \
    help='Date from which to start looking(Format=DD-MM-YYYY).')

    parser.add_argument('-w', '--wizard', metavar='Wizard', type=bool, nargs='?', required=False, const=True, default=False, \
    help='For using user friendly interface')

    parser.add_argument('-e', '--email', metavar='Email', type=str, required=False, \
    help='Email on which to notify when slots are available')

    parser.add_argument('-i', '--interval', metavar='Interval', type=int, required=False, default=300, \
    help='Interval in seconds after which to recheck the slots(Default=300).')

    parser.add_argument('--port', metavar='Port', type=int, required=False, default=PORT, \
    help=f'Port of the SMTP server(Default={PORT})')

    parser.add_argument('--smtp-server', metavar='Smtp Server', type=str, required=False, default=SMTP_SERVER, \
    help=f'SMTP Server address to use for sending email.(Default={SMTP_SERVER}) !Avoid using default due to security issues!')

    parser.add_argument('--sender-email', metavar='Sender email', type=str, required=False, default=SENDER_EMAIL, \
    help=f'Email of the sender to connect to SMTP server for sending email(Default={SENDER_EMAIL}) !Avoid using default due to security issues!')

    parser.add_argument('--sender-pass', metavar='Sender pass', type=str, required=False, default=SENDER_PASS, \
    help=f'Password of the sender to connect to SMTP server for sending email(Default={SENDER_PASS}) !Avoid using default due to security issues!')

    args = vars(parser.parse_args())
    if not args['pincode'] and not args['wizard']:
        error('Select either --pincode with value or use --wizard', 'critical')
    elif not re.search(r"\d{2}\-\d{2}\-\d{4}", args['date']):
        error(f"Date {args['date']} is not in DD-MM-YYYY format", 'critical')
    return args

def wizard():
    global SMTP_SERVER, PORT, SENDER_EMAIL, SENDER_PASS
    output = {'pincode': [], 'age': 18, 'date': date.today().strftime('%d-%m-%Y'), 'email': '', 'interval': 300, 'smtp_server': SMTP_SERVER, 'port': PORT, 'sender_email': SENDER_EMAIL, 'sender_pass': SENDER_PASS}
    print('\nEnter the answer to following questions as asked. If you don\'t know any, skip it, the default value will be used.\
    \nHowever, don\'t skip the pincode which is crucial. Also, make sure to enter the email if you wish to be informed when slot is open!\n')
    
    output['pincode'] = str(input('Enter single or multiple picodes separated by space i.e. 1234 1235 1236:')).split(' ') or output['pincode']
    output['age'] = str(input('Enter user age i.e. 23 (Default=18):')) or output['age']
    output['date'] = str(input(f"Enter date in DD-MM-YYYY format i.e. 01-02-2021 (Default={output['date']}):")) or output['date']
    output['email'] = str(input('Enter email address to send message when slots found:')) or output['email']
    output['interval'] = str(input('Enter interval in which to scan in seconds (Default=300):')) or output['interval']
    output['smtp_server'] = str(input(f'Enter the address of SMTP Server to use for sending emails(Default={SMTP_SERVER}) !Avoid using default due to security issues!:')) or output['smtp_server']
    output['port'] = str(input(f'Enter the port of SMTP server(Default={PORT}):')) or output['port']
    output['sender_email'] = str(input(f'Enter the email to connect to the SMTP Server for sending emails(Default={SENDER_EMAIL}) !Avoid using default due to security issues!:')) or output['sender_email']
    output['sender_pass'] = str(input(f'Enter the password to connect to the SMTP Server for sending emails(Default={SENDER_PASS}) !Avoid using default due to security issues!:')) or output['sender_pass']
    
    if not re.search(r"\d{2}\-\d{2}\-\d{4}", output['date']):
        error(f"Date {output['date']} is not in DD-MM-YYYY format", 'critical')
    return output
######### User input parsing functions end #########

######## Class starts #############
class vaccinator:

    def __init__(self, args):
        self.pincode = args['pincode']
        self.age = int(args['age'])
        self.date = args['date']

    def detect(self, data):
        output = {self.pincode: []}
        if 'error' in data.keys():
            error(data['error'])
            return output
        if data == {'centers': []} or data == {'sessions': []}:
            return output
        for center in data['centers']:
            for session in center['sessions']:
                if session['min_age_limit'] <= self.age and session['available_capacity'] > 0:
                    output[self.pincode].append([f"{center['name']}, {center['block_name']}, {center['district_name']}, {center['state_name']}, {center['pincode']}",\
                                                   session['date'], session['slots']])
        debug(output, 'detect')
        return output

    def search_by_state():
        # Will add in future
        pass

    def search_by_pin(self):
        url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={self.pincode}&date={self.date}"
        try:
            res = r.get(url)
        except Exception as e:
            error(e)
        else:
            debug(json.dumps(res.json(), indent = 1), 'search_by_pin')
            return self.detect(res.json())

######## Class ends #############

######## Alert functions ########    
def notification(data):
    Notification(
        title='vaccinator Slots Found!',
    	description=data,
    	duration=3,                              # Duration in seconds
    	urgency='normal'
    ).send()
    time.sleep(4) # Sleeping to avoid toast errors caused by continous calling before earlier request is over

def send_email(args, data):
    global SENT_MAIL_QUEUE
    if not args['email']:
        error('No email found to send slot info')
        return ''
    if data in SENT_MAIL_QUEUE:
        error('Email already sent so skipping it')
        return ''
    else:
        SENT_MAIL_QUEUE.add(data)
    message = f"""\
Subject: Some slots have opened up which are as follows:
{data}

******This message was sent by vaccinator script*****"""
    smtp_server = args['smtp_server']
    port = int(args['port'])
    sender_email = args['sender_email'] 
    password = args['sender_pass']
    email = args['email']
    context = ssl.create_default_context()
    
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.starttls(context=context) # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message)
        print('Info: Email sent')
        server.quit()
    except Exception as e:
        error(f"{e}\nUnable to send email.")
        server.quit()
######## Alert functions end ########


def repeater(args):
    search_args = dict(list(args.items())[:3])
    data = {}
    messages = ''
    run = vaccinator(search_args)
    data = run.search_by_pin()
    if data == {args['pincode']:[]} or not data:
        print(f"No slots found for pincode {args['pincode']}")
        return ''

    sequence = 1
    for i in data[args['pincode']]:
        messages += f"\n{sequence}. Date: {i[1]}\n   Location: {i[0]}\n   Slots: {i[2]}"
        sequence += 1
    messages = f"***Available at Pincode: {args['pincode']}***{messages}"
    if messages:
        print(messages)
        notification(f"{sequence-1} slots available at Pincode: {args['pincode']}. Check terminal for detailed info.")
        if args['email']:
            send_email(args, messages)
    return messages

def main():
    # Parsing and settting options
    all_args = wizard() if parse()['wizard'] else parse()
    debug(all_args, 'main')
    
    # Infinite loop
    counter = 1
    pins = all_args['pincode']
    found = ''
    while True:
        print(f"\n[Time: {datetime.now().strftime('%H:%M:%S')}]============================ Try: {counter} =========================")
        for pin in pins :
            all_args['pincode'] = pin # To send single pin instead of list
            found += repeater(all_args)
        print(f"[Time: {datetime.now().strftime('%H:%M:%S')}]==============================================================\n")

        if found: # Script will keep beeping while waiting if slots are found
            print('Info: Slots have been found. Exit the program to stop the beeping sound')
            for _ in range(1,int(all_args['interval'])):
                sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(1)
        else:
            print(f"Info: Going to sleep for {int(all_args['interval'])/60} minutes till next try.")
            time.sleep(int(all_args['interval']))
        counter += 1
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        error('User aborted!', 'critical')
