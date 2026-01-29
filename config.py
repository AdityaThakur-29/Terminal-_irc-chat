"""
Configuration settings for IRC chat
"""

import os


class Config:
    """Server configuration"""

    # Network settings
    HOST = os.getenv('IRC_HOST', '127.0.0.1')  # localhost for dev
    PORT = int(os.getenv('IRC_PORT', 6667))

    # Limits
    MAX_CLIENTS = 100
    MAX_MESSAGE_LENGTH = 500
    MAX_NICKNAME_LENGTH = 20

    # Rate limiting
    MAX_MESSAGES_PER_MINUTE = 30
    RATE_LIMIT_WINDOW = 60  # seconds

    # Default rooms
    DEFAULT_ROOMS = ['general', 'random', 'help']
    AUTO_JOIN_ROOM = 'general'

    # Server info
    SERVER_NAME = "IRC Terminal Chat"
    VERSION = "1.0.0"
    MOTD = """
╔═══════════════════════════════════════╗
║     IRC-Style Terminal Chat v1.0      ║
║      Type /help for commands          ║
╚═══════════════════════════════════════╝
"""