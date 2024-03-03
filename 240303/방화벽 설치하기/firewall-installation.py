from collections import deque

def diffusion(grid_copy):
    visited = [[False] * len(grid_copy[0]) for _ in range(len(grid_copy))]
    delta = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for fire_row, fire_col in fire_list:
        queue = deque()
        queue.append((fire_row, fire_col))
        cur_x, cur_y = fire_row, fire_col
        
        while len(queue) > 0:
            cur_x, cur_y = queue.popleft()
            
            for dx, dy in delta:
                if cur_x + dx >= 0 and cur_x + dx < len(grid_copy) and cur_y + dy >= 0 and cur_y + dy < len(grid_copy[0]):
                    if grid_copy[cur_x + dx][cur_y + dy] != 1 and not visited[cur_x + dx][cur_y + dy]:
                        queue.append((cur_x + dx, cur_y + dy))
                        visited[cur_x + dx][cur_y + dy] = True
                        grid_copy[cur_x + dx][cur_y + dy] = 2
    
    return grid_copy
                        
def num_of_not_fire(wall_list):
    num = 0
    
    grid_copy = [[None] * len(grid[0]) for _ in range(len(grid))]
    
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            grid_copy[row][col] = grid[row][col]
    
    for wall_row, wall_col in wall_list:
        grid_copy[wall_row][wall_col] = 1
    
    after_diffusion = diffusion(grid_copy)
    
    for row in range(len(after_diffusion)):
        for col in range(len(after_diffusion[0])):
            if after_diffusion[row][col] == 0:
                num += 1
    
    return num

def dfs(idx, wall_list):     
    if len(wall_list) == 3:
        
        result = num_of_not_fire(wall_list)
        result_list.append(result)
        return

    for j in range(idx, len(candidate)):
        
        if candidate[j] not in wall_list:
            wall_list.append(candidate[j])
            dfs(j, wall_list)
            wall_list.pop()

N, M = map(int, input().split())

grid = []
fire_list = []
candidate = []
result_list = []

for _ in range(N):
    grid.append(list(map(int, input().split())))

for row in range(len(grid)):
    for col in range(len(grid[0])):
        if grid[row][col] == 0:
            candidate.append((row, col))
        if grid[row][col] == 2:
            fire_list.append((row, col))
dfs(0, [])

if len(result_list) > 0:
    print(max(result_list))
else:
    print(0)