# pubsub-chat

A terminal-based real-time messaging system using the **publish/subscribe pattern** built with Python and ZeroMQ. Supports named users, fixed channels, timestamps, and message logging — mimicking how real-time trading feeds, telemetry services, or distributed chat systems work.

---

## 📦 Features

- Real-time **publisher-subscriber architecture**
- Multiple subscribers can listen to different **channels (topics)**
- Publisher selects a **fixed topic** and sends messages continuously
- Subscribers receive **only messages for their subscribed topic**
- Each message is **timestamped and user-tagged**
- Messages are **logged to local files** by subscribers
- Graceful shutdown with `Ctrl+C` support

---

## 🚀 Setup

### 🐍 Requirements
- Python 3.x
- ZeroMQ
- Install dependencies:

```
pip install pyzmq
```

---

## 📁 Project Structure

```
pubsub-chat/
├── publisher.py         # Sends messages to a fixed topic
├── subscriber.py        # Listens to a single topic and logs messages
├── README.md            # You're reading it
```

---

## 🔧 Usage

### ✅ Start a subscriber
```bash
python subscriber.py
```
You'll be asked to enter the **channel** to subscribe to (e.g. `news`, `tech`).

### ✅ Start a publisher
```bash
python publisher.py
```
You'll enter your **name** and the **channel** you want to publish to (should match what subscriber is listening for).

### ✅ Example Flow

**In Terminal 1 (subscriber):**
```
Enter channel to subscribe to (e.g. news): tech

📥 Subscribed to 'tech'. Listening for messages...

>> [12:05:31] Alice: Python 4.0 released!
```

**In Terminal 2 (publisher):**
```
Enter your name: Alice
Enter channel to publish to: tech
You: Python 4.0 released!
```

---

## 💡 How It Works

- **ZeroMQ PUB/SUB sockets** send messages prefixed by a topic (e.g. `tech`)
- **Subscribers use filters** to receive only messages from their chosen channel
- Each message includes:
  - Timestamp (`[12:05:31]`)
  - Sender name (`Alice`)
  - Content
- Messages are **printed and logged** to a file named `<channel>_log.txt`

---

## 🧠 Real-World Inspiration

This project simulates simplified versions of:

- **Market data feeds** in finance
- **Telemetry pipelines** in distributed systems
- **Room-based messaging** in chat infrastructure
- **Channel-based logging** in ops/dev tooling

---

## 📄 License

MIT License — free to use, extend, or modify.

---

> Built in < 2 hours to demonstrate real-time systems thinking and messaging infrastructure 💬
