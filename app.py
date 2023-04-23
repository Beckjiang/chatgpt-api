from flask import Flask, request, Response
from revChatGPT.V1 import Chatbot
from ChatbotAgent import ChatbotAgent
from ChatGPTServer import ChatGPTServer
from UserToken import UserToken
import time
import os
from gevent.pywsgi import WSGIServer
import hashlib

SCENE_ID_SEP = "-0-"

app = Flask(__name__)

run_env = os.environ.get('RUN_ENV', '')
config_file = 'config/config.ini'
if run_env != '' and os.path.exists(f'config/config.%s.ini' % run_env) :
    config_file = f'config/config.%s.ini' % run_env

user_token = UserToken(config_file)
agent = ChatbotAgent(config_file)
chat_gpt_server = ChatGPTServer(agent)

@app.route('/v1/chat/completions', methods=['POST'])
def completions():
    if not validate_token(request.headers):
        return Response("Forbidden: Invalid token.", status=403, mimetype='text/plain')

    model = request.json.get('model', '')
    messages = request.json.get('messages', [])
    scene_id = (parse_scene_id(request.headers) or 'default') + model
    stream = bool(request.json.get('stream', True))

    final_response = ''
    system_content = ''

    for message in messages:
        role = message.get('role', '')
        content = message.get('content', '')

        if role == 'user':
            user_message = content
            final_response += f'\n{user_message}'
        elif role == 'assistant':
            final_response += f'\n{content}'
        elif role == 'system':
            system_content = content
            pass

    final_response = system_content + "\n" + final_response + "\n"

    if final_response and scene_id:
        response_gen = chat_gpt_server.send_chunked_response(final_response, scene_id, stream, model)
        content_type = 'application/json'
        if stream :
            content_type = 'text/event-stream'
        return Response(response_gen, headers={'Content-Type': content_type, 'Cache-Control': 'no-cache'})
    else:
        return Response("Bad Request.", status=400, mimetype='text/plain')


def validate_token(headers):
    auth_header = headers.get('Authorization')
    if not auth_header or not user_token.is_valid(auth_header.split(SCENE_ID_SEP)[0].replace("Bearer ", "")):
        return False
    return True

def parse_scene_id(headers):
    auth_header = headers.get('Authorization')
    hash_object = hashlib.md5()
    hash_object.update(auth_header.encode())
    return hash_object.hexdigest()

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8082)
    # Production
    http_server = WSGIServer(('', 8082), app)
    http_server.serve_forever()