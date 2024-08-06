from flask import Flask, request
from functions import send_message, fetch_message
from flask import Flask, request
from functions import generate_subtitles, generate_image, generate_titles,generate_ctas
import time
import requests
import os
from requests.auth import HTTPBasicAuth
import re
import json

app = Flask(__name__)

user_no = 'whatsapp:'
ai_no = 'whatsapp:'
file_path = 'data.json'



    
@app.route('/')
def home():
    return 'All is well...'


@app.route('/twilio/receiveMessage', methods=['POST', 'GET'])

def receiveMessage():

    try:
        # Extract incoming parameters from Twilio
        message = request.form['Body']
        sender_id = request.form['From']
        msg_sid = request.form['MessageSid']
        media_url = request.form.get('MediaUrl0')
        
        session_data = load_user_session() or {}
        

        # fetching the sid list
        with open("sids.txt", "r") as text_file:
            sids = text_file.readlines()

        if 'status' not in session_data:
             session_data['status'] = 'awaiting_campaign_info'
             text = """
                    Hi, I am your personal assistant. Please Enter your business description
                """
             save_session(session_data)
             send_message(sender_id, text)
             
        elif session_data['status'] == 'awaiting_campaign_info':
            generate_titles(campaign_info=message)
            data = load_data_session()
            session_data['selected_campaign_info'] = message
            titles = data.get('titles', {}) # Returns an empty dict if 'titles' doesn't exist   
            formatted_titles = "\n".join([f"{option}  - {title}" for option,title in titles.items()])
            print(formatted_titles)
            text = f"Great! Now let's have some options for the title of your business.\nHere are three Options for Title:\n{formatted_titles}\n\n\n Please Enter the option you like the most e.g: Option 1"

            session_data['status'] = 'awaiting_title'
            save_session(session_data)
            send_message(sender_id, text)
        
        elif session_data['status'] == 'awaiting_title':
            generate_subtitles(campaign_info=session_data['selected_campaign_info'])
            value = message
            data = load_data_session()
            selected_title = data['titles'][value]
            session_data['selected_title'] = selected_title
            subtitles = data.get('Subtitles', {}) # Returns an empty dict if 'Subtitles' doesn't exist   
            formatted_subtitles = "\n".join([f"{option}  - {subtitle}" for option,subtitle in subtitles.items()])
            text = f"Perfect! Now let's have some options for the subtitle of your business.\nHere are three Options for Subtitles:\n{formatted_subtitles}\n\n\n Please Enter the option you like the most e.g: Option 1"
            session_data['status'] = 'awaiting_subtitle'
            save_session(session_data)
            send_message(sender_id,text)
        
        elif session_data['status'] == 'awaiting_subtitle':
            generate_ctas(campaign_info=session_data['selected_campaign_info'])
            value = message
            data = load_data_session()
            selected_subtitle = data['Subtitles'][value]
            session_data['selected_subtitle'] = selected_subtitle
            ctas = data.get('ctas', {}) # Returns an empty dict if 'Subtitles' doesn't exist   
            formatted_ctas = "\n".join([f"{option}  - {cta}" for option,cta in ctas.items()])
            text = f"Great! Now let's have some options for Call to Actions of your business.\nHere are three Options for Subtitles:\n{formatted_ctas}\n\n\n Please Enter the option you like the most e.g: Option 1"
            session_data['status'] = 'awaiting_cta'
            save_session(session_data)
            send_message(sender_id,text)
            
        
        elif session_data['status'] == 'awaiting_cta':
            value = message
            data = load_data_session()
            selected_cta = data['ctas'][value]
            session_data['selected_cta'] = selected_cta
            session_data['status'] = 'awaiting_logo'
            text=f"Great! Now please send me your logo"
            save_session(session_data)
            send_message(sender_id, text)
            
        elif session_data['status'] == 'awaiting_logo':
         if media_url:
                content_type = request.form.get('MediaContentType0')
                r = requests.get(media_url)
                if content_type == 'image/jpeg':
                    filename = f'logos/logo.jpeg'
                elif content_type == 'image/png':
                    filename = f'logos/logo.png'
                else:
                    filename = None

                if filename:
                    if not os.path.exists(f'logos'):
                        os.mkdir(f'logos')
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    session_data['status'] = 'awaiting_bg'
                    session_data['logo'] = filename
                    save_session(session_data)
                    text = f"Great! Now please send me your background image"
                    send_message(sender_id, text)
                    print('Thank you! Your image was received.')
                else:
                    print('The file that you submitted is not a supported image type.')
                    
        elif session_data['status'] == 'awaiting_bg':
         if media_url:
                content_type = request.form.get('MediaContentType0')
                r = requests.get(media_url)
                if content_type == 'image/jpeg':
                    filename = f'bg/bg.jpeg'
                elif content_type == 'image/png':
                    filename = f'bg/bg.png'
                else:
                    filename = None

                if filename:
                    if not os.path.exists(f'bg'):
                        os.mkdir(f'bg')
                    with open(filename, 'wb') as f:
                        f.write(r.content)
                    session_data['status'] = 'awaiting_ad'
                    session_data['bg'] = filename
                    save_session(session_data)
                    text = f"Great! Now type 'generate' to get the ad"
                    send_message(sender_id, text)
                    print('Thank you! Your image was received.')
                else:
                    print('The file that you submitted is not a supported image type.')
        elif session_data['status'] == 'awaiting_ad':
            if message == "generate":
                title = session_data['selected_title']
                subtitle = session_data['selected_subtitle']
                cta = session_data['selected_cta']
                bgImage = session_data['bg']
                logoImage = session_data['logo']
                
            
                if title and subtitle and cta:
                    print(title,subtitle,cta)
                    send_message(sender_id, "Your ad is ready!")
                    generate_image(title,subtitle,cta,logoImage,bgImage)

                    #send_message(user_no, output.png)
                    
                    # session_data['status'] = 'awaiting_campaign_info'
                    save_session(session_data)
                else:
                    send_message("Please send logo and bg first!")
        


    except:
        print("Error here")
        pass

    return 'OK', 200

