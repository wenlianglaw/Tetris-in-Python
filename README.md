# Tetris python implementation

Implemented the Tetirs with Python, and some basic AI agents for personal learning.

![demo1.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/demo1_pc_setup.gif)

![demo2.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/demo2_normal_play.gif)

![demo3.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/near_perfect_bot.gif)

## Requirements & Install

- numpy
- pyopengl
- pyopengl-accelerate
- readerwriterlock
- PIL
- keyboard (keyboard simulation for tetr.io bot)
- mss (faster screenshot lib)
- parameterized (for testing)
- scipy

```bash
python3 -m pip install numpy pyopengl pyopengl-accelerate readerwriterlock PIL keyboard mss parameterized scipy
```

## If you counter OpenGL issue

### For MacOS Big Sur

Probably https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos

You might need to manually update pyopengl config ctypesloader.py, change
`fullName=...`
to
`fullName = "/System/Library/Frameworks/{}.framework/{}".format(name, name)`

ctypesloader.py file is located in the python package folder, for example,

```bash
vim /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/OpenGL/platform/ctypesloader.py
```

### For Windows
*Use this link to install PyOpenGL*

Suggested pyopengl and pyopengl-accelerate download location since it contains the runtime, otherwise you might run into .dll missing errors
- https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl

## How to play
```py
python ./main.py
```

To play with keyboard.  Set `keyboard=True` in main.py

To play in AI mode, set `keyboard = False` and pass the agent with
the AI you want.

```
Arrow key: Move left, right or soft drop
Arrow up: Swap the current piece and held piece
Space: Hard drop
r: 90 Rotation
e: 270 Rotation
w: 180 Rotation
g: Restart
```

These settings are defined in the `settings.py`

## Tetris default settings

Map size: 10 * 20

Length buffer lines: 3

Bags: 7-Bag random

Sliding: Yes

Locking: Yes
- 1s incremental locking time
- 3s maximum locking time

Spins:
-  T-Spin
-  ZS Spin: Yes
-  LJ Spin: Yes
-  I Spin: Yes
- O Spin: NO since I don't know how it works, and its rarely used in real games.

B2B: No

Rotations:
- 90 Degree rotation: Yes
- 180 Degree rotation: Yes. No wall-kicks
- 270 Degree rotation: Yes

Backend: game_client

Frontend: PyOPenGL

- DAS: YES
- ARR: YES

Reference:

- Spins: https://tetris.fandom.com/wiki/SRS

# Tetr.io bot

The bot is made for the [Tetr.io](https://tetr.io/), **Zen mode only**. It uses mss python lib to grab your screenshot,
analyze the Tetr.io window and extract the current game state. Then it interacts with the TetrIO game client using
keyboard lib.

Before using the TetrIO bot, you need to first configure the bot setting by running `./tetrio/init_my_configuration.py`
Select the window size, then cilck the border of the hold area, game board area and the next pieces area. After this you
could run `./tetrio/tetr_bot_v1.py` with TetrIO client running on Zen mode.

![demo3.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/tetrio_zen_mode.gif)

