import pygame
import asyncio  # 1. Required for WASM/browser compatibility

points = [
    # red
    (350, 290),
    (390, 290),
    (390, 215),
    (450, 215),
    (450, 140),
    (380, 140),
    (310, 140),
    (310, 50),
    (170, 50),
    (50, 50),
    (50, 140),
    (50, 215),
    (170, 215),
    (170, 140),
    (240, 140),
    # yellow
    (240, 215),
    (310, 215),
    (310, 290),
    (240, 290),
    (240, 355)
]


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    running = True

    # initialize maze
    maze = pygame.image.load("maze.png")
    maze_rect = maze.get_rect()
    maze_rect.topleft = (10, 10)

    # initialize blinky
    class Ghost:
        pos = pygame.Vector2(0, 0)
        sprites = []
        next_point = 0

    blinky = Ghost()
    # starting pos
    blinky.pos = pygame.Vector2(320, 325)
    for i in range(4):
        blinky.sprites.append(pygame.image.load(f"blinky/blinky_{i}.png"))

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

        # draw ghosts
        scaled = pygame.transform.scale(
            blinky.sprites[0],
            (blinky.sprites[0].get_width() * 3, blinky.sprites[0].get_height() * 3),
        )
        rect = scaled.get_rect()
        rect.x = blinky.pos.x
        rect.y = blinky.pos.y
        screen.blit(scaled, rect)

        # draw all points (debugging)
        interval = 15
        for p in range(len(points)):
            if p < interval * 1:
                col = min(p / interval * 1 * 255 + 10, 255)
                pygame.draw.circle(screen, (col, 0, 0), points[p], 5, 2)
            elif p < interval * 2:
                col = min(p / interval * 2 * 255 + 10, 255)
                pygame.draw.circle(screen, (col, col, 0), points[p], 5, 2)

        pygame.display.flip()
        print(pygame.mouse.get_pos())

        clock.tick(60)
        # 3. Yield control to the browser loop so it doesn't freeze
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
