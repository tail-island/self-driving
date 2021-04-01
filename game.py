import pymunk
import random

from funcy import concat, distinct, first, mapcat, repeatedly
from math import pi
from simulator import Car, Obstacle, Star
from ui import create_surface


OBSTACLE_COUNT = 40
STAR_COUNT = 2
GAME_PERIOD_SEC = 30


class Game:
    @classmethod
    def _crash(cls, arbiter, space, data):
        for car in filter(lambda body: isinstance(body, Car), distinct(map(lambda body: body.car if hasattr(body, 'car') else body, map(lambda shape: shape.body, arbiter.shapes)))):
            car.crash_energy = min(car.crash_energy + arbiter.total_ke / 2, 10 * 30 * 100000)

    @classmethod
    def _catch(cls, arbiter, space, data):
        car = first(filter(lambda body: isinstance(body, Car), distinct(map(lambda body: body.car if hasattr(body, 'car') else body, map(lambda shape: shape.body, arbiter.shapes)))))

        if not car:
            return True

        car.score += 1

        star = first(filter(lambda body: isinstance(body, Star), distinct(map(lambda shape: shape.body, arbiter.shapes))))
        star.is_catched = True

        return False

    def _random_position(self, sigma):
        return first(filter(lambda p: all(map(lambda b: (b.position - p).length >= 50, concat(self.cars, self.obstacles, self.stars))), filter(lambda p: 100 < p.length < 950, repeatedly(lambda: pymunk.Vec2d(random.gauss(0, sigma), 0).rotated(random.uniform(0, pi * 2))))))

    def _reset_star_position(self, star):
        star.set_position_and_angle(self._random_position(300), random.uniform(0, pi * 2))
        star.is_catched = False

    def _append_wall(self, a, b):
        wall = pymunk.Body(body_type=pymunk.Body.STATIC)

        shape = pymunk.Segment(wall, a, b, 10)
        shape.elasticity = 1

        self.space.add(wall, shape)

    def _append_car(self, position, angle):
        car = Car(self.space)
        car.set_position_and_angle(position, angle)
        car.crash_energy = 0
        car.score = 0

        for shape in concat(car.shapes, mapcat(lambda tire: tire.shapes, (car.tire_lf, car.tire_rf, car.tire_lr, car.tire_rr))):
            shape.collision_type = 1

        self.cars.append(car)

    def _append_obstacle(self):
        obstacle = Obstacle(self.space)
        obstacle.set_position_and_angle(self._random_position(500), random.uniform(0, pi * 2))

        self.obstacles.append(obstacle)

    def _append_star(self):
        star = Star(self.space)

        for shape in star.shapes:
            shape.collision_type = 2

        self._reset_star_position(star)
        self.stars.append(star)

    def __init__(self, players):
        self.players = players
        self.elapse = 0

        self.space = pymunk.Space()

        self.space.add_wildcard_collision_handler(1).post_solve = self._crash
        self.space.add_wildcard_collision_handler(2).begin = self._catch

        self.cars = []
        self.obstacles = []
        self.stars = []

        for a, b in ((-1000, 1000), (1000, 1000)), ((1000, 1000), (1000, -1000)), ((1000, -1000), (-1000, -1000)), ((-1000, -1000), (-1000, 1000)):
            self._append_wall(a, b)

        for position, angle in map(lambda i: (pymunk.Vec2d(80, 0).rotated(pi * 2 / 8 * i), pi * 2 / 8 * i), range(8)):
            self._append_car(position, angle)

        for _ in range(OBSTACLE_COUNT):
            self._append_obstacle()

        for _ in range(STAR_COUNT):
            self._append_star()

    @classmethod
    def _normalize_angle(cls, angle):
        return (angle + pi * 2) % (pi * 2)

    @classmethod
    def _normalize_relative_angle(cls, angle):
        result = cls._normalize_angle(angle)

        return result if result < pi else result - pi * 2

    @classmethod
    def _get_my_car_observation(cls, my_car):
        return {
            'position': my_car.position,
            'angle': cls._normalize_relative_angle(my_car.angle),
            'velocity': my_car.velocity.rotated(-my_car.angle) / 30,
            'steering_angle': cls._normalize_relative_angle(my_car.tire_lf.angle - my_car.angle),
            'steering_torque': (my_car.tire_lf.moment * my_car.tire_lf.angular_velocity + my_car.tire_rf.moment * my_car.tire_rf.angular_velocity) / 20000,
            'score': my_car.score,
            'crash_energy': my_car.crash_energy / 100000
        }

    @classmethod
    def _get_other_car_observation(cls, other_car, my_car):
        return {
            'position_angle': cls._normalize_relative_angle((other_car.position - my_car.position).rotated(-my_car.angle).angle),
            'position_distance': (other_car.position - my_car.position).length,
            'car_angle': cls._normalize_relative_angle(other_car.angle - my_car.angle),
            'car_velocity': (other_car.velocity - my_car.velocity).rotated(-my_car.angle) / 30,
            'steering_angle': cls._normalize_relative_angle(other_car.tire_lf.angle - other_car.angle),
            'score': other_car.score,
            'crash_energy': other_car.crash_energy / 100000,
        }

    @classmethod
    def _get_obstacle_or_star_observation(cls, obstacle_or_star, my_car):
        return {
            'position_angle': cls._normalize_relative_angle((obstacle_or_star.position - my_car.position).rotated(-my_car.angle).angle),
            'position_distance': (obstacle_or_star.position - my_car.position).length,
        }

    def create_observation(self, my_car):
        return {
            'my_car': self._get_my_car_observation(my_car),
            'other_cars': tuple(map(lambda other_car: self._get_other_car_observation(other_car, my_car), filter(lambda car: car != my_car, self.cars))),
            'obstacles': tuple(map(lambda obstacle: self._get_obstacle_or_star_observation(obstacle, my_car), self.obstacles)),
            'stars': tuple(map(lambda star: self._get_obstacle_or_star_observation(star, my_car), self.stars))
        }

    def step(self):
        self.elapse += 1

        for car, player in zip(self.cars, self.players):
            acceleration, braking, steering = player.get_action(self.create_observation(car))

            if car.crash_energy > 0:
                car.crash_energy = max(car.crash_energy - 100000, 0)
                continue

            car.accelerate(acceleration * 20000)
            car.brake(braking * 200000)
            car.steer(steering * 20000)

        self.space.step(1 / 30)

        for star in self.stars:
            if star.is_catched:
                self._reset_star_position(star)

        return self.elapse >= GAME_PERIOD_SEC * 30  # ゲームはGAME_PERIOD_SECで終了。

    def create_surface(self):
        return create_surface(self.space)


if __name__ == '__main__':
    import pygame
    import sys

    from funcy import last
    from player_proxy import PlayerProxy

    pygame.init()
    pygame.display.set_caption('self driving')

    pymunk.pygame_util.positive_y_is_up = True

    screen = pygame.display.set_mode((640, 640))

    game = Game((PlayerProxy('christine'),))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        car = last(game.cars)

        if car.crash_energy == 0:
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                car.accelerate(20000)

            if keys[pygame.K_DOWN]:
                car.accelerate(-10000)

            if keys[pygame.K_SPACE]:
                car.brake(200000)

            if keys[pygame.K_LEFT]:
                car.steer( 20000)  # noqa: E201

            if keys[pygame.K_RIGHT]:
                car.steer(-20000)

        if game.step():
            break

        screen.blit(pygame.transform.smoothscale(game.create_surface(), (640, 640)), (0, 0))
        pygame.display.flip()
