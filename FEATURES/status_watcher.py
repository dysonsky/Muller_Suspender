class StatusWatcher:
    def __init__(self):
        self.viewed_statuses = []
    
    def watch(self, status):
        if status not in self.viewed_statuses:
            print(f"👀 Viewed {status}")
            self.viewed_statuses.append(status)
