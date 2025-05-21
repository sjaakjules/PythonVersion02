'''
Purpose: Models the 5x4 Realm grid of locations and all in-game cards and tokens.
Responsibilities:
	•	Manages Locations (grid squares) and Borders (for auras and large minions).
	•	Differentiates regions (surface, underwater, underground, void).
	•	Visualizes state of each grid location and supports card placements.
	•	Maintains which zones (surface vs. subsurface) minions or artifacts occupy.
	•	Shows zones: player's Atlas, Spellbook, Hand, and Cemetery.
	•	Calls Util_Effects.py to animate the cards, tokens, hands and tapping etc.
'''
from typing import List, Optional, Tuple
import Util_Effects
from Card import Card


class Location:
	def __init__(self) -> None:
		self.site: Optional[Card] = None
		self.surfaceSpells: Optional[Card] = []
		self.subSurfaceSpells: Optional[Card] = []
		self.isWater: bool = False
		self.bodyIndex: int = -1
		self.index: int = -1


class Intersection:
	def __init__(self, adjacent_locations: List[Location]) -> None:
		self.spells: Optional[Card] = []
		self.adjacent_locations: List[Location] = adjacent_locations  # 1 to 4 Locations


class Board:
	ROWS = 5
	COLS = 4
	ZONES: List[str] = ['Atlas', 'Spellbook', 'Hand', 'Cemetery', 'Discard']

	def __init__(self) -> None:
		self.locations: List[List[Location]] = []
		index = 1
		for i in range(self.ROWS):
			row = []
			for j in range(self.COLS):
				loc = Location()
				loc.index = index
				index += 1
				row.append(loc)
			self.locations.append(row)
		self.intersections: List[List[Intersection]] = self.create_intersections()

	def create_intersections(self) -> List[List[Intersection]]:
		intersections: List[List[Intersection]] = []
		for i in range(self.ROWS):
			row: List[Intersection] = []
			for j in range(self.COLS):
				adj: List[Location] = []

				if i < self.ROWS - 1 and j < self.COLS - 1:
					adj = [
						self.locations[i][j],
						self.locations[i][j + 1],
						self.locations[i + 1][j],
						self.locations[i + 1][j + 1]
					]
				else:
					if i < self.ROWS - 1:
						adj.append(self.locations[i + 1][j])
					if j < self.COLS - 1:
						adj.append(self.locations[i][j + 1])
					adj.append(self.locations[i][j])  # Always include base location

				row.append(Intersection(adj))
			intersections.append(row)
		return intersections

	def get_location(self, row: int, col: int) -> Optional[Location]:
		"""Return the location at the specified coordinates, or None if out of bounds."""
		if 0 <= row < self.ROWS and 0 <= col < self.COLS:
			return self.locations[row][col]
		return None

	def get_intersection(self, row: int, col: int) -> Optional[Intersection]:
		"""Return the intersection at the specified coordinates, or None if out of bounds."""
		if 0 <= row < self.ROWS and 0 <= col < self.COLS:
			return self.intersections[row][col]
		return None

	def get_projectile_locations(self, row: int, col: int) -> List[List[Tuple[int, int, Location]]]:
		"""Return all straight-line paths in 4 directions from a location."""
		directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
		lines: List[List[Tuple[int, int, Location]]] = []

		for dr, dc in directions:
			line: List[Tuple[int, int, Location]] = []
			r, c = row + dr, col + dc
			while 0 <= r < self.ROWS and 0 <= c < self.COLS:
				loc = self.locations[r][c]
				line.append((r, c, loc))
				r += dr
				c += dc
			lines.append(line)

		return lines
	
	def get_adjacent_locations(self, row: int, col: int) -> List[Tuple[int, int, Location]]:
		"""Return orthogonally adjacent locations to the given location."""
		directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
		adjacent: List[Tuple[int, int, Location]] = []

		for dr, dc in directions:
			r, c = row + dr, col + dc
			loc = self.get_location(r, c)
			if loc:
				adjacent.append((r, c, loc))

		return adjacent

	def get_nearby_locations(self, row: int, col: int) -> List[Tuple[int, int, Location]]:
		"""Return all adjacent and diagonal nearby locations to the given location."""
		directions = [
			(-1, -1), (-1, 0), (-1, 1),  # top-left, top, top-right
			(0, -1),		   (0, 1),   # left,	   right
			(1, -1),  (1, 0),  (1, 1)	# bottom-left, bottom, bottom-right
		]
		nearby: List[Tuple[int, int, Location]] = []

		for dr, dc in directions:
			r, c = row + dr, col + dc
			loc = self.get_location(r, c)
			if loc:
				nearby.append((r, c, loc))

		return nearby