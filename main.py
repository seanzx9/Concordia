import pyttsx3
import speedtest
import speech_recognition
import imaplib
import phonenumbers
from phonenumbers import carrier
import requests
import json
import pickle

settings = {
    'name': '',
    'voice_volume': 1.0,
    'voice_rate': 160,
    'voice_enabled': False
}


#outputs response based on query
def process(query):
    greeting_list = ['hello', 'hi', 'yo']
    farewell_list = ['bye', 'done', 'exit']
    name_list = ['set name', 'my name', 'change name']
    email_list = ['my emails', 'my email', 'unread emails', 'unread email']

    if any(word in query for word in farewell_list):
        output('Goodbye.')
        exit()
    elif any(word in query for word in greeting_list):
        intro()
    elif 'settings' in query:
        change_settings()
    elif any(word in query for word in name_list):
        change_name()
    elif 'internet speed' in query:
        internet_speed()
    elif 'download speed' in query:
        download_speed()
    elif 'upload speed' in query:
        upload_speed()
    elif any(word in query for word in email_list):
        check_email()
    elif 'phone' in query:
        phone_number_info()
    else:
        output('Sorry, I don\'t understand.')


#modified text to speech
def say(txt):
    tts = pyttsx3.init()

    #changes voice/accent
    voice = tts.getProperty('voices')[1]
    tts.setProperty('voice', voice.id)

    #sets volume
    tts.setProperty('volume', settings['voice_volume'])

    #adjusts the speech rate
    tts.setProperty('rate', settings['voice_rate'])

    #text to speech
    tts.say(txt)
    tts.runAndWait()


#speech to text
def listen():
    try:
        r = speech_recognition.Recognizer()

        with speech_recognition.Microphone() as source:
            r.adjust_for_ambient_noise(source, 1)

            output('Speak now...')
            # listens for the user's input
            audio = r.listen(source)

            # Using google to recognize audio
            txt = r.recognize_google(audio).lower()

            say("Did you say, " + txt)

    except speech_recognition.RequestError as e:
        output('Could not request results; {0}'.format(e))

    except speech_recognition.UnknownValueError:
        output('Unknown error occurred.')


#outputs text
def output(txt):
    print('\n' + txt)
    if settings['voice_enabled']:
        say(txt)


#opening message
def intro():
    if settings['name'] == '':
        output('Hello. How can I help you?')
    else:
        output(f"Hi {settings['name']}. How can I help you?")


#change general assistant settings
def change_settings():
    while True:
        choice = str(input('\nWhat would you like to change?\n'
                           '(1) Your name\n'
                           '(2) Voice volume\n'
                           '(3) Voice rate\n'
                           '(4) Voice enabled\n\n'
                           '>>>')).strip().lower()
        if choice not in ['1', '2', '3', '4',
                          'your name', 'voice volume', 'voice rate', 'voice enabled',
                          'name', 'volume', 'rate']:
            output("Please choose a valid option...\n")
        else:
            break

    if choice in ['1', 'your name', 'name']:
        change_name()
    elif choice in ['2', 'voice volume', 'volume']:
        pass
    elif choice in ['3', 'voice rate', 'rate']:
        pass
    elif choice in ['4', 'voice enabled', 'enable', 'disable']:
        pass


#change name of user
def change_name():
    global settings

    settings['name'] = str(input("\nYour name: ")).strip()
    output(f"Hi {settings['name']}. Nice to meet you.")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#change the voice volume
def change_volume():
    global settings


#change the voice rate
def change_rate():
    global settings


#toggle voice on or off
def toggle_voice():
    global settings


#introduction message and gets name of user
def init_name():
    global settings

    print('My name is Concordia, your virtual assistant. What should I call you?')
    settings['name'] = str(input("Your name: ")).strip()
    print(f"Hi {settings['name']}. How can I help you today?\n")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#finds download and upload speed
def internet_speed():
    st = speedtest.Speedtest()
    output('Please give me a moment to calculate...')
    st.get_best_server()
    output(f"Your download speed is about{st.download() / 1048576: .0f} Mbps, "
           f"and your upload speed is about{st.upload() / 1048576: .0f} Mbps.")


#finds download speed using best server
def download_speed():
    st = speedtest.Speedtest()
    output('Please give me a moment to calculate...')
    st.get_best_server()
    output(f"Your download speed is about{st.download() / 1048576: .0f} Mbps.")


#finds upload speed using best server
def upload_speed():
    st = speedtest.Speedtest()
    output('Please give me a moment to calculate...')
    st.get_best_server()
    output(f"Your upload speed is about{st.upload() / 1048576: .0f} Mbps.")


#checks amount of unread emails
def check_email():
    obj = imaplib.IMAP4_SSL('imap.gmail.com', 993)

    try:
        email = str(input('\nPlease enter your email: ')).strip()
        email_password = str(input('Please enter your password: ')).strip()
        obj.login(email, email_password)
    except:
        output('Login failed. Make sure you enter your correct credentials or allow read permissions for this app.')
        return

    obj.select()
    num_emails = len(obj.search(None, 'UnSeen')[1][0].split())
    if num_emails > 0:
        output(f"You have {num_emails} unread emails." if num_emails > 1 else f"You have {num_emails} unread email.")
    else:
        output('You have no unread emails.')


#gets phone provider
def phone_number_info():
    number = '+' + str(input("\nEnter number with country code: ")).strip()
    if '+1' in number:
        number = number.replace('+1', '')
        url = 'https://api.telnyx.com/v1/phone_number/1' + number
        html = requests.get(url).text
        data = json.loads(html)
        data = data["carrier"]
        provider = data["name"]
        parsed_num = phonenumbers.parse(number, 'US')
        output(f"Number: {phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.NATIONAL)}\n"
               f"Provider: {provider}")
    else:
        try:
            parsed_num = phonenumbers.parse(number)
            provider = carrier.name_for_number(parsed_num, "en")
            output(f"Number: {phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
                   f"Provider: {provider}")
        except:
            output('Invalid number.')
            print(number)


#load previous settings from file
def load_settings():
    global settings

    try:
        with open('settings.pkl', 'rb') as f:
            settings = pickle.load(f)
    except FileNotFoundError:
        with open('settings.pkl', 'wb') as f:
            pickle.dump(settings, f)


def main():
    load_settings()
    if settings['name'] == '':
        init_name()
    while True:
        query = str(input('>>> ')).strip().lower()
        process(query)
        print()


if __name__ == '__main__':
    main()
