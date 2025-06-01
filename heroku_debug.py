import os

print("=== Heroku Environment Check ===")
print(f"Python Version: {os.sys.version}")
print(f"Environment: {dict(os.environ)}")
