import configparser
import redis
import time
import random
from revChatGPT.V1 import Chatbot

class ChatbotAgent:
    def __init__(self, config_file='config/config.ini', account_file='config/account.ini'):
        common_config = configparser.ConfigParser()
        common_config.read(config_file)

        account_config = configparser.ConfigParser()
        account_config.read(account_file)

        # 获取 Redis 的配置
        redis_section = 'redis'
        redis_host = common_config.get(redis_section, 'host')
        redis_port = common_config.getint(redis_section, 'port')
        redis_db = common_config.getint(redis_section, 'db')
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

        # 获取 ChatGPT 的配置
        self.chatbots = {}
        chatgpt_section_names = [section for section in account_config.sections() if section.startswith('chatgpt_')]
        for chatgpt_section_name in chatgpt_section_names:
            chatgpt_email = account_config.get(chatgpt_section_name, 'email')
            # chatgpt_password = account_config.get(chatgpt_section_name, 'password')
            access_token = account_config.get(chatgpt_section_name, 'access_token')
            print(f'chatgpt_email: {chatgpt_email}')
            self.use_email(chatgpt_email)
            self.chatbots[chatgpt_email] = Chatbot(config={
                # "email": chatgpt_email,
                # "password": chatgpt_password,
                "access_token": access_token,
                # "puid": PUID
            })

    def cleanup_expired_users(self):
        # 获取所有最后活跃时间距离当前时间超过一天的用户
        expired_users = [
            scene_id.decode() for scene_id, last_active_time in self.redis.zrangebyscore(
                'chat:last_active_time', 0, time.time() - 24 * 3600
            )
        ]

        # 删除最后活跃时间距离当前时间超过一天的用户的 scene_id 和 conversation_id 的关联关系
        for scene_id in expired_users:
            result = self.get_conversation_id(scene_id)
            if result is None or len(result) == 0:
                continue
            else:
                conversation_id = result[0]
                parent_id = result[1]
                email = result[2]
                if conversation_id:
                    self.redis.delete(self.parse_user_conversation_key(scene_id))
                    self.redis.zrem('chat:last_active_time', scene_id)

                if email and conversation_id :
                    email = email.decode()
                    chatbot = self.chatbots.get(email)
                    # 删除对应的 conversation_id
                    chatbot.delete_conversation(conversation_id.decode('utf-8'))

    def get_chatbot(self, email=None):
        # cache key 每个小时处理初始化一遍
        self.init_use_email_key()

        if email:
            self.use_email(email)
            return self.chatbots.get(email), email
        else:
            least_used_email = self.get_least_used_email()
            if least_used_email :
                chatbot = self.chatbots.get(least_used_email)
                if chatbot :
                    self.use_email(least_used_email)
                    return chatbot, least_used_email
                
            email = random.choice(list(self.chatbots.keys()))
            self.use_email(email)
            chatbot = self.chatbots.get(email)

            return chatbot, email

    def get_use_email_key(self):
        current_hour = time.strftime("%Y%m%d%H", time.localtime())
        email_use_count_key = f"email_use_count_{current_hour}"

        return email_use_count_key
    
    def init_use_email_key(self):
        cache_key = self.get_use_email_key()
        # 判断key是否存在
        if not self.redis.exists(cache_key):
            keys = self.chatbots.keys()
            # 判断keys是否为空
            if keys:
                # 遍历keys调用use_email方法
                for key in keys:
                    self.use_email(key)


    def use_email(self, email):
        email_use_count_key = self.get_use_email_key()
        self.redis.zincrby(email_use_count_key, 1, email)
        
    def clear_email(self, keep_time = 3600):
        email_use_count_key = 'chat:email_use_count'
        # self.redis.zremrangebyscore(email_use_count_key, 0, time.time() - keep_time)

    def get_least_used_email(self):
        email_use_count_key = self.get_use_email_key()
        result = self.redis.zrange(email_use_count_key, 0, 0, withscores=False)
        if result:
            return result[0].decode('utf-8')
        else:
            return None

    # 1. 获取 scene_id 与 conversation_id 的关联关系
    def get_conversation_id(self, scene_id):
        return self.redis.hmget(self.parse_user_conversation_key(scene_id), ["conversation_id", "parent_id", "email"])
    # 2. 设置 scene_id 与 conversation_id 的关联关系
    def set_conversation_id(self, scene_id, conversation_id, parent_id, email):
        cache_key = self.parse_user_conversation_key(scene_id)
        self.redis.hset(cache_key, "conversation_id", conversation_id)
        self.redis.hset(cache_key, "parent_id", parent_id)
        self.redis.hset(cache_key, "email", email)

    # 更新用户的最后活跃时间
    def update_last_active_time(self, scene_id):
        self.redis.zadd('chat:last_active_time', {scene_id: time.time()})

    def lock(self, email):
        key = self.get_account_lock_key(email)
        count = 0
        while True:
            if self.redis.setnx(key, '1'):
                self.redis.expire(key, 120)
                # 获取到锁
                return True
            else:
                # 获取不到锁，等待
                time.sleep(2)
            
            # 判断等待次数是否超过5次
            if count > 5:
                return False

    def unlock(self, email):
        key = self.get_account_lock_key(email)
        self.redis.delete(key)
        
    def get_account_lock_key(self, email):
        return f'chat:account_lock:{email}'

    def parse_user_conversation_key(self, scene_id):
        return f'chat:scene_id:{scene_id}:conversation_id'
