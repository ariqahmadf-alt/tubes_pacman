import os
import pygame
import asyncio
from copy import deepcopy
import config
import maze

import heapq
from itertools import count

path = [(0, 0), (0, 1), (0, 2), (0, 3)]

ROOT = os.path.dirname(os.path.abspath(__file__))

original_speed = config.ghost_speed


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

    def __init__(self, point, name, ai_type):
        self.pos = pygame.Vector2(point.spos(), point.spos())
        self.path = [point]
        self.sprites = []
        self.last_point = point
        self.ai_type = ai_type
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
            for y in range(len(maze.points)):
                for x in range(len(maze.points[y])):
                    maze.points[y][x].prio = -1

            self.last_point = maze.points[int(self.path[0].pos.y)][
                int(self.path[0].pos.x)
            ]
            self.last_point.prio = 0

            # process AI based on type
            match self.ai_type:
                case 0:
                    self.path = []
                    self.dummy(self.last_point, pygame.mouse.get_pos())
                case 1:
                    self.path = []
                    self.queue = []
                    self.queue_curr = 0
                    if hasattr(self, "target_point"):
                        del self.target_point
                    self.ucs_explore(self.last_point)
                    if hasattr(self, "target_point"):
                        self.ucs_path(self.target_point)
                        self.path.reverse()
                        # print(self.path[0].pos)
                case 2:
                    self.path = []
                    self.queue = []
                    self.queue_curr = 0

                    if hasattr(self, "target_point"):
                        del self.target_point

                    self.astar_explore(self.last_point)

                    if hasattr(self, "target_point"):
                        self.ucs_path(self.target_point)
                        self.path.reverse()
                case 3:
                    self.path = []
                    self.queue = []
                    self.queue_curr = 0
                
                    if hasattr(self, "target_point"):
                        del self.target_point
                
                    self.greedy_explore(self.last_point)
                
                    if hasattr(self, "target_point"):
                        self.ucs_path(self.target_point)
                        self.path.reverse()

    # from GPT 5.6 (using main.py and maze.py as context)
    def astar_explore(self, start):
        frontier = []
        tie_breaker = count()
        target_pos = pygame.mouse.get_pos()

        start.prio = 0
        self.queue = []

        heuristic = lambda point: dist(point.spos(), target_pos)

        heapq.heappush(
            frontier,
            (heuristic(start), next(tie_breaker), 0, start),
        )

        while frontier:
            _, _, cost, point = heapq.heappop(frontier)

            # Ignore stale entries after a cheaper route was found.
            if cost != point.prio:
                continue

            self.queue.append(point)

            if dist(target_pos, point.spos()) < 10:
                self.target_point = point
                return

            neighbors = (
                getattr(point, "right", None),
                getattr(point, "left", None),
                getattr(point, "top", None),
                getattr(point, "bottom", None),
            )

            for neighbor in neighbors:
                if neighbor is None:
                    continue

                new_cost = cost + 1

                if neighbor.prio == -1 or new_cost < neighbor.prio:
                    neighbor.prio = new_cost
                    priority = new_cost + heuristic(neighbor)

                    heapq.heappush(
                        frontier,
                        (priority, next(tie_breaker), new_cost, neighbor),
                    )

    # from GPT 5.6 (using main.py and maze.py as context)
    # Osman's first attempt made a FIFO list by accident
    def ucs_explore(self, start):
        frontier = []
        tie_breaker = count()

        start.prio = 0
        self.queue = []

        heapq.heappush(
            frontier,
            (0, next(tie_breaker), start),
        )

        target_pos = pygame.mouse.get_pos()

        while frontier:
            cost, _, point = heapq.heappop(frontier)

            # Ignore stale entries left behind after a cheaper route was found.
            if cost != point.prio:
                continue

            self.queue.append(point)

            if dist(target_pos, point.spos()) < 10:
                self.target_point = point
                return

            neighbors = (
                getattr(point, "right", None),
                getattr(point, "left", None),
                getattr(point, "top", None),
                getattr(point, "bottom", None),
            )

            for neighbor in neighbors:
                if neighbor is None:
                    continue

                new_cost = cost + 1

                if neighbor.prio == -1 or new_cost < neighbor.prio:
                    neighbor.prio = new_cost

                    heapq.heappush(
                        frontier,
                        (new_cost, next(tie_breaker), neighbor),
                    )

    def greedy_explore(self, start):
        frontier = []
        tie_breaker = count()
        target_pos = pygame.mouse.get_pos()

        start.prio = 0
        self.queue = []

        heuristic = lambda point: dist(point.spos(), target_pos)

        heapq.heappush(
            frontier,
            (heuristic(start), next(tie_breaker), 0, start),
        )

        while frontier:
            _, _, cost, point = heapq.heappop(frontier)

            # Ignore stale entries after a cheaper route was found.
            if cost != point.prio:
                continue

            self.queue.append(point)

            if dist(target_pos, point.spos()) < 10:
                self.target_point = point
                return

            neighbors = (
                getattr(point, "right", None),
                getattr(point, "left", None),
                getattr(point, "top", None),
                getattr(point, "bottom", None),
            )

            for neighbor in neighbors:
                if neighbor is None:
                    continue

                new_cost = cost + 1

                if neighbor.prio == -1 or new_cost < neighbor.prio:
                    neighbor.prio = new_cost

                    # Greedy best-first uses only h(n), unlike A*'s g(n) + h(n).
                    heapq.heappush(
                        frontier,
                        (heuristic(neighbor), next(tie_breaker), new_cost, neighbor),
                    )

    def ucs_path(self, point):
        next_point = point
        closest = point.prio

        # if hasattr(point, "right"):
        #     print("r", point.right.prio)
        # if hasattr(point, "left"):
        #     print("l", point.left.prio)
        # if hasattr(point, "top"):
        #     print("t", point.top.prio)
        # if hasattr(point, "bottom"):
        #     print("b", point.bottom.prio)

        # go to neighbor with smallest prio
        if (
            hasattr(point, "right")
            and point.right.prio != -1
            and point.right.prio < closest
        ):
            next_point = point.right
            closest = point.right.prio
        if (
            hasattr(point, "left")
            and point.left.prio != -1
            and point.left.prio < closest
        ):
            next_point = point.left
            closest = point.left.prio
        if hasattr(point, "top") and point.top.prio != -1 and point.top.prio < closest:
            next_point = point.top
            closest = point.top.prio
        if (
            hasattr(point, "bottom")
            and point.bottom.prio != -1
            and point.bottom.prio < closest
        ):
            next_point = point.bottom
            closest = point.bottom.prio

        if next_point.pos == point.pos:
            return
        self.path.append(point)
        self.ucs_path(next_point)

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
            closest_point.prio = next_point.prio + 1
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
        font = pygame.font.SysFont("Arial", 16)
        highest_queue_prio = 1
        for queue in self.queue:
            highest_queue_prio = max(highest_queue_prio, queue.prio)
        highest_path_prio = 1
        for path in self.path:
            highest_path_prio = max(highest_path_prio, path.prio)
        for y in range(len(maze.points)):
            for x in range(len(maze.points[y])):
                if maze.points[y][x].wall:
                    continue
                pos = deepcopy(maze.points[y][x].pos)

                # use different points if this point is in the queue, path, or is target
                col = "#dda49c"
                if hasattr(self, "target_point") and self.target_point.pos == pos:
                    col = "green"
                else:
                    for queue in self.queue:
                        if queue.pos == pos:
                            col = "blue" if config.maze_type == 0 else "magenta"
                    for path in self.path:
                        if path.pos == pos:
                            col = "red"
                pos *= config.maze_scale
                pos.x += config.maze_scale / 2
                pos.y += config.maze_scale / 2

                pos.x -= 7.5
                pos.y -= 7.5

                screen.blit(font.render(str(maze.points[y][x].prio), True, col), pos)
                # use different color if this point is in the expanded list
                # pygame.draw.circle(screen, col, pos, 3, 5)


