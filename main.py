import pygame
import asyncio  # 1. Required for WASM/browser compatibility


class Ghost:
    pos = pygame.Vector2(0, 0)
    sprites = []

    # direction (1-4, right left up down)
    dir = 0

    # next point index - which point this ghost is currently going to
    npi = 0

    def ai(self):
        # current point
        point = points[self.npi]

        # move ghost to their npi
        #
        # when moving, always check against ghost and point pos to ensure
        # that ghost lands on the point instead of overshooting
        speed = 3
        if self.pos.x > point[0]:
            self.pos.x -= min(speed, abs(point[0] - self.pos.x))
            self.dir = 1
        elif self.pos.x < point[0]:
            self.pos.x += min(speed, abs(point[0] - self.pos.x))
            self.dir = 0

        if self.pos.y > point[1]:
            self.pos.y -= min(speed, abs(point[1] - self.pos.y))
            self.dir = 2
        elif self.pos.y < point[1]:
            self.pos.y += min(speed, abs(point[1] - self.pos.y))
            self.dir = 3

        # move to next point if ghost is close to its current
        if abs(point[0] - self.pos.x) + abs(point[1] - self.pos.y) < 1:
            self.npi += 1
            print(self.npi)

    def draw(self, screen):
        sprite = self.sprites[self.dir]
        scaled = pygame.transform.scale(
            sprite,
            (
                sprite.get_width() * 3,
                sprite.get_height() * 3,
            ),
        )
        rect = scaled.get_rect()
        rect.x = self.pos.x - rect.height / 2
        rect.y = self.pos.y - rect.width / 2
        screen.blit(scaled, rect)


points = [
    # red
    (310, 290),
    (310, 215),
    (240, 215),
    (240, 140),
    (310, 140),
    (310, 50),
    (170, 50),
    (50, 50),
    (50, 140),
    (50, 215),
    (170, 215),
    (170, 355),
    # (170, 140),
    (240, 355),
    (240, 290),
]

# initialize maze
maze = pygame.image.load("maze.png")
maze_rect = maze.get_rect()
maze_rect.topleft = (10, 10)


# initialize blinky
blinky = Ghost()
blinky.pos = pygame.Vector2(350, 290)
for i in range(4):
    blinky.sprites.append(pygame.image.load(f"blinky/blinky_{i}.png"))


def draw_points(screen):
    # draw all points (debugging)
    interval = 16
    for p in range(len(points)):
        if p < interval * 1:
            col = min(p / interval * 1 * 255 + 50, 255)
            pygame.draw.circle(screen, (col, 0, 0), points[p], 5, 2)
        elif p < interval * 2:
            col = min(p / interval * 2 * 255 + 10, 255)
            pygame.draw.circle(screen, (col, col, 0), points[p], 5, 2)


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
        scaled = pygame.transform.scale(
            maze, (maze.get_width() * 3, maze.get_height() * 3)
        )
        screen.blit(scaled, maze_rect)

        blinky.ai()
        blinky.draw(screen)

        draw_points(screen)

        pygame.display.flip()
        print(pygame.mouse.get_pos())

        clock.tick(60)
        # 3. Yield control to the browser loop so it doesn't freeze
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
