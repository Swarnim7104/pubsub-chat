import zmq
import json
import logging
import sys
import os
from datetime import datetime
from collections import defaultdict

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "network": {"host": "localhost", "port": 5555},
            "logging": {"level": "INFO", "file": "subscriber.log"}
        }

config = load_config()

# Setup logging
logging.basicConfig(
    level=getattr(logging, config['logging']['level']),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config['logging']['file']),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MessageStats:
    def __init__(self):
        self.total_messages = 0
        self.messages_by_user = defaultdict(int)
        self.start_time = datetime.now()
        
    def update(self, user):
        self.total_messages += 1
        self.messages_by_user[user] += 1
        
    def get_stats(self):
        runtime = datetime.now() - self.start_time
        return {
            "total_messages": self.total_messages,
            "runtime_seconds": runtime.total_seconds(),
            "messages_per_minute": self.total_messages / max(runtime.total_seconds() / 60, 1),
            "active_users": len(self.messages_by_user),
            "top_users": dict(sorted(self.messages_by_user.items(), 
                                   key=lambda x: x[1], reverse=True)[:5])
        }

def main():
    context = None
    socket = None
    stats = MessageStats()
    
    try:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        
        # Connect using config
        host = config['network']['host']
        port = config['network']['port']
        socket.connect(f"tcp://{host}:{port}")
        logger.info(f"Connected to tcp://{host}:{port}")

        topic = input("Enter exact channel to subscribe to (e.g. news): ").strip()
        if not topic:
            logger.error("Channel cannot be empty")
            sys.exit(1)
            
        socket.setsockopt_string(zmq.SUBSCRIBE, topic + " ")
        logger.info(f"Subscribed to channel '{topic}'")
        
        print(f"\n📥 Subscribed to '{topic}'. Listening for messages...")
        print("📊 Press Ctrl+C to see statistics and exit.\n")

        log_file = f"{topic}_log.txt"
        with open(log_file, "a") as log:
            log.write(f"\n--- Session started at {datetime.now()} ---\n")
            
            while True:
                try:
                    full_msg = socket.recv_string(zmq.NOBLOCK)
                    _, msg = full_msg.split(' ', 1)
                    
                    # Extract user from message format: [timestamp] user: content
                    try:
                        user_part = msg.split('] ')[1].split(': ')[0]
                        stats.update(user_part)
                    except:
                        stats.update("unknown")
                    
                    print(f">> {msg}")
                    log.write(msg + "\n")
                    log.flush()
                    
                except zmq.Again:
                    # No message available
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Show statistics
        if stats.total_messages > 0:
            stats_data = stats.get_stats()
            print(f"\n📊 Session Statistics:")
            print(f"   Total messages: {stats_data['total_messages']}")
            print(f"   Runtime: {stats_data['runtime_seconds']:.1f} seconds")
            print(f"   Rate: {stats_data['messages_per_minute']:.1f} msg/min")
            print(f"   Active users: {stats_data['active_users']}")
            if stats_data['top_users']:
                print(f"   Top users: {stats_data['top_users']}")
        
        # Cleanup
        if socket:
            socket.close()
            logger.info("Socket closed")
        if context:
            context.term()
            logger.info("Context terminated")
        
        print("\n❌ Subscriber exiting.")

if __name__ == "__main__":
    main()