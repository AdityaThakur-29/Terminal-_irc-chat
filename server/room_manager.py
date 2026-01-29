"""
Room management for chat server
"""

import threading


class RoomManager:
    """Manages chat rooms and user membership"""

    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()

    def create_room(self, room_name, topic=""):
        """Create a new room"""
        with self.lock:
            if room_name not in self.rooms:
                self.rooms[room_name] = {
                    'users': set(),
                    'topic': topic
                }
                return True
            return False

    def join_room(self, nickname, room_name):
        """Add user to room (removes from all other rooms first)"""
        with self.lock:
            # Leave all current rooms
            self.leave_all_rooms(nickname)

            # Create room if doesn't exist
            if room_name not in self.rooms:
                self.create_room(room_name)

            # Add user to room
            self.rooms[room_name]['users'].add(nickname)
            return True

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
        """Get all rooms with user counts"""
        with self.lock:
            return {
                name: {
                    'count': len(data['users']),
                    'topic': data['topic']
                }
                for name, data in self.rooms.items()
            }

    def room_exists(self, room_name):
        """Check if room exists"""
        with self.lock:
            return room_name in self.rooms