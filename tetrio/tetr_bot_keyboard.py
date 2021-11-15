# This file provides the function to simulate the keyboard
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

import keyboard as kb

import actions


def Rotate90():
  kb.press_and_release('r')


def Rotate180():
  kb.press_and_release('w')


def Rotate270():
  kb.press_and_release('e')


def Down():
  kb.press_and_release('down')


def Left():
  kb.press_and_release('left')


def Right():
  kb.press_and_release('right')


def SoftDrop():
  kb.press_and_release('down')


def HardDrop():
  kb.press_and_release('space')


def SimulateAction(action: actions.Action):
  if action.rotation == 1:
    Rotate90()
  if action.rotation == 2:
    Rotate180()
  if action.rotation == 3:
    Rotate270()

  if action.direction == 1 or action.down:
    Down()
  if action.direction == 2:
    Left()
  if action.direction == 3:
    Right()
  # Soft drop
  if action.direction == 4:
    SoftDrop()
  # Hard drop
  if action.direction == 5:
    HardDrop()
