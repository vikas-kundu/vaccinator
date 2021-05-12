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
from plyer import notification

# Global vars
DEBUG = False
SENT_MAIL_QUEUE = set()
SENT_TELEGRAM_QUEUE = set()
PORT = 587

######### Util functions #########
def debug(data, name):
    if DEBUG:
        print(f"Data: {data}\nFunction name: {name}\n\n")

def error(err, err_type='normal'):
    if err_type == 'critical':
        print(f"Error: {err}")
        input('Press any key to exit...')
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

    parser.add_argument('-s', '--state', metavar='State', type=str, required=False, \
    help='Interval in seconds after which to recheck the slots(Default=300).')

    parser.add_argument('-t', '--district', metavar='District', type=str, required=False, \
    help='Interval in seconds after which to recheck the slots(Default=300).')

    parser.add_argument('--port', metavar='Port', type=int, required=False, default=PORT, \
    help=f'Port of the SMTP server(Default={PORT})')

    parser.add_argument('--smtp-server', metavar='Smtp Server', type=str, required=False,  \
    help=f'SMTP Server address to use for sending email.')

    parser.add_argument('--sender-email', metavar='Sender email', type=str, required=False,  \
    help=f'Email of the sender to connect to SMTP server for sending email.')

    parser.add_argument('--sender-pass', metavar='Sender pass', type=str, required=False,  \
    help=f'Password of the sender to connect to SMTP server for sending email.')

    parser.add_argument('--bot-token', metavar='Telegram bot token', type=str, required=False, \
    help=f'Token of the telegram bot to send messsages.')

    parser.add_argument('--bot-chatid', metavar='Telegram bot chatid', type=str, required=False, \
    help=f'Chat ID of the telegram bot to send messages.')

    args = vars(parser.parse_args())
    if not args['state'] and not args['pincode'] and not args['wizard']:
        error('Neither --pincode, nor --state with --district entered. So calling wizard...')
        args['wizard'] = True
    elif not re.search(r"\d{2}\-\d{2}\-\d{4}", args['date']):
        error(f"Date {args['date']} is not in DD-MM-YYYY format", 'critical')
    return args

