import pyttsx3
import speedtest
import speech_recognition
import imaplib
import phonenumbers
from phonenumbers import carrier
import requests
import json
import pickle
import re

TTS = pyttsx3.init()
settings = {
    'name': '',
    'voice_volume': 1.0,
    'voice_rate': 160,
    'voice_enabled': False,
    'voice_accent': 0
}


#text to speech
def speak(txt):
    #changes voice/accent
    voice = TTS.getProperty('voices')[settings['voice_accent']].id
    TTS.setProperty('voice', voice)

    #sets volume
    TTS.setProperty('volume', settings['voice_volume'])

    #adjusts the speech rate
    TTS.setProperty('rate', settings['voice_rate'])

    #text to speech
    TTS.say(txt)
    TTS.runAndWait()


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

            speak("Did you say, " + txt)

    except speech_recognition.RequestError as e:
        output('Could not request results; {0}'.format(e))

    except speech_recognition.UnknownValueError:
        output('Unknown error occurred.')


#outputs text
def output(txt):
    print('\n' + txt)
    if settings['voice_enabled']:
        speak(txt)


#outputs response based on query
def process(query):
    #lists of text to identify query meaning
    farewell_list = {'bye', 'done', 'exit', 'quit', "q"}
    greeting_list = {'hello', 'hi'}
    name_list = {'set my name', 'change my name'}
    voice_toggle_list = {'enable voice', 'disable voice'}
    unread_email_list = {'my emails', 'my email', 'unread emails', 'unread email'}
    phone_carrier_list = {'phone provider', 'phone carrier'}

    #choose action based off input
    if farewell_list & query:
        output('Goodbye.')
        exit()
    elif greeting_list & query:
        intro()
    elif 'settings' in query:
        change_settings()
    elif name_list & query:
        change_name()
    elif 'voice volume' in query:
        change_voice_volume()
    elif 'voice rate' in query:
        change_voice_rate()
    elif 'voice rate' in query:
        change_voice_rate()
    elif voice_toggle_list & query:
        toggle_voice()
    elif 'voice accent' in query:
        change_voice_accent()
    elif 'internet speed' in query:
        internet_speed()
    elif 'download speed' in query:
        download_speed()
    elif 'upload speed' in query:
        upload_speed()
    elif unread_email_list & query:
        check_email()
    elif phone_carrier_list & query:
        phone_number_info()
    else:
        output('Sorry, I don\'t understand.')


#load previous settings from file
def load_settings():
    global settings

    try:
        with open('settings.pkl', 'rb') as f:
            settings = pickle.load(f)
    except FileNotFoundError:
        with open('settings.pkl', 'wb') as f:
            pickle.dump(settings, f)


#change general assistant settings
def change_settings():
    while True:
        choice = str(input('\nWhat would you like to change?\n'
                           '(1) Your name\n'
                           '(2) Voice volume\n'
                           '(3) Speech rate\n'
                           '(4) Voice enabled\n'
                           '(5) Change voice accent\n'
                           '(6) Reset default settings\n\n'
                           '>>> ')).strip().lower()
        if choice not in ['1', '2', '3', '4', '5', '6'
                          'your name', 'voice volume', 'voice rate', 'speech rate', 'voice enabled', 'voice accent',
                          'name', 'volume', 'rate', 'accent', 'reset', 'default']:
            output("Please choose a valid option...")
        else:
            break

    if choice in ['1', 'your name', 'name']:
        change_name()
    elif choice in ['2', 'voice volume', 'volume']:
        change_voice_volume()
    elif choice in ['3', 'voice rate', 'rate']:
        change_voice_rate()
    elif choice in ['4', 'voice enabled', 'enable', 'disable']:
        toggle_voice()
    elif choice in ['5', 'voice_accent', 'accent']:
        change_voice_accent()
    elif choice in ['6', 'reset', 'default']:
        default_settings()


#change name of user
def change_name():
    global settings

    settings['name'] = str(input("\nYour name: ")).strip()
    output(f"Hi {settings['name']}. Nice to meet you.")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#change volume of assistant
def change_voice_volume():
    global settings

    output(f"The current volume is {int(settings['voice_volume'] * 100)}%.")
    ans = str(input("\nNew volume: ")).strip()
    if '%' in ans:
        ans = ans.replace('%', '')
    settings['voice_volume'] = float(ans) / 100
    output(f"Volume set to {int(settings['voice_volume'] * 100)}%.")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#change voice rate of assistant
def change_voice_rate():
    global settings

    output(f"The current speech rate is {int(settings['voice_rate'])}.")
    settings['voice_rate'] = float(input("\nNew rate: "))
    output(f"Rate set to {int(settings['voice_rate'])}.")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#enable/disable voice
def toggle_voice():
    global settings

    if settings['voice_enabled'] is False:
        output('My voice is currently disabled, would you like to enable it?\n')
        ans = str(input('>>> ')).lower().strip()
        if ans in ['y', 'yes', 'enable']:
            settings['voice_enabled'] = True
            with open('settings.pkl', 'wb') as f:
                pickle.dump(settings, f)
    else:
        output('My voice is currently enabled, would you like to disable it?\n')
        ans = str(input('>>> ')).lower().strip()
        if ans in ['y', 'yes', 'disable']:
            settings['voice_enabled'] = False
            with open('settings.pkl', 'wb') as f:
                pickle.dump(settings, f)

    if settings['voice_enabled'] is False:
        output('Voice disabled.')
    else:
        output('Voice enabled')


#change voice accent
def change_voice_accent():
    global settings

    voices = TTS.getProperty('voices')
    output(f"Your current voice is {voices[settings['voice_accent']].name}.\n\n"
           f"Your choices to choose from are:")
    for i in range(len(voices)):
        print(f"({i + 1}) {voices[i].name}")

    settings['voice_accent'] = int(input('\n>>> ')) - 1
    output(f"Voice set to {voices[settings['voice_accent']].name}.")
    with open('settings.pkl', 'wb') as f:
        pickle.dump(settings, f)


#reset all settings to default
def default_settings():
    global settings

    output('Are you sure you want to clear your settings?\n')
    ans = str(input('>>> '))
    if ans in ['y', 'yes']:
        settings['name'] = ''
        settings['voice_volume'] = 1.0
        settings['voice_rate'] = 160
        settings['voice_enabled'] = False
        settings['voice_accent'] = 0
        output('Default settings set.')
        with open('settings.pkl', 'wb') as f:
            pickle.dump(settings, f)


# opening message
def intro():
    if settings['name'] == '':
        output('Hello. How can I help you?')
    else:
        output(f"Hi {settings['name']}. How can I help you?")


#introduction message and gets name of user
def init_name():
    global settings

    print('My name is Concordia, your virtual assistant. What should I call you?\n')
    settings['name'] = str(input("Your name: ")).strip()
    print(f"\nHi {settings['name']}. How can I help you today?\n")
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


def main():
    load_settings()
    if settings['name'] == '':
        init_name()
    while True:
        query = str(input('>>> ')).strip().lower()
        process(set(query.split()))
        print()


if __name__ == '__main__':
    main()
