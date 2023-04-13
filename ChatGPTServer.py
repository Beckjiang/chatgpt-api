import json
from ChatbotAgent import ChatbotAgent

class ChatGPTServer:
    chatserver: ChatbotAgent = None

    def __init__(self, chatserver):
        self.chatserver: ChatbotAgent = chatserver

    def send_first_chunk(self, data, email, stream):
        self.chatserver.update_last_active_time(email)
        new_conversation_id = data.get('conversation_id')
        parent_id = data.get('parent_id')
        if new_conversation_id and parent_id:
            self.chatserver.set_conversation_id(email, new_conversation_id, parent_id, email)

        if stream:
            role_response = data.copy()
            del role_response['message']
            role_response['choices'] = [{'index': 0, 'finish_reason': None, 'delta': {'role': 'assistant'}}]
            msg = json.dumps(role_response)
            # print(f'send_first_chunk: {msg}')
            yield f"data: {msg}\n\n".encode('utf-8')

    def send_stream_chunk(self, data, prev_text, stream):
        resp_message = data.get('message')[len(prev_text):]
        choices = [{'index': 0, 'finish_reason': None, 'delta': {'content': resp_message}, 'message': {'role': 'assistant', 'content': resp_message}}]
        data['choices'] = choices
        data['object'] = "chat.completion.chunk"
        del data['message']

        if stream:
            del data['choices'][0]['message']
            msg = json.dumps(data)
            # print(f'send_stream_chunk: {msg}')
            yield f"data: {msg}\n\n".encode('utf-8')

    def send_final_chunk(self, last_one, stream):
        del last_one['message']
        if not stream:
            msg = json.dumps(last_one)
        else:
            last_one['choices'] = [{'index': 0, 'finish_reason': 'stop', 'delta': {}}]
            msg = json.dumps(last_one)

        yield f"data: {msg}\n\n".encode('utf-8')

    def execute_chat_response(self, chatbot, email, stream, message, conversation_id=None, parent_id=None):
        is_first = True
        last_one = {}
        prev_text = ""

        # print(f'execute_chat_response: {message}')
        for data in chatbot.ask(prompt=message, conversation_id=conversation_id, parent_id=parent_id):
            if is_first:
                yield from self.send_first_chunk(data, email, stream)
                is_first = False

            if data.get('message') is None or len(data.get('message')) == 0:
                continue

            replace = prev_text
            prev_text = data.get('message')
            # print(f'prev_text: {prev_text}')
            last_one = data.copy()

            yield from self.send_stream_chunk(data, replace, stream)


        yield from self.send_final_chunk(last_one, stream)
        msg = "data: [DONE]"
        yield f"{msg}\n\n".encode('utf-8')

    def send_chunked_response(self, message, user_id, stream):
        result = self.chatserver.get_conversation_id(user_id)
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