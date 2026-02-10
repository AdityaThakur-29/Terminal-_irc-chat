"""
Room management for chat server with private room support
"""

import threading

class RoomManager:
    """Manages chat rooms and user membership with private room support"""

    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, room_name, topic="", is_private=False, password=None, owner=None):
        """
        Create a new room

        Args:
            room_name: Name of the room
            topic: Room topic/description
            is_private: Whether room is private (invite-only)
            password: Password for password-protected rooms
            owner: Username of room creator
        """
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = {
                    'users': set(),
                    'topic': topic,
                    'is_private': is_private,
                    'password': password,
                    'owner': owner,
                    'invited_users': set(),  # Users allowed in private room
                    'banned_users': set()     # Banned users
                }
                return True
            return False

    def join_room(self, nickname, room_name, password=None):
        """
        Add user to room (removes from all other rooms first)

        Returns:
            (success, error_message)
        """
        with self.lock:
            # Create room if doesn't exist (as public)
            if room_name not in self.rooms:
                self.create_room(room_name, owner=nickname)

            room = self.rooms[room_name]

            # Check if user is banned
            if nickname in room['banned_users']:
                return False, "You are banned from this room"

            # Check if room is private
            if room['is_private']:
                # Allow owner
                if nickname != room['owner']:
                    # Check if invited
                    if nickname not in room['invited_users']:
                        return False, "This is a private room (invite-only)"

            # Check password if set
            if room['password']:
                if password != room['password']:
                    return False, "Incorrect room password"

            # Leave all current rooms
            self.leave_all_rooms(nickname)

            # Add user to room
            room['users'].add(nickname)
            return True, None

    def leave_room(self, nickname, room_name):
        """Remove user from specific room"""
        with self.lock:
            if room_name in self.rooms:
                self.rooms[room_name]['users'].discard(nickname)

    def leave_all_rooms(self, nickname):
        """Remove user from all rooms"""
        # Note: lock already held by caller
        for room in self.rooms.values():
            room['users'].discard(nickname)

    def invite_user(self, room_name, inviter, invitee):
        """
        Invite a user to a private room

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can invite
            if room['owner'] != inviter:
                return False, "Only the room owner can invite users"

            # Add to invited list
            room['invited_users'].add(invitee)
            return True, None

    def kick_user(self, room_name, kicker, kickee):
        """
        Kick a user from a room

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can kick
            if room['owner'] != kicker:
                return False, "Only the room owner can kick users"

            # Can't kick yourself
            if kicker == kickee:
                return False, "You can't kick yourself"

            # Remove from room
            room['users'].discard(kickee)
            return True, None

    def ban_user(self, room_name, banner, banee):
        """
        Ban a user from a room

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can ban
            if room['owner'] != banner:
                return False, "Only the room owner can ban users"

            # Can't ban yourself
            if banner == banee:
                return False, "You can't ban yourself"

            # Add to banned list and remove from room
            room['banned_users'].add(banee)
            room['users'].discard(banee)
            room['invited_users'].discard(banee)
            return True, None

    def set_room_password(self, room_name, setter, password):
        """
        Set password for a room

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can set password
            if room['owner'] != setter:
                return False, "Only the room owner can set password"

            room['password'] = password
            return True, None

    def make_private(self, room_name, requester):
        """
        Make a room private (invite-only)

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can make private
            if room['owner'] != requester:
                return False, "Only the room owner can make room private"

            room['is_private'] = True
            # Current users are automatically invited
            room['invited_users'] = room['users'].copy()
            return True, None

    def make_public(self, room_name, requester):
        """
        Make a room public

        Returns:
            (success, error_message)
        """
        with self.lock:
            if room_name not in self.rooms:
                return False, "Room does not exist"

            room = self.rooms[room_name]

            # Only owner can make public
            if room['owner'] != requester:
                return False, "Only the room owner can make room public"

            room['is_private'] = False
            room['invited_users'].clear()
            return True, None

    def get_room_users(self, room_name):
        """Get list of users in room"""
        with self.lock:
            if room_name in self.rooms:
                return list(self.rooms[room_name]['users'])
            return []

    def get_user_room(self, nickname):
        """Find which room user is in"""
        with self.lock:
            for room_name, room_data in self.rooms.items():
                if nickname in room_data['users']:
                    return room_name
            return None

    def list_rooms(self):
        """Get all rooms with user counts (only public or owned)"""
        with self.lock:
            return {
                name: {
                    'count': len(data['users']),
                    'topic': data['topic'],
                    'is_private': data['is_private'],
                    'has_password': bool(data['password']),
                    'owner': data['owner']
                }
                for name, data in self.rooms.items()
            }

    def room_exists(self, room_name):
        """Check if room exists"""
        with self.lock:
            return room_name in self.rooms

    def get_room_info(self, room_name):
        """Get detailed room information"""
        with self.lock:
            if room_name in self.rooms:
                room = self.rooms[room_name]
                return {
                    'name': room_name,
                    'topic': room['topic'],
                    'is_private': room['is_private'],
                    'has_password': bool(room['password']),
                    'owner': room['owner'],
                    'users': list(room['users']),
                    'user_count': len(room['users'])
                }
            return None