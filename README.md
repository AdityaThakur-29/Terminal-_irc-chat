# IRC-Style Terminal Chat Application

A lightweight, real-time chat application built entirely in Python using only the standard library. Features multiple chat rooms, private messaging, and a colorful terminal interface.

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 📸 Screenshots
```
╔═══════════════════════════════════════╗
║     IRC-Style Terminal Chat v1.0      ║
║      Type /help for commands          ║
╚═══════════════════════════════════════╝

[SERVER] Welcome to IRC Chat!
[SERVER] Alice joined #general
[#general] Alice: Hello everyone!
[#general] Bob: Hi Alice!
[PM from Charlie] Hey, check out #random!

You: _
```

## ✨ Features

### Core Features
- 💬 **Real-time multi-user chat**
- 🏠 **Multiple chat rooms (channels)**
- 📨 **Private messaging between users**
- 👤 **Custom nicknames**
- 🎨 **Colorful terminal UI**
- ⚡ **Thread-safe concurrent operations**

### Advanced Features
- 🚦 **Rate limiting** to prevent spam
- 🔒 **Input validation** for security
- 🎯 **IRC-style commands** (`/join`, `/msg`, etc.)
- 🧵 **Multi-threaded server** for scalability
- 🎭 **User presence** (join/leave notifications)
- 📊 **Room and user management**

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Windows, macOS, or Linux
- Terminal/Command Prompt

### Installation

1. **Clone or download the repository**
```bash
git clone https://github.com/yourusername/irc-chat.git
cd irc-chat
```

2. **Verify project structure**
```
irc-chat/
├── server/
│   ├── __init__.py
│   ├── server.py
│   ├── room_manager.py
│   └── rate_limiter.py
├── client/
│   ├── __init__.py
│   ├── client.py
│   └── ui.py
├── shared/
│   ├── __init__.py
│   ├── protocol.py
│   └── validators.py
├── config.py
├── requirements.txt
└── README.md
```

3. **No dependencies needed!** (Uses only Python standard library)

### Running the Application

#### Start the Server
```bash
# Navigate to project directory
cd irc-chat

# Start server
python server/server.py
```

**Expected output:**
```
==================================================
IRC-Style Terminal Chat Server
==================================================
[SERVER] IRC Terminal Chat v1.0
[SERVER] Listening on 127.0.0.1:6667
[SERVER] Press Ctrl+C to stop
```

#### Start the Client (New Terminal)
```bash
# Open a new terminal window
cd irc-chat

# Start client
python client/client.py
```

**Expected output:**
```
╔═══════════════════════════════════════╗
║     IRC-Style Terminal Chat v1.0      ║
║      Type /help for commands          ║
╚═══════════════════════════════════════╝
Connecting to 127.0.0.1:6667...
✓ Connected to server
Type /help for available commands
Tip: Set your nickname with /nick <name>

You: _
```

### First Steps

1. **Set your nickname:**
```
   You: /nick Alice
```

2. **You'll auto-join #general:**
```
   [SERVER] Nickname set to Alice
   [SERVER] Alice joined #general
```

3. **Start chatting:**
```
   You: Hello everyone!
```

4. **Open another terminal and connect a second client to chat with yourself!**

## 📖 Commands Reference

### User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/nick <name>` | Set your nickname | `/nick Alice` |
| `/join <room>` | Join/switch to a chat room | `/join random` |
| `/leave` | Leave current room | `/leave` |
| `/msg <user> <text>` | Send private message | `/msg Bob Hey there!` |
| `/users` | List users in current room | `/users` |
| `/rooms` | List all available rooms | `/rooms` |
| `/whoami` | Show your current info | `/whoami` |
| `/help` | Display help message | `/help` |
| `/clear` | Clear terminal screen | `/clear` |
| `/quit` | Disconnect from server | `/quit` |

### Command Aliases

