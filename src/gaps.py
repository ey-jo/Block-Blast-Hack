def count_gaps(matrix):
    def dfs(matrix, visited, i, j):
        # Depth-first search to count the size of a sector
        stack = [(i, j)]
        count = 0
        while stack:
            x, y = stack.pop()
            # Check if the current position is out of bounds or already visited or not a gap
            if x < 0 or x >= len(matrix) or y < 0 or y >= len(matrix[0]) or visited[x][y] or matrix[x][y] != 0:
                continue
            # Mark the current position as visited
            visited[x][y] = True
            count += 1
            # Add all 4 possible directions (up, down, left, right) to the stack
            stack.append((x-1, y))
            stack.append((x+1, y))
            stack.append((x, y-1))
            stack.append((x, y+1))
        return count

    # Initialize the visited matrix with False values
    visited = [[False for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
    sectors = []

    # Iterate through each cell in the matrix
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            # If the cell is a gap (0) and not visited, perform DFS to find the sector size
            if matrix[i][j] == 0 and not visited[i][j]:
                sector_size = dfs(matrix, visited, i, j)
                if sector_size > 0:
                    sectors.append(sector_size)

    return sectors