import zmq
from datetime import datetime

# Setup context and PUB socket
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5555")

# Get sender name and fixed topic
name = input("Enter your name: ").strip()
channel = input("Enter channel to publish to (e.g. news, tech): ").strip()

print(f"\n📢 Publisher started on channel '{channel}'. Use Ctrl+C to exit.\n")

try:
    while True:
        msg = input("You: ").strip()
        ts = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{ts}] {name}: {msg}"
        socket.send_string(f"{channel} {full_msg}")
except KeyboardInterrupt:
    print("\n❌ Publisher exiting.")
    socket.close()
    context.term()