- `/nick` = `/name`
- `/join` = `/j`
- `/leave` = `/part`
- `/msg` = `/pm` = `/whisper`
- `/users` = `/names` = `/who`
- `/rooms` = `/channels` = `/list`
- `/whoami` = `/me`
- `/help` = `/h` = `/?`
- `/quit` = `/exit`
- `/clear` = `/cls`

## 🎮 Usage Examples

### Basic Chat Session
```bash
# Terminal 1 - Alice
You: /nick Alice
[SERVER] Nickname set to Alice
[SERVER] Alice joined #general

You: Hello everyone!
[#general] Bob: Hi Alice!

You: /join random
[SERVER] Alice left #general
[SERVER] Alice joined #random
```
```bash
# Terminal 2 - Bob
You: /nick Bob
[SERVER] Nickname set to Bob
[SERVER] Bob joined #general

[#general] Alice: Hello everyone!
You: Hi Alice!

[SERVER] Alice left #general
```

### Private Messaging
```bash
# Alice sends PM to Bob
You: /msg Bob Want to join #random?
[PM to Bob] Want to join #random?

# Bob receives and replies
[PM from Alice] Want to join #random?
You: /msg Alice Sure!
[PM to Alice] Sure!
```

### Room Management
```bash
# List all rooms
You: /rooms
Available rooms:
  #general (2 users)
  #random (1 users)
  #help (0 users)

# List users in current room
You: /users
Users in #general: Alice, Bob, Charlie

# Check your info
You: /whoami
Your Info:
  Nickname: Alice
  Room: #general
  Address: 127.0.0.1:54321
```

## ⚙️ Configuration

Edit **`config.py`** to customize server settings:
```python
class Config:
    # Network settings
    HOST = '127.0.0.1'        # Server IP (0.0.0.0 for all interfaces)
    PORT = 6667               # Server port
    
    # Limits
    MAX_CLIENTS = 100                # Maximum concurrent users
    MAX_MESSAGE_LENGTH = 500         # Maximum message size
    MAX_NICKNAME_LENGTH = 20         # Maximum nickname length
    
    # Rate limiting
    MAX_MESSAGES_PER_MINUTE = 30     # Messages allowed per minute
    RATE_LIMIT_WINDOW = 60           # Rate limit time window (seconds)
    
    # Default rooms
    DEFAULT_ROOMS = ['general', 'random', 'help']
    AUTO_JOIN_ROOM = 'general'       # Room users join automatically
```

## 🌐 Network Usage

### Running on Local Network

To allow connections from other computers on your network:

1. **Edit `config.py`:**
```python
   HOST = '0.0.0.0'  # Listen on all network interfaces
```

2. **Find your IP address:**
```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   # or
   ip addr show
```

3. **Open firewall port (if needed):**
```bash
   # Linux (UFW)
   sudo ufw allow 6667
   
   # Windows
   # Go to Windows Defender Firewall > Advanced Settings > Inbound Rules
   # Create new rule for port 6667
```

4. **Start server:**
```bash
   python server/server.py
```

5. **Clients connect using your IP:**
```bash
   python client/client.py 192.168.1.100
```

### Running on Internet (Advanced)

⚠️ **Security Warning:** Running on the internet requires additional security measures!

1. **Port forwarding on router** (forward external port to internal port 6667)
2. **Use a domain name** or dynamic DNS service
3. **Consider adding:**
   - SSL/TLS encryption
   - Authentication system
   - Stronger rate limiting
   - IP whitelisting/blacklisting

## 🏗️ Architecture

### System Design
```
┌─────────────┐         ┌─────────────┐
│  Client A   │◄───────►│             │
├─────────────┤         │             │
│  Client B   │◄───────►│   SERVER    │
├─────────────┤         │             │
│  Client C   │◄───────►│             │
└─────────────┘         └─────────────┘
                              │
                              ▼
                        ┌──────────┐
                        │ Room Mgr │
                        │ Rate Lim │
                        │ Protocol │
                        └──────────┘
```

### Protocol

