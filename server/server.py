"""
IRC-style chat server
"""

import socket
import threading
import sys
import signal
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from shared.protocol import Protocol
from shared.validators import InputValidator
from room_manager import RoomManager  # Changed from server.room_manager
from rate_limiter import RateLimiter  # Changed from server.rate_limiter




class ChatServer:
    """Main chat server"""

    def __init__(self):
        self.host = Config.HOST
        self.port = Config.PORT
        self.clients = {}  # {socket: {nickname, address}}
        self.clients_lock = threading.Lock()
        self.room_manager = RoomManager()
        self.rate_limiter = RateLimiter(
            Config.MAX_MESSAGES_PER_MINUTE,
            Config.RATE_LIMIT_WINDOW
        )
        self.running = False
        self.server_socket = None

        # Create default rooms
        for room in Config.DEFAULT_ROOMS:
            self.room_manager.create_room(room)

        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n[SERVER] Shutting down gracefully...")
        self.shutdown()
        sys.exit(0)

    def start(self):
        """Start the server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[SERVER] {Config.SERVER_NAME} v{Config.VERSION}")
            print(f"[SERVER] Listening on {self.host}:{self.port}")
            print(f"[SERVER] Press Ctrl+C to stop")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()

                    # Check if server is full
                    with self.clients_lock:
                        if len(self.clients) >= Config.MAX_CLIENTS:
                            client_socket.send(b"SERVER_FULL\n")
                            client_socket.close()
                            continue

                    # Handle client in new thread
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    thread.start()

                except Exception as e:
                    if self.running:
                        print(f"[ERROR] Accept failed: {e}")

        except Exception as e:
            print(f"[ERROR] Server failed to start: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown server gracefully"""
        self.running = False

        # Close all client connections
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.send(b"SERVER_SHUTDOWN\n")
                    client_socket.close()
                except:
                    pass
            self.clients.clear()

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("[SERVER] Shutdown complete")

    def handle_client(self, client_socket, address):
        """Handle a single client connection"""
        nickname = None

        try:
            # Send welcome message
            client_socket.send(Config.MOTD.encode('utf-8'))
            welcome = Protocol.encode(
                Protocol.RPL_WELCOME,
                "Welcome! Please set your nickname with /nick <name>"
            )
            client_socket.send(welcome.encode('utf-8'))

            # Main message loop
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode('utf-8').strip()
                if not message:
                    continue

                command, args = Protocol.decode(message)

                # Handle commands
                if command == Protocol.CMD_NICK:
                    nickname = self.handle_nick(client_socket, address, args, nickname)

                elif command == Protocol.CMD_JOIN:
                    self.handle_join(client_socket, nickname, args)

                elif command == Protocol.CMD_LEAVE:
                    self.handle_leave(client_socket, nickname)

                elif command == Protocol.CMD_MSG:
                    self.handle_message(client_socket, nickname, args)

                elif command == Protocol.CMD_PM:
                    self.handle_pm(client_socket, nickname, args)

                elif command == Protocol.CMD_USERS:
                    self.handle_users(client_socket, nickname)

                elif command == Protocol.CMD_ROOMS:
                    self.handle_rooms(client_socket)

                elif command == Protocol.CMD_WHOAMI:
                    self.handle_whoami(client_socket, nickname, address)

                elif command == Protocol.CMD_HELP:
                    self.handle_help(client_socket)

                elif command == Protocol.CMD_QUIT:
                    break

                else:
                    # Treat unknown commands as messages
                    self.handle_message(client_socket, nickname, message)

        except Exception as e:
            print(f"[ERROR] Client handler error: {e}")

        finally:
            # Cleanup
            if nickname:
                # Leave all rooms
                self.room_manager.leave_all_rooms(nickname)

                # Announce departure
                room = self.room_manager.get_user_room(nickname)
                if room:
                    self.broadcast_to_room(
                        room,
                        f"[SERVER] {nickname} has left",
                        client_socket
                    )

                # Remove from clients
                with self.clients_lock:
                    if client_socket in self.clients:
                        del self.clients[client_socket]

                print(f"[DISCONNECT] {nickname} ({address[0]}:{address[1]})")

            try:
                client_socket.close()
            except:
                pass

    def handle_nick(self, client_socket, address, nickname, old_nickname):
        """Handle nickname command"""
        nickname = nickname.strip()

        # Validate nickname
        is_valid, error = InputValidator.validate_nickname(nickname)
        if not is_valid:
            error_msg = Protocol.encode(Protocol.RPL_NICKERR, error)
            client_socket.send(error_msg.encode('utf-8'))
            return old_nickname

        # Check if taken
        with self.clients_lock:
            taken = any(
                info['nickname'] == nickname
                for info in self.clients.values()
            )

        if taken:
            error_msg = Protocol.encode(
                Protocol.RPL_NICKERR,
                "Nickname already in use"
            )
            client_socket.send(error_msg.encode('utf-8'))
            return old_nickname

        # Set nickname
        with self.clients_lock:
            self.clients[client_socket] = {
                'nickname': nickname,
                'address': address
            }

        # Confirm
        confirm = Protocol.encode(Protocol.RPL_NICKOK, f"Nickname set to {nickname}")
        client_socket.send(confirm.encode('utf-8'))

        # Auto-join default room if first time
        if not old_nickname:
            self.room_manager.join_room(nickname, Config.AUTO_JOIN_ROOM)
            self.broadcast_to_room(
                Config.AUTO_JOIN_ROOM,
                f"[SERVER] {nickname} has joined #{Config.AUTO_JOIN_ROOM}",
                client_socket
            )
            print(f"[CONNECT] {nickname} ({address[0]}:{address[1]})")
        else:
            # Announce name change
            room = self.room_manager.get_user_room(nickname)
            if room:
                self.broadcast_to_room(
                    room,
                    f"[SERVER] {old_nickname} is now known as {nickname}",
                    client_socket
                )

        return nickname

    def handle_join(self, client_socket, nickname, room_name):
        """Handle join room command"""
        if not nickname:
            client_socket.send(b"Set nickname first with /nick <name>\n")
            return

        room_name = InputValidator.sanitize_room_name(room_name)
        if not room_name:
            client_socket.send(b"Invalid room name\n")
            return

        # Get old room
        old_room = self.room_manager.get_user_room(nickname)

        # Join new room
        self.room_manager.join_room(nickname, room_name)

        # Announce in old room
        if old_room and old_room != room_name:
            self.broadcast_to_room(
                old_room,
                f"[SERVER] {nickname} left #{old_room}",
                client_socket
            )

        # Announce in new room
        self.broadcast_to_room(
            room_name,
            f"[SERVER] {nickname} joined #{room_name}",
            client_socket
        )

        # Send confirmation with user list
        users = self.room_manager.get_room_users(room_name)
        msg = Protocol.encode(
            Protocol.RPL_JOINED,
            room_name,
            f"Users in #{room_name}: {', '.join(users)}"
        )
        client_socket.send(msg.encode('utf-8'))

    def handle_leave(self, client_socket, nickname):
        """Handle leave room command"""
        if not nickname:
            return

        room = self.room_manager.get_user_room(nickname)
        if room:
            self.room_manager.leave_all_rooms(nickname)
            self.broadcast_to_room(
                room,
                f"[SERVER] {nickname} left #{room}",
                client_socket
            )
            client_socket.send(f"Left #{room}\n".encode('utf-8'))

    def handle_message(self, client_socket, nickname, message):
        """Handle chat message"""
        if not nickname:
            client_socket.send(b"Set nickname first with /nick <name>\n")
            return

        # Check rate limit
        if not self.rate_limiter.is_allowed(nickname):
            wait_time = self.rate_limiter.get_wait_time(nickname)
            error = Protocol.encode(
                Protocol.ERR_RATELIMIT,
                f"Rate limit exceeded. Wait {wait_time}s"
            )
            client_socket.send(error.encode('utf-8'))
            return

        # Validate message
        is_valid, cleaned = InputValidator.validate_message(message)
        if not is_valid:
            client_socket.send(f"Error: {cleaned}\n".encode('utf-8'))
            return

        # Get current room
        room = self.room_manager.get_user_room(nickname)
        if not room:
            client_socket.send(b"Join a room first with /join <room>\n")
            return

        # Broadcast to room
        self.broadcast_to_room(
            room,
            f"[#{room}] {nickname}: {cleaned}",
            client_socket
        )

    def handle_pm(self, client_socket, nickname, args):
        """Handle private message"""
        if not nickname:
            client_socket.send(b"Set nickname first with /nick <name>\n")
            return

        # Parse: recipient:message
        if ':' not in args:
            client_socket.send(b"Usage: /msg <user> <message>\n")
            return

        recipient, message = args.split(':', 1)
        recipient = recipient.strip()

        # Find recipient socket
        recipient_socket = None
        with self.clients_lock:
            for sock, info in self.clients.items():
                if info['nickname'] == recipient:
                    recipient_socket = sock
                    break

        if not recipient_socket:
            error = Protocol.encode(Protocol.ERR_NOUSER, f"User {recipient} not found")
            client_socket.send(error.encode('utf-8'))
            return

        # Send PM
        pm_msg = f"[PM from {nickname}] {message}"
        try:
            recipient_socket.send(pm_msg.encode('utf-8'))
            # Confirm to sender
            client_socket.send(f"[PM to {recipient}] {message}".encode('utf-8'))
        except:
            client_socket.send(b"Failed to send PM\n")

    def handle_users(self, client_socket, nickname):
        """Handle list users command"""
        if not nickname:
            return

        room = self.room_manager.get_user_room(nickname)
        if not room:
            client_socket.send(b"You are not in any room\n")
            return

        users = self.room_manager.get_room_users(room)
        msg = Protocol.encode(
            Protocol.RPL_USERLIST,
            f"Users in #{room}: {', '.join(users)}"
        )
        client_socket.send(msg.encode('utf-8'))

    def handle_rooms(self, client_socket):
        """Handle list rooms command"""
        rooms = self.room_manager.list_rooms()
        if not rooms:
            client_socket.send(b"No rooms available\n")
            return

        rooms_str = '\n'.join(
            f"  #{name} ({info['count']} users)"
            for name, info in sorted(rooms.items())
        )
        msg = Protocol.encode(Protocol.RPL_ROOMLIST, f"Available rooms:\n{rooms_str}")
        client_socket.send(msg.encode('utf-8'))

    def handle_whoami(self, client_socket, nickname, address):
        """Handle whoami command"""
        if not nickname:
            client_socket.send(b"Nickname not set\n")
            return

        room = self.room_manager.get_user_room(nickname)
        info = f"""Your Info:
  Nickname: {nickname}
  Room: #{room or 'none'}
  Address: {address[0]}:{address[1]}"""

        msg = Protocol.encode(Protocol.RPL_INFO, info)
        client_socket.send(msg.encode('utf-8'))

    def handle_help(self, client_socket):
        """Handle help command"""
        help_text = """
Available Commands:
  /nick <name>        Set your nickname
  /join <room>        Join a chat room
  /leave              Leave current room
  /msg <user> <text>  Send private message
  /users              List users in current room
  /rooms              List all rooms
  /whoami             Show your info
  /help               Show this help
  /quit               Disconnect

Tips:
  - Messages without / are sent to your current room
  - Room names are case-insensitive
  - Use /join to switch between rooms
"""
        client_socket.send(help_text.encode('utf-8'))

    def broadcast_to_room(self, room_name, message, sender_socket=None):
        """Broadcast message to all users in room except sender"""
        users_in_room = self.room_manager.get_room_users(room_name)

        with self.clients_lock:
            for client_socket, client_info in self.clients.items():
                if client_info['nickname'] in users_in_room:
                    if client_socket != sender_socket:
                        try:
                            client_socket.send((message + '\n').encode('utf-8'))
                        except:
                            pass


def main():
    """Main entry point"""
    server = ChatServer()
    server.start()


if __name__ == "__main__":
    main()