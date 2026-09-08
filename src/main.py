import os
import pygame
import asyncio
from copy import deepcopy
import config
import maze

path = [(0, 0), (0, 1), (0, 2), (0, 3)]

ROOT = os.path.dirname(os.path.abspath(__file__))


class Ghost:
    pos = pygame.Vector2(0, 0)
    sprites = []

    # direction (1-4, right left up down)
    dir = 0

    # next point index - which point this ghost is currently going to
    npi = (1, 1)

    def ai(self):
        # current point
        point = deepcopy(maze.points[self.npi[1]][self.npi[0]])
        point.pos *= config.maze_scale
        point.pos.x += config.maze_scale / 2
        point.pos.y += config.maze_scale / 2

        # move ghost to their npi
        #
        # when moving, always check against ghost and point pos to ensure
        # that ghost lands on the point instead of overshooting
        if self.pos.x > point.pos.x:
            self.pos.x -= min(config.ghost_speed, abs(point.pos.x - self.pos.x))
            self.dir = 1
        elif self.pos.x < point.pos.x:
            self.pos.x += min(config.ghost_speed, abs(point.pos.x - self.pos.x))
            self.dir = 0

        if self.pos.y > point.pos.y:
            self.pos.y -= min(config.ghost_speed, abs(point.pos.y - self.pos.y))
            self.dir = 2
        elif self.pos.y < point.pos.y:
            self.pos.y += min(config.ghost_speed, abs(point.pos.y - self.pos.y))
            self.dir = 3

        # move to next point if ghost is close to its current
        if abs(point.pos.x - self.pos.x) + abs(point.pos.y - self.pos.y) < 1:
            if not maze.points[point.right[1]][point.right[0]].wall:
                self.npi = (point.right[0], point.right[1])
            elif not maze.points[point.bottom[1]][point.bottom[0]].wall:
                self.npi = (point.bottom[0], point.bottom[1])
            elif not maze.points[point.left[1]][point.left[0]].wall:
                self.npi = (point.left[0], point.left[1])

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
            pygame.draw.circle(screen, (0, 0, 150), pos, 5, 2)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")

        # draw maze
        img_to_use = maze.img if config.maze_type != 2 else maze.original_img
        divisor = 1.0 if config.maze_type != 2 else 8.0
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
