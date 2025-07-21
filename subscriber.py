import zmq
import json
import logging
import sys
import os
from datetime import datetime
from collections import defaultdict, deque
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
import time

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
        self.topic = None
        
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
    

def create_layout() -> Layout:
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main"),
        Layout(size=5, name="footer"),
    )

    layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
    return layout

def generate_dashboard(stats: MessageStats, message_queue: deque) -> Panel:
    stats_data = stats.get_stats()

    # Create a table for statistics
    stats_table = Table(title="[bold cyan]Live Statistics[/bold cyan]", expand=True)
    stats_table.add_column("Metric", style="green")
    stats_table.add_column("Value", style="magenta")
    stats_table.add_row("Total Messages", str(stats_data['total_messages']))
    stats_table.add_row("Messages/Min", f"{stats_data['messages_per_minute']:.2f}")
    stats_table.add_row("Active Users", str(stats_data['active_users']))
    stats_table.add_row("Top User", str(stats_data['top_users']))

    message_list = "\n".join(message_queue)
    message_panel = Panel(
        message_list,
        title="[bold green]Live Message Feed[/bold green]",
        border_style="green",
        expand=True
    )

    dashboard_panel = Panel(
        stats_table,
        title="[bold yellow]Real-time Messaging Dashboard[/bold yellow]",
        subtitle=f"[bold blue]Subscribed to: {stats.topic}[/bold blue]" # We will add topic to stats
    )

    main_layout = Layout()
    main_layout.split_column(dashboard_panel, message_panel)
    return main_layout

def main():
    context = None
    socket = None
    stats = MessageStats()

    message_queue = deque(maxlen=10)

    try:
        context = zmq.Context()
        socket = context.socket(zmq.SUB)

        host = config['network']['host']
        port = config['network']['port']
        socket.connect(f"tcp://{host}:{port}")
        logger.info(f"Connected to tcp://{host}:{port}")

        topic = input("Enter exact channel to subscribe to (e.g. news): ").strip()
        if not topic:
            logger.error("Channel cannot be empty")
            sys.exit(1)


        stats.topic = topic
        socket.setsockopt_string(zmq.SUBSCRIBE, topic + " ")
        logger.info(f"Subscribed to channel '{topic}'")


        with Live(generate_dashboard(stats, message_queue), screen=True, auto_refresh=False) as live:
            log_file = f"{topic}_log.txt"
            with open(log_file, "a") as log:
                log.write(f"\n--- Session started at {datetime.now()} ---\n")

                while True:
                    try:
                        full_msg = socket.recv_string(zmq.NOBLOCK)
                        _, msg = full_msg.split(' ', 1)


                        try:
                            user_part = msg.split('] ')[1].split(': ')[0]
                            stats.update(user_part)
                        except:
                            stats.update("unknown")


                        message_queue.append(msg)


                        log.write(msg + "\n")
                        log.flush()


                        live.update(generate_dashboard(stats, message_queue), refresh=True)

                    except zmq.Again:

                        time.sleep(0.1)

                        live.update(generate_dashboard(stats, message_queue), refresh=True)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:

        print("\n--- Final Session Statistics ---")
        if stats.total_messages > 0:
            stats_data = stats.get_stats()
            print(f"   Total messages: {stats_data['total_messages']}")
            print(f"   Runtime: {stats_data['runtime_seconds']:.1f} seconds")
            # ... and so on

        if socket:
            socket.close()
        if context:
            context.term()
        print("\n❌ Subscriber exiting.")

if __name__ == "__main__":
    main()
