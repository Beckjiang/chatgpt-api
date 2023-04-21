
# chatgpt-api

chatgpt-api is a tool that converts the functionality of the ChatGPT website into a chat API protocol. With this tool, you can easily integrate ChatGPT into your own applications and chatbots.

## Installation

To install chatgpt-api, follow these steps:

1. Clone the repository to your local machine.
```
git clone git@github.com:Beckjiang/chatgpt-api.git
```
2. Navigate to the project directory.
```
cd chatgpt-api
```
3. Copy And Configure the `config/config.ini` file with your email and access token in `[chatgpt_1]`.
```
cp config/config.sample.ini config/config.ini
```
4. Configure the `config/config.ini` file with API Key in `[api_key]`.
5. [OPTIONAL]Build the Docker image by running `docker build -t xx/xxx ./`
6. Run the application using `docker-compose up`
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