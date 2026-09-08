import pygame
import config
import os
from copy import deepcopy

ROOT = os.path.dirname(os.path.abspath(__file__))
# initialize maze
img = pygame.image.load(f"{ROOT}/assets/maze{config.maze_type}.png")
rect = img.get_rect()
rect.topleft = (0, 0)

original_img = {}
if config.maze_type == 2:
    original_img = pygame.image.load(f"{ROOT}/assets/original_maze.png")


class Point:
    pos: pygame.Vector2
    wall = True
    right: Point
    left: Point
    top: Point
    bottom: Point

    def __init__(self, pos, wall):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.wall = wall

    def print(self):
        print(self.pos, self.right, self.left, self.top, self.bottom, self.wall)

    def spos(self):
        pos = deepcopy(self.pos)
        pos *= config.maze_scale
        pos.x += config.maze_scale / 2
        pos.y += config.maze_scale / 2
        return pos


points = []
# get raw points from maze image
for y in range(img.height):
    row = []
    for x in range(img.width):
        col = img.get_at((x, y))

        # this is a point if the pixel is black
        point = Point((x, y), col.r > 10 or col.g > 10 or col.b > 10)
        row.append(point)

        if point.wall:
            continue

        # add this point as a neighbor to the left one, and vice versa
        left_point = row[x - 1]
        if x > 0 and not left_point.wall and left_point.pos.x == row[x].pos.x - 1:
            row[x - 1].right = row[x]
            row[x].left = row[x - 1]

        # add this point as a neighbor to the top one, and vice versa
        top_point = points[y - 1][x]
        if y > 0 and not top_point.wall and top_point.pos.y == row[x].pos.y - 1:
            points[y - 1][x].bottom = row[x]
            row[x].top = points[y - 1][x]

    points.append(row)
