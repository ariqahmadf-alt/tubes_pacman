import pygame
import config

# initialize maze
img = pygame.image.load(f"maze{config.maze_type}.png")
rect = img.get_rect()
rect.topleft = (0, 0)


class Point:
    pos: pygame.Vector2
    wall = True
    right = (-1, -1)
    left = (-1, -1)
    top = (-1, -1)
    bottom = (-1, -1)

    def __init__(self, pos, wall):
        self.pos = pygame.Vector2(pos[0], pos[1])
        self.wall = wall

    def print(self):
        print(self.pos, self.right, self.left, self.top, self.bottom, self.wall)


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
            row[x - 1].right = (x, y)
            row[x].left = (x - 1, y)

        # add this point as a neighbor to the top one, and vice versa
        top_point = points[y - 1][x]
        if y > 0 and not top_point.wall and top_point.pos.y == row[x].pos.y - 1:
            points[y - 1][x].bottom = (x, y)
            row[x].top = (x, y - 1)

    points.append(row)