# initialize ghosts
ghosts = []
ghosts.append(Ghost(maze.points[4][6], "blinky", 2))
ghosts.append(Ghost(maze.points[1][26], "pinky", 1))
ghosts.append(Ghost(maze.points[29][26], "inky", 0))
ghosts.append(Ghost(maze.points[29][1], "clyde", 3))

def draw_points(screen):
    for y in range(len(maze.points)):
        for x in range(len(maze.points[y])):
            if maze.points[y][x].wall:
                continue
            pos = deepcopy(maze.points[y][x].pos)
            col = "#dda49c"
            pos *= config.maze_scale
            pos.x += config.maze_scale / 2
            pos.y += config.maze_scale / 2
            pygame.draw.circle(screen, col, pos, 3, 5)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()
    running = True
    maze_og_toggle = True
    active_ghost = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill("black")

        # switch ghosts based on keys 1-4
        if pygame.key.get_just_pressed()[pygame.K_1]:
            active_ghost = 0
        if pygame.key.get_just_pressed()[pygame.K_2]:
            active_ghost = 1
        if pygame.key.get_just_pressed()[pygame.K_3]:
            active_ghost = 2
        if pygame.key.get_just_pressed()[pygame.K_4]:
            active_ghost = 3
        if pygame.key.get_just_pressed()[pygame.K_4]:
            active_ghost = 4

        # draw maze
        if pygame.key.get_just_pressed()[pygame.K_SPACE]:
            maze_og_toggle = not maze_og_toggle
        if pygame.key.get_just_pressed()[pygame.K_a]:
            config.ghost_speed = (
                0 if config.ghost_speed == original_speed else original_speed
            )

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

        if active_ghost != 4:
            ghosts[active_ghost].draw_points(screen)
            ghosts[active_ghost].ai()
            ghosts[active_ghost].draw(screen)
        else:
            draw_points(screen)
            for ghost in ghosts:
                ghost.ai()
                ghost.draw(screen)

        pygame.display.flip()
        # print(pygame.mouse.get_pos())

        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
