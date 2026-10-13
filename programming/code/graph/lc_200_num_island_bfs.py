# LC 200. Number of Islands

# Tricks:
# - Use queue to store neighbors of current node
# - Store cur node and neighbors as soon as possible to 
#     avoid visiting the same node multiple times

from collections import deque

class Solution:
    def __init__(self):
        self.visited: set = set()
        self._row: int = 0
        self._col: int = 0

    def _getNeighbors(self, loc:tuple[int, int]) -> List[tuple[int, int]]:
        i, j = loc
        top: tuple = (i, j - 1)
        bottom: tuple = (i, j + 1)
        left: tuple = (i - 1, j)
        right: tuple = (i + 1, j)

        all_neighbors = [top, bottom, left, right]
        valid_neighbors = []

        for N in all_neighbors:
            x, y = N

            if not (x < 0 or y < 0 or x >= self._row or y >= self._col) and N not in self.visited:
                valid_neighbors.append((x,y))
        
        return valid_neighbors

    def _visitIsland(self, grid: List[List[str]], loc):
        to_visit: deque = deque()
        to_visit.append(loc)

        # Very important to add to visited here.
        # Else, we will visit more times than needed. It runs longer.
        self.visited.add(cur_loc)

        while len(to_visit) > 0:
            cur_loc = to_visit.popleft()
            neighbors = self._getNeighbors(cur_loc)

            for N in neighbors:
                x, y = N
                if(grid[x][y] == "1"):
                    # Very important to add to visited here.
                    # Else, we will visit more times than needed. It runs longer.
                    self.visited.add(cur_loc)
                    to_visit.append(N)


    def numIslands(self, grid: List[List[str]]) -> int:
        res: int = 0

        self._row = len(grid)
        self._col = len(grid[0])

        for i in range(self._row):
            for j in range(self._col):
                loc = (i, j)
                
                if loc not in self.visited and grid[i][j] == "1":
                    res += 1
                    self._visitIsland(grid, loc)
            

        return res
        