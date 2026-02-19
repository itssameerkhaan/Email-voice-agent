import ngrok
import time

# Establish connectivity
listener = ngrok.forward(5000, authtoken="1wRsYmu9EC3qhkfHQgPEKkKrwIW_7K6nfiD7FbHVpykRkPTe3")

# Output ngrok url to console
print(f"Ingress established at {listener.url()}")

# Keep the listener alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Closing listener")