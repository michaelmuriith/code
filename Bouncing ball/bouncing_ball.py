'''
    simulation assigment - group woek
        1. Michael andrew muriithi wanjiru - pa101/g/4705/18
        2. Mwaniki Moses njuguna - pa101/g/4724/18
        3. Abdullahi Salah Diis - PA101/G/5395/18
        4. Kiio Erick - PA101/G/4714/18
        5. Warugu Brandon - PA101/G/4701/18
'''


#!/usr/bin/env python

import getopt
import math
import sys

import pygame

# display constants
SIZE = WIDTH, HEIGHT = 1000, 600
BG_COLOR = 0, 0, 0
BALL_COLOR = 255, 200, 0
MINIMUM_HEIGHT = 0.05

# physics engine constants
RADIUS = 0.2
METER = 250.0
GRAVITY = 9.8
FRICTION = 0.1
POST_EXPLOSION_RESTITUTION = 0.9
RESTITUTION = 0.9
AIR_DENSITY = 1.25
DRAG = 0.75


# TODO friction has inconsistent effects. debug this.


def hex_to_rgb(color):
    hlen = len(color)
    return tuple(clamp(int(color[i:i + hlen // 3], 16), maximum=255) for i in range(0, hlen, hlen // 3))


def clamp(val, minimum=0.0, maximum=sys.maxsize):
    assert minimum <= maximum, "clamp: minimum greater than maximum"
    if val < minimum:
        val = minimum
    elif val > maximum:
        val = maximum
    return val


def break_speed_limit():
    print("warning: no exceeding the speed of light!", file=sys.stderr)
    sys.exit(1)


def main(argv):
    global SIZE, WIDTH, HEIGHT, BG_COLOR, BALL_COLOR, RADIUS, METER, GRAVITY, FRICTION, RESTITUTION
    usage_text = """
    description: runs bouncing ball physics simulation.
    
    usage: python main.py [options]
    
    options:
        -h, --help          Displays this usage guide.
        --width=SIZE        Sets width of the screen to SIZE pixels.
        --height=SIZE       Sets height of the screen to SIZE pixels.
        --bgcolor=COLOR     Sets the background color of the screen to COLOR.
        --ballcolor=COLOR   Sets the color of the ball to COLOR.
        --radius=NUM        Sets the radius of the ball to NUM meters.
        --meter=NUM         Sets the length of a meter in the simulation to NUM pixels.
        --gravity=NUM       Sets the acceleration due to gravity in the simulation to NUM meters squared per second.
        --friction=NUM      Sets the coefficient of friction in the simulation to NUM.
        --restitution=NUM   Sets the coefficient of restitution in the simulation to NUM.
        
        COLOR format examples: 25C3F1, 00FF46, 789ABC, 789abc
    """
    try:
        opts, args = getopt.getopt(argv, "", ["help=", "width=", "height=", "bgcolor=", "ballcolor=", "radius=",
                                              "meter=", "gravity=", "friction=", "restitution="])
    except getopt.GetoptError:
        print(usage_text, file=sys.stderr)
        sys.exit(2)

    try:
        for opt, arg in opts:
            if opt == '--help':
                print(usage_text)
                sys.exit()
            elif opt == '--width':
                WIDTH = clamp(int(arg), 150, 4000)
                SIZE = WIDTH, HEIGHT
            elif opt == '--height':
                HEIGHT = clamp(int(arg), 150, 4000)
                SIZE = WIDTH, HEIGHT
            elif opt == '--bgcolor':
                if len(arg) != 6:
                    print(usage_text, file=sys.stderr)
                    sys.exit(2)
                BG_COLOR = hex_to_rgb(arg)
            elif opt == '--ballcolor':
                if len(arg) != 6:
                    print(usage_text, file=sys.stderr)
                    sys.exit(2)
                BALL_COLOR = hex_to_rgb(arg)
            elif opt == '--radius':
                RADIUS = clamp(float(arg), 0.01, 5)
            elif opt == '--meter':
                METER = clamp(float(arg), 50, 10000)
            elif opt == '--gravity':
                GRAVITY = clamp(float(arg), maximum=50)
            elif opt == '--friction':
                FRICTION = clamp(float(arg), maximum=2)
            elif opt == '--restitution':
                RESTITUTION = clamp(float(arg), maximum=10)

        if BG_COLOR == BALL_COLOR:
            print("warning: bgcolor and ballcolor should not be identical!", file=sys.stderr)
            sys.exit(1)
        if RADIUS * 2 * METER > min(SIZE):
            print("warning: ball radius too large for given window size!", file=sys.stderr)
            sys.exit(1)
    except ValueError:
        print(usage_text, file=sys.stderr)
        sys.exit(2)

    pygame.init()

    global screen
    screen = pygame.display.set_mode(SIZE)
    screen.fill(BG_COLOR)
    pygame.display.flip()

    b = Ball()
    clock = pygame.time.Clock()

    while True:
        picked_up = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                b.held = True
                pygame.mouse.get_rel()
                picked_up = True
            if event.type == pygame.MOUSEBUTTONUP:
                b.held = False

        b.old_rect = b.rect.copy()

        if picked_up:
            coords = [x - RADIUS * METER for x in pygame.mouse.get_pos()]
            b.rect.left = coords[0]
            b.rect.top = coords[1]

        interval = clock.tick(60) / 1000.0
        if b.held:
            b.drag(interval)
        else:
            b.move(interval)

        b.update_graphics()


def calculate_speed(velocity):
    try:
        return math.sqrt(velocity[0] ** 2.0 + velocity[1] ** 2.0)
    except OverflowError:
        break_speed_limit()


class Ball:
    def __init__(self, center_location=(WIDTH / 2, HEIGHT / 2), vel=(0.0, 0.0)):
        r = int(RADIUS * METER)
        self.image = pygame.Surface((2 * r, 2 * r))
        self.image.set_colorkey(BG_COLOR)
        self.image.fill(BG_COLOR)
        pygame.draw.circle(self.image, BALL_COLOR, (r, r), r, 0)

        self.shadow = pygame.Surface((2 * r, 2 * r))
        self.shadow.set_colorkey(BALL_COLOR)
        self.shadow.fill(BALL_COLOR)
        pygame.draw.circle(self.shadow, BG_COLOR, (r, r), r, 0)

        self.vel = list(vel)

        self.held = False
        self.exploded = False

        self.rect = self.image.get_rect(center=center_location)
        self.old_rect = None

    def move(self, interval):

        # apply gravity to ball
        self.vel[1] += GRAVITY * interval

        # apply air resistance to ball
        speed = calculate_speed(self.vel)
        assert speed >= 0
        if speed > 0:
            drag_force = AIR_DENSITY * DRAG * math.pi * RADIUS ** 2.0 / 2.0 * speed ** 2.0
            self.vel[0] -= drag_force * interval * self.vel[0] / speed
            self.vel[1] -= drag_force * interval * self.vel[1] / speed

        # update ball position
        delta = [x * interval * METER for x in self.vel]

        if math.isinf(delta[0]) or math.isinf(delta[1]):
            break_speed_limit()

        # constraining delta to prevent overflow in rect.move_ip
        delta[0] = clamp(delta[0], minimum=-WIDTH, maximum=WIDTH)
        delta[1] = clamp(delta[1], minimum=-HEIGHT, maximum=HEIGHT)

        self.rect.move_ip(delta)
        self.rect.clamp_ip(screen.get_rect())

        # deal with bounce mechanics
        assert self.rect.left >= 0 and self.rect.top >= 0, "screen dimensions invalid"
        if self.rect.left == 0:
            self.vel[0] = abs(self.vel[0])
            self.bounce_calculation(0)
        if self.rect.right == WIDTH:
            self.vel[0] = -abs(self.vel[0])
            self.bounce_calculation(0)
        if self.rect.top == 0:
            self.vel[1] = abs(self.vel[1])
            self.bounce_calculation(1)
        if self.rect.bottom == HEIGHT:
            # prevents ball from shaking when at bottom of screen
            if abs(self.vel[1]) < MINIMUM_HEIGHT:
                self.vel[1] = 0

                # apply friction to ball
                delta = FRICTION * (4.0 / 3.0 * math.pi * RADIUS ** 3.0) * GRAVITY * float(interval)
                if self.vel[0] > 0:
                    self.vel[0] = clamp(self.vel[0] - delta, minimum=0.0)
                else:
                    self.vel[0] = clamp(self.vel[0] + delta, maximum=0.0)
            else:
                self.vel[1] = -abs(self.vel[1])
                self.bounce_calculation(1)

    def drag(self, interval):
        delta = pygame.mouse.get_rel()
        self.rect.move_ip(delta)
        self.vel = [float(x) / METER / interval for x in delta]

    def bounce_calculation(self, axis):
        bounce = RESTITUTION
        if self.exploded:
            bounce = POST_EXPLOSION_RESTITUTION
        self.vel[axis] *= bounce
        if bounce > 1:
            self.exploded = True

    def update_graphics(self):
        # fix the values of rect and old_rect to ensure that display update is synchronized with ball position
        old = self.old_rect
        curr = self.rect

        # clear old ball image from screen
        screen.blit(self.shadow, old)

        # draw current ball image on screen
        screen.blit(self.image, curr)

        pygame.display.flip()
        # TODO pygame.display.update([old, curr])

if __name__ == '__main__':
    main(sys.argv[1:])