Custom text-based protocol format:
```
COMMAND:arg1:arg2:...\n

Examples:
NICK:Alice
JOIN:general
MSG:Hello everyone!
PM:Bob:Hey there!
```

### Threading Model

- **Server**: Main thread accepts connections, spawns handler thread per client
- **Client**: Main thread handles input, background thread receives messages

## 🧪 Testing

### Manual Testing
```bash
# Terminal 1: Start server
python server/server.py

# Terminal 2: Client 1
python client/client.py

# Terminal 3: Client 2
python client/client.py

# Terminal 4: Client 3
python client/client.py

# Test different features:
# - Multiple users chatting
# - Private messages
# - Room switching
# - User lists
```

### Stress Testing

Test with 50 concurrent clients:
```python
# stress_test.py
import socket
import threading

def test_client(client_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6667))
        s.send(f'NICK:User{client_id}\n'.encode())
        s.send(b'MSG:Hello from stress test!\n')
        s.recv(1024)
        s.close()
        print(f"Client {client_id} completed")
    except Exception as e:
        print(f"Client {client_id} failed: {e}")

# Run 50 clients
threads = []
for i in range(50):
    t = threading.Thread(target=test_client, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("Stress test complete!")
```

Run with: `python stress_test.py`

## 🐛 Troubleshooting

### Common Issues

#### "Connection refused"
**Problem:** Server not running or wrong port  
**Solution:**
```bash
# Check if server is running
# Check if port is already in use
netstat -an | grep 6667  # Linux/Mac
netstat -an | findstr 6667  # Windows

# Kill process using port (Linux/Mac)
lsof -ti:6667 | xargs kill

# Change port in config.py if needed
```

#### "Address already in use"
**Problem:** Another process is using port 6667  
**Solution:**
- Kill the other process
- Or change `PORT` in `config.py` to another port (e.g., 8000)

#### Client can't connect from another machine
**Problem:** Server only listening on localhost  
**Solution:**
- Change `HOST = '0.0.0.0'` in `config.py`
- Check firewall settings
- Verify IP address with `ipconfig` or `ifconfig`

#### Messages not appearing
**Problem:** Not joined a room or nickname not set  
**Solution:**
```bash
# Set nickname first
/nick YourName

# Join a room
/join general

# Verify status
/whoami
```

#### Colors not showing on Windows
**Problem:** Old Windows terminal doesn't support ANSI colors  
**Solution:**
- Use Windows Terminal (Windows 10+)
- Or use PowerShell
- Or modify `client/ui.py` to disable colors

#### Rate limit errors
**Problem:** Sending messages too fast  
**Solution:**
- Wait a few seconds
- Increase `MAX_MESSAGES_PER_MINUTE` in `config.py` for testing

## 🔧 Advanced Usage

### Running as Background Service

#### Linux (systemd)
```bash
# Create service file
sudo nano /etc/systemd/system/irc-chat.service
```
```ini
[Unit]
Description=IRC Terminal Chat Server
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/irc-chat
ExecStart=/usr/bin/python3 /path/to/irc-chat/server/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
# Enable and start
sudo systemctl enable irc-chat
sudo systemctl start irc-chat
sudo systemctl status irc-chat

# View logs
sudo journalctl -u irc-chat -f
```

#### Using Screen/Tmux
```bash
# Start in detached screen session
screen -dmS irc-chat python server/server.py

# Reattach to view
screen -r irc-chat

# Detach: Ctrl+A then D

# Or use tmux
tmux new -s irc-chat -d python server/server.py
tmux attach -t irc-chat
```

### Docker Deployment (Optional)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

EXPOSE 6667

CMD ["python", "server/server.py"]
```
```bash
# Build
docker build -t irc-chat .

# Run
docker run -p 6667:6667 irc-chat

