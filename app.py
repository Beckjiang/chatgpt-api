from flask import Flask, request, Response
from revChatGPT.V1 import Chatbot
from ChatbotAgent import ChatbotAgent
from ChatGPTServer import ChatGPTServer
import time
from gevent.pywsgi import WSGIServer

TOKEN = "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"
USER_ID_SEP = "-0-"

app = Flask(__name__)
agent = ChatbotAgent()
chat_gpt_server = ChatGPTServer(agent)


@app.route('/v1/chat/completions', methods=['POST'])
def completions():
    if not validate_token(request.headers):
        return Response("Forbidden: Invalid token.", status=403, mimetype='text/plain')

    messages = request.json.get('messages', [])
    user_id = parse_user_id(request.headers) or 'default'
    stream = request.json.get('stream', 1)
    stream = True if stream == 1 else False

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

    if final_response and user_id:
        response_gen = chat_gpt_server.send_chunked_response(final_response, user_id, stream)
        return Response(response_gen, headers={'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache'})
    else:
        return Response("Bad Request.", status=400, mimetype='text/plain')


def validate_token(headers):
    auth_header = headers.get('Authorization')
    if not auth_header or auth_header.split(USER_ID_SEP)[0] != f"Bearer {TOKEN}":
        return False
    return True


def parse_user_id(headers):
    auth_header = headers.get('Authorization')
    return auth_header.replace("Bearer ", "").split(USER_ID_SEP)[-1]


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=8082)
    # Production
    http_server = WSGIServer(('', 8082), app)
    http_server.serve_forever()