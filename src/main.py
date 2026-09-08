import os
import pygame
import asyncio
from copy import deepcopy
import config
import maze

path = [(0, 0), (0, 1), (0, 2), (0, 3)]

ROOT = os.path.dirname(os.path.abspath(__file__))


def dist(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


class Ghost:
    pos = pygame.Vector2(0, 0)
    sprites = []

    # direction (1-4, right left up down)
    dir = 0

    # the points to traverse
    path = [maze.points[1][1]]
    last_point: Point

    blacklist = []

    def ai(self):
        if len(self.path) == 0:
            self.path = [self.last_point]

        # current point
        point = deepcopy(self.path[0])

        # move ghost to their npi
        #
        # when moving, always check against ghost and point pos to ensure
        # that ghost lands on the point instead of overshooting
        if self.pos.x > point.spos().x:
            self.pos.x -= min(config.ghost_speed, abs(point.spos().x - self.pos.x))
            self.dir = 1
        elif self.pos.x < point.spos().x:
            self.pos.x += min(config.ghost_speed, abs(point.spos().x - self.pos.x))
            self.dir = 0

        if self.pos.y > point.spos().y:
            self.pos.y -= min(config.ghost_speed, abs(point.spos().y - self.pos.y))
            self.dir = 2
        elif self.pos.y < point.spos().y:
            self.pos.y += min(config.ghost_speed, abs(point.spos().y - self.pos.y))
            self.dir = 3

        # move to next point if ghost is close to its current
        if dist(point.spos(), self.pos) < 1:
            self.last_point = deepcopy(self.path[0])
            self.path = []
            self.get_closest_point(self.last_point)
            # if not maze.points[point.right[1]][point.right[0]].wall:
            #     self.npi = (point.right[0], point.right[1])
            # elif not maze.points[point.bottom[1]][point.bottom[0]].wall:
            #     self.npi = (point.bottom[0], point.bottom[1])
            # elif not maze.points[point.left[1]][point.left[0]].wall:
            #     self.npi = (point.left[0], point.left[1])

    def check_closest_point(self, dir, next_point, closest):
        mouse = pygame.mouse.get_pos()

        if hasattr(next_point, dir):
            distance = dist(mouse, next_point.right.spos())
            if distance < closest:
                closest_point = next_point.right
                closest = dist(mouse, closest_point.spos())

    def get_closest_point(self, next_point):
        mouse = pygame.mouse.get_pos()

        # find next point's closest neighbor to target
        closest_point = next_point
        closest = dist(mouse, closest_point.spos())

        if hasattr(next_point, "right"):
            distance = dist(mouse, next_point.right.spos())
            if distance < closest:
                closest_point = next_point.right
                closest = dist(mouse, closest_point.spos())

        if hasattr(next_point, "left"):
            distance = dist(mouse, next_point.left.spos())
            if distance < closest:
                closest_point = next_point.left
                closest = dist(mouse, closest_point.spos())

        if hasattr(next_point, "top"):
            distance = dist(mouse, next_point.top.spos())
            if distance < closest:
                closest_point = next_point.top
                closest = dist(mouse, closest_point.spos())

        if hasattr(next_point, "bottom"):
            distance = dist(mouse, next_point.bottom.spos())
            if distance < closest:
                closest_point = next_point.bottom
                closest = dist(mouse, closest_point.spos())

        if closest_point != next_point:
            self.path.append(closest_point)
            self.get_closest_point(closest_point)

    def draw(self, screen):
        sprite = self.sprites[self.dir]
        scaled = pygame.transform.scale(
            sprite,
            (
                sprite.get_width() * config.maze_scale / 10,
                sprite.get_height() * config.maze_scale / 10,
            ),
        )
        rect = scaled.get_rect()
        rect.x = self.pos.x - rect.height / 2
        rect.y = self.pos.y - rect.width / 2
        screen.blit(scaled, rect)


# initialize blinky
blinky = Ghost()
blinky.pos = pygame.Vector2(maze.points[0][0].pos.x, maze.points[0][0].pos.y)
for i in range(4):
    blinky.sprites.append(pygame.image.load(f"{ROOT}/assets/blinky/blinky_{i}.png"))


def draw_points(screen):
    for y in range(len(maze.points)):
        for x in range(len(maze.points[y])):
            if maze.points[y][x].wall:
                continue
            pos = maze.points[y][x].pos * config.maze_scale
            pos.x += config.maze_scale / 2
            pos.y += config.maze_scale / 2
            pygame.draw.circle(screen, "#dda49c", pos, 3, 5)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    running = True
    original_img_toggle = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")

        # draw maze
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            original_img_toggle = not original_img_toggle

        use_original_img = config.maze_type != 2 or not original_img_toggle
        img_to_use = maze.img if use_original_img else maze.original_img
        divisor = 1.0 if use_original_img else 8.0
        final_img = pygame.transform.scale(
            img_to_use,
            (
                img_to_use.get_width() * config.maze_scale / divisor,
                img_to_use.get_height() * config.maze_scale / divisor,
            ),
        )
        screen.blit(final_img, maze.rect)

        draw_points(screen)

        blinky.ai()
        blinky.draw(screen)

        pygame.display.flip()
        # print(pygame.mouse.get_pos())

        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
