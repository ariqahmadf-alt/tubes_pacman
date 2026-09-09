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
    queue = []
    queue_curr = 0

    # 0 - dummy AI
    # 1 - UCS
    ai_type = 0

    def __init__(self, point, name):
        self.pos = pygame.Vector2(point.spos(), point.spos())
        self.path = [point]
        self.sprites = []
        self.last_point = point
        for i in range(4):
            sprite = pygame.image.load(f"{ROOT}/assets/{name}/{name}_{i}.png")
            self.sprites.append(sprite)

    def ai(self):
        # safeguard: stay at last point if there's no path
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
            self.dir = 2
        elif self.pos.x < point.spos().x:
            self.pos.x += min(config.ghost_speed, abs(point.spos().x - self.pos.x))
            self.dir = 0

        if self.pos.y > point.spos().y:
            self.pos.y -= min(config.ghost_speed, abs(point.spos().y - self.pos.y))
            self.dir = 3
        elif self.pos.y < point.spos().y:
            self.pos.y += min(config.ghost_speed, abs(point.spos().y - self.pos.y))
            self.dir = 1

        # move to next point if ghost is close to its current
        if dist(point.spos(), self.pos) < 1:

            # prepare points for ghost AI
            for row in maze.points:
                for point in row:
                    point.prio = -1
            self.last_point = deepcopy(self.path[0])
            self.last_point.prio = 0

            # process AI based on type
            match(self.ai_type):
                case 0:
                    self.last_point = deepcopy(self.path[0])
                    self.path = []
                    self.dummy(self.last_point, pygame.mouse.get_pos())
                case 1:
                    self.queue = []
                    self.queue_curr = 0
                    self.ucs(self.last_point)

    def ucs(self, point):
        if dist(pygame.mouse.get_pos(), point.spos()) < 30:
            self.target_point = point
            return

        point.add_to_queue(self.queue)

        if hasattr(point, 'right'):
            point.right.set_queue_properties(self.pos, point.prio+1)
        if hasattr(point, 'left'):
            point.left.set_queue_properties(self.pos, point.prio+1)
        if hasattr(point, 'top'):
            point.top.set_queue_properties(self.pos, point.prio+1)
        if hasattr(point, 'bottom'):
            point.bottom.set_queue_properties(self.pos, point.prio+1)

        # go to the next point in the queue
        self.queue_curr += 1
        if self.queue_curr > len(self.queue) - 1:
            return
        self.ucs(self.queue[self.queue_curr])

    # recursively find the closest point to target
    def dummy(self, next_point, target):
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
            self.dummy(closest_point, mouse)

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

    def draw_points(self, screen):
        highest_prio = 1
        for queue in self.queue:
            highest_prio = max(highest_prio, queue.prio)
        for y in range(len(maze.points)):
            for x in range(len(maze.points[y])):
                if maze.points[y][x].wall:
                    continue
                pos = deepcopy(maze.points[y][x].pos)

                # use different color if this point is in the expanded list
                col = "#dda49c"
                if hasattr(self, 'target_point') and self.target_point.pos == pos:
                    col = "green"
                else:
                    for queue in self.queue:
                        if queue.pos == pos:
                            col = (0, 0, (queue.prio / highest_prio) * 255)
                pos *= config.maze_scale
                pos.x += config.maze_scale / 2
                pos.y += config.maze_scale / 2
                # use different color if this point is in the expanded list
                pygame.draw.circle(screen, col, pos, 3, 5)


# initialize ghosts
ghosts = []
ghosts.append(Ghost(maze.points[4][6], "blinky"))
# ghosts.append(Ghost(maze.points[1][26], "pinky"))
# ghosts.append(Ghost(maze.points[29][26], "inky"))
# ghosts.append(Ghost(maze.points[29][1], "clyde"))


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    running = True
    maze_og_toggle = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")

        # draw maze
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            maze_og_toggle = not maze_og_toggle

        img_to_use = maze.maze_og_img if maze_og_toggle else maze.img
        divisor = 8.0 if maze_og_toggle else 1.0
        final_img = pygame.transform.scale(
            img_to_use,
            (
                img_to_use.get_width() * config.maze_scale / divisor,
                img_to_use.get_height() * config.maze_scale / divisor,
            ),
        )
        screen.blit(final_img, maze.rect)

        ghosts[0].draw_points(screen)

        for ghost in ghosts:
            ghost.ai()
            ghost.draw(screen)

        pygame.display.flip()
        # print(pygame.mouse.get_pos())

        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
