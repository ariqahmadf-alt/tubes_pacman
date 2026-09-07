# Tubes Pacman

This is the tubes (tugas besar) for Kecedarsan Buatan (FPMIPA).

## Architecture

This simulation is created and run with Python, as well as pygame-ce (Community Edition).

## How it Works

The maze is filled with invisible points that ghosts use to determine their next position.
These points are also used as nodes in a graph to determine the closest position to Pac-man.

*Everything after this is WIP and not yet implemented.*

Each ghost will use a different searching algorithm:

- Clyde (Orange) - Greedy
- Inky (Blue) - UCS
- Pinky (Pink) - BFS
- Blinky (Red) - A*
