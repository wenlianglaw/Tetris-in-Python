# Tetris python implementation 

Implemented the Tetirs with Python, and some basic AI agents for personal learning.

![demo1.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/demo1_pc_setup.gif)

![demo2.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/demo2_normal_play.gif)

![demo3.gif](https://github.com/wenlianglaw/Tetris-in-Python/blob/master/gifs/near_perfect_bot.gif)

## Requirements & Install

- numpy
- scipy
- pyopengl
- pyopengl-accelerate
- readerwriterlock
- PIL
- keyboardr (keyboard simulation for tetr.io bot)
- mss (faster screenshot lib)

### For Mac
```
pip install numpy scipy pyopengl pyopengl-accelerate readerwriterlock pillow keyboard mss
```

#### If you counter OpenGL issue in MacOS Big Sur

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

```
pip install numpy scipy readerwriterlock
```

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
-  O Spin: NO since I don't know how it works,
     and its rarely used in real games.

B2B: No

Rotations:
- 90 Degree rotation: Yes
- 180 Degree rotation: Yes. No wall-kicks
- 270 Degree rotation: Yes

Backend: game_client

Frontend: PyOPenGL
-  DAS: YES
-  ARR: YES


Reference:

  - Spins: https://tetris.fandom.com/wiki/SRS

