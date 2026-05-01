import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import heapq
from collections import deque
from typing import List, Dict, Optional, Tuple
#List[str] = list every item is str
#List[int] = every item is int
# Tuple[str, str] = tuple w 2 strings inside
#Dict = fictionary
# Optional[str] = either str or None, works same way ip Optional[int]


import time
import os
from PIL import Image, ImageTk, ImageFilter, ImageDraw



'''from scipy.interpolate import Akima1DInterpolator
import matplotlib.pyplot as plt
import math
class SceneNode:
    def __init__(self, scene_id, scene_title, scene_description,next_scene,previous_scene,choices=True,get_clue = None,rewind = True):
        self.scene_id = scene_id
        self.scene_title = scene_title
        self.scene_description = scene_description
        self.choices = choices if choices is not None else []
        self.next_scene = next_scene
        self.previous_scene = previous_scene
        self.clue = get_clue
        self.rewind = rewind
    def get_clue(self,get_clue):
        clue_description = self.scene_description
        next_scene = scenes[self.next_scene]
        print(next_scene.get_clue())
        return ' '.join(clue_description.split()[:10]) + '...'
            if get_clue is None:
                get_clue = False

    def choices(self,choices):
        if choices == 'A':
            next_scene = self.next_scene
        if choices == 'B':
            next_scene = self.next_scene


    def make_choice(self, choice_id):
        for choice in self.choices:
            if choice['id'] == choice_id:
                return scenes[choice['next']]  # returns the next SceneNode
            return None


    def rewind(self,previous_scene,rewind=True):
        if self.rewind:
            previos_scene = scenes[self.previous_scene]
            print('returnings next sceeneeeee.....', previos_scene)
            return previos_scene

        else:
            rewind = False






scenes = {
    'S1': SceneNode('S1', 'Title', 'Description...', 'S2','None',),
    'S2': SceneNode('S2', 'Title', 'Description...', 'Q1','S1',),
    'Q1': SceneNode('Q1', 'Title', 'Description...', 'sA......', 'S2',),
}

choices = [
      {'id': 'A', 'text': 'Go left',  'next': 'S2'},
      {'id': 'B', 'text': 'Go right', 'next': 'Q1'},
  ]

'''


class Dependencygraph:
    def __init__(self) -> None:
        self._ifAthanB: Dict[str, List[str]] = {}
        self._ifBthanA: Dict[str, List[str]] = {}

    def set_default(self):
        self._ifAthanB.setdefault('id', [])
        self._ifBthanA.setdefault('id', [])

    def if_requirements_met(self,clue_id,found):
        re
