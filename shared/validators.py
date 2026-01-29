"""
Input validation and sanitization
"""

import re


class InputValidator:
    """Validate user input"""

    MAX_NICKNAME_LEN = 20
    MAX_MESSAGE_LEN = 500
    MAX_ROOM_NAME_LEN = 30

    @staticmethod
    def validate_nickname(nickname):
        """
        Validate nickname format
        Returns: (is_valid, error_message)
        """
        if not nickname:
            return False, "Nickname cannot be empty"

        if len(nickname) > InputValidator.MAX_NICKNAME_LEN:
            return False, f"Nickname too long (max {InputValidator.MAX_NICKNAME_LEN})"

        if len(nickname) < 2:
            return False, "Nickname too short (min 2 chars)"

        # Only alphanumeric, underscore, hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', nickname):
            return False, "Nickname can only contain letters, numbers, _, -"

        return True, ""

    @staticmethod
    def validate_message(message):
        """
        Validate message content
        Returns: (is_valid, sanitized_message)
        """
        if len(message) > InputValidator.MAX_MESSAGE_LEN:
            return False, f"Message too long (max {InputValidator.MAX_MESSAGE_LEN})"

        # Strip dangerous characters
        message = message.replace('\x00', '').replace('\r', '')

        return True, message

    @staticmethod
    def sanitize_room_name(room_name):
        """
        Sanitize room name
        Returns: cleaned room name
        """
        # Convert to lowercase, remove special chars
        room_name = room_name.lower().strip()

        # Remove # prefix if present
        if room_name.startswith('#'):
            room_name = room_name[1:]

        # Only allow alphanumeric, underscore, hyphen
        room_name = re.sub(r'[^a-z0-9_-]', '', room_name)

        if len(room_name) > InputValidator.MAX_ROOM_NAME_LEN:
            room_name = room_name[:InputValidator.MAX_ROOM_NAME_LEN]

        return room_name