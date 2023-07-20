import os
import re
import json
import random
import openai
import datetime
import numpy as np
from uuid import uuid4
from numpy.linalg import norm
from time import time, sleep
from fastapi import FastAPI
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from utils import open_file, save_file, save_json, load_json, timestamp_to_datetime, process_knowledgebase, gpt3_completion, process_file, send_email

load_dotenv() 
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define the directory where conversation history files will be saved
HISTORY_DIR = "conversation_histories/"

# Create the directory if it does not exist
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# Define a dictionary to keep track of conversations
conversations = {}

@app.get("/")
async def root():
    return {"message": "The server is running"}

@app.post("/api/generate")
async def generate(message: str, user_id: str = None):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # If user_id is not specified, generate a new one
    if user_id is None or len(user_id.strip()) == 0:
        user_id = str(uuid4())

    # Load the conversation history for this user from file, if it exists
    history_file = os.path.join(HISTORY_DIR, user_id + ".json")
    if os.path.exists(history_file):
        conversations[user_id] = load_json(history_file)
    else:
        conversations[user_id] = {'convo_id': str(uuid4()), 'requests': []}
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    info = {'speaker': 'USER', 'time': timestamp, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    conversations[user_id]['requests'].append(info)
    conversation = '\n'.join([i['message'] for i in conversations[user_id]['requests']])
    knowledgebase_file = "kb.txt"
    prompt_file = "prompt.txt"
    #prompt_file = open_file('prompt.txt').replace('<<CONVERSATION>>', conversation).replace('<<MESSAGE>>', message)
    output = gpt3_completion(knowledgebase_file, prompt_file, message)
    timestamp = time()
    timestring = timestamp_to_datetime(timestamp)
    message = output
    info = {'speaker': 'Tracy', 'time': timestamp, 'message': message, 'uuid': str(uuid4()), 'timestring': timestring}
    conversations[user_id]['requests'].append(info)
    save_json(history_file, conversations[user_id])
    return {'message': output, 'user_id': user_id, 'convo_id': conversations[user_id]['convo_id']}
