"""
Protocol definitions for IRC-style chat
"""

class Protocol:
    """Message format and command definitions"""

    # Existing commands...
    CMD_NICK = "NICK"
    CMD_JOIN = "JOIN"
    CMD_LEAVE = "LEAVE"
    CMD_MSG = "MSG"
    CMD_PM = "PM"
    CMD_USERS = "USERS"
    CMD_ROOMS = "ROOMS"
    CMD_WHOAMI = "WHOAMI"
    CMD_HELP = "HELP"
    CMD_QUIT = "QUIT"

    # NEW: Private room commands
    CMD_CREATE = "CREATE"       # Create private room
    CMD_INVITE = "INVITE"       # Invite user to room
    CMD_KICK = "KICK"           # Kick user from room
    CMD_BAN = "BAN"             # Ban user from room
    CMD_SETPASS = "SETPASS"     # Set room password
    CMD_PRIVATE = "PRIVATE"     # Make room private
    CMD_PUBLIC = "PUBLIC"       # Make room public
    CMD_ROOMINFO = "ROOMINFO"   # Get room details

    # Server responses...
    RPL_WELCOME = "001"
    RPL_NICKOK = "002"
    RPL_NICKERR = "003"
    RPL_USERLIST = "004"
    RPL_JOINED = "005"
    RPL_ROOMLIST = "006"
    RPL_PM = "007"
    RPL_INFO = "008"
    RPL_ROOMINFO = "009"        # NEW: Room info response

    ERR_NOUSER = "401"
    ERR_NOROOM = "402"
    ERR_RATELIMIT = "403"
    ERR_NOPERMISSION = "404"    # NEW: No permission
    ERR_WRONGPASS = "405"       # NEW: Wrong password

    @staticmethod
    def encode(command, *args):
        """Create protocol message"""
        if args:
            return f"{command}:{':'.join(str(a) for a in args)}\n"
        return f"{command}\n"

    @staticmethod
    def decode(message):
        """Parse protocol message"""
        message = message.strip()
        if ':' in message:
            parts = message.split(':', 1)
            return parts[0], parts[1]
        return message, ""