import sys
import os
from collections import defaultdict
from Manager import * 
class Broker:
    def __init__(self):
        self.topics = defaultdict(set)  # 存储主题及其订阅者
        self.users = defaultdict(set)   # 存储用户及其订阅的主题
        self.manager =  SubscriptionManager(db_config)
        self.memory = [] 
        self.load_users()

    def load_users(self):
        subscriptions = self.manager.get_all_subscriptions()
        for subscription in subscriptions:
            self.subscribe(subscription['chatid'],subscription['topic_name'])


    def subscribe(self, user, topic):
        self.topics[topic].add(user)
        self.users[user].add(topic)
        self.manager.add_subscription(user,topic)
        print(f"{user} has subscribed to {topic}")


    def unsubscribe(self, user, topic):
        if topic in self.topics:
            self.topics[topic].discard(user)
            print(f"{user} has unsubscribed from {topic}")

        if user in self.users:
            self.users[user].discard(topic)

        self.manager.delete_subscription(user,topic)

    def push_message(self, topic, message):
        if topic in self.topics:
            for user in self.topics[topic]:
                self.send_message(user, topic, message)
        else:
            print(f"No subscribers for topic: {topic}")

    def send_message(self, user, topic, message):
        # 模拟发送消息给用户
        print(f"Sending message to {user}: [{topic}] {message}")
        self.memory.append({'chatid':f'{user}','topic_name':f'{topic}','message':f'{message}'})

    def get_message(self):
        data = self.memory.copy()
        self.memory = [] 
        return data

# 测试示例
if __name__ == "__main__":
    system = PubSubSystem()

    # 用户订阅
    # system.subscribe("6904184189", "午餐")
    # 推送消息
    system.push_message("午餐", "好吃")

    # 获取并显示消息
    messages = system.get_message()
    for message in messages:
        print(f"Chat ID: {message['chat_id']}, Topic: {message['topic']}, Message: {message['message']}")

    print(system.get_message())
