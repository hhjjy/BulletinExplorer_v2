from collections import defaultdict

class PubSubSystem:
    def __init__(self):
        self.topics = defaultdict(set)  # 存储主题及其订阅者
        self.users = defaultdict(set)   # 存储用户及其订阅的主题

    
    def load_users(self):
        pass 


    def subscribe(self, user, topic):
        self.topics[topic].add(user)
        self.users[user].add(topic)
        print(f"{user} has subscribed to {topic}")

    def unsubscribe(self, user, topic):
        if topic in self.topics:
            self.topics[topic].discard(user)
            print(f"{user} has unsubscribed from {topic}")
        if user in self.users:
            self.users[user].discard(topic)

    def push_message(self, topic, message):
        if topic in self.topics:
            for user in self.topics[topic]:
                self.send_message(user, topic, message)
        else:
            print(f"No subscribers for topic: {topic}")

    def send_message(self, user, topic, message):
        # 模拟发送消息给用户
        print(f"Sending message to {user}: [{topic}] {message}")

# 测试示例
if __name__ == "__main__":
    system = PubSubSystem()

    # 用户订阅
    system.subscribe("user1", "Python")
    system.subscribe("user2", "Python")
    system.subscribe("user1", "AI")
    system.subscribe("user3", "AI")

    # 推送消息
    system.push_message("Python", "New Python version released!")
    system.push_message("AI", "New breakthrough in AI technology!")

    # 用户取消订阅
    system.unsubscribe("user1", "Python")
    system.push_message("Python", "Python conference 2024 announced!")
