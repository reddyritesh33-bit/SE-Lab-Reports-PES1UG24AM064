"""
GameEngine: owns the puck, both paddles, and the computer AI, and runs
one frame's worth of game logic.

Starter version: the puck bounces around and paddles can hit it, but
there is no scoring, no match timer, and the reset that happens after
a goal is incomplete. That's what Tasks 2-4 fix/add.
"""

import math
import random

from game.puck import Puck
from game.paddle import Paddle
from game.ai import ComputerAI
from game.collisions import handle_paddle_collision
from game.renderer import WIDTH, HEIGHT, MARGIN, GOAL_TOP, GOAL_BOTTOM

PLAYER_SPEED = 6
PUCK_RADIUS = 12
PADDLE_RADIUS = 28
INITIAL_PUCK_SPEED = 4.5
MAX_STEP = PUCK_RADIUS / 2   # max px the puck travels per physics sub-step


class GameEngine:
    def __init__(self):
        self.puck = Puck(WIDTH / 2, HEIGHT / 2, PUCK_RADIUS)
        self._launch_puck()

        self.player = Paddle(
            x=WIDTH * 0.15, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=MARGIN + PADDLE_RADIUS, max_x=WIDTH / 2 - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.computer = Paddle(
            x=WIDTH * 0.85, y=HEIGHT / 2, radius=PADDLE_RADIUS,
            min_x=WIDTH / 2 + PADDLE_RADIUS, max_x=WIDTH - MARGIN - PADDLE_RADIUS,
            min_y=MARGIN + PADDLE_RADIUS, max_y=HEIGHT - MARGIN - PADDLE_RADIUS,
        )
        self.ai = ComputerAI()

        self.player_score = 0
        self.computer_score = 0

    def _launch_puck(self):
        angle_choices = [0.3, 0.6, -0.3, -0.6]
        direction = random.choice([-1, 1])
        vy_factor = random.choice(angle_choices)
        self.puck.vx = INITIAL_PUCK_SPEED * direction
        self.puck.vy = INITIAL_PUCK_SPEED * vy_factor

    def handle_input(self, keys_pressed):
        import pygame
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys_pressed[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        if keys_pressed[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys_pressed[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        self.player.move_by(dx, dy)

    def update(self):
        self.ai.update(self.computer, self.puck)
        self.player.track_velocity()
        self.computer.track_velocity()

        # Move the puck in small sub-steps so a fast puck can't jump over
        # (or deep inside) a paddle between two frames.
        steps = max(1, math.ceil(self.puck.speed() / MAX_STEP))
        for _ in range(steps):
            self.puck.move(1 / steps)
            self.puck.bounce_off_walls(HEIGHT, MARGIN)

            handle_paddle_collision(self.puck, self.player)
            handle_paddle_collision(self.puck, self.computer)

            if self._handle_goals():
                break

    def _handle_goals(self):
        """
        Bounce off the end walls, or let the puck into the goal mouth and
        score once it has fully crossed the goal line.
        Returns True if a goal was scored.
        """
        puck = self.puck
        r = puck.radius
        if puck.x - r < MARGIN:
            wall_x, away = MARGIN, 1             # player's goal (left)
        elif puck.x + r > WIDTH - MARGIN:
            wall_x, away = WIDTH - MARGIN, -1    # computer's goal (right)
        else:
            return False

        depth = (wall_x - puck.x) * away   # how far the centre is past the goal line
        if depth > 0:
            # Already in the goal mouth: the posts keep it inside the gap.
            if puck.y - r < GOAL_TOP:
                puck.y = GOAL_TOP + r
                puck.vy = abs(puck.vy)
            elif puck.y + r > GOAL_BOTTOM:
                puck.y = GOAL_BOTTOM - r
                puck.vy = -abs(puck.vy)
        elif not (GOAL_TOP <= puck.y - r and puck.y + r <= GOAL_BOTTOM):
            # Hit the wall (or a post) rather than the gap: bounce back.
            puck.x = wall_x + away * r
            puck.vx = abs(puck.vx) * away
            return False

        if depth > r:   # the whole puck is past the goal line
            if away == 1:
                self.computer_score += 1
            else:
                self.player_score += 1
            self._reset_puck()
            return True
        return False

    def result_text(self):
        if self.player_score > self.computer_score:
            return "You win!"
        if self.computer_score > self.player_score:
            return "Computer wins!"
        return "Draw!"

    def _reset_puck(self):
        self.puck.x, self.puck.y = WIDTH / 2, HEIGHT / 2
        self.puck.vx = 0
        self.puck.vy = 0

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_table(surface)
        renderer.draw_paddle(surface, self.player, renderer.COLOR_PLAYER)
        renderer.draw_paddle(surface, self.computer, renderer.COLOR_COMPUTER)
        renderer.draw_puck(surface, self.puck)
        renderer.draw_scores(surface, font, self.player_score, self.computer_score)
