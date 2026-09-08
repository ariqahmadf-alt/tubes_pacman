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
generation.

![Simple maze layout. Points will be automatically generated based on all pixels](assets/maze0.png)

_Everything after this is WIP and not yet implemented._

Each ghost will use a different searching algorithm:

- Clyde (Orange) - Greedy
- Inky (Blue) - UCS
- Pinky (Pink) - BFS
- Blinky (Red) - A\*

## Configuring

The configuration file, `config.py`, provides a few settings to edit the
simulation:

- `maze_type` - Changes the type of maze being used. Currently 3 are supported
  (simple, big, original).
- `maze_scale` - Changes the size of everything in the simulation. Use if the
  maze type is too big for the screen.
- `ghost_speed` - How fast all ghosts move. Can be set to 0 to freeze them.
