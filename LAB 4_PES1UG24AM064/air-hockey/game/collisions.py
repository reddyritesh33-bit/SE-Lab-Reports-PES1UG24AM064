"""
collisions: puck-vs-paddle collision handling.
"""

import math

MIN_SPEED = 4.0    # a hit never leaves the puck crawling
MAX_SPEED = 14.0   # cap so the puck stays playable (and can't tunnel)


def handle_paddle_collision(puck, paddle):
    """
    If the puck overlaps the paddle, push it back out and bounce it off
    along the line between the two centres (circle-vs-circle), taking the
    paddle's own movement into account.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = math.hypot(dx, dy)
    min_distance = puck.radius + paddle.radius

    if distance >= min_distance:
        return False

    # Collision normal, pointing from the paddle centre to the puck centre.
    if distance > 0:
        nx, ny = dx / distance, dy / distance
    else:
        # Centres coincide: push the puck back the way it came.
        speed = math.hypot(puck.vx, puck.vy)
        nx, ny = (-puck.vx / speed, -puck.vy / speed) if speed > 0 else (1.0, 0.0)

    # Separate the two so the puck can never stay stuck inside the paddle.
    puck.x = paddle.x + nx * min_distance
    puck.y = paddle.y + ny * min_distance

    # Reflect the puck's velocity relative to the (possibly moving) paddle,
    # but only if it is still heading into the paddle - otherwise a second
    # overlap in a row would flip it straight back in (the old jitter bug).
    rel_vx = puck.vx - paddle.vx
    rel_vy = puck.vy - paddle.vy
    approach = rel_vx * nx + rel_vy * ny
    if approach < 0:
        puck.vx -= 2 * approach * nx
        puck.vy -= 2 * approach * ny

    _clamp_speed(puck)
    return True


def _clamp_speed(puck):
    speed = math.hypot(puck.vx, puck.vy)
    if speed == 0:
        return
    if speed > MAX_SPEED:
        scale = MAX_SPEED / speed
    elif speed < MIN_SPEED:
        scale = MIN_SPEED / speed
    else:
        return
    puck.vx *= scale
    puck.vy *= scale
