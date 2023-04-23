chatgpt-api
===========
中文 | [English](./README_en.md) 

chatgpt-api是一个将ChatGPT网站的功能转换成Chat API协议的工具。使用此工具，您可以轻松地将ChatGPT集成到自己的应用程序和聊天机器人中。
支持gpt3.5、gpt-4(需plus账号)，不排除封号的可能，使用者请自行承担使用风险。

(项目基于[revChatGPT](https://github.com/acheong08/ChatGPT)实现，以及默认使用[go-chatgpt-api](https://github.com/linweiyuan/go-chatgpt-api)公开的代理绕过cloudflare)

安装
--

要安装chatgpt-api，请按照以下步骤操作：

1.  克隆存储库到本地机器上。
    ```bash
    git clone git@github.com:Beckjiang/chatgpt-api.git
    ```
    
2.  进入项目目录。
    
    ```bash
    cd chatgpt-api
    ```
    
3.  复制和配置 `config/config.ini` 文件，在 `[chatgpt_1]` 中填写您的email和access_token。
    
    ```arduino
    cp config/config.sample.ini config/config.ini
    ```
    
4.  在 `[api_key]` 中填写API密钥。
5.  \[可选\] 使用 `docker build -t xx/xxx ./` 命令构建Docker镜像。
6.  运行应用程序，使用 `docker-compose up` 命令启动。

使用
--

要使用chatgpt-api，可向`http://127.0.0.1:8082/v1/chat/completes` 发送POST请求，接口定义与OpenAI一致，可参考https://platform.openai.com/docs/api-reference/chat. 这里是一个示例请求：（您需要将 `$CONFIG_API_KEY` 更改为 `[api_key]` 中配置的值。）


```
curl http://127.0.0.1:8082/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CONFIG_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**参数 `stream: true` 也支持。**

贡献
--

如果您想为chatgpt-api做出贡献，请在提交拉取请求之前阅读我们的贡献指南。

许可证
---

本项目基于MIT许可证 - 请查看LICENSE文件以了解详细信息。

联系方式
----

如果您对chatgpt-api有任何问题或意见，请随时通过[beckjiang.fun@gmail.com](mailto:beckjiang.fun@gmail.com)联系项目维护人员。
