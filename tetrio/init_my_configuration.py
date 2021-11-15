# Run this file to init your configurations.
# It creates a setting.bmp
# Follow the instructions prompted in console.

import time

import PIL
import matplotlib.pylab as plt
from PIL import Image
from PIL import ImageDraw
from PIL import ImageGrab

WINDOW_SIZE = (0, 0, 1700, 1700)


def GetScreen() -> PIL.Image:
  im = ImageGrab.grab(WINDOW_SIZE)
  draw = ImageDraw.Draw(im)

  r = (255, 0, 0)
  g = (0, 255, 0)
  b = (0, 0, 255)

  green_box = []
  red_box = []
  blue_box = []

  def DrawSingleRect(xy, fill):
    l1 = [xy[0], (xy[1][0], xy[0][1])]
    l2 = [xy[0], (xy[0][0], xy[1][1])]
    l3 = [(xy[0][0], xy[1][1]), xy[1]]
    l4 = [(xy[1][0], xy[0][1]), xy[1]]
    draw.line(l1, fill=fill)
    draw.line(l2, fill=fill)
    draw.line(l3, fill=fill)
    draw.line(l4, fill=fill)

  def DrawRectangles():
    print("Drawing...")
    DrawSingleRect(green_box, fill=g)
    DrawSingleRect(red_box, fill=r)
    DrawSingleRect(blue_box, fill=b)

  def Onclick(event):
    data = (event.xdata, event.ydata)
    print(data, Onclick.n)
    if Onclick.n < 2:
      print("Click the left top and bot right corner for game board.")
      green_box.append(data)
    elif Onclick.n < 4:
      print("Click the left top and bot right corner for held box.")
      red_box.append(data)
    elif Onclick.n < 5:
      print("Click the left top corner for next pieces.")
      blue_box.append(data)
    elif Onclick.n < 6:
      print("Click the bot right corner for next pieces.")
      blue_box.append(data)
      DrawRectangles()
      print("You may close this window now.")
    Onclick.n += 1

  Onclick.n = 0

  fig = plt.figure()
  plt.margins(x=0)
  fig.tight_layout()
  fig.canvas.mpl_connect("button_press_event", Onclick)
  plt.imshow(im)
  plt.show()

  im.save("settings.png")

  print("setting.png saved.")


if __name__ == "__main__":
  if True:
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
  GetScreen()
