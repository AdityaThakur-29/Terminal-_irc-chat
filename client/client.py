"""
IRC-style chat client with private room support
"""

import socket
import threading
import sys
import os

# Add parent directory to Python path to find modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import from parent directory
from config import Config
from shared.protocol import Protocol

# Import from same directory (client/)
sys.path.insert(0, current_dir)
from ui import TerminalUI, Colors

class ChatClient:
    """Chat client for IRC-style terminal chat with private room support"""

    def __init__(self, host=Config.HOST, port=Config.PORT):
        """
        Initialize chat client

        Args:
            host (str): Server hostname or IP
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.ui = TerminalUI()
        self.nickname = None
        self.current_room = None

    def connect(self):
        """
        Connect to chat server

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            print(f"{Colors.GREEN}✓ Connected to server{Colors.RESET}")
            return True
        except ConnectionRefusedError:
            print(f"{Colors.RED}✗ Connection refused. Is the server running?{Colors.RESET}")
            return False
        except socket.gaierror:
            print(f"{Colors.RED}✗ Invalid hostname or IP address{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to connect: {e}{Colors.RESET}")
            return False

    def disconnect(self):
        """Disconnect from server gracefully"""
        self.running = False
        if self.socket:
            try:
                # Send quit command
                quit_msg = Protocol.encode(Protocol.CMD_QUIT)
                self.socket.send(quit_msg.encode('utf-8'))
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None

    def receive_messages(self):
        """
        Receive messages from server in background thread
        This runs continuously until disconnected
        """
        while self.running:
            try:
                # Set timeout so we can check self.running periodically
                self.socket.settimeout(1.0)
                data = self.socket.recv(1024)

                # Empty data means server closed connection
                if not data:
                    print(f"\n{Colors.RED}✗ Disconnected from server{Colors.RESET}")
                    self.running = False
                    break

                # Decode and strip message
                message = data.decode('utf-8').strip()

                # Handle special server messages
                if message == "SERVER_FULL":
                    print(f"\n{Colors.RED}✗ Server is full. Try again later.{Colors.RESET}")
                    self.running = False
                    break

                if message == "SERVER_SHUTDOWN":
                    print(f"\n{Colors.YELLOW}⚠ Server is shutting down{Colors.RESET}")
                    self.running = False
                    break

                # Print received message with color
                if message:
                    # Clear current input line
                    print(f"\r{' ' * 100}\r", end='')

                    # Print the message with colors
                    self.ui.print_message(message)

                    # Redisplay input prompt
                    print(f"{Colors.BRIGHT_GREEN}You: {Colors.RESET}", end='', flush=True)

            except socket.timeout:
                # Timeout is normal, just check if we should continue
                continue

            except OSError:
                # Socket was closed
                if self.running:
                    print(f"\n{Colors.RED}✗ Connection lost{Colors.RESET}")
                break

            except Exception as e:
                if self.running:
                    print(f"\n{Colors.RED}✗ Error receiving message: {e}{Colors.RESET}")
                break

        # Ensure we stop the main loop
        self.running = False

    def send_message(self, message):
        """
        Send message to server

        Args:
            message (str): Message to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if not self.socket:
                print(f"{Colors.RED}Not connected to server{Colors.RESET}")
                return False

            # Parse and process command
            if message.startswith('/'):
                processed = self.process_command(message)
                if processed is None:
                    # Command was handled client-side or had an error
                    return True
                # Send processed command to server
                self.socket.send(processed.encode('utf-8'))
            else:
                # Regular message - send to current room
                msg = Protocol.encode(Protocol.CMD_MSG, message)
                self.socket.send(msg.encode('utf-8'))

            return True

        except BrokenPipeError:
            print(f"\n{Colors.RED}✗ Connection broken{Colors.RESET}")
            self.running = False
            return False

        except Exception as e:
            print(f"{Colors.RED}✗ Failed to send message: {e}{Colors.RESET}")
            return False

    def process_command(self, message):
        """
        Process client-side commands

        Args:
            message (str): Command message starting with /

        Returns:
            str or None: Encoded protocol message to send to server, or None if handled locally
        """
        # Remove leading / and split into command and arguments
        parts = message[1:].split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ''

        # Quit command
        if cmd == 'quit' or cmd == 'exit':
            return Protocol.encode(Protocol.CMD_QUIT)

        # Set nickname
        elif cmd == 'nick' or cmd == 'name':
            if not args:
                print(f"{Colors.YELLOW}Usage: /nick <nickname>{Colors.RESET}")
                return None
            self.nickname = args
            return Protocol.encode(Protocol.CMD_NICK, args)

        # Join room (with optional password)
        elif cmd == 'join' or cmd == 'j':
            if not args:
                print(f"{Colors.YELLOW}Usage: /join <room>[:password]{Colors.RESET}")
                print(f"{Colors.CYAN}Example: /join myroom:secretpass{Colors.RESET}")
                return None
            # Remove # if user included it
            room = args.lstrip('#')
            self.current_room = room.split(':')[0]  # Store room name without password
            return Protocol.encode(Protocol.CMD_JOIN, room)

        # Leave room
        elif cmd == 'leave' or cmd == 'part':
            self.current_room = None
            return Protocol.encode(Protocol.CMD_LEAVE)

        # Private message
        elif cmd == 'msg' or cmd == 'pm' or cmd == 'whisper' or cmd == 'w':
            if not args or ' ' not in args:
                print(f"{Colors.YELLOW}Usage: /msg <user> <message>{Colors.RESET}")
                print(f"{Colors.CYAN}Example: /msg Alice Hello there!{Colors.RESET}")
                return None
            user, text = args.split(' ', 1)
            return Protocol.encode(Protocol.CMD_PM, f"{user}:{text}")

        # Create private room
        elif cmd == 'create' or cmd == 'createroom':
            if not args:
                print(f"{Colors.YELLOW}Usage: /create <room> [password] [topic]{Colors.RESET}")
                print(f"{Colors.CYAN}Examples:{Colors.RESET}")
                print(f"  /create myroom")
                print(f"  /create myroom:password123")
                print(f"  /create myroom:pass123:Private discussions")
                return None
            return Protocol.encode(Protocol.CMD_CREATE, args)

        # Invite user to room
        elif cmd == 'invite' or cmd == 'inv':
            if not args:
                print(f"{Colors.YELLOW}Usage: /invite <user> [room]{Colors.RESET}")
                print(f"{Colors.CYAN}Examples:{Colors.RESET}")
                print(f"  /invite Alice")
                print(f"  /invite Bob:myroom")
                return None
            return Protocol.encode(Protocol.CMD_INVITE, args)

        # Kick user from room
        elif cmd == 'kick':
            if not args:
                print(f"{Colors.YELLOW}Usage: /kick <user> [room]{Colors.RESET}")
                print(f"{Colors.CYAN}Example: /kick Bob{Colors.RESET}")
                return None
            return Protocol.encode(Protocol.CMD_KICK, args)

        # Ban user from room
        elif cmd == 'ban':
            if not args:
                print(f"{Colors.YELLOW}Usage: /ban <user> [room]{Colors.RESET}")
                print(f"{Colors.CYAN}Example: /ban Spammer{Colors.RESET}")
                return None
            return Protocol.encode(Protocol.CMD_BAN, args)

        # Set room password
        elif cmd == 'password' or cmd == 'setpass' or cmd == 'passwd':
            if not args:
                print(f"{Colors.YELLOW}Usage: /password <password> [room]{Colors.RESET}")
                print(f"{Colors.CYAN}Examples:{Colors.RESET}")
                print(f"  /password newpass123")
                print(f"  /password secret:myroom")
                return None
            return Protocol.encode(Protocol.CMD_SETPASS, args)

        # Make room private
        elif cmd == 'private' or cmd == 'lock':
            print(f"{Colors.CYAN}Making room private (invite-only)...{Colors.RESET}")
            return Protocol.encode(Protocol.CMD_PRIVATE, args)

        # Make room public
        elif cmd == 'public' or cmd == 'unlock':
            print(f"{Colors.CYAN}Making room public...{Colors.RESET}")
            return Protocol.encode(Protocol.CMD_PUBLIC, args)

        # Room info
        elif cmd == 'roominfo' or cmd == 'info' or cmd == 'room':
            return Protocol.encode(Protocol.CMD_ROOMINFO, args)

        # List users in current room
        elif cmd == 'users' or cmd == 'names' or cmd == 'who':
            return Protocol.encode(Protocol.CMD_USERS)

        # List all rooms
        elif cmd == 'rooms' or cmd == 'channels' or cmd == 'list':
            return Protocol.encode(Protocol.CMD_ROOMS)

        # Show user info
        elif cmd == 'whoami' or cmd == 'me':
            return Protocol.encode(Protocol.CMD_WHOAMI)

        # Help
        elif cmd == 'help' or cmd == 'h' or cmd == '?' or cmd == 'commands':
            return Protocol.encode(Protocol.CMD_HELP)

        # Clear screen (client-side only)
        elif cmd == 'clear' or cmd == 'cls':
            self.ui.clear_screen()
            self.ui.print_banner()
            if self.nickname:
                print(f"{Colors.CYAN}Logged in as: {self.nickname}{Colors.RESET}")
            if self.current_room:
                print(f"{Colors.CYAN}Current room: #{self.current_room}{Colors.RESET}")
            print()
            return None

        # Quick help (client-side)
        elif cmd == 'quickhelp' or cmd == 'qh':
            self.show_quick_help()
            return None

        # Unknown command
        else:
            print(f"{Colors.RED}✗ Unknown command: /{cmd}{Colors.RESET}")
            print(f"{Colors.YELLOW}Type /help for list of commands{Colors.RESET}")
            return None

    def show_quick_help(self):
        """Show quick help reference (client-side)"""
        help_text = f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║         QUICK COMMAND REFERENCE        ║
╚════════════════════════════════════════╝{Colors.RESET}

{Colors.BRIGHT_GREEN}BASIC:{Colors.RESET}
  /nick <name>              Set nickname
  /join <room>[:pass]       Join room
  /msg <user> <text>        Private message
  /rooms                    List rooms
  /help                     Full help

{Colors.BRIGHT_MAGENTA}PRIVATE ROOMS:{Colors.RESET}
  /create <room> [pass]     Create private room
  /invite <user>            Invite to room
  /roominfo                 Show room details
  /password <pass>          Set room password

{Colors.BRIGHT_CYAN}MANAGEMENT:{Colors.RESET}
  /kick <user>              Kick user (owner)
  /private                  Make room private (owner)
  /public                   Make room public (owner)

{Colors.YELLOW}TIP: Type /help for detailed explanations{Colors.RESET}
"""
        print(help_text)

    def run(self):
        """Main client loop - handles user input and manages connection"""

        # Clear screen and show banner
        self.ui.clear_screen()
        self.ui.print_banner()

        # Display connection info
        print(f"{Colors.CYAN}Connecting to {self.host}:{self.port}...{Colors.RESET}")

        # Connect to server
        if not self.connect():
            return

        print(f"{Colors.GREEN}Type /help for available commands{Colors.RESET}")
        print(f"{Colors.YELLOW}Tip: Set your nickname with /nick <name>{Colors.RESET}")
        print(f"{Colors.CYAN}Quick help: /quickhelp or /qh{Colors.RESET}\n")

        # Start background thread to receive messages
        receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True,
            name="ReceiveThread"
        )
        receive_thread.start()

        # Main input loop
        try:
            while self.running:
                try:
                    # Get user input
                    message = self.ui.get_input()

                    # Skip empty messages
                    if not message or message.isspace():
                        continue

                    # Handle quit command
                    if message.strip() == '/quit' or message.strip() == '/exit':
                        print(f"{Colors.YELLOW}Disconnecting...{Colors.RESET}")
                        break

                    # Send message to server
                    if not self.send_message(message):
                        # Failed to send, likely disconnected
                        break

                except KeyboardInterrupt:
                    # User pressed Ctrl+C
                    print(f"\n{Colors.YELLOW}Interrupted{Colors.RESET}")
                    break

                except EOFError:
                    # End of input (Ctrl+D on Unix)
                    break

        finally:
            # Cleanup
            print(f"\n{Colors.YELLOW}Disconnecting...{Colors.RESET}")
            self.disconnect()

            # Wait briefly for receive thread to finish
            if receive_thread.is_alive():
                receive_thread.join(timeout=2)

            print(f"{Colors.GREEN}✓ Disconnected. Goodbye!{Colors.RESET}")

