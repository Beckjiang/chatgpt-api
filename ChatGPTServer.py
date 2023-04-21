import json
import random
import string
import time
from ChatbotAgent import ChatbotAgent

def generate_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

class ChatGPTServer:
    chatserver: ChatbotAgent = None

    def __init__(self, chatserver):
        self.chatserver: ChatbotAgent = chatserver
    
    def format_to_api_struct(self, id, message, stream):
        if stream :
            choices = [{'index': 0, 'finish_reason': None, 'delta': {'content': message}}]
        else :
            choices = [{'index': 0, 'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': message}}]
        
        object = "chat.completion"
        if stream :
            object = "chat.completion.chunk"

        new_one = {
            "id": id,
            "object": object,
            "created": int(time.time()),
            "model": "gpt-3.5-turbo-0301",
            "choices": choices,
        }
        if not stream :
            new_one['usage'] = {
                'prompt_tokens': 0,
                'completion_tokens': 0,
                'total_tokens': 0,
            }
        return new_one

    def send_first_chunk(self, id, data, email, stream):
        self.chatserver.update_last_active_time(email)
        new_conversation_id = data.get('conversation_id')
        parent_id = data.get('parent_id')
        if new_conversation_id and parent_id:
            self.chatserver.set_conversation_id(email, new_conversation_id, parent_id, email)

        if stream:
            role_response = self.format_to_api_struct(id, '', stream)
            role_response['choices'] = [{'index': 0, 'finish_reason': None, 'delta': {'role': 'assistant'}}]
            msg = json.dumps(role_response)
            # print(f'send_first_chunk: {msg}')
            yield f"data: {msg}\n\n".encode('utf-8')

    def send_stream_chunk(self, id, data, prev_text, stream):
        resp_message = data.get('message')[len(prev_text):]
        resp = self.format_to_api_struct(id, resp_message, stream)

        if stream:
            msg = json.dumps(resp)
            # print(f'send_stream_chunk: {msg}')
            yield f"data: {msg}\n\n".encode('utf-8')

    def send_final_chunk(self, id, last_one, stream):
        resp = self.format_to_api_struct(id, last_one['message'], stream)
        if not stream:
            msg = json.dumps(resp)
            yield f"{msg}\n\n".encode('utf-8')
        else:
            resp['choices'] = [{'index': 0, 'finish_reason': 'stop', 'delta': {}}]
            msg = json.dumps(resp)
            yield f"data: {msg}\n\n".encode('utf-8')

        

    def execute_chat_response(self, chatbot, email, stream, message, conversation_id=None, parent_id=None):
        is_first = True
        last_one = {}
        prev_text = ""
        message_id = f'chatcmpl-%s' % generate_random_string(32)

        # print(f'execute_chat_response: {message}')
        for data in chatbot.ask(prompt=message, conversation_id=conversation_id, parent_id=parent_id):
            if is_first:
                yield from self.send_first_chunk(message_id, data, email, stream)
                is_first = False

            if data.get('message') is None or len(data.get('message')) == 0:
                continue

            replace = prev_text
            prev_text = data.get('message')
            # print(f'prev_text: {prev_text}')
            last_one = data.copy()

            yield from self.send_stream_chunk(message_id, data, replace, stream)


        yield from self.send_final_chunk(message_id, last_one, stream)
        if stream :
            msg = "data: [DONE]"
            yield f"{msg}\n\n".encode('utf-8')

    def send_chunked_response(self, message, scene_id, stream):
        result = self.chatserver.get_conversation_id(scene_id)
        if result is None or len(result) == 0:
            chatbot, email = self.chatserver.get_chatbot()
            conversation_id = None
            parent_id = None
        else:
            conversation_id, parent_id, email = self.get_chat_info(result)
            if email:
                chatbot, email = self.chatserver.get_chatbot(email)
            else:
                chatbot, email = self.chatserver.get_chatbot()

        print(f'lock_email: {email}')

        if self.chatserver.lock(email):
            try:
                yield from self.execute_chat_response(chatbot, email, stream, message, conversation_id, parent_id)
            except Exception as e:
                self.chatserver.unlock(email)
                print(e)
                raise e
            finally:
                self.chatserver.unlock(email)
        else:
            print('try get lock failed')

    def get_chat_info(self, result):
        conversation_id, parent_id, email = result
        if conversation_id:
            conversation_id = conversation_id.decode("utf-8")
        if parent_id:
            parent_id = parent_id.decode("utf-8")
        if email:
            email = email.decode("utf-8")
        return conversation_id, parent_id, email