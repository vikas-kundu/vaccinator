# Vaccinator
## _Hasta La Vista Corona_
Vaccinator is a python script to find open slots for vaccination in India based on pincode (or multiple pincodes) or state and district. This script will recheck after every few minutes and as soon the slots open, inform you via
- Beeping sound
- Desktop notification
- Email (optional)
- Telegram Bot (optional)

Since India has started the vaccination drive for those above 18 years of age, there is a heavy rush and slots get booked soon. This script will come in handy for finding those slots as soon as they open.

![Alt Text](https://github.com/vikas-kundu/vaccinator/blob/main/usage.gif)

## Features

- Search slots through multiple pincodes.
- -w or --wizard option for noobs.
- Recieve notifications through multiple channels.

## Tech
Vaccinator requires Python3 to work and contains only two modules outside the standard python libray which are as follows:
- plyer (2.0.0)
- requests (2.25.1)

The data is retrieved using the open public APIs at [API Setu](https://apisetu.gov.in/public/marketplace/api/cowin). It works on both Linux and Windows.

## Installation

Vaccinator requires Python3 and pip3 to run. To use the script, download it and install the dependencies using the following commands: 
```sh
git clone https://github.com/vikas-kundu/vaccinator
cd vaccinator
pip3 install -r requirements.txt
python3 vaccinator.py -h
```
## Updating:
```sh
cd vaccinator
git pull
```

## Usage 
#### Options:
#####  -h, --help
Show help message and exit.
#####  -p, --pincode 
Pincode(s) to look for slots.
#####  -a, --age
Age of the user(Default=18).
#####  -d, --date
Date from which to start looking(Format=DD-MM-YYYY).
#####  -w, --wizard
For calling using user friendly interface for beginners.
#####  -e, --email 
Email on which to notify when slots are available.
#####  -s, --state 
State in which to find open slots.
#####  -t, --district 
District of the state to find open slots.
#####  -i, --interval 
Interval in seconds after which to recheck the slots(Default=300) i.e. 5 minutes.
#####  --port 
Port of the SMTP server(Default=587)
#####  --smtp-server
SMTP Server address to use for sending email.
#####  --sender-email
Email of the sender to connect to SMTP server for sending email.
#####  --sender-pass 
Password of the sender to connect to SMTP server for sending email.
#####  --bot-token 
Token of the telegram bot to send messages.
#####  --bot-chatid
Chat id of the telegram bot to send messages.

#### Examples:
```sh
python3 vaccinator.py -p 110003 -d 09-05-2021
python3 vaccinator.py -s haryana -d sonipat
python3 vaccinator.py -p 110003 -a 24 -e user@example.com
python3 vaccinator.py -p 110003 -a 24 -e user@example.com --smtp-server smtp.gmail.com --sender-email username@gmail.com --sender-pass my_gmail_password
python3 vaccinator.py -w 
```

See usage examples for more info.
## License

MIT

**Free Software, Hell Yeah!**

