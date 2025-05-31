class MullerBot:
    def __init__(self, name, prefix, admins):
        self.name = name
        self.prefix = "*" 
        self.admins = "MULLER"
    
    def run(self):
        print(f"{self.name} is now running!")
        # WhatsApp connection logic here
