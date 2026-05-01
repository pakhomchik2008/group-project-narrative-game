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




'''class SceneNode:
    def __init__(self, scene_id, scene_title, scene_description, next_scene, previous_scene, choices=None, allow_rewind=True):
        self.scene_id = scene_id
        self.scene_title = scene_title
        self.scene_description = scene_description
        self.choices = choices if choices is not None else []
        self.next_scene = next_scene
        self.previous_scene = previous_scene
        self.allow_rewind = allow_rewind

    def get_clue(self):
        if self.next_scene is None:
            return 'No further scenes.'
        next_node = scenes[self.next_scene]
        words = next_node.scene_description.split()
        return ' '.join(words[:10]) + '...'

    def make_choice(self, choice_id):
        for choice in self.choices:
            if choice['id'] == choice_id:
                return scenes[choice['next']]
        return None

    def do_rewind(self):
        if not self.allow_rewind:
            print('Rewind not allowed at this scene.')
            return None
        if self.previous_scene is None:
            print('Already at the first scene.')
            return None
        previous = scenes[self.previous_scene]
        print('Rewinding to:', previous.scene_title)
        return previous


choices_s1 = [
    {'id': 'A', 'text': 'Go left',  'next': 'S2'},
    {'id': 'B', 'text': 'Go right', 'next': 'Q1'},
]

scenes = {
    'S1': SceneNode('S1', 'The Beginning', 'You wake up in a dark room with two doors ahead of you.', next_scene='S2', previous_scene=None, choices=choices_s1),
    'S2': SceneNode('S2', 'The Corridor',  'A long corridor stretches before you, flickering lights overhead.', next_scene='Q1', previous_scene='S1'),
    'Q1': SceneNode('Q1', 'The Exit',      'You find a locked door. There is no way forward.', next_scene=None, previous_scene='S2', allow_rewind=False),
}
'''
class ClueDependencyGraph:
    # some clues have to come before others - sophia's hint before adrian's
    # finances, parking record before the poison stuff etc.
    # i'm storing both directions so i don't have to loop to find either side
    #   _adj[A]      = what A unlocks
    #   _prereqs[B]  = what you need before B

    def __init__(self) -> None:
        self._adj: Dict[str, List[str]] = {}
        self._prereqs: Dict[str, List[str]] = {}

    def add_clue(self, clue_id: str) -> None: #if clue doesnt exist in _adj = add automatically
        self._adj.setdefault(clue_id, [])
        self._prereqs.setdefault(clue_id, [])

    def add_dependency(self, before: str, after: str) -> None:
        # before unlocks after
        self.add_clue(before)
        self.add_clue(after)
        self._adj[before].append(after)
        self._prereqs[after].append(before)

    '''def prerequisites_met(self, clue_id: str, found: set) -> bool:
        # don't show the clue unless the player already has everything it needs
        return all(p in found for p in self._prereqs.get(clue_id, []))'''

    def topological_sort(self) -> Optional[List[str]]:
        # figure out a valid order to discover all clues
        # returns None if there's a cycle (A needs B, B needs A - impossible)
        # kahn's algorithm: start with clues that need nothing,
        # process them, unlock what they gate, repeat

            in_degree = {node: len(prereqs)
                     for node, prereqs in self._prereqs.items()}

        queue = deque(node for node, deg in in_degree.items() if deg == 0)
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)
            for dependent in self._adj[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(self._prereqs):
            return None  # cycle somewhere, can't sort
        return result
