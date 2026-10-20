# Leet Code 200 - Num Island

# Key Trick
# - Count island as soon as encounter 1
# - Perform DFS
# - Reuse grid to marked visited by setting to 0

class Solution:
    def numIslands(self, grid):
        m = len(grid)
        n = len(grid[0])
        count = 0

        for i in range(m):
            for j in range(n):
                if grid[i][j] == '1':
                    count += 1
                    self.traveseid(grid, i, j, m, n)

        return count

    def traveseid(self, grid, i, j, m, n):
        # To handle boundary conditions and water cells
        if i < 0 or j < 0 or i >= m or j >= n or grid[i][j] == '0':
            return

        # To mark as visited
        grid[i][j] = '0'

        self.traveseid(grid, i, j + 1, m, n)
        self.traveseid(grid, i + 1, j, m, n)
        self.traveseid(grid, i, j - 1, m, n)
        self.traveseid(grid, i - 1, j, m, n)