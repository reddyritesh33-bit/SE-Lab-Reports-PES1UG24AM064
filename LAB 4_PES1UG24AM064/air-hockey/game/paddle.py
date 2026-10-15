"""
Paddle: a player's or the computer's mallet, confined to their own half
of the table.
"""


class Paddle:
    def __init__(self, x, y, radius, min_x, max_x, min_y, max_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.home_x = x
        self.home_y = y
        # Velocity in px/frame, so a moving paddle can strike the puck.
        self.vx = 0.0
        self.vy = 0.0
        self._last_x = x
        self._last_y = y

    def reset(self):
        """Back to the starting spot, at rest (no fake velocity from the jump)."""
        self.x = self._last_x = self.home_x
        self.y = self._last_y = self.home_y
        self.vx = self.vy = 0.0

    def track_velocity(self):
        """Record how far the paddle moved since the last call (once per frame)."""
        self.vx = self.x - self._last_x
        self.vy = self.y - self._last_y
        self._last_x = self.x
        self._last_y = self.y

    def clamp(self):
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))

    def move_by(self, dx, dy):
        self.x += dx
        self.y += dy
        self.clamp()

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.clamp()
