import os
from twilio.rest import Client
from keys import twilio_sid, twilio_account_token, openai_apikey
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import os
import subprocess
from flask import jsonify
from PIL import Image
from collections import Counter
import json


account_sid = twilio_sid
auth_token = twilio_account_token
client = Client(account_sid, auth_token)


user_no = 'whatsapp:'
ai_no = 'whatsapp:'

os.environ["OPENAI_API_KEY"] = openai_apikey

# ----------------------------------------------------------------------------
def send_message(to: str, message: str) -> None:
    """
    Send message to a Telegram user.
    Parameters:
    1- to(str): sender whatsapp number in this whatsapp:
    2- message(str): text message body
    """

    client.messages.create(
        from_=ai_no,
        body=message,
        to=to
    )

# ----------------------------------------------------------------------------
def fetch_message(to, from_):

    # Fetch WhatsApp messages
    messages = client.messages.list(
        to=ai_no,
        from_=user_no,  # Replace with the sender's WhatsApp number
        limit=1  # Adjust the number of messages to fetch
    )

    # Process and print the messages
    for message in messages:
        print("")
        # print(f"Message SID: {message.sid}")
        # print(f"From: {message.from_}")
        # print(f"To: {message.to}")
        # print(f"Body: {message.body}")
        # print(f"Date Sent: {message.date_sent}")
        # print("\n")

    return message.body, message.sid

# ----------------------------------------------------------------------------
def get_image(media_url, from_, to):
    image = client.messages.create(
        media_url= ['https://images.unsplash.com/photo-1545093149-618ce3bcf49d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=668&q=80'],
        from_ = user_no,
        to= ai_no
    )

    print(image.sid)
    
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
        json.dump(data, f,ensure_ascii=False, indent=4)
# ----------------------------------------------------------------------------
def gpt_titles(campaign_info):
    template = """
    You are a cutting-edge marketing strategist with a knack for producing viral social media content. You're tasked 
    with generating three unique and catchy titles for a social media campaign with maximum 30 characters.

    {history}
    I want you to keep two very important things in mind while responding.

    First, please generate and share the titles in hebrew and max 5-7 words.
    Secondly, please generate the output exactly in the format below.

    Option 1: Enter generated title 1 in hebrew here:
    Option 2: Enter generated title 2 in hebrew here:
    Option 3: Enter generated title 3 in hebrew here:

    The campaign is centered around these keywords: {campaign_info}

    Keeping the above keyword in mind, please generate three good titles. 
    Once again, please respond only in the format I specified. 
    The response should contain only the options and the generated titles in 
    hebrew as shown in the format, and nothing else. 

    """

    prompt = PromptTemplate(
        input_variables={"history", "campaign_info"},
        template=template
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2, openai_api_key=openai_apikey),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output = chatgpt_chain.predict(campaign_info=campaign_info)
    return output


def generate_titles(campaign_info):
    generated_titles = gpt_titles(campaign_info)
    lines = generated_titles.strip().split('\n')
    my_dict = {}
    i=1
    for line in lines:
        line = line.strip()
        if line.lower().startswith(f"option {i}"):
            x = line.split(': ')[1]
            my_dict[f"Option {i}"] = x
            i+=1
        else:
            print("this was not the selected option!")
        
    data_to_save = {"titles": my_dict}
    file_path = 'data.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data_to_save, file, ensure_ascii=False, indent=4)


def gpt_subtitles(campaign_info):
    template = """
    You are a cutting-edge marketing strategist with a knack for producing viral social media content. You're tasked 
    with generating three unique and catchy subtitles for a social media campaign with maximum 40 characters.

    {history}
    I want you to keep two very important things in mind while responding.

    First, please generate and share the subtitles in hebrew and max 5-7 words.
    Secondly, please generate the output exactly in the format below.

    Option 1: Enter generated subtitle 1 in hebrew here:
    Option 2: Enter generated subtitle 2 in hebrew here:
    Option 3: Enter generated subtitle 3 in hebrew here:

    The campaign is centered around these keywords: {campaign_info}

    Keeping the above keyword in mind, please generate three good subtitles. 
    Once again, please respond only in the format I specified. 
    The response should contain only the options and the generated subtitles in 
    hebrew as shown in the format, and nothing else. 

    """

    prompt = PromptTemplate(
        input_variables={"history", "campaign_info"},
        template=template
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2, openai_api_key=openai_apikey),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output = chatgpt_chain.predict(campaign_info=campaign_info)
    return output


def generate_subtitles(campaign_info):
    generated_subtitles = gpt_subtitles(campaign_info)
    lines = generated_subtitles.strip().split('\n')
    my_dict = {}
    i=1
    for line in lines:
        line = line.strip()
        if line.lower().startswith(f"option {i}"):
            x = line.split(': ')[1]
            my_dict[f"Option {i}"] = x
            i+=1
        else:
            print("this was not the selected option!")
    data = load_data_session()
    data['Subtitles'] = my_dict
    save_data_session(data)
# ----------------------------------------------------------------------------

def gpt_CTA(campaign_info):
    template = """
    You are a cutting-edge marketing strategist with a knack for producing viral social media content. You're tasked 
    with generating three unique and catchy call to actions for a social media campaign with maximum 20 characters.

    {history}
    I want you to keep two very important things in mind while responding.

    First, please generate and share the call to actions in hebrew.
    Secondly, please generate the output exactly in the format below.

    Option 1: Enter generated call to action 1 in hebrew here:
    Option 2: Enter generated call to action 2 in hebrew here:
    Option 3: Enter generated call to action 3 in hebrew here:

    The campaign is centered around these keywords: {campaign_info}

    Keeping the above keyword in mind, please generate three good call to actions. 
    Once again, please respond only in the format I specified. 
    The response should contain only the options and the generated call to actions in 
    hebrew as shown in the format, and nothing else. 

    """

    prompt = PromptTemplate(
        input_variables={"history", "campaign_info"},
        template=template
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2, openai_api_key=openai_apikey),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output = chatgpt_chain.predict(campaign_info=campaign_info)
    return output

def generate_ctas(campaign_info):
    generated_ctas= gpt_CTA(campaign_info)
    lines = generated_ctas.strip().split('\n')
    my_dict = {}
    i=1
    for line in lines:
        line = line.strip()
        if line.lower().startswith(f"option {i}"):
            x = line.split(': ')[1]
            my_dict[f"Option {i}"] = x
            i+=1
        else:
            print("this was not the selected option!")
    data = load_data_session()
    print(my_dict)
    data['ctas'] = my_dict
    save_data_session(data)

def get_response_from_ai(campaign_info):
    template = """
    You are a cutting-edge marketing strategist with a knack for producing viral social media content. You're tasked 
    with generating three unique and catchy options for each of the following components of a social media banner. 
    Keep the copy fresh, engaging, and non-repetitive.

    1. Titles: Create three titles that could go viral, each limited to 25 characters. They should encapsulate the 
    essence of the campaign.
      - Option 1:
      - Option 2:
      - Option 3:

    2. Subtitles: Provide three memorable subtitles that are each under 30 characters. They should complement 
    the titles and be catchy.
      - Option 1:
      - Option 2:
      - Option 3:

    3. Calls to Action (CTA): Craft three Calls to Action that are energetic and limited to 30 characters. 
    They should encourage immediate engagement.
      - Option 1:
      - Option 2:
      - Option 3:

    {history}
    The campaign is centered around these keywords: {campaign_info}
    Your copy will be featured on platforms like Facebook and Instagram, so make it shareable and stand out.
    """

    prompt = PromptTemplate(
        input_variables={"history", "campaign_info"},
        template=template
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2, openai_api_key=openai_apikey),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output = chatgpt_chain.predict(campaign_info=campaign_info)
    return output


# ----------------------------------------------------------------------------
def save_options_ask_logo(context):
    template_2 = """
    Based on the context provided, please show the user's preferred options in the form of bullet points. Please write the content of the chosen options exactly as it is

    {history}
    {context}
    Based on the info provided, the user selected the following options.
    
    Selected Title: write title here
    Selected Subtitle: write subtitle here
    Selected CTA: write cta here
    """

    prompt = PromptTemplate(
        input_variables={"history", "context"},
        template=template_2
    )

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.2, openai_api_key=openai_apikey),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2)
    )

    output_2 = chatgpt_chain.predict(context=context)
    return output_2

def is_valid_color(rgb):
    # Define what 'invalid' means: here, we'll say a color is invalid if it's too light
    # Adjust the threshold as necessary for your use case
    threshold = 200
    if sum(rgb) / 3 > threshold:
        return False
    return True

def replace_invalid_colors(most_common_colors, fallback_colors, num_colors):
    valid_colors = [color for color in most_common_colors if is_valid_color(color)]
    # Fill up the remaining colors needed from the fallback list
    while len(valid_colors) < num_colors:
        valid_colors.append(fallback_colors.pop(0))
    return valid_colors

def extract_most_used_colors(image_path, num_colors=2):
    fallback_colors = [(40, 40, 40), (80, 70, 60), (50, 60, 70)]  # Dark aesthetic colors
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = list(img.getdata())
        color_counts = Counter(pixels)
        most_common_colors = [color[0] for color in color_counts.most_common(10)]  # Get more colors to have options

        # Replace white or near-white and invalid colors
        most_common_colors = [
            color for color in most_common_colors 
            if color != (255, 255, 255) and is_valid_color(color)
        ]

        # Ensure we have enough unique colors and replace invalid ones from fallback
        most_common_colors = replace_invalid_colors(most_common_colors, fallback_colors, num_colors)

        # Convert RGB to HEX
        hex_codes = [f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}" for color in most_common_colors[:num_colors]]

        return hex_codes
    except Exception as e:
        # Return fallback colors if there's an error
        return [f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}" for color in fallback_colors[:num_colors]]

def remove_white_background(input_path, output_path):
    # Open the image
    image = Image.open(input_path)

    # Convert the image to RGBA
    image = image.convert("RGBA")

    # Get data of the image
    data = image.getdata()

    # Create a new data list with a transparent background
    new_data = []
    for item in data:
        # If the pixel is white, make it transparent
        if item[:3] == (255, 255, 255):
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    # Update the image data
    image.putdata(new_data)

    # Save the new image
    image.save(output_path)

    
def generate_image(title,subtitle,cta,logoImage,bgImage):
    print("Here at generate image function")
    output_path = "logos/logo_no_bg.png"
    remove_white_background(logoImage, output_path)
    most_used_colors = extract_most_used_colors('logos/logo_no_bg.png')
    
    color1, color2 = most_used_colors[0], most_used_colors[1]
    node_script_path = 'node-app.js'

    try:
     subprocess.check_call(['node', node_script_path, title, subtitle, cta,logoImage,bgImage, color1,color2])

     return jsonify({"message": "Image generation request sent successfully"})
    except subprocess.CalledProcessError as e:
    # Print the details of the error
     print(e)
     return jsonify({"error": "Image generation failed", "details": str(e)})