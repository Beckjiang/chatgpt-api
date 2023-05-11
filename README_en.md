
# chatgpt-api
English | [中文](./README.md)

chatgpt-api is a tool that converts the functionality of the ChatGPT website into a chat API protocol. With this tool, you can easily integrate ChatGPT into your own applications and chatbots. It supports gpt3.5, gpt-4 (requires a plus account), and there is a possibility of being banned, so users are advised to use it at their own risk. 

The project is implemented based on [revChatGPT](https://github.com/acheong08/ChatGPT) and defaults to using the [go-chatgpt-api](https://github.com/linweiyuan/go-chatgpt-api) proxy to bypass Cloudflare.

## Installation

To install chatgpt-api, follow these steps:

1. Clone the repository to your local machine:
   ```bash
   git clone git@github.com:Beckjiang/chatgpt-api.git
   ```

2. Navigate to the project directory:
   ```bash
   cd chatgpt-api
   ```

3. Copy the sample configuration files `config/config.sample.ini` and `config/account.sample.ini`:
   ```
   cp config/config.sample.ini config/config.ini
   cp config/account.sample.ini config/account.ini
   ```

4. In the `config/config.ini` file, fill in your custom API Key under `[api_key]`.

5. Configure your ChatGPT account email and token in the `config/account.ini` file. You can configure multiple accounts.
   (Access tokens can be obtained here: https://chat.openai.com/api/auth/session)
   Example:
   ```
   [chatgpt_1]
   email=youremail@xx.com
   access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiIxaDFyYmNtYm9AeXVud2VpbG9naW5taDMuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsidXNlcl9pZCI6InVzZXItZ2wyVmZJMUI3d3g5WlpITHVDZ0FBaldhIn0sImlzcyI6Imh0dHBzOxxxxxxxxxxxxxxxxxxx

   [chatgpt_2]
   email=youremail2@xx.com
   access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1UaEVOVUpHTkVNMVFURTRNMEZCTWpkQ05UZzVNRFUxUlRVd1FVSkRNRU13UmtGRVFrRXpSZyJ9.eyJodHRwczovL2FwaS5vcGVuYWkuY29tL3Byb2ZpbGUiOnsiZW1haWwiOiIxaDFyYmNtYm9AeXVud2VpbG9naW5taDMuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWV9LCJodHRwczovL2FwaS5vcGVuYWkuY29tL2F1dGgiOnsidXNlcl9pZCI6InVzZXItZ2wyVmZJMUI3d3g5WlpITHVDZ0FBaldhIn0sImlzcyI6Imh0dHBzOxxxxxxxxxxxxxxxxxxx
   ```

6. Run the application by executing the `docker-compose up` command to
## Usage

To use chatgpt-api, make a POST request to http://127.0.0.1:8082/v1/chat/completes with a JSON payload containing the message you want to send to OpenAI(https://platform.openai.com/docs/api-reference/chat). Here's an example request:
(you need to change the `$CONFIG_API_KEY` to that configure in `[api_key]`)
```
curl http://127.0.0.1:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CONFIG_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```
**the param `stream: true` also supports.**

## Contributing

If you'd like to contribute to chatgpt-api, please read our contributing guidelines before submitting a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

If you have any questions or comments about chatgpt-api, please feel free to contact the project maintainer at beckjiang.fun@gmail.com.
