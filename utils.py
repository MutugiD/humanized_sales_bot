import os
import re
import json
import openai
import time 
import random
import smtplib
import datetime
import numpy as np
from numpy.linalg import norm
from time import time,sleep
from uuid import uuid4
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return json.load(infile)


def save_json(filepath, payload):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        json.dump(payload, outfile, ensure_ascii=False, sort_keys=True, indent=2)


def timestamp_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(unix_time).strftime("%A, %B %d, %Y at %I:%M%p %Z")

def gpt3_embedding(content, engine='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII',errors='ignore').decode()
    response = openai.Embedding.create(input=content,engine=engine)
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector


def similarity(v1, v2):
    # based upon https://stackoverflow.com/questions/18424228/cosine-similarity-between-2-number-lists
    return np.dot(v1, v2)/(norm(v1)*norm(v2))  # return cosine similarity

#engine='text-davinci-003',
#gpt-3.5-turbo-16k
def gpt_completion(prompt, engine='text-davinci-003',  temp=0.0, top_p=1.0, tokens=100, freq_pen=0.0,
                    pres_pen=0.0, stop=['USER:', 'Tracy:']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('[\r\n]+', '\n', text)
            text = re.sub('[\t ]+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            if not os.path.exists('gpt3_logs'):
                os.makedirs('gpt3_logs')
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                pass
            print('Error communicating with OpenAI:', oops)
            sleep(2)
            
def gpt35_completion(prompt, message, model="gpt-3.5-turbo-16k"):
    prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
    message = prompt.encode(encoding='ASCII', errors='ignore').decode()
    messages = [{"role": "system", "content": prompt}]
    messages.append({'role': 'user', 'content': message})
    #messages = system_line + user_line
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=1.0
            )
            text = response['choices'][0]['message']['content'].strip()
            text = re.sub('[\r\n]+', '\n', text)
            text = re.sub('[\t ]+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            
            if not os.path.exists('gpt3_logs'):
                os.makedirs('gpt3_logs')
            
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                pass
            print('Error communicating with OpenAI:', oops)
            sleep(2)



def gpt3_chat(prompt, engine='gpt-3.5-turbo', temp=0.0, top_p=1.0, tokens=400, freq_pen=0.0, pres_pen=0.0, 
              stop=['USER:', 'Tracy:']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                model=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                n=1,
                stop=stop
            )
            text = response['choices'][0]['text'].strip()
            text = re.sub('[\r\n]+', '\n', text)
            text = re.sub('[\t ]+', ' ', text)
            filename = f"{time()}_gpt3.txt"
            if not os.path.exists('gpt3_logs'):
                os.makedirs('gpt3_logs')
            save_file(f"gpt3_logs/{filename}", prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                pass
            print('Error communicating with OpenAI:', oops)
            sleep(2)


def process_file(conversation_text, llm):
    name_schema = ResponseSchema(
        name="client's name",
        description="What was the name? that the client said they are called? Extract the client's name"
    )
    email_schema = ResponseSchema(
        name="email",
        description="What was the email of the client? Extract the user's email"
    )
    contact_schema = ResponseSchema(
        name="contact",
        description="What was the contact or the mobile phone of the user? Extract the mobile number"
    )

    response_schemas = [name_schema, email_schema, contact_schema]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    email_template = """\
    For the following text, extract the following information:

    name: What was the name that the client said they are called? Extract the client's name.

    email: What was the email of the client? Extract the user's email.

    contact: What was the contact or the mobile phone of the user? Extract the mobile number.

    text: {text}

    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_template(template=email_template)
    messages = prompt.format_messages(text=conversation_text, format_instructions=format_instructions)
    response = llm(messages)
    return output_parser.parse(response.content)

def send_email(json_data, sender_email, sender_password, recipient_email):
    # Convert the JSON data to a string
    json_string = json.dumps(json_data, indent=4)

    # Create a MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "JSON Data"

    # Attach the JSON data as a plain text
    message.attach(MIMEText(json_string, "plain"))

    # Connect to the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)


