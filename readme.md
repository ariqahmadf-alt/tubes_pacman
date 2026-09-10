# Tubes Pacman

This is the tubes (tugas besar) for Kecedarsan Buatan (Ilmu Komputer FPMIPA).

## Architecture

This simulation is created and run with Python, as well as pygame-ce (Community
Edition).

## How it Works

The maze is filled with invisible points that ghosts use to determine their next
position. These points are also used as nodes in a graph to determine the
closest position to Pac-man.

### Maze generation

Ghosts navigate the maze using a set of automatically-generated, invisible
points.

These points are generated based on the maze image. Each pixel of the maze image
is considered:

- **White pixel** - wall
- **Black pixel** - free spot

Neighbours are automatically set for each point (orthogonally) during
generation. Whenever a point is created, the following is checked:

- Is there a point on the left side? If yes, set it as the left neighbor of this
  point (and vice versa)
- Is there a point on the top side? If yes, set it as the top neighbor of this
  point (and vice versa)

![The layout image used to generate the original Pac-Man maze](src/assets/maze0.png)

Each ghost will use a different searching algorithm:

- Clyde (Orange) - Greedy
- Inky (Blue) - UCS
- Pinky (Pink) - BFS
- Blinky (Red) - A\*

## Configuring

The configuration file, `config.py`, provides a few settings to edit the
simulation:

- `maze_type` - Changes the type of maze being used. Currently 2 are supported:
  - Pac-Man
  - Ms. Pac-Man 1
- `maze_scale` - Changes the size of everything in the simulation. Use if the
  maze type is too big for the screen.
- `ghost_speed` - How fast all ghosts move. Can be set to 0 to freeze them.