def wizard():
    global SMTP_SERVER, PORT, SENDER_EMAIL, SENDER_PASS
    output = {'pincode': [], 'age': 18, 'date': date.today().strftime('%d-%m-%Y'), 'email': '', 'state': '', 'district': '', 'interval': 300, \
              'smtp_server': '', 'port': PORT, 'sender_email': '', 'sender_pass': '', 'bot_token': '', 'bot_chatid': ''}
    print('\nEnter the answer to following questions as asked. If you don\'t know any, skip it by pressing Enter, the default value will be used.\
    \nAlso, make sure to enter the email if you wish to be informed when slot is open!\n')

    output['pincode'] = str(input('Enter single or multiple picodes separated by space i.e. 1234 1235 1236 (Skip if wish to search by state and district):')).split(' ') or output['pincode']
    output['state'] = str(input('Enter state (skip if using pincode):')) or output['state']
    output['district'] = str(input('Enter district (skip if using pincode):')) or output['district']
    output['age'] = str(input('Enter user age i.e. 23 (Default=18):')) or output['age']
    output['date'] = str(input(f"Enter date in DD-MM-YYYY format i.e. 01-02-2021. It is advised to use default date so press Enter(Default={output['date']}):")) or output['date']
    output['email'] = str(input('Enter email address to send message when slots found:')) or output['email']
    output['interval'] = str(input('Enter interval in which to scan cowin website in seconds (Default=300):')) or output['interval']
    output['smtp_server'] = str(input(f'Enter the address of SMTP Server to use for sending emails:')) or output['smtp_server']
    output['port'] = str(input(f'Enter the port of SMTP server(Default={PORT}):')) or output['port']
    output['sender_email'] = str(input(f'Enter the email to connect to the SMTP Server for sending emails:')) or output['sender_email']
    output['sender_pass'] = str(input(f'Enter the password to connect to the SMTP Server for sending emails:')) or output['sender_pass']
    output['bot_token'] = str(input(f'Enter the Telegram bot token to send messages:')) or output['bot_token']
    output['bot_chatid'] = str(input(f'Enter the Telegram bot chat ID to send messages')) or output['bot_chatid']
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
        self.state = args['state']
        self.district = args['district']
        

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

    def search_by_state(self):
        hdrs={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
        did = state_id = 0
        res = district_data = ''
        states = { 'andaman and nicobar islands': 1, 'andhra pradesh': 2, 'arunachal pradesh': 3, 'assam': 4, 'bihar': 5, 'chandigarh': 6, 'chhattisgarh': 7, 'dadra and nagar haveli': 8, 'daman and diu': 37, 'delhi': 9, 'goa': 10, 'gujarat': 11, 'haryana': 12, 'himachal pradesh': 13, 'jammu and kashmir': 14, 'jharkhand': 15, 'karnataka': 16, 'kerala': 17, 'ladakh': 18, 'lakshadweep': 19, 'madhya pradesh': 20, 'maharashtra': 21, 'manipur': 22, 'meghalaya': 23, 'mizoram': 24, 'nagaland': 25, 'odisha': 26, 'puducherry': 27, 'punjab': 28, 'rajasthan': 29, 'sikkim': 30, 'tamil nadu': 31, 'telangana': 32, 'tripura': 33, 'uttar pradesh': 34, 'uttarakhand': 35, 'west bengal': 36 }
        try:
            state_id = states[self.state.lower()]
        except KeyError:
            error('State invalid')
            return ''

        fetch_districts_url = f"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
        try:
            res = r.get(fetch_districts_url, headers=hdrs)
        except Exception as e:
            error(f"Error while fetching district list\n{e}")
            return ''
        district_data = res.json()
        for district in district_data['districts']:
            if district['district_name'].lower() == self.district.lower():
                did = district['district_id']
        if did == 0:
            error('District not found!!')
            return ''
        statewise_url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={did}&date={self.date}"
        try:
            res = r.get(statewise_url, headers=hdrs)
        except Exception as e:
            error(f"Error while fetching statewise data\n{e}")
            return ''

        if res.status_code != 200:
            error('Response code not ok')
            return ''
        try:
            debug(json.dumps(res.json(), indent = 1), 'search_by_state')
        except Exception as e:
            error('JSON decode error')
        else:
            return self.detect(res.json())
        return ''

    def search_by_pin(self):
        hdrs={'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
        url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={self.pincode}&date={self.date}"
        try:
            res = r.get(url, headers=hdrs)
        except Exception as e:
            error(e)
        else:
            if res.status_code != 200:
                error('Response code not ok')
                return ''
            try:
                debug(json.dumps(res.json(), indent = 1), 'search_by_pin')
            except Exception as e:
                error('JSON decoder error')
            else:
                return self.detect(res.json())
        return ''

######## Class ends #############

######## Alert functions ########    
def desktop_notification(data):
    notification.notify(
        title = 'vaccinator Slots Found!',
        message = data,
        timeout = 10
        )

def send_email(args, data):
    global SENT_MAIL_QUEUE
    if not args['email']:
        error('No email found to send slot info')
        return ''
    if not args['smtp_server'] or not args['sender_email'] or not args['sender_pass']:
        error('Email options not set properly, cannot send mail')
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

def telegram_bot_sendtext(args, message):
    global SENT_TELEGRAM_QUEUE
    if not args['bot_token'] or not args['bot_chatid']:
        error('Telegram bot options not set properly, cannot send telegram message')
        return ''
    if message in SENT_TELEGRAM_QUEUE:
        error('This Telegram message is already sent so skipping it')
        return ''
    else:
        SENT_TELEGRAM_QUEUE.add(message)
    send_text = f"https://api.telegram.org/bot{args['bot_token']}/sendMessage?chat_id={args['bot_chatid']}&parse_mode=Markdown&text={message}"
    try:
        res = r.get(send_text)
    except Exception as e:
        error(f"Error while sending telegram message {e}")
    else:
        return res.json()

######## Alert functions end ########

def repeater(args):
    location_type = ''
    data = {}
    messages = ''
    run = vaccinator(args)
    if args['state']:
        location_type = f"State: {args['state']}, District: {args['district']}" 
        data = run.search_by_state()
    if args['pincode']:
        location_type = f"Pincode: {args['pincode']}"
        data = run.search_by_pin()

    if data == {args['pincode']:[]} or not data:
        print(f"No slots found for {location_type}")
        return ''
    sequence = 1
    for i in data[args['pincode']]:
        messages += f"\n{sequence}. Date: {i[1]}\n   Location: {i[0]}\n   Slots: {i[2]}"
        sequence += 1
    messages = f"***Available at {location_type}***{messages}"
    return messages

def main():
    # Parsing and settting options
    all_args = wizard() if parse()['wizard'] else parse()
    debug(all_args, 'main')
    
    counter = 1
    pins = all_args['pincode']
    # Infinite loop
    while True:
        print(f"\n[Time: {datetime.now().strftime('%H:%M:%S')}]  Try: [{counter}]")
        found = ''
        if pins:
            for pin in pins :
                all_args['pincode'] = pin # To send single pin instead of list
                found += repeater(all_args)
        else:
            found += repeater(all_args)

        if found: # Script will keep beeping while waiting if slots are found
            ############ All alerts #################
            print(found)
            telegram_bot_sendtext(all_args, found)
            if all_args['email']:
                send_email(all_args, found)
            print('Info: Slots have been found. Exit the program to stop the beeping sound')
            desktop_notification(f"Slots available at State: {all_args['state']} or Pincode: {all_args['pincode']}. Check terminal for detailed info.")
            for _ in range(1,int(all_args['interval'])):
                sys.stdout.write('\a')
                sys.stdout.flush()
                time.sleep(1)
            ############ All alerts end ################
        else:
            print(f"Info: Going to sleep for {int(all_args['interval'])/60} minutes till next try.")
            time.sleep(int(all_args['interval']))
        counter += 1
        
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nUser Aborted')
        sys.exit()
