"""
Terminal UI utilities
"""

import os
import sys


class Colors:
    """ANSI color codes for terminal"""

    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class TerminalUI:
    """Terminal user interface utilities"""

    @staticmethod
    def clear_screen():
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def colorize_message(message):
        """Add colors to different message types"""

        # Private messages
        if '[PM from' in message or '[PM to' in message:
            return f"{Colors.MAGENTA}{message}{Colors.RESET}"

        # Server messages
        if message.startswith('[SERVER]'):
            return f"{Colors.YELLOW}{message}{Colors.RESET}"

        # Channel messages
        if message.startswith('[#'):
            # Color the channel name
            if ']' in message:
                channel_end = message.index(']')
                channel_part = f"{Colors.CYAN}{message[:channel_end + 1]}{Colors.RESET}"
                return channel_part + message[channel_end + 1:]

        # Error messages
        if 'error' in message.lower() or 'failed' in message.lower():
            return f"{Colors.RED}{message}{Colors.RESET}"

        # Success messages
        if 'joined' in message.lower() or 'success' in message.lower():
            return f"{Colors.GREEN}{message}{Colors.RESET}"

        return message

    @staticmethod
    def print_message(message):
        """Print message with colors"""
        colored = TerminalUI.colorize_message(message)
        print(colored)

    @staticmethod
    def print_banner():
        """Print startup banner"""
        banner = f"""{Colors.CYAN}
╔═══════════════════════════════════════╗
║     IRC-Style Terminal Chat v1.0      ║
║      Type /help for commands          ║
╚═══════════════════════════════════════╝
{Colors.RESET}"""
        print(banner)

    @staticmethod
    def get_input(prompt="You: "):
        """Get user input"""
        try:
            return input(f"{Colors.BRIGHT_GREEN}{prompt}{Colors.RESET}")
        except (EOFError, KeyboardInterrupt):
            return '/quit'