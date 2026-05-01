"""
Whispers at Victor's Manor
FP016 Computer Science — Summative Assessment 2

A branching narrative mystery game built in Python.
The player investigates a suspicious death at Victor's Manor
and must uncover the truth through a series of choices.

My role: Game Engine Developer (Algorithms & Logic)
"""

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


# =============================================================================
# SECTION 1 — DATA STRUCTURES
# =============================================================================

class StoryNode:

    def __init__(self,node_id: str,title: str,text: str,choices: Optional[List[Tuple[str, str]]] = None ,clue: Optional[Dict] = None,is_ending: bool = False,ending_type: str = "",allow_rewind: bool = True,) -> None:
        #Optional[List[Tuple[str, str]]] = None returns either none or the list of tuples
        self.node_id = node_id
        self.title = title
        self.text = text
        self.choices = choices if choices else []   # if choices is falsy use empty [] instead
        self.clue = clue
        self.is_ending = is_ending
        self.ending_type = ending_type
        self.allow_rewind = allow_rewind

    def __repr__(self) -> str:
        return f"StoryNode(id={self.node_id!r}, title={self.title!r})"   #r! add quotes automatically


class Stack:
    def __init__(self) -> None: #this function returns none
        self._data: List[str] = []

    def push(self, item: str) -> None:
        self._data.append(item)

    def pop(self) -> Optional[str]: # this item return either str or none
        if self.is_empty():
            return None
        return self._data.pop()

    def peek(self) -> Optional[str]:
        if self.is_empty():
            return None
        return self._data[-1]

    def is_empty(self) -> bool:           #Returns True if the list has 0 items, False otherwise.
        return len(self._data) == 0

    def size(self) -> int:  #Returns how many items are in the stack.
        return len(self._data)

    def copy_list(self) -> List[str]:   # Returns a copy of the internal list
        return list(self._data)


class ClueHeap:
    def __init__(self) -> None:
        self.heap: List[Tuple] = []
        self.counter: int = 0  # used as a tiebreaker

    def add_clue(self, clue_id: str, name: str, description: str,importance: int, time_found: int) -> None:
        entry = (-importance, time_found, self.counter, clue_id, name, description)
        heapq.heappush(self.heap, entry)
        self.counter += 1
        print(f"Clue added to heap: {name!r} (importance={importance})")

    def get_sorted_clues(self) -> List[Dict]:
        copy_heap = list(self.heap)
        heapq.heapify(copy_heap)
        result = []
        while copy_heap:
            neg_imp, time_f, _, cid, name, desc = heapq.heappop(copy_heap)
            result.append({
                "id": cid,
                "name": name,
                "description": desc,
                "importance": -neg_imp,
                "time_found": time_f,
            })
        return result

    def size(self) -> int:
        return len(self.heap)


# =============================================================================
# SECTION 2 — STORY GRAPH
# =============================================================================

def build_story_graph() -> Dict[str, StoryNode]:
    """
    Creates all the scenes and connects them into a graph.
    The story starts at S1 and branches into two main routes
    (Security Guard or Sophia), each leading to different endings.
    Using a dict means we can look up any scene in O(1) by its id.
    """
    graph: Dict[str, StoryNode] = {}

    # --- Opening scenes ---
    graph["S1"] = StoryNode(
        "S1",
        "Arrival at Victor's Manor",
        (
            "Emma is an investigative journalist who has spent years covering financial "
            "crime. Months earlier, she published a piece questioning Victor's conglomerate "
            "— hinting at irregularities in the financial statements. The article was quickly "
            "buried, but the suspicion stayed with her.\n\n"
            "Late one night, her phone rings. A panicked female voice whispers:\n"
            "  \"If you still doubt that company, come to Victor's mansion tonight.\n"
            "   This might be your last chance to see the truth.\"\n\n"
            "Driven by instinct, Emma heads to the manor. The front gate is half open. "
            "Garden lights are still on — but the house is unnaturally quiet. "
            "No servants. No guests. Only silence."
        ),
        choices=[("Enter the manor and investigate", "S2")],
    )

    graph["S2"] = StoryNode(
        "S2",
        "The Library — A Body on the Carpet",
        (
            "Inside the library, Emma finds Victor lying on the carpet beside a fallen "
            "wine glass. There are no obvious signs of a struggle. His expression is "
            "pained but oddly calm — as if he simply collapsed from his chair.\n\n"
            "Two people are present:\n\n"
            "  • The Security Guard insists he just saw someone climb over the wall:\n"
            "    \"This must have been an external hitman. I only guard the gate;\n"
            "    what happens inside is none of my business.\"\n\n"
            "  • Sophia, Victor's personal assistant, is visibly shaken. She says Victor\n"
            "    has recently been tormented by a business partner and a 'financial hole',\n"
            "    but refuses to give details.\n\n"
            "Emma knows time is limited. She cannot investigate both leads at once.\n"
            "Whose story does she trust first?"
        ),
        choices=[
            ("Trust the Security Guard — investigate the external intruder theory", "Q1_SECURITY"),
            ("Trust Sophia — investigate the internal conspiracy", "Q1_SOPHIA"),
        ],
        clue={
            "id": "C0",
            "name": "Victor's Body",
            "description": "Victor found dead beside a spilled wine glass. Possible poisoning.",
            "importance": 10,
        },
    )

    # --- Route 1: Security Branch ---
    graph["Q1_SECURITY"] = StoryNode(
        "Q1_SECURITY",
        "The Guard's Account",
        (
            "The guard describes a vague figure climbing over the east wall from the "
            "shadows, disappearing into the garden. He insists this was a professional "
            "killer for hire, and hints that Victor had 'many enemies' in business.\n\n"
            "Emma weighs his words carefully. The story is detailed — but almost "
            "too convenient. She must decide how much weight to give it."
        ),
        choices=[
            ("Believe him — follow the intruder's trail into the garden", "A3_GARDEN"),
            ("Doubt him — demand access to the CCTV system", "A3_CCTV"),
        ],
        clue={
            "id": "C1",
            "name": "Guard's Testimony",
            "description": "Guard claims a figure climbed the east wall. Story is vague but detailed.",
            "importance": 3,
        },
        allow_rewind=False,
    )

    graph["A3_GARDEN"] = StoryNode(
        "A3_GARDEN",
        "Garden Trail",
        (
            "Emma follows the route described by the guard. Near the east wall she finds "
            "a trail of blurred footprints and several discarded cigarette ends.\n\n"
            "The traces suggest a stranger might have been here — but the footprints are "
            "smudged, and the shoe model is extremely common. Nothing is conclusive.\n\n"
            "Still, the guard seems confident. Perhaps the storage room in the basement "
            "might hold more answers."
        ),
        choices=[("Search deeper — head to the underground storage room", "A4_BASEMENT")],
        clue={
            "id": "C2",
            "name": "Garden Footprints",
            "description": "Blurred footprints and cigarette ends near the east wall. Inconclusive.",
            "importance": 2,
        },
        allow_rewind=False,
    )

    graph["A4_BASEMENT"] = StoryNode(
        "A4_BASEMENT",
        "Underground Storage Room",
        (
            "Emma searches the underground storage room. Old tools, cardboard boxes, "
            "years of dust. Nothing that clearly points to any specific suspect.\n\n"
            "These 'plausible but inconclusive' external clues have dragged her "
            "investigation in the wrong direction. Convinced there was an outside killer, "
            "she writes an article speculating about a professional hitman.\n\n"
            "With no better leads, the police temporarily file the case as 'suspected "
            "external homicide'. The real internal culprit remains untouched."
        ),
        choices=[("Publish the article", "ENDING_2A")],
        clue={
            "id": "C3",
            "name": "Empty Basement",
            "description": "Old tools and dust — no meaningful evidence found here.",
            "importance": 1,
        },
    )

    graph["A3_CCTV"] = StoryNode(
        "A3_CCTV",
        "CCTV Control Room",
        (
            "Emma and the guard go to the control room together. She immediately notices "
            "something wrong: the footage from the critical time window is missing — "
            "marked as 'file corrupted'.\n\n"
            "The surrounding hours are perfectly intact. This is not a random glitch.\n\n"
            "Someone has deliberately erased evidence from the system. But who — and why?\n"
            "There may be backup tapes in the storage cabinet."
        ),
        choices=[("Search for backup tapes in the cabinet", "A4_TAPES")],
        clue={
            "id": "C4",
            "name": "Deleted CCTV Footage",
            "description": "Critical time window deleted. Surrounding hours intact — deliberate tampering.",
            "importance": 5,
        },
        allow_rewind=False,
    )

    graph["A4_TAPES"] = StoryNode(
        "A4_TAPES",
        "Discarded Backup Tapes",
        (
            "In a cabinet beneath the monitor desk, Emma discovers a pile of discarded "
            "backup tapes. Someone has clearly 'cleaned up' the evidence — but "
            "there is no way to restore what was recorded.\n\n"
            "Emma strongly suspects that someone inside the house is manipulating "
            "the evidence. But all she has are missing segments and vague timestamps. "
            "No single piece of proof clearly points to a specific person.\n\n"
            "She publishes a report noting 'inconsistencies' and possible tampering. "
            "Some officers read it — but without hard evidence, nothing happens."
        ),
        choices=[("Publish the incomplete report", "ENDING_2B")],
        clue={
            "id": "C5",
            "name": "Wiped Backup Tapes",
            "description": "Backup tapes erased. Evidence of tampering — but nothing is recoverable.",
            "importance": 4,
        },
    )

    # --- Route 2: Sophia Branch ---
    graph["Q1_SOPHIA"] = StoryNode(
        "Q1_SOPHIA",
        "Sophia's Revelation",
        (
            "Sophia speaks in hushed, urgent tones. In the days before his death, "
            "Victor was extremely anxious. He told her:\n"
            "  \"If one particular partner is ever exposed, he might do anything.\"\n\n"
            "Victor planned to confront this partner — a man named Adrian — after the "
            "evening's private dinner. He may even have been planning to reveal some of "
            "the financial irregularities.\n\n"
            "Sophia whispers: 'If the truth explodes all at once, a lot of people will "
EXP            "go down together.'\n\n"
            "Emma realises this is not a simple crime of passion. She must now decide "
            "how to begin her investigation into Adrian's world."
        ),
        choices=[
            ("Investigate Adrian's personal movements first — direct evidence route", "B3_PARKING"),
            ("Investigate the company's finances first — systemic route", "B3_FINANCE"),
        ],
        clue={
            "id": "C6",
            "name": "Sophia's Testimony",
            "description": "Victor feared business partner Adrian. A confrontation was planned that evening.",
            "importance": 7,
        },
        allow_rewind=False,
    )

    graph["B3_PARKING"] = StoryNode(
        "B3_PARKING",
        "Parking Lot Camera Records",
        (
            "Emma reviews the parking-lot camera timestamps. She finds an odd pattern:\n\n"
            "Adrian's car leaves the premises before the dinner begins, then returns "
            "within a short window that overlaps precisely with the estimated poisoning "
            "time. There is no record of any other vehicle entering during this window.\n\n"
            "This places him at the scene. It is not conclusive alone — but the "
            "timing is suspicious enough to dig further. The kitchen records may "
            "confirm what he was doing when he returned."
        ),
        choices=[("Check kitchen storage and back-of-house records", "B4_POISON")],
        clue={
            "id": "C7",
            "name": "Adrian's Car Log",
            "description": "Adrian's car returned during the estimated poisoning window.",
            "importance": 8,
        },
        allow_rewind=False,
    )

    graph["B4_POISON"] = StoryNode(
        "B4_POISON",
        "Chemical Purchase Record",
        (
            "In the kitchen storage records, Emma discovers a bottle of special "
            "chemicals locked in a separate cabinet. The purchase log shows the "
            "authorisation signature: Adrian.\n\n"
            "The substance is a controlled compound intended for laboratory use — "
            "not for any kitchen application. There is no legitimate reason for it "
            "to be here.\n\n"
            "Motive. Opportunity. Means.\n"
            "The chain of evidence is forming. One final piece could complete it."
        ),
        choices=[("Unlock Victor's private safe with Sophia's help", "B5_USB")],
        clue={
            "id": "C8",
            "name": "Chemical Purchase Log",
            "description": "Poison authorised by Adrian. Labelled for lab use — found near the kitchen.",
            "importance": 9,
        },
        allow_rewind=False,
    )

    graph["B5_USB"] = StoryNode(
        "B5_USB",
        "Victor's USB Drive",
        (
            "Sophia leads Emma to Victor's private office. With trembling hands, "
            "she opens the wall safe and retrieves a USB drive.\n\n"
            "The files inside are damning. Spreadsheets, email threads, transfer "
            "authorisations — all showing Adrian systematically embezzling company "
            "funds through a series of complex financial schemes stretching back years.\n\n"
            "Victor had been quietly collecting this evidence. He was building a case "
            "against Adrian — and Adrian must have known.\n\n"
            "Emma now holds a complete chain:\n"
            "  • Motive: Adrian faced exposure for large-scale embezzlement.\n"
            "  • Opportunity: parking records prove he had access to the scene.\n"
            "  • Means: the chemical purchase, linked directly to him.\n"
            "  • Documentation: Victor's USB with the full financial trail.\n\n"
            "What will Emma do with this?"
        ),
        choices=[("Assemble the case file and hand it to police and media", "ENDING_1")],
        clue={
            "id": "C9",
            "name": "USB Financial Files",
            "description": "Proof of Adrian's embezzlement. Victor was building a case against him.",
            "importance": 10,
        },
        allow_rewind=False,
    )

    graph["B3_FINANCE"] = StoryNode(
        "B3_FINANCE",
        "Finance Department",
        (
            "Emma visits the finance office late in the evening. The senior financial "
            "officer answers her questions with barely concealed dread:\n\n"
            "  \"If this ever comes out all at once, the company will collapse overnight\n"
            "   and hundreds of people — people who had nothing to do with any of this —\n"
            "   will be dragged down with it.\"\n\n"
            "The scale of what Emma is uncovering is far greater than a single murder. "
            "This is a systemic financial crime network. Sophia offers to take her "
            "to the underground archive room, where years of documents are kept."
        ),
        choices=[("Enter the underground archive room with Sophia", "B4_ARCHIVE")],
        clue={
            "id": "C10",
            "name": "Finance Officer's Warning",
            "description": "Corruption spans multiple executives and threatens hundreds of innocent employees.",
            "importance": 6,
        },
        allow_rewind=False,
    )

    graph["B4_ARCHIVE"] = StoryNode(
        "B4_ARCHIVE",
        "Underground Archive Room",
        (
            "Row upon row of filing cabinets. Emma and Sophia spend hours working through "
            "internal emails, signed approvals, and financial flow diagrams.\n\n"
            "The picture that emerges is enormous: a long-running crime network involving "
            "multiple senior executives. Ordinary employees' pensions, bonuses, and project "
            "budgets have all been quietly drained over years.\n\n"
            "Emma faces a brutal choice:\n\n"
            "  → Release everything to the media immediately: the criminals fall, but the\n"
            "    company likely collapses overnight. The first people to suffer would be\n"
            "    thousands of innocent staff.\n\n"
            "  → Do nothing: the 'last chance' mentioned in the anonymous call is gone.\n"
            "    The real masterminds continue unchallenged.\n\n"
            "Emma chooses a third path — slower, lonelier, and without recognition."
        ),
        choices=[("Send evidence anonymously to regulators — then disappear", "ENDING_3")],
        clue={
            "id": "C11",
            "name": "Archive Documents",
            "description": "Extensive proof of a multi-executive financial crime network spanning years.",
            "importance": 8,
        },
        allow_rewind=False,
    )

    # --- Endings ---
    graph["ENDING_1"] = StoryNode(
        "ENDING_1",
        "⚖  Ending 1 — Justice",
        (
            "Emma assembles a complete case file and delivers it simultaneously to the "
            "police and three major media outlets.\n\n"
            "The response is immediate and overwhelming. Public outrage explodes across "
            "every platform. Adrian is arrested within 48 hours. Senior executives are "
            "forced to appear before regulators. The conglomerate's market value collapses.\n\n"
            "The price is enormous — legal chaos, reputational ruin, financial damage to "
            "thousands of shareholders. But the facts are finally, irrevocably public.\n\n"
            "The main culprit falls in full view of the world.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  JUSTICE — The truth came out in the most dramatic way possible.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        is_ending=True,
        ending_type="Justice",
    )

    graph["ENDING_2A"] = StoryNode(
        "ENDING_2A",
        "🔇  Ending 2A — Silence",
        (
            "Emma publishes an article speculating about a professional hitman. "
            "With no better leads and no hard evidence, the police temporarily file "
            "the case as 'suspected external homicide'.\n\n"
            "The real internal culprit remains entirely untouched. The financial crimes "
            "continue. Emma worked hard — but she was chasing the wrong story all along.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  SILENCE — The truth is buried under a carefully constructed false narrative.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        is_ending=True,
        ending_type="Silence",
    )

    graph["ENDING_2B"] = StoryNode(
        "ENDING_2B",
        "🔇  Ending 2B — Silence",
        (
            "Emma publishes a report detailing the 'inconsistencies' she found: missing "
            "footage, wiped tapes, and a guard whose account doesn't quite add up. "
            "Some officers read it and raise an eyebrow. But without hard evidence, "
            "nothing happens.\n\n"
            "Emma has seen through part of the lie. Yet she lacks the tools to break it open.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  SILENCE — Clear-eyed helplessness: she saw the lie but could not prove it.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        is_ending=True,
        ending_type="Silence",
    )

    graph["ENDING_3"] = StoryNode(
        "ENDING_3",
        "👻  Ending 3 — Vanishing Truth",
        (
            "Emma carefully packages only the core evidence that can directly pin down "
            "the key decision-makers: critical email chains, signed authorisations, and "
            "money-flow diagrams. She sends it anonymously to financial regulators and "
            "an internal anti-corruption unit within the police.\n\n"
            "She deliberately holds back the most explosive data — the full scale of the "
            "undisclosed losses — to prevent an immediate market panic that would "
            "destroy innocent livelihoods.\n\n"
            "Then Emma wipes every trace of her involvement, leaves the city, and "
            "refuses every interview and call.\n\n"
            "Months later, the case is officially reopened. Regulators announce a new "
            "investigation. The media receive 'official' leaks and the truth surfaces "
            "piece by piece. No one knows it all started with a single anonymous package "
            "from an investigative journalist who chose to vanish from her own story.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "  VANISHING TRUTH — Justice unfolds slowly, and Emma disappears.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        is_ending=True,
        ending_type="Vanishing",
    )

    return graph


# =============================================================================
# SECTION 3 — ALGORITHMS
# =============================================================================

def dfs_reachability(graph: Dict[str, StoryNode], start: str) -> Dict[str, bool]:
    """
    Depth-First Search starting from 'start'.
    I use this to verify that every scene in the graph is actually reachable —
    useful for testing that no branch is accidentally disconnected.
    Iterative version (explicit stack) to avoid Python's recursion limit.
    Time complexity: O(V + E) where V = scenes, E = choices between them.
    """
    visited: Dict[str, bool] = {}
    stack: List[str] = [start]

    while stack:
        node_id = stack.pop()
        if node_id in visited:
            continue
        visited[node_id] = True

        if node_id in graph:
            for _, next_id in graph[node_id].choices:
                if next_id not in visited:
                    stack.append(next_id)

    return visited


def bfs_shortest_path(graph: Dict[str, StoryNode], start: str, target: str) -> List[str]:
    """
    Breadth-First Search — finds the fewest decisions needed to reach a target scene.
    BFS explores level by level, so the first time we reach the target node
    we're guaranteed it's the shortest path.
    Returns the path as a list of node ids, or [] if the target can't be reached.
    Time: O(V + E)
    """
    if start == target:
        return [start]

    queue: deque = deque([(start, [start])])
    visited: set = {start}

    while queue:
        node_id, path = queue.popleft()

        if node_id not in graph:
            continue

        for _, next_id in graph[node_id].choices:
            if next_id == target:
                return path + [next_id]
            if next_id not in visited:
                visited.add(next_id)
                queue.append((next_id, path + [next_id]))

    return []


def insertion_sort_clues(clues: List[Dict]) -> List[Dict]:
    """
    Sorts a list of clues by the step they were discovered (time_found).
    I implemented this manually rather than using Python's sorted() to
    demonstrate how insertion sort works.
    - Best case (already sorted): O(n)
    - Worst case (reverse order): O(n^2)
    - Stable: clues found at the same step keep their original order.
    """
    result: List[Dict] = list(clues)
    n = len(result)

    for i in range(1, n):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j]["time_found"] > key["time_found"]:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key

    return result


def topological_sort(dependencies: Dict[str, List[str]]) -> List[str]:
    """
    Kahn's algorithm — produces a valid order for discovering clues.
    An edge A → B in the dependency graph means clue A must be found before B.
    The algorithm works by repeatedly removing nodes with no remaining prerequisites,
    which ensures we always process clues in a valid order.
    If a cycle exists (which shouldn't happen in a proper story graph),
    the result will be shorter than the full node list — we return [] in that case.
    Time: O(V + E)
    """
    all_nodes: set = set(dependencies.keys())
    for children in dependencies.values():
        all_nodes.update(children)

    in_degree: Dict[str, int] = {node: 0 for node in all_nodes}
    for node, children in dependencies.items():
        for child in children:
            in_degree[child] += 1

    queue: deque = deque(sorted(n for n in all_nodes if in_degree[n] == 0))
    result: List[str] = []

    while queue:
        node = queue.popleft()
        result.append(node)
        for child in sorted(dependencies.get(node, [])):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(result) != len(all_nodes):
        print("topological_sort: cycle detected, returning empty list")
        return []

    return result


def get_clue_dependencies() -> Dict[str, List[str]]:
    """Returns the DAG of clue discovery dependencies (mirrors the story branches)."""
    return {
        "C0":  ["C6", "C1"],
        "C1":  ["C2", "C4"],
        "C2":  ["C3"],
        "C4":  ["C5"],
        "C6":  ["C7", "C10"],
        "C7":  ["C8"],
        "C8":  ["C9"],
        "C10": ["C11"],
        "C3":  [],
        "C5":  [],
        "C9":  [],
        "C11": [],
    }


# =============================================================================
# SECTION 4 — GAME ENGINE
# =============================================================================

class GameEngine:
    """
    Core game engine — holds all game state and exposes actions to the UI.
    The UI layer calls methods here and renders the returned data.
    No UI code lives in this class.
    """

    def __init__(self) -> None:
        self.story_graph = build_story_graph()
        self.current_node_id = "S1"
        self.rewind_stack = Stack()
        self.clue_heap = ClueHeap()
        self.discovered_clues: List[Dict] = []
        self.step_counter = 0
        self._collect_clue("S1")

    def get_current_node(self) -> StoryNode:
        return self.story_graph[self.current_node_id]

    def get_path_history(self) -> List[str]:
        return self.rewind_stack.to_list()

    def make_choice(self, choice_index: int) -> bool:
        """
        Advance to the next scene based on the player's choice.
        The current node is pushed onto the rewind stack before moving,
        so the player can undo the action later.
        """
        node = self.get_current_node()
        if choice_index < 0 or choice_index >= len(node.choices):
            return False

        self.rewind_stack.push(self.current_node_id)
        _, next_id = node.choices[choice_index]
        self.current_node_id = next_id
        self.step_counter += 1
        self._collect_clue(next_id)

        print(f"Moved to {next_id!r} (step {self.step_counter})")
        return True

    def can_rewind(self) -> bool:
        """Check whether rewinding is allowed from the current scene."""
        if self.rewind_stack.is_empty():
            return False
        current_node = self.get_current_node()
        if current_node.is_ending:
            return False
        if not current_node.allow_rewind:
            return False
        return True

    def rewind(self) -> bool:
        """Go back to the previous scene, if allowed."""
        if not self.can_rewind():
            print("Cannot rewind from this scene")
            return False

        prev_id = self.rewind_stack.pop()
        if prev_id is None:
            return False
        self.current_node_id = prev_id
        print(f"Rewound to {prev_id!r}")
        return True

    def restart(self) -> None:
        """Reset everything back to the start."""
        self.current_node_id = "S1"
        self.rewind_stack = Stack()
        self.clue_heap = ClueHeap()
        self.discovered_clues = []
        self.step_counter = 0
        self._collect_clue("S1")
        print("Game restarted")

    def _collect_clue(self, node_id: str) -> None:
        """Add the clue from a scene to our heap and list (no duplicates)."""
        node = self.story_graph.get(node_id)
        if node and node.clue:
            clue = node.clue
            existing_ids = {c["id"] for c in self.discovered_clues}
            if clue["id"] not in existing_ids:
                self.clue_heap.add_clue(
                    clue["id"],
                    clue["name"],
                    clue["description"],
                    clue["importance"],
                    self.step_counter,
                )
                self.discovered_clues.append({**clue, "time_found": self.step_counter})

    def get_prioritised_clues(self) -> List[Dict]:
        return self.clue_heap.get_sorted_clues()

    def get_timeline_clues(self) -> List[Dict]:
        return insertion_sort_clues(self.discovered_clues)

    def run_dfs_analysis(self) -> Dict:
        visited = dfs_reachability(self.story_graph, "S1")
        all_endings = ["ENDING_1", "ENDING_2A", "ENDING_2B", "ENDING_3"]
        reachable_endings = [e for e in all_endings if visited.get(e, False)]
        dead_scenes = [nid for nid in self.story_graph if not visited.get(nid, False)]
        print(f"DFS: visited {len(visited)} nodes, {len(reachable_endings)} endings reachable")
        return {
            "total_visited": len(visited),
            "reachable_endings": reachable_endings,
            "dead_scenes": dead_scenes,
        }

    def run_bfs_analysis(self) -> Dict:
        endings = {
            "Justice (Ending 1)": "ENDING_1",
            "Silence A (Ending 2A)": "ENDING_2A",
            "Silence B (Ending 2B)": "ENDING_2B",
            "Vanishing Truth (Ending 3)": "ENDING_3",
        }
        results = {}
        for label, eid in endings.items():
            path = bfs_shortest_path(self.story_graph, "S1", eid)
            steps = len(path) - 1 if path else -1
            results[label] = {
                "steps": steps,
                "path": " → ".join(path) if path else "Unreachable",
            }
            print(f"BFS to {eid}: {steps} steps")
        return results

    def run_topo_analysis(self) -> List[str]:
        deps = get_clue_dependencies()
        result = topological_sort(deps)
        print(f"Topo sort result: {result}")
        return result


# =============================================================================
# SECTION 5 — GRAPHICAL USER INTERFACE
# =============================================================================

BG_DARK   = "#0d1117"
BG_PANEL  = "#161b22"
BG_INPUT  = "#1c2128"
FG_MAIN   = "#e6edf3"
FG_DIM    = "#8b949e"
ACCENT    = "#e6a817"
ACCENT2   = "#58a6ff"
SUCCESS   = "#3fb950"
DANGER    = "#f85149"
WARNING   = "#d29922"
BORDER    = "#30363d"

FONT_TITLE  = ("Georgia", 18, "bold")
FONT_SCENE  = ("Georgia", 13, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_CHOICE = ("Helvetica", 11, "bold")
FONT_SMALL  = ("Helvetica", 9)
FONT_MONO   = ("Courier", 10)


def create_dark_gradient_bg(width: int, height: int) -> ImageTk.PhotoImage:
    """Creates a dark gradient background image for the start screen."""
    img = Image.new('RGB', (width, height), color=BG_DARK)
    draw = ImageDraw.Draw(img, 'RGBA')

    for y in range(height):
        r = int(25 + (13 - 25) * (y / height))
        g = int(27 + (17 - 27) * (y / height))
        b = int(23 + (23 - 23) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # subtle scanline effect
    for y in range(0, height, 40):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, 8))

    return ImageTk.PhotoImage(img)


class StartWindow:
    """Title/start screen — shows game info and lets the player begin."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Whispers at Victor's Manor — Start")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1000x750")
        self.root.minsize(1000, 750)
        self.root.resizable(True, True)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 500
        y = (self.root.winfo_screenheight() // 2) - 375
        self.root.geometry(f"1000x750+{x}+{y}")

        self.game_started = False
        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        main_frame.pack(fill="both", expand=True)

        self.bg_image = create_dark_gradient_bg(1000, 750)
        bg_label = tk.Label(main_frame, image=self.bg_image, bg=BG_DARK)
        bg_label.image = self.bg_image
        bg_label.place(x=0, y=0, width=1000, height=750)
        bg_label.lower()

        content = tk.Frame(main_frame, bg=BG_DARK)
        content.place(relx=0.5, rely=0.5, anchor="center", width=800, height=650)

        title_frame = tk.Frame(content, bg=BG_DARK)
        title_frame.pack(pady=(60, 20))

        tk.Label(
            title_frame, text="WHISPERS",
            font=("Georgia", 56, "bold"), bg=BG_DARK, fg=ACCENT,
        ).pack()

        tk.Label(
            title_frame, text="at Victor's Manor",
            font=("Georgia", 44, "bold"), bg=BG_DARK, fg=ACCENT2,
        ).pack()

        tk.Label(
            title_frame, text="━" * 40,
            font=("Georgia", 10), bg=BG_DARK, fg=BORDER,
        ).pack(pady=8)

        desc_frame = tk.Frame(content, bg=BG_DARK)
        desc_frame.pack(pady=(0, 30))

        desc_text = (
            "A narrative mystery where your choices shape the outcome.\n\n"
            "Investigate a death, uncover conspiracies, and decide\n"
            "what truth is worth exposing.\n\n"
            "Navigate between four different endings:\n"
            "⚖  Justice  •  🔇  Silence  •  👻  Vanishing Truth"
        )

        tk.Label(
            desc_frame, text=desc_text,
            font=("Helvetica", 12), bg=BG_DARK, fg=FG_MAIN,
            justify="center", wraplength=700,
        ).pack()

        mode_frame = tk.LabelFrame(
            content, text="Game Mode",
            bg=BG_PANEL, fg=ACCENT, font=("Georgia", 10, "bold"),
            padx=16, pady=12,
        )
        mode_frame.pack(pady=20, fill="x")

        self.difficulty = tk.StringVar(value="normal")

        for mode, label, desc in [
            ("normal",  "Standard",    "Original difficulty with all puzzles"),
            ("explore", "Exploration", "Fewer time constraints, focus on story"),
        ]:
            f = tk.Frame(mode_frame, bg=BG_PANEL)
            f.pack(anchor="w", pady=6)
            tk.Radiobutton(
                f, text=f"{label}: {desc}",
                variable=self.difficulty, value=mode,
                bg=BG_PANEL, fg=FG_MAIN, selectcolor=BG_INPUT,
                activebackground=BG_PANEL, activeforeground=ACCENT,
                font=("Helvetica", 11),
            ).pack(side="left")

        button_frame = tk.Frame(content, bg=BG_DARK)
        button_frame.pack(pady=(30, 0))

        start_btn = tk.Button(
            button_frame,
            text="  ▶  BEGIN INVESTIGATION  ▶  ",
            font=("Georgia", 15, "bold"),
            bg=ACCENT2, fg=BG_DARK,
            activebackground=ACCENT, activeforeground=BG_DARK,
            relief="flat", cursor="hand2",
            padx=28, pady=14,
            command=self._start_game,
        )
        start_btn.pack()

        start_btn.bind("<Enter>", lambda e: start_btn.configure(bg=ACCENT, relief="raised"))
        start_btn.bind("<Leave>", lambda e: start_btn.configure(bg=ACCENT2, relief="flat"))

        footer = tk.Frame(content, bg=BG_DARK)
        footer.pack(expand=True, side="bottom", pady=20)

        tk.Label(
            footer, text="FP016 • Computer Science • Summative Assessment 2",
            font=("Helvetica", 8), bg=BG_DARK, fg=FG_DIM,
        ).pack()

        tk.Label(
            footer, text="© 2026 Zhengjiang — Game Engine Developer",
            font=("Helvetica", 8), bg=BG_DARK, fg=FG_DIM,
        ).pack()

    def _start_game(self) -> None:
        self.game_started = True
        self.root.destroy()


class StartScreen:
    """Manages the start screen lifecycle."""

    @staticmethod
    def show(root: tk.Tk) -> bool:
        """Show the start window; returns True if the player clicked Start."""
        start_win = StartWindow(root)
        root.wait_window(start_win.root)
        return start_win.game_started


class AnalysisWindow:
    """
    Separate window showing the algorithm analysis results.
    Four tabs: DFS reachability, BFS shortest paths,
    insertion sort timeline, and topological clue order.
    """

    def __init__(self, parent: tk.Widget, engine: GameEngine) -> None:
        self.win = tk.Toplevel(parent)
        self.win.title("Algorithm Analysis — Whispers at Victor's Manor")
        self.win.configure(bg=BG_DARK)
        self.win.geometry("720x580")
        self.win.resizable(True, True)
        self._build(engine)

    def _build(self, engine: GameEngine) -> None:
        tk.Label(
            self.win, text="🔬  Algorithm Analysis Dashboard",
            font=("Georgia", 15, "bold"), bg=BG_DARK, fg=ACCENT,
        ).pack(pady=(16, 4))

        nb = ttk.Notebook(self.win)
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=BG_PANEL, foreground=FG_DIM,
                        padding=[12, 6], font=FONT_SMALL)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_INPUT)],
                  foreground=[("selected", ACCENT)])

        # Tab 1 — DFS
        f1 = self._make_frame(nb)
        nb.add(f1, text="  DFS Reachability  ")
        dfs_data = engine.run_dfs_analysis()
        lines = [
            f"Depth-First Search from S1\n{'─'*50}",
            f"Total nodes visited:  {dfs_data['total_visited']}",
            f"Reachable endings:    {len(dfs_data['reachable_endings'])} / 4",
            "",
        ]
        for e in dfs_data["reachable_endings"]:
            lines.append(f"  ✔  {e}")
        if dfs_data["dead_scenes"]:
            lines += ["", "Dead scenes (unreachable):"]
            for d in dfs_data["dead_scenes"]:
                lines.append(f"  ✘  {d}")
        else:
            lines += ["", "No dead scenes — all nodes are reachable."]
        self._add_text(f1, "\n".join(lines))

        # Tab 2 — BFS
        f2 = self._make_frame(nb)
        nb.add(f2, text="  BFS Shortest Paths  ")
        bfs_data = engine.run_bfs_analysis()
        lines2 = [f"Breadth-First Search from S1\n{'─'*50}", ""]
        for label, info in bfs_data.items():
            lines2.append(f"▸ {label}")
            lines2.append(f"  Decisions required: {info['steps']}")
            parts = info["path"].split(" → ")
            wrapped = "\n    ".join(" → ".join(parts[i:i+3]) for i in range(0, len(parts), 3))
            lines2.append(f"  Path: {wrapped}")
            lines2.append("")
        self._add_text(f2, "\n".join(lines2))

        # Tab 3 — Insertion Sort (Timeline)
        f3 = self._make_frame(nb)
        nb.add(f3, text="  Evidence Timeline  ")
        sorted_clues = engine.get_timeline_clues()
        lines3 = [
            f"Insertion Sort — Clues in Discovery Order\n{'─'*50}",
            f"Total clues found so far: {len(sorted_clues)}",
            "",
        ]
        if not sorted_clues:
            lines3.append("(No clues discovered yet — play the game to collect evidence.)")
        else:
            for c in sorted_clues:
                lines3.append(f"  Step {c['time_found']:>2} │ [{c['id']}] {c['name']}")
                lines3.append(f"         Importance: {c['importance']}/10")
                lines3.append(f"         {c['description']}")
                lines3.append("")
        self._add_text(f3, "\n".join(lines3))

        # Tab 4 — Topological Sort
        f4 = self._make_frame(nb)
        nb.add(f4, text="  Clue Dependency Order  ")
        topo = engine.run_topo_analysis()
        clue_names = {
            "C0": "Victor's Body",          "C1": "Guard's Testimony",
            "C2": "Garden Footprints",      "C3": "Empty Basement",
            "C4": "Deleted CCTV Footage",   "C5": "Wiped Backup Tapes",
            "C6": "Sophia's Testimony",     "C7": "Adrian's Car Log",
            "C8": "Chemical Purchase Log",  "C9": "USB Financial Files",
            "C10": "Finance Officer Warning", "C11": "Archive Documents",
        }
        lines4 = [
            f"Kahn's Topological Sort — Clue Dependency DAG\n{'─'*50}",
            "Valid logical discovery order (A → B means A must precede B):\n",
        ]
        if not topo:
            lines4.append("⚠  Cycle detected in dependency graph!")
        else:
            for i, cid in enumerate(topo, 1):
                name = clue_names.get(cid, cid)
                lines4.append(f"  {i:>2}. {cid:<5} — {name}")
        lines4 += [
            "",
            "Key dependency chains:",
            "  C0 → C6 → C7 → C8 → C9  (Justice path)",
            "  C0 → C6 → C10 → C11     (Vanishing path)",
            "  C0 → C1 → C4 → C5       (Silence B path)",
            "  C0 → C1 → C2 → C3       (Silence A path)",
        ]
        self._add_text(f4, "\n".join(lines4))

    @staticmethod
    def _make_frame(parent: ttk.Notebook) -> tk.Frame:
        f = tk.Frame(parent, bg=BG_INPUT)
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)
        return f

    @staticmethod
    def _add_text(frame: tk.Frame, content: str) -> None:
        txt = scrolledtext.ScrolledText(
            frame, bg=BG_INPUT, fg=FG_MAIN,
            font=FONT_MONO, wrap=tk.WORD,
            relief="flat", borderwidth=0,
            padx=12, pady=12,
        )
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)


class EvidencePanel(tk.Toplevel):
    """
    Secondary window showing discovered clues.
    Can be sorted by priority (heap) or by discovery time (insertion sort).
    """

    def __init__(self, parent: tk.Widget, engine: GameEngine) -> None:
        super().__init__(parent)
        self.engine = engine
        self.title("Evidence Panel")
        self.configure(bg=BG_DARK)
        self.geometry("480x520")
        self.resizable(True, True)
        self._sort_mode = tk.StringVar(value="priority")
        self._build()
        self.refresh()

    def _build(self) -> None:
        tk.Label(
            self, text="🗂  Emma's Evidence Panel",
            font=("Georgia", 14, "bold"), bg=BG_DARK, fg=ACCENT,
        ).pack(pady=(14, 4))

        ctrl = tk.Frame(self, bg=BG_DARK)
        ctrl.pack()

        for text, val in [("Priority order", "priority"), ("Timeline order", "timeline")]:
            tk.Radiobutton(
                ctrl, text=text, variable=self._sort_mode, value=val,
                command=self.refresh,
                bg=BG_DARK, fg=FG_DIM, selectcolor=BG_PANEL,
                activebackground=BG_DARK, activeforeground=FG_MAIN,
                font=FONT_SMALL,
            ).pack(side="left", padx=8)

        self._text = scrolledtext.ScrolledText(
            self, bg=BG_INPUT, fg=FG_MAIN,
            font=FONT_BODY, wrap=tk.WORD,
            relief="flat", borderwidth=0,
            padx=14, pady=10,
        )
        self._text.pack(fill="both", expand=True, padx=14, pady=(6, 14))

    def refresh(self) -> None:
        if self._sort_mode.get() == "priority":
            clues = self.engine.get_prioritised_clues()
            header = "Ordered by importance (most critical first):\n\n"
        else:
            clues = self.engine.get_timeline_clues()
            header = "Ordered by discovery time (insertion sort):\n\n"

        self._text.configure(state="normal")
        self._text.delete("1.0", tk.END)

        if not clues:
            self._text.insert(tk.END, "No clues discovered yet.")
        else:
            self._text.insert(tk.END, header)
            for c in clues:
                self._text.insert(
                    tk.END,
                    f"[{c['id']}]  {c['name']}  (importance: {c['importance']}/10)\n",
                )
                self._text.insert(tk.END, f"     {c['description']}\n\n")

        self._text.configure(state="disabled")


class GameApp:
    """
    Main application window — renders the current scene, handles UI events.

    Layout:
    - Top bar:    title + step counter + toolbar buttons
    - Scene card: scene title + narrative text (scrollable)
    - Choices:    dynamically generated buttons
    - Status bar: path breadcrumb + clue count
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.engine = GameEngine()
        self._evidence_window: Optional[EvidencePanel] = None
        self._analysis_window: Optional[AnalysisWindow] = None
        self._setup_window()
        self._build_ui()
        self._render_scene()

    def _setup_window(self) -> None:
        self.root.title("Whispers at Victor's Manor")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("880x680")
        self.root.minsize(700, 520)
        self.root.resizable(True, True)

    def _build_ui(self) -> None:
        # Top bar
        top = tk.Frame(self.root, bg=BG_PANEL, pady=0)
        top.pack(fill="x")

        tk.Label(
            top, text="WHISPERS AT VICTOR'S MANOR",
            font=("Georgia", 11, "bold"), bg=BG_PANEL, fg=ACCENT,
        ).pack(side="left", padx=16, pady=10)

        self._step_label = tk.Label(top, text="", font=FONT_SMALL, bg=BG_PANEL, fg=FG_DIM)
        self._step_label.pack(side="left", padx=4)

        btn_cfg = {"relief": "flat", "cursor": "hand2", "padx": 10, "pady": 5, "font": FONT_SMALL}

        tk.Button(
            top, text="⟲  Restart", bg=BG_INPUT, fg=FG_DIM,
            activebackground=BORDER, command=self._on_restart, **btn_cfg
        ).pack(side="right", padx=6, pady=6)

        tk.Button(
            top, text="📊  Analysis", bg=BG_INPUT, fg=ACCENT2,
            activebackground=BORDER, command=self._open_analysis, **btn_cfg
        ).pack(side="right", padx=2, pady=6)

        tk.Button(
            top, text="🗂  Evidence", bg=BG_INPUT, fg=ACCENT,
            activebackground=BORDER, command=self._open_evidence, **btn_cfg
        ).pack(side="right", padx=2, pady=6)

        self._rewind_btn = tk.Button(
            top, text="↩  Rewind", bg=BG_INPUT, fg=FG_DIM,
            activebackground=BORDER, command=self._on_rewind, **btn_cfg
        )
        self._rewind_btn.pack(side="right", padx=2, pady=6)

        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

        # Main content
        content = tk.Frame(self.root, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=24, pady=16)

        self._scene_title = tk.Label(
            content, text="", font=FONT_SCENE,
            bg=BG_DARK, fg=ACCENT, anchor="w",
        )
        self._scene_title.pack(fill="x", pady=(0, 8))

        self._text_area = scrolledtext.ScrolledText(
            content, bg=BG_PANEL, fg=FG_MAIN,
            font=FONT_BODY, wrap=tk.WORD,
            relief="flat", borderwidth=0,
            padx=18, pady=14, height=14,
        )
        self._text_area.pack(fill="both", expand=True)
        self._text_area.configure(state="disabled")

        self._clue_banner = tk.Label(
            content, text="", font=FONT_SMALL,
            bg="#1f2d1f", fg=SUCCESS, anchor="w", padx=12, pady=4,
        )

        self._choice_frame = tk.Frame(content, bg=BG_DARK)
        self._choice_frame.pack(fill="x", pady=(12, 0))

        # Status bar
        status = tk.Frame(self.root, bg=BG_PANEL, pady=0)
        status.pack(fill="x", side="bottom")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", side="bottom")

        self._path_label = tk.Label(
            status, text="Path: —", font=FONT_SMALL,
            bg=BG_PANEL, fg=FG_DIM, anchor="w",
        )
        self._path_label.pack(side="left", padx=16, pady=6)

        self._clue_count_label = tk.Label(
            status, text="Clues: 0", font=FONT_SMALL, bg=BG_PANEL, fg=FG_DIM,
        )
        self._clue_count_label.pack(side="right", padx=16, pady=6)

    def _render_scene(self, prev_clue_count: int = 0) -> None:
        """Refresh all UI elements to match the current engine state."""
        node = self.engine.get_current_node()

        self._step_label.configure(text=f"— Step {self.engine.step_counter}")

        title_colour = {
            "Justice":   SUCCESS,
            "Silence":   DANGER,
            "Vanishing": WARNING,
        }.get(node.ending_type, ACCENT)
        self._scene_title.configure(text=node.title, fg=title_colour)

        self._text_area.configure(state="normal")
        self._text_area.delete("1.0", tk.END)
        self._text_area.insert(tk.END, node.text)
        self._text_area.configure(state="disabled")
        self._text_area.see("1.0")

        # Show a clue banner briefly if a new clue was just found
        current_count = self.engine.clue_heap.size()
        if current_count > prev_clue_count and node.clue:
            self._clue_banner.configure(
                text=f"  🔍 New clue: {node.clue['name']}  (importance {node.clue['importance']}/10)"
            )
            self._clue_banner.pack(fill="x", pady=(4, 0))
            self.root.after(3500, self._clue_banner.pack_forget)
        else:
            self._clue_banner.pack_forget()

        for w in self._choice_frame.winfo_children():
            w.destroy()

        if node.is_ending:
            self._render_ending(node)
        else:
            for i, (label, _) in enumerate(node.choices):
                self._make_choice_button(label, i)

        path = self.engine.get_path_history()
        if path:
            display = " → ".join(path[-4:])
            if len(path) > 4:
                display = "... → " + display
        else:
            display = "—"
        self._path_label.configure(text=f"Path: {display}")
        self._clue_count_label.configure(text=f"Clues: {self.engine.clue_heap.size()}")

        # Enable/disable the rewind button depending on current scene
        if self.engine.can_rewind():
            self._rewind_btn.configure(state="normal", fg=ACCENT)
        else:
            self._rewind_btn.configure(state="disabled", fg=FG_DIM)

        if self._evidence_window and self._evidence_window.winfo_exists():
            self._evidence_window.refresh()

    def _make_choice_button(self, label: str, index: int) -> None:
        btn = tk.Button(
            self._choice_frame,
            text=f"  {index + 1}.  {label}  ",
            font=FONT_CHOICE,
            bg=BG_PANEL, fg=FG_MAIN,
            activebackground=ACCENT2, activeforeground=BG_DARK,
            relief="flat", cursor="hand2",
            anchor="w", padx=12, pady=8,
            command=lambda i=index: self._on_choice(i),
        )
        btn.pack(fill="x", pady=3)
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BORDER))
        btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BG_PANEL))

    def _render_ending(self, node: StoryNode) -> None:
        colour = {
            "Justice":   SUCCESS,
            "Silence":   DANGER,
            "Vanishing": WARNING,
        }.get(node.ending_type, FG_DIM)

        tk.Label(
            self._choice_frame,
            text=f"— {node.ending_type} Ending —",
            font=("Georgia", 13, "bold"),
            bg=BG_DARK, fg=colour,
        ).pack(pady=(8, 4))

        tk.Button(
            self._choice_frame,
            text="  🔄  Play Again — Return to the Beginning  ",
            font=FONT_CHOICE,
            bg=BG_PANEL, fg=FG_MAIN,
            activebackground=ACCENT2, activeforeground=BG_DARK,
            relief="flat", cursor="hand2",
            padx=12, pady=8,
            command=self._on_restart,
        ).pack(fill="x", pady=6)

    def _on_choice(self, index: int) -> None:
        prev_count = self.engine.clue_heap.size()
        if self.engine.make_choice(index):
            self._render_scene(prev_count)

    def _on_rewind(self) -> None:
        if self.engine.rewind():
            self._render_scene()
        else:
            messagebox.showinfo(
                "Rewind",
                "You are already at the beginning of the story.",
                parent=self.root,
            )

    def _on_restart(self) -> None:
        if messagebox.askyesno(
            "Restart",
            "Start the investigation from the beginning?\nAll progress will be lost.",
            parent=self.root,
        ):
            self.engine.restart()
            self._render_scene()

    def _open_evidence(self) -> None:
        if self._evidence_window and self._evidence_window.winfo_exists():
            self._evidence_window.lift()
            self._evidence_window.refresh()
        else:
            self._evidence_window = EvidencePanel(self.root, self.engine)

    def _open_analysis(self) -> None:
        if self._analysis_window and self._analysis_window.winfo_exists():
            self._analysis_window.win.lift()
        else:
            self._analysis_window = AnalysisWindow(self.root, self.engine)


# =============================================================================
# SECTION 6 — ENTRY POINT
# =============================================================================

def main() -> None:
    start_root = tk.Tk()
    style = ttk.Style(start_root)
    style.theme_use("default")

    if StartScreen.show(start_root):
        main_root = tk.Tk()
        style = ttk.Style(main_root)
        style.theme_use("default")
        app = GameApp(main_root)
        main_root.mainloop()
    else:
        print("Player closed the start screen.")


if __name__ == "__main__":
    main()
