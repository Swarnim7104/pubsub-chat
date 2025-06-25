import zmq
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('publisher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    context = None
    socket = None
    
    try:
        # Setup context and PUB socket
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:5555")
        logger.info("Publisher socket bound to tcp://*:5555")

        # Get sender name and fixed topic
        name = input("Enter your name: ").strip()
        if not name:
            logger.error("Name cannot be empty")
            sys.exit(1)
            
        channel = input("Enter channel to publish to (e.g. news, tech): ").strip()
        if not channel:
            logger.error("Channel cannot be empty")
            sys.exit(1)

        logger.info(f"Publisher '{name}' started on channel '{channel}'")
        print(f"\n📢 Publisher started on channel '{channel}'. Use Ctrl+C to exit.\n")

        message_count = 0
        while True:
            try:
                msg = input("You: ").strip()
                if not msg:
                    continue
                    
                ts = datetime.now().strftime("%H:%M:%S")
                full_msg = f"[{ts}] {name}: {msg}"
                
                socket.send_string(f"{channel} {full_msg}")
                message_count += 1
                logger.debug(f"Sent message #{message_count} to channel '{channel}'")
                
            except EOFError:
                logger.info("EOF received, shutting down")
                break
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Cleanup
        if socket:
            socket.close()
            logger.info("Socket closed")
        if context:
            context.term()
            logger.info("Context terminated")
        
        if 'message_count' in locals():
            logger.info(f"Publisher exiting. Total messages sent: {message_count}")
        print("\n❌ Publisher exiting.")

if __name__ == "__main__":
    main()