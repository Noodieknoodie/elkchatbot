from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit 
import openai
import os
from dotenv import load_dotenv
from time import localtime, strftime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!' 
socketio = SocketIO(app, cors_allowed_origins="*")

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_history = []

@app.route('/')
def index():
  return render_template('index.html', chats=chat_history)

@socketio.on('new chat')
def on_new_chat(data):
  chat = {
    'id': len(chat_history) + 1,
    'messages': [],
    'timestamp': strftime('%Y-%m-%d %H:%M:%S', localtime()) 
  }
  chat_history.insert(0, chat)
  emit('chat created', chat, broadcast=True)

@socketio.on('message')
def handleMessage(data):
  chat_id = data['chatId']
  user_input = data['userInput']

  # Instead of hardcoded values, extract the values from the client's payload
  system_message = data['systemMessage']
  model = data['model']
  temperature = float(data['temperature'])
  max_tokens = int(data['maxTokens'])
  
  completion = openai.ChatCompletion.create(
    model=model, 
    temperature=temperature,
    max_tokens=max_tokens,
    messages=[
      {"role": "system", "content": system_message},
      {"role": "user", "content": user_input}
    ]
  )
  
  ai_response = completion.choices[0].message.content

  chat_history[chat_id]['messages'].append({
    'user': 'User',
    'message': user_input,
    'timestamp': strftime('%Y-%m-%d %H:%M:%S', localtime())
  })

  chat_history[chat_id]['messages'].append({
    'user': 'Assistant',
    'message': ai_response,
    'timestamp': strftime('%Y-%m-%d %H:%M:%S', localtime()) 
  })
  
  emit('message received', {
      'chatId': chat_id, 
      'user': 'Assistant',
      'message': ai_response,
      'timestamp': strftime('%Y-%m-%d %H:%M:%S', localtime())
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)