# Run in background
docker run -d -p 6667:6667 --name irc-server irc-chat
```

## 🎓 Learning Outcomes

Building this project teaches:

- ✅ Socket programming (TCP/IP)
- ✅ Multi-threading and concurrency
- ✅ Client-server architecture
- ✅ Protocol design
- ✅ Input validation and security
- ✅ Terminal UI programming
- ✅ Error handling and debugging
- ✅ Code organization and modularity

## 🚀 Extension Ideas

### Beginner Extensions
- [ ] Add `/away` status
- [ ] Add room topics (`/topic`)
- [ ] Add message timestamps
- [ ] Add user colors
- [ ] Add sound notifications

### Intermediate Extensions
- [ ] User authentication (login/register)
- [ ] Persistent message history (SQLite)
- [ ] File transfer support
- [ ] Admin commands (kick, ban)
- [ ] Channel operators/moderators
- [ ] SSL/TLS encryption

### Advanced Extensions
- [ ] Web-based client (Flask + WebSockets)
- [ ] Voice chat integration
- [ ] Bot API for chatbots
- [ ] Redis for distributed servers
- [ ] PostgreSQL for scalability
- [ ] REST API for integrations
- [ ] Mobile app (React Native)

### Hackathon Ideas
- 🤖 **AI Chatbot Integration** - Add GPT-powered bot
- 🎮 **Gamification** - Points, badges, leaderboards
- 📊 **Analytics Dashboard** - Real-time statistics web app
- 🖼️ **Rich Media** - Image sharing, code highlighting
- 🌍 **Translation Bot** - Real-time message translation

## 📝 Project Structure
```
irc-chat/
├── server/                 # Server-side code
│   ├── __init__.py
│   ├── server.py          # Main server logic
│   ├── room_manager.py    # Room/channel management
│   └── rate_limiter.py    # Anti-spam rate limiting
├── client/                 # Client-side code
│   ├── __init__.py
│   ├── client.py          # Main client logic
│   └── ui.py              # Terminal UI utilities
├── shared/                 # Shared modules
│   ├── __init__.py
│   ├── protocol.py        # Protocol definitions
│   └── validators.py      # Input validation
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies (empty - no external deps!)
└── README.md             # This file
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the repository**
2. **Create a feature branch**
```bash
   git checkout -b feature/amazing-feature
```
3. **Make your changes**
4. **Test thoroughly**
5. **Commit your changes**
```bash
   git commit -m 'Add amazing feature'
```
6. **Push to your fork**
```bash
   git push origin feature/amazing-feature
```
7. **Open a Pull Request**

### Code Style
- Follow PEP 8
- Add docstrings to functions
- Include type hints where possible
- Write clear commit messages

## 📄 License

This project is licensed under the MIT License - see below:
```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👤 Author

**Your Name**
- GitHub: [AdityaThakur-29](https://github.com/AdityaThakur-29)
- LinkedIn: [Aditya Thakur](https://www.linkedin.com/in/aditya-thakur-901ab6392/)
- Email: adityathakur77749@gmail.com

## 🙏 Acknowledgments

- Inspired by the IRC protocol (RFC 1459)
- Built with Python's powerful socket and threading libraries
- Thanks to the open-source community

## 📚 Additional Resources

- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [IRC Protocol RFC 1459](https://tools.ietf.org/html/rfc1459)
- [Terminal Colors (ANSI)](https://en.wikipedia.org/wiki/ANSI_escape_code)

## 💡 Tips for Resume/Portfolio

Describe this project on your resume as:

> **IRC-Style Terminal Chat Application**  
> Developed a scalable multi-threaded TCP chat server in Python supporting 100+ concurrent users. Implemented custom text-based protocol, room-based architecture, private messaging, rate limiting, and thread-safe operations. Features include real-time message broadcasting, input validation, and colorful terminal UI.  
> *Technologies: Python, Sockets, TCP/IP, Threading, Protocol Design*

---

## 🎉 Getting Help

- **Issues:** Open an issue on GitHub
- **Questions:** Check existing issues or start a discussion
- **Community:** Join our chat server! (If you deploy one publicly)

**Happy Chatting! 💬**