"""
Protocol definitions for IRC-style chat
"""


class Protocol:
    """Message format and command definitions"""

    # Client → Server commands
    CMD_NICK = "NICK"  # Set nickname
    CMD_JOIN = "JOIN"  # Join room
    CMD_LEAVE = "LEAVE"  # Leave room
    CMD_MSG = "MSG"  # Send message to room
    CMD_PM = "PM"  # Private message
    CMD_USERS = "USERS"  # List users in room
    CMD_ROOMS = "ROOMS"  # List all rooms
    CMD_WHOAMI = "WHOAMI"  # Get user info
    CMD_HELP = "HELP"  # Get help
    CMD_QUIT = "QUIT"  # Disconnect

    # Server → Client responses
    RPL_WELCOME = "001"  # Welcome message
    RPL_NICKOK = "002"  # Nickname accepted
    RPL_NICKERR = "003"  # Nickname rejected
    RPL_USERLIST = "004"  # User list
    RPL_JOINED = "005"  # Successfully joined room
    RPL_ROOMLIST = "006"  # Room list
    RPL_PM = "007"  # Private message received
    RPL_INFO = "008"  # User info

    ERR_NOUSER = "401"  # User not found
    ERR_NOROOM = "402"  # Room not found
    ERR_RATELIMIT = "403"  # Rate limit exceeded

    @staticmethod
    def encode(command, *args):
        """
        Create protocol message
        Format: COMMAND:arg1:arg2:...\n
        """
        if args:
            return f"{command}:{':'.join(str(a) for a in args)}\n"
        return f"{command}\n"

    @staticmethod
    def decode(message):
        """
        Parse protocol message
        Returns: (command, data)
        """
        message = message.strip()
        if ':' in message:
            parts = message.split(':', 1)
            return parts[0], parts[1]
        return message, ""