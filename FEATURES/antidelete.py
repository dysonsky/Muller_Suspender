class AntiDelete:
    def __init__(self):
        self.deleted_messages = []
    
    def log_deletion(self, msg):
        self.deleted_messages.append(msg)
        print(f"🚫 Deleted message logged: {msg[:20]}...")
