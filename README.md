# Plane War

A vertical-scrolling arcade shooter built in Python with Pygame. Originally a Grade 10 CS project, rewritten with delta-time physics, sprite animations, and a proper game loop.

## Requirements

- Python 3.8+
- `pygame`

Install dependencies:

```
pip install pygame
```

## Run

From the project root:

```
python main.py
```

## Controls

| Key | Action |
| --- | --- |
| `W` / `A` / `S` / `D` or arrow keys | Move the plane |
| `Shift` (Left or Right) | Boost (consumes energy, regenerates when released) |
| `P` or `Esc` | Pause / resume |
| `R` | Restart (on the game-over screen) |
| `M` | Return to main menu (on the game-over screen) |
| Mouse click on `PLAY` / `EXIT` | Menu navigation |

Bullets fire automatically every 0.6 seconds. Enemies spawn from the top. Contact with an enemy costs 20 health.

## Project Layout

```
main.py        # Main loop, menu, UI, collision handling
sprites.py     # Player, Bullet, Enemy classes + asset loading helpers
resources/     # Images, fonts, sound
```