def load_user_session():
    try:
        with open(f'sessions.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        empty_session = {}
        save_session(empty_session)
        return empty_session

def save_session(session_data):
    file_path = f'sessions.json'

    with open(file_path, 'w') as f:
        json.dump(session_data, f,ensure_ascii=False)
        
def load_data_session():
    try:
        with open(f'data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        empty_data = {}
        save_data_session(empty_data)
        return empty_data

def save_data_session(data):
    file_path = f'data.json'

    with open(file_path, 'w') as f:
        json.dump(data, f,ensure_ascii=False)


    return "Not Found"

def get_option_value(section, option_number):
    option_value = "Not Found"
    recording = False

    with open('ans.txt', 'r', encoding='utf-8') as file:
        for line in file:
            # Clean up the line to remove excess whitespace and check for the section header
            if section in line.strip() and line.strip().endswith(':'):
                recording = True
                continue
            
            # If we're in the correct section, look for the option number
            if recording and line.strip().startswith(f"- {option_number}:"):
                # Assuming the line format is: - Option N: "Option Value"
                # We split by ':' then strip the whitespace and quotes
                option_value = line.split(':', 1)[1].strip().strip('"')
                break  # No need to continue through the file
            
            # If we reach a new section or end of the section, stop recording
            if recording and line.strip() == '':
                break

    return option_value


def find_choice(section, choice):
    with open('ans.txt', 'r', encoding='utf-8') as file:  # Ensure the correct encoding
        file_contents = file.read()

    
    pattern = rf"{section}:\s*[\s\S]*?-\s*{choice}:\s*\"([^\"]*)\""
    match = re.search(pattern, file_contents, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    else:
        # No match found, print debug information
        print("No match found. Check the regex pattern and the section/option formatting.")
        return "Not Found"
    
def extract_section_options(file_contents, section_start, section_end):
    # Regex to find the block for the section
    section_regex = rf'{section_start}:(.*?){section_end}'
    section_match = re.search(section_regex, file_contents, re.DOTALL)
    if section_match:
        section_content = section_match.group(1).strip()
        # Find all options within the section
        options = re.findall(r'- Option \d+: (.+)', section_content)
        return options
    else:
        return []


if __name__ == '__main__':
    app.run(debug=True)