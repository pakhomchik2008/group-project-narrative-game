"""
Whispers at Victor's Manor
FP016 Computer Science — Summative Assessment 2

A branching narrative mystery game built in Python.
The player investigates a suspicious death at Victor's Manor
and must uncover the truth through a series of choices.

My role: Game Engine Developer (Algorithms & Logic)
"""

# ── Standard / third-party imports ─────────────────────────────────────────
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import heapq
from collections import deque
from typing import List, Dict, Optional, Tuple
import os

# Folder that holds all background images (sits next to this script)
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cs photos")


# =============================================================================
# SECTION 1 — DATA STRUCTURES(GLEB PART)
# =============================================================================

class StoryNode:

    def __init__(
        self,
        node_id: str,
        title: str,
        text: str,
        choices: Optional[List[Tuple[str, str]]] = None,
        clue: Optional[Dict] = None,
        is_ending: bool = False,
        ending_type: str = "",
        allow_rewind: bool = True,
        bg_image: str = "",
    ) -> None:
        self.node_id    = node_id
        self.title      = title
        self.text       = text
        self.choices    = choices if choices else []
        self.clue       = clue
        self.is_ending  = is_ending
        self.ending_type = ending_type
        self.allow_rewind = allow_rewind
        self.bg_image   = bg_image          # filename inside IMAGE_DIR

    def __repr__(self) -> str:
        return f"StoryNode(id={self.node_id!r}, title={self.title!r})"


class Stack:
    def __init__(self) -> None:
        self._data: List[str] = []

    def push(self, item: str) -> None:
        self._data.append(item)

    def pop(self) -> Optional[str]:
        if self.is_empty():
            return None
        return self._data.pop()

    def peek(self) -> Optional[str]:
        if self.is_empty():
            return None
        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def size(self) -> int:
        return len(self._data)

    def copy_list(self) -> List[str]:
        return list(self._data)

    # alias kept for compatibility
    def to_list(self) -> List[str]:
        return self.copy_list()


class ClueHeap:
    def __init__(self) -> None:
        self.heap: List[Tuple] = []
        self.counter: int = 0

    def add_clue(self, clue_id: str, name: str, description: str,
                 importance: int, time_found: int) -> None:
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
                "id": cid, "name": name, "description": desc,
                "importance": -neg_imp, "time_found": time_f,
            })
        return result

    def size(self) -> int:
        return len(self.heap)

#=====================GLEB PART END==============================


# =============================================================================
# SECTION 2 — STORY GRAPH(MEHLI PART)
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
        bg_image="Mansion.png",
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
        bg_image="Library.png",
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
        bg_image="Security guard.png",
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
        bg_image="Garden trail.png",
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
        bg_image="Basement.png",
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
        bg_image="CCTV.png",
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
        bg_image="CCTV room.png",
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
            "go down together.'\n\n"
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
        bg_image="Sophia.png",
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
        bg_image="Parking lot.png",
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
        bg_image="Kitchen.png",
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
        bg_image="Victor's private office.png",
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
        bg_image="Finance office.png",
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
        bg_image="Archive room.png",
    )

    # --- Endings ---
    graph["ENDING_1"] = StoryNode(
        "ENDING_1",
        "Ending 1 — Justice",
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
        "Ending 2A — Silence",
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
        "Ending 2B — Silence",
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
        "Ending 3 — Vanishing Truth",
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
# SECTION 3 — ALGORITHMS(ZHINI PART)
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
# SECTION 4 — GAME ENGINE(ZHINI PART)
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
            "Justice (Ending 1)":      "ENDING_1",
            "Silence A (Ending 2A)":   "ENDING_2A",
            "Silence B (Ending 2B)":   "ENDING_2B",
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
# SECTION 5 — POPUP WINDOWS  (Evidence Panel + Algorithm Analysis) (GLEB PART)
# =============================================================================

# Shared colour / font constants for popup windows
_BG_DARK  = "#111111"
_BG_PANEL = "#1a1a1a"
_FG_MAIN  = "#ffffff"
_FG_DIM   = "#aaaaaa"
_ACCENT   = "#e6a817"
_ACCENT2  = "#58a6ff"
_SUCCESS  = "#3fb950"
_BORDER   = "#333333"
_FONT_MONO  = ("Courier", 10)
_FONT_SMALL = ("Arial", 9)
_FONT_BODY  = ("Arial", 11)


class AnalysisWindow:
    """
    Separate window showing the algorithm analysis results.
    Four tabs: DFS reachability, BFS shortest paths,
    insertion sort timeline, and topological clue order.
    """

    def __init__(self, parent: Widget, engine: GameEngine) -> None:
        self.win = Toplevel(parent)
        self.win.title("Algorithm Analysis — Whispers at Victor's Manor")
        self.win.configure(bg=_BG_DARK)
        self.win.geometry("720x580")
        self.win.resizable(True, True)
        self._build(engine)

    def _build(self, engine: GameEngine) -> None:
        Label(
            self.win, text="Algorithm Analysis Dashboard",
            font=("Arial", 15, "bold"), bg=_BG_DARK, fg=_ACCENT,
        ).pack(pady=(16, 4))

        nb = ttk.Notebook(self.win)
        nb.pack(fill="both", expand=True, padx=16, pady=8)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",     background=_BG_DARK,  borderwidth=0)
        style.configure("TNotebook.Tab", background=_BG_PANEL, foreground=_FG_DIM,
                        padding=[12, 6], font=_FONT_SMALL)
        style.map("TNotebook.Tab",
                  background=[("selected", "#2a2a2a")],
                  foreground=[("selected", _ACCENT)])

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
            lines.append(f"  v  {e}")
        if dfs_data["dead_scenes"]:
            lines += ["", "Dead scenes (unreachable):"]
            for d in dfs_data["dead_scenes"]:
                lines.append(f"  x  {d}")
        else:
            lines += ["", "No dead scenes — all nodes are reachable."]
        self._add_text(f1, "\n".join(lines))

        # Tab 2 — BFS
        f2 = self._make_frame(nb)
        nb.add(f2, text="  BFS Shortest Paths  ")
        bfs_data = engine.run_bfs_analysis()
        lines2 = [f"Breadth-First Search from S1\n{'─'*50}", ""]
        for label, info in bfs_data.items():
            lines2.append(f"> {label}")
            lines2.append(f"  Decisions required: {info['steps']}")
            parts = info["path"].split(" -> ")
            wrapped = "\n    ".join(" -> ".join(parts[i:i+3]) for i in range(0, len(parts), 3))
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
                lines3.append(f"  Step {c['time_found']:>2} | [{c['id']}] {c['name']}")
                lines3.append(f"         Importance: {c['importance']}/10")
                lines3.append(f"         {c['description']}")
                lines3.append("")
        self._add_text(f3, "\n".join(lines3))

        # Tab 4 — Topological Sort
        f4 = self._make_frame(nb)
        nb.add(f4, text="  Clue Dependency Order  ")
        topo = engine.run_topo_analysis()
        clue_names = {
            "C0": "Victor's Body",            "C1": "Guard's Testimony",
            "C2": "Garden Footprints",        "C3": "Empty Basement",
            "C4": "Deleted CCTV Footage",     "C5": "Wiped Backup Tapes",
            "C6": "Sophia's Testimony",       "C7": "Adrian's Car Log",
            "C8": "Chemical Purchase Log",    "C9": "USB Financial Files",
            "C10": "Finance Officer Warning",  "C11": "Archive Documents",
        }
        lines4 = [
            f"Kahn's Topological Sort — Clue Dependency DAG\n{'─'*50}",
            "Valid logical discovery order (A -> B means A must precede B):\n",
        ]
        if not topo:
            lines4.append("Cycle detected in dependency graph!")
        else:
            for i, cid in enumerate(topo, 1):
                name = clue_names.get(cid, cid)
                lines4.append(f"  {i:>2}. {cid:<5} — {name}")
        lines4 += [
            "",
            "Key dependency chains:",
            "  C0 -> C6 -> C7 -> C8 -> C9  (Justice path)",
            "  C0 -> C6 -> C10 -> C11      (Vanishing path)",
            "  C0 -> C1 -> C4 -> C5        (Silence B path)",
            "  C0 -> C1 -> C2 -> C3        (Silence A path)",
        ]
        self._add_text(f4, "\n".join(lines4))

    @staticmethod
    def _make_frame(parent: ttk.Notebook) -> Frame:
        f = Frame(parent, bg="#222222")
        f.columnconfigure(0, weight=1)
        f.rowconfigure(0, weight=1)
        return f

    @staticmethod
    def _add_text(frame: Frame, content: str) -> None:
        txt = scrolledtext.ScrolledText(
            frame, bg="#222222", fg=_FG_MAIN,
            font=_FONT_MONO, wrap=WORD,
            relief="flat", borderwidth=0,
            padx=12, pady=12,
        )
        txt.insert("1.0", content)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True)


class EvidencePanel(Toplevel):
    """
    Secondary window showing discovered clues.
    Can be sorted by priority (heap) or by discovery time (insertion sort).
    """

    def __init__(self, parent: Widget, engine: GameEngine) -> None:
        super().__init__(parent)
        self.engine = engine
        self.title("Evidence Panel")
        self.configure(bg=_BG_DARK)
        self.geometry("480x520")
        self.resizable(True, True)
        self._sort_mode = StringVar(value="priority")
        self._build()
        self.refresh()

    def _build(self) -> None:
        Label(
            self, text="Emma's Evidence Panel",
            font=("Arial", 14, "bold"), bg=_BG_DARK, fg=_ACCENT,
        ).pack(pady=(14, 4))

        ctrl = Frame(self, bg=_BG_DARK)
        ctrl.pack()

        for text, val in [("Priority order", "priority"), ("Timeline order", "timeline")]:
            Radiobutton(
                ctrl, text=text, variable=self._sort_mode, value=val,
                command=self.refresh,
                bg=_BG_DARK, fg=_FG_DIM, selectcolor=_BG_PANEL,
                activebackground=_BG_DARK, activeforeground=_FG_MAIN,
                font=_FONT_SMALL,
            ).pack(side=LEFT, padx=8)

        self._text = scrolledtext.ScrolledText(
            self, bg="#222222", fg=_FG_MAIN,
            font=_FONT_BODY, wrap=WORD,
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
        self._text.delete("1.0", END)

        if not clues:
            self._text.insert(END, "No clues discovered yet.")
        else:
            self._text.insert(END, header)
            for c in clues:
                self._text.insert(
                    END,
                    f"[{c['id']}]  {c['name']}  (importance: {c['importance']}/10)\n",
                )
                self._text.insert(END, f"     {c['description']}\n\n")

        self._text.configure(state="disabled")


# =============================================================================
# SECTION 6 — MAIN GUI  (based on GUI.py — window, layout, widgets, functions) (SYLVIE PART)
# =============================================================================

# Instantiate the engine
engine = GameEngine()

# Popup window references (None when closed)
_evidence_window = None
_analysis_window = None

# ── Window ──────────────────────────────────────────────────────────────────
root = Tk()
root.title("Whispers at Victor's Manor")
root.geometry("1200x800")
root.configure(bg="#111111")

# ── Toolbar (top bar — added on top of GUI.py's base) ───────────────────────
toolbar = Frame(root, bg="#1a1a1a")
toolbar.pack(fill=X, side=TOP)

Label(
    toolbar,
    text="WHISPERS AT VICTOR'S MANOR",
    font=("Arial", 11, "bold"),
    bg="#1a1a1a", fg="#e6a817",
).pack(side=LEFT, padx=16, pady=8)

_step_label = Label(toolbar, text="", font=("Arial", 9), bg="#1a1a1a", fg="#888888")
_step_label.pack(side=LEFT, padx=4)

_tb_btn = {"relief": "solid", "cursor": "hand2", "padx": 10, "pady": 4,
           "font": ("Arial", 9, "bold"), "bg": "#c8a96e", "fg": "#1a1a2e",
           "activebackground": "#e8c98e", "activeforeground": "#1a1a2e", "bd": 1}

# Buttons are packed right-to-left
Button(toolbar, text="Restart",
       command=lambda: _on_restart(), **_tb_btn).pack(side=RIGHT, padx=6, pady=6)
Button(toolbar, text="Analysis",
       command=lambda: _open_analysis(), **_tb_btn).pack(side=RIGHT, padx=2, pady=6)
Button(toolbar, text="Evidence",
       command=lambda: _open_evidence(), **_tb_btn).pack(side=RIGHT, padx=2, pady=6)

_rewind_btn = Button(toolbar, text="Rewind",
                     command=lambda: _on_rewind(), **_tb_btn)
_rewind_btn.pack(side=RIGHT, padx=2, pady=6)

# Accent line below toolbar
Frame(root, bg="#e6a817", height=2).pack(fill=X)

# ── Status bar (bottom — added on top of GUI.py's base) ─────────────────────
Frame(root, bg="#333333", height=1).pack(fill=X, side=BOTTOM)
status_bar = Frame(root, bg="#1a1a1a")
status_bar.pack(fill=X, side=BOTTOM)

_path_label = Label(status_bar, text="Path: —", font=("Arial", 9),
                    bg="#1a1a1a", fg="#888888", anchor=W)
_path_label.pack(side=LEFT, padx=16, pady=5)

_clue_count_label = Label(status_bar, text="Clues: 0", font=("Arial", 9),
                          bg="#1a1a1a", fg="#888888")
_clue_count_label.pack(side=RIGHT, padx=16, pady=5)

# ── Background label (from GUI.py — covers the full root window) ─────────────
bg_photo = None
background_label = Label(root)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# ── Story widgets (from GUI.py — unchanged style) ────────────────────────────
title_label = Label(
    root,
    text="",
    font=("Arial", 28, "bold"),
    bg="#1a1a2e",
    fg="#f5deb3",
    padx=20,
    pady=8,
)

story_text = Text(
    root,
    width=90,
    height=9,
    font=("Arial", 14),
    wrap=WORD,
    bg="#1a1a2e",
    fg="#f5deb3",
    insertbackground="#f5deb3",
    relief="solid",
    bd=1,
    padx=10,
    pady=15,
)

main_button = Button(
    root,
    text="",
    font=("Arial", 15, "bold"),
    width=22,
    height=2,
    bg="#c8a96e",
    fg="#1a1a2e",
    activebackground="#e8c98e",
    activeforeground="#1a1a2e",
    relief="solid",
    bd=2,
    cursor="hand2",
)

choice_frame = Frame(root, bg="#1a1a2e")
choice_button1 = Button(
    choice_frame,
    text="",
    font=("Arial", 12, "bold"),
    width=40,
    height=2,
    bg="#c8a96e",
    fg="#1a1a2e",
    activebackground="#e8c98e",
    activeforeground="#1a1a2e",
    relief="solid",
    bd=2,
    cursor="hand2",
)
choice_button2 = Button(
    choice_frame,
    text="",
    font=("Arial", 12, "bold"),
    width=40,
    height=2,
    bg="#c8a96e",
    fg="#1a1a2e",
    activebackground="#e8c98e",
    activeforeground="#1a1a2e",
    relief="solid",
    bd=2,
    cursor="hand2",
)

ending_frame = Frame(root, bg="#1a1a2e")
analyze_button = Button(
    ending_frame,
    text="Analyze",
    font=("Arial", 14, "bold"),
    width=12,
    height=2,
    bg="#c8a96e",
    fg="#1a1a2e",
    activebackground="#e8c98e",
    activeforeground="#1a1a2e",
    relief="solid",
    bd=2,
    cursor="hand2",
)
restart_button = Button(
    ending_frame,
    text="Restart",
    font=("Arial", 14, "bold"),
    width=12,
    height=2,
    bg="#c8a96e",
    fg="#1a1a2e",
    activebackground="#e8c98e",
    activeforeground="#1a1a2e",
    relief="solid",
    bd=2,
    cursor="hand2",
)
exit_button = Button(
    ending_frame,
    text="Exit",
    font=("Arial", 14, "bold"),
    width=12,
    height=2,
    bg="#8b2020",
    fg="#ffffff",
    activebackground="#a83030",
    activeforeground="#ffffff",
    relief="solid",
    bd=2,
    cursor="hand2",
)

# Clue-found banner (brief notification below the title)
_clue_banner = Label(
    root,
    text="",
    font=("Arial", 10),
    bg="#1a2a1a",
    fg="#3fb950",
    anchor=W,
    padx=14,
    pady=4,
)


# =============================================================================
# SECTION 7 — FUNCTIONS  (from GUI.py, adapted to use GameEngine) (SYLVIE PART)
# =============================================================================

def set_background(filename: str) -> None:
    """Load an image from cs photos and set it as the full-window background."""
    global bg_photo
    if not filename:
        return
    full_path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(full_path):
        print(f"Background not found: {full_path}")
        return
    image = Image.open(full_path)
    image = image.resize((1200, 800))
    bg_photo = ImageTk.PhotoImage(image)
    background_label.config(image=bg_photo)
    background_label.lower()


def clear_screen() -> None:
    """Hide all story widgets before re-drawing the current scene."""
    title_label.pack_forget()
    title_label.place_forget()

    story_text.pack_forget()
    story_text.place_forget()

    main_button.pack_forget()
    main_button.place_forget()

    choice_frame.pack_forget()
    choice_frame.place_forget()
    choice_button1.pack_forget()
    choice_button1.place_forget()
    choice_button2.pack_forget()
    choice_button2.place_forget()

    ending_frame.pack_forget()
    ending_frame.place_forget()
    analyze_button.pack_forget()
    restart_button.pack_forget()
    exit_button.pack_forget()

    _clue_banner.pack_forget()
    _clue_banner.place_forget()


def _update_toolbar() -> None:
    """Refresh toolbar step counter, rewind button state, and status bar."""
    _step_label.config(text=f"— Step {engine.step_counter}")

    if engine.can_rewind():
        _rewind_btn.config(state=NORMAL, fg="#1a1a2e")
    else:
        _rewind_btn.config(state=DISABLED, fg="#888888")

    path = engine.get_path_history()
    if path:
        display = " > ".join(path[-4:])
        if len(path) > 4:
            display = "... > " + display
    else:
        display = "—"
    _path_label.config(text=f"Path: {display}")
    _clue_count_label.config(text=f"Clues: {engine.clue_heap.size()}")

    # Refresh evidence panel if it's open
    if _evidence_window and _evidence_window.winfo_exists():
        _evidence_window.refresh()


def show_page(new_clue: bool = False) -> None:
    """Rebuild the screen to match the current engine state (mirrors GUI.py's show_page)."""
    clear_screen()

    node = engine.get_current_node()

    # Background image
    if node.bg_image:
        set_background(node.bg_image)

    # Title
    title_label.config(text=node.title)
    title_label.pack(pady=20)

    # Story text
    story_text.config(state=NORMAL)
    story_text.delete("1.0", END)
    story_text.insert(END, node.text)
    story_text.place(relx=0.5, rely=0.78, anchor=CENTER)
    story_text.config(state=DISABLED)

    # New-clue banner (auto-hides after 3.5 s)
    if new_clue and node.clue:
        _clue_banner.config(text=f"  New clue found: {node.clue['name']}  "
                                  f"(importance {node.clue['importance']}/10)")
        _clue_banner.place(relx=0.5, rely=0.13, anchor=CENTER)
        root.after(3500, _clue_banner.place_forget)

    # Buttons — mirrors GUI.py page-type logic, driven by StoryNode
    if node.is_ending:
        # Ending: Analyze / Restart / Exit
        ending_frame.place(relx=0.5, rely=0.55, anchor=CENTER)
        analyze_button.config(command=_open_analysis)
        analyze_button.pack(side=LEFT, padx=15)
        restart_button.config(command=_on_restart)
        restart_button.pack(side=LEFT, padx=15)
        exit_button.config(command=root.destroy)
        exit_button.pack(side=LEFT, padx=15)

    elif len(node.choices) == 2:
        # Two-choice scene
        choice_frame.place(relx=0.5, rely=0.55, anchor=CENTER)
        choice_button1.config(
            text=node.choices[0][0],
            command=lambda: _make_choice(0),
        )
        choice_button1.pack(side=TOP, pady=6)
        choice_button2.config(
            text=node.choices[1][0],
            command=lambda: _make_choice(1),
        )
        choice_button2.pack(side=TOP, pady=6)

    elif len(node.choices) == 1:
        # Single-choice scene → "Next" button
        label = node.choices[0][0]
        btn_text = "Start" if engine.step_counter == 0 else "Next"
        main_button.config(text=btn_text, command=lambda: _make_choice(0))
        main_button.place(relx=0.5, rely=0.55, anchor=CENTER)

    _update_toolbar()


# ── Action handlers ──────────────────────────────────────────────────────────

def _make_choice(index: int) -> None:
    prev_count = engine.clue_heap.size()
    if engine.make_choice(index):
        new_clue = engine.clue_heap.size() > prev_count
        show_page(new_clue=new_clue)


def _on_rewind() -> None:
    if engine.rewind():
        show_page()
    else:
        messagebox.showinfo(
            "Rewind",
            "You cannot rewind from this scene.",
            parent=root,
        )


def _on_restart() -> None:
    if messagebox.askyesno(
        "Restart",
        "Start the investigation from the beginning?\nAll progress will be lost.",
        parent=root,
    ):
        engine.restart()
        show_page()


def _open_evidence() -> None:
    global _evidence_window
    if _evidence_window and _evidence_window.winfo_exists():
        _evidence_window.lift()
        _evidence_window.refresh()
    else:
        _evidence_window = EvidencePanel(root, engine)


def _open_analysis() -> None:
    global _analysis_window
    if _analysis_window and _analysis_window.winfo_exists():
        _analysis_window.win.lift()
    else:
        _analysis_window = AnalysisWindow(root, engine)


# =============================================================================
# SECTION 8 — ENTRY POINT
# =============================================================================

show_page()
root.mainloop()
