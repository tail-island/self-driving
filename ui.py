import pygame
import pymunk.pygame_util
import pymunk.space_debug_draw_options

from funcy import juxt, mapcat
from simulator import Car, Star, Tire


def draw_circle(options, left_top, shape, outline_color, fill_color):
    options.draw_circle(
        shape.offset + shape.body.position - left_top,
        shape.body.angle,
        shape.radius,
        outline_color,
        fill_color
    )


def draw_segment(options, left_top, shape, outline_color, fill_color):
    options.draw_fat_segment(
        shape.a + shape.body.position - left_top,
        shape.b + shape.body.position - left_top,
        shape.radius,
        outline_color,
        fill_color
    )


def draw_poly(options, left_top, shape, outline_color, fill_color):
    options.draw_polygon(
        tuple(map(lambda v: v.rotated(shape.body.angle) + shape.body.position - left_top, shape.get_vertices())),
        shape.radius,
        outline_color,
        fill_color
    )


def create_surface(space):
    def get_min_max_coordinate():
        coordinates = tuple(mapcat(lambda shape: (shape.bb.left, shape.bb.top, shape.bb.right, shape.bb.bottom), filter(lambda shape: shape.body.body_type == pymunk.Body.DYNAMIC, space.shapes)))

        return juxt(max, min)(coordinates)

    def get_car_from_shape(shape):
        if isinstance(shape.body, Tire):
            return shape.body.car

        if isinstance(shape.body, Car):
            return shape.body

        return None

    def get_color(r, g, b):
        return pymunk.space_debug_draw_options.SpaceDebugColor(r, g, b, 255)

    def get_fill_color(shape):
        if isinstance(shape.body, Star):
            return get_color(128, 255, 128)

        if get_car_from_shape(shape):
            if get_car_from_shape(shape).crash_energy == 0:
                return get_color(128, 128, 255)
            else:
                return get_color(255, 128, 128)

        return get_color(192, 192, 192)

    max_coordinate, min_coordinate = get_min_max_coordinate()

    size = (max_coordinate - min_coordinate, max_coordinate - min_coordinate)
    left_top = (min_coordinate, min_coordinate)

    surface = pygame.surface.Surface(size)
    options = pymunk.pygame_util.DrawOptions(surface)

    for shape in space.shapes:
        fill_color = get_fill_color(shape)

        if isinstance(shape, pymunk.shapes.Circle):
            draw_circle(options, left_top, shape, fill_color, fill_color)
        elif isinstance(shape, pymunk.shapes.Segment):
            draw_segment(options, left_top, shape, fill_color, fill_color)
        elif isinstance(shape, pymunk.shapes.Poly):
            draw_poly(options, left_top, shape, fill_color, fill_color)

    return surface
