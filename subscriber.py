import zmq
from datetime import datetime

context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5555")

topic = input("Enter exact channel to subscribe to (e.g. news): ").strip()
socket.setsockopt_string(zmq.SUBSCRIBE, topic + " ")  # add space to match prefix format

print(f"\n📥 Subscribed to '{topic}'. Listening for messages...\n")

try:
    with open(f"{topic}_log.txt", "a") as log:
        while True:
            full_msg = socket.recv_string()
            _, msg = full_msg.split(' ', 1)  # remove topic from front
            print(f">> {msg}")
            log.write(msg + "\n")
except KeyboardInterrupt:
    print("\n❌ Subscriber exiting.")
    socket.close()
    context.term()
