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
        speed = 0
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
    # top-left
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
    (170, 140),  # middle
    (240, 355),
    (240, 290),
    #
    # top-right
    (385, 290),
    (385, 215),
    (450, 215),
    (450, 140),
    (385, 140),
    (385, 50),
    (450, 50),
    (530, 50),
    (640, 50),
    (640, 140),
    (640, 215),
    (530, 215),
    (530, 355),
    (530, 140),  # middle
    (450, 355),
    (450, 290),
    #
    # bottom left
    (240, 430),  # fruit left
    (240, 500),
    (170, 500),
    (50, 500),
    (50, 575),
    (90, 575),
    (90, 645),
    (50, 645),
    (50, 710),
    (310, 710),
    (310, 645),
    (240, 645),
    (240, 575),
    (300, 575),
    (300, 500),
    (170, 575),  # middle
    (170, 645),  # middle
    #
    # bottom right
    (450, 430),  # fruit right
    (450, 500),
    (385, 500),
    (385, 575),
    (450, 575),
    (450, 645),
    (385, 645),
    (385, 710),
    (640, 710),
    (640, 645),
    (595, 645),
    (595, 575),
    (640, 575),
    (640, 500),
    (530, 500),
    (530, 575), # middle
    (530, 645), # middle
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
    interval = 15
    for p in range(len(points)):
        if p < interval * 1:
            col = min(p / interval * 1 * 255 + 50, 255)
            pygame.draw.circle(screen, (col, 0, 0), points[p], 5, 2)
        elif p < interval * 2:
            col = min(p / interval * 2 * 255 + 10, 255)
            pygame.draw.circle(screen, (col, col, 0), points[p], 5, 2)
        else:
            pygame.draw.circle(screen, (col, col, col), points[p], 5, 2)


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