def main():
    """
    Main entry point for chat client
    Parses command line arguments and starts client
    """
    # Default values
    host = Config.HOST
    port = Config.PORT

    # Parse command line arguments
    if len(sys.argv) > 1:
        # Check for help flag first
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_usage()
            sys.exit(0)

        # First argument is host
        host = sys.argv[1]

    if len(sys.argv) > 2:
        # Second argument is port
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"{Colors.RED}Invalid port number: {sys.argv[2]}{Colors.RESET}")
            print(f"{Colors.YELLOW}Usage: python client.py [host] [port]{Colors.RESET}")
            sys.exit(1)

    # Create and run client
    try:
        client = ChatClient(host, port)
        client.run()
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.RESET}")
        sys.exit(1)

def show_usage():
    """Display usage information"""
    print(f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║   IRC-Style Terminal Chat Client       ║
╚════════════════════════════════════════╝{Colors.RESET}

{Colors.BRIGHT_GREEN}USAGE:{Colors.RESET}
    python client/client.py [host] [port]

{Colors.BRIGHT_GREEN}ARGUMENTS:{Colors.RESET}
    host    Server hostname or IP address (default: 127.0.0.1)
    port    Server port number (default: 6667)

{Colors.BRIGHT_GREEN}EXAMPLES:{Colors.RESET}
    python client/client.py
        → Connect to localhost:6667
    
    python client/client.py 192.168.1.100
        → Connect to 192.168.1.100:6667
    
    python client/client.py 192.168.1.100 8000
        → Connect to 192.168.1.100:8000

{Colors.BRIGHT_GREEN}BASIC COMMANDS:{Colors.RESET}
    /nick <name>              Set your nickname
    /join <room>[:password]   Join a chat room
    /msg <user> <text>        Send private message
    /users                    List users in room
    /rooms                    List all rooms
    /help                     Show all commands
    /quit                     Disconnect

{Colors.BRIGHT_MAGENTA}PRIVATE ROOM COMMANDS:{Colors.RESET}
    /create <room> [pass] [topic]   Create a private room
    /invite <user> [room]           Invite user to private room
    /kick <user> [room]             Kick user from room
    /password <pass> [room]         Set room password
    /private [room]                 Make room private
    /roominfo [room]                Show room details

{Colors.BRIGHT_GREEN}EXAMPLES:{Colors.RESET}
    {Colors.CYAN}# Create a private room with password{Colors.RESET}
    /create myroom secretpass Private discussions
    
    {Colors.CYAN}# Join room with password{Colors.RESET}
    /join myroom:secretpass
    
    {Colors.CYAN}# Invite someone to your room{Colors.RESET}
    /invite Alice
    
    {Colors.CYAN}# Make a room invite-only{Colors.RESET}
    /private myroom
    
    {Colors.CYAN}# Send private message{Colors.RESET}
    /msg Bob Hey, want to join #myroom?

{Colors.YELLOW}For more help, connect to the server and type /help{Colors.RESET}
""")

if __name__ == "__main__":
    main()