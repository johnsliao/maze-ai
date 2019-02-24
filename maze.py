import random
import sys

from PIL import Image, ImageDraw


class Cell:
    def __init__(self):
        self.north = True
        self.south = True
        self.east = True
        self.west = True
        self.visited = False
        self.weight = random.choice(range(5))


class Maze:
    def __init__(self, width=20, height=20, cell_width=20):
        self.width = width
        self.height = height
        self.cell_width = cell_width
        self.start = (width / 2, 0)
        self.end = (width / 2, height - 1)
        self.cells = [[Cell() for _ in range(height)] for _ in range(width)]

    def generate(self):
        x, y = random.choice(range(self.width)), random.choice(range(self.height))
        self.cells[x][y].visited = True
        path = [(x, y)]

        while not all(all(c.visited for c in cell) for cell in self.cells):
            x, y = path[len(path) - 1][0], path[len(path) - 1][1]

            good_adj_cells = []
            if self.exists(x, y - 1) and not self.cells[x][y - 1].visited:
                good_adj_cells.append('north')
            if self.exists(x, y + 1) and not self.cells[x][y + 1].visited:
                good_adj_cells.append('south')
            if self.exists(x + 1, y) and not self.cells[x + 1][y].visited:
                good_adj_cells.append('east')
            if self.exists(x - 1, y) and not self.cells[x - 1][y].visited:
                good_adj_cells.append('west')

            if good_adj_cells:
                go = random.choice(good_adj_cells)
                if go == 'north':
                    self.cells[x][y].north = False
                    self.cells[x][y - 1].south = False
                    self.cells[x][y - 1].visited = True
                    path.append((x, y - 1))
                if go == 'south':
                    self.cells[x][y].south = False
                    self.cells[x][y + 1].north = False
                    self.cells[x][y + 1].visited = True
                    path.append((x, y + 1))
                if go == 'east':
                    self.cells[x][y].east = False
                    self.cells[x + 1][y].west = False
                    self.cells[x + 1][y].visited = True
                    path.append((x + 1, y))
                if go == 'west':
                    self.cells[x][y].west = False
                    self.cells[x - 1][y].east = False
                    self.cells[x - 1][y].visited = True
                    path.append((x - 1, y))
            else:
                path.pop()

    def exists(self, x, y):
        if x < 0 or x > self.width - 1 or y < 0 or y > self.height - 1:
            return False
        return True

    def render(self):
        canvas_width, canvas_height = self.cell_width * self.width, self.cell_width * self.height
        im = Image.new('RGB', (canvas_width, canvas_height))
        draw = ImageDraw.Draw(im)

        for x in range(self.width):
            for y in range(self.height):
                # Render cell walls
                if self.cells[x][y].north:
                    draw.line(
                        (x * self.cell_width, y * self.cell_width, (x + 1) * self.cell_width, y * self.cell_width))
                if self.cells[x][y].south:
                    draw.line((x * self.cell_width, (y + 1) * self.cell_width, (x + 1) * self.cell_width,
                               (y + 1) * self.cell_width))
                if self.cells[x][y].east:
                    draw.line(((x + 1) * self.cell_width, y * self.cell_width, (x + 1) * self.cell_width,
                               (y + 1) * self.cell_width))
                if self.cells[x][y].west:
                    draw.line(
                        (x * self.cell_width, y * self.cell_width, x * self.cell_width, (y + 1) * self.cell_width))

                # Render cell weight in top left corner
                draw.text((x * self.cell_width + 5, y * self.cell_width + 5), str(self.cells[x][y].weight),
                          fill=(255, 255, 255, 255))

                # Draw (x,y) at lower left corner
                draw.text((x * self.cell_width + 5, y * self.cell_width + self.cell_width - 15),
                          str('(%s, %s)' % (x, y)),
                          fill=(255, 255, 255, 255))

        draw.text((self.start[0] * self.cell_width + self.cell_width / 10,
                   self.start[1] * self.cell_width + self.cell_width / 2), 'START', fill=(255, 255, 255, 255))
        draw.text(
            (self.end[0] * self.cell_width + self.cell_width / 10, self.end[1] * self.cell_width + self.cell_width / 2),
            'END',
            fill=(255, 255, 255, 255))
        im.show()


class AI:

    def __init__(self, maze):
        self.maze = maze

    def greedy(self):
        x, y = self.maze.start[0], maze.start[1]
        path = [(x, y)]
        visited = []
        traversed_cells_count = 0
        traversed_cells_total_weight = 0

        look_ahead = 3

        while (x, y) != self.maze.end:
            good_adj_cells = []
            min_weight = sys.maxsize
            go = None

            x, y = path[len(path) - 1][0], path[len(path) - 1][1]
            visited.append((x, y))
            traversed_cells_count += 1
            traversed_cells_total_weight += self.maze.cells[x][y].weight

            # Find valid adjacent cells
            if self.maze.exists(x, y - 1) and not self.maze.cells[x][y].north:
                for l in range(look_ahead):
                good_adj_cells.append('north')
            if self.maze.exists(x, y + 1) and not self.maze.cells[x][y].south:
                good_adj_cells.append('south')
            if self.maze.exists(x + 1, y) and not self.maze.cells[x][y].east:
                good_adj_cells.append('east')
            if self.maze.exists(x - 1, y) and not self.maze.cells[x][y].west:
                good_adj_cells.append('west')

            if good_adj_cells:
                # Calculate path weights for each valid adjacent cell
                for good_adj_cell in good_adj_cells:
                    for l in range(look_ahead):
                        x_t, y_t = x, y

                        if self.maze.exists(x, y - 1) and not self.maze.cells[x][y].north:
                            good_adj_cells.append('north')
                        if self.maze.exists(x, y + 1) and not self.maze.cells[x][y].south:
                            good_adj_cells.append('south')
                        if self.maze.exists(x + 1, y) and not self.maze.cells[x][y].east:
                            good_adj_cells.append('east')
                        if self.maze.exists(x - 1, y) and not self.maze.cells[x][y].west:
                            good_adj_cells.append('west')

                        # Find valid adjacent cells
                        if good_adj_cell == 'north' and (x, y - 1) not in path and (x, y - 1) not in visited:
                            path_weight = self.calculate_path_weight(x, y - 1)
                            if path_weight < min_weight:
                                go = 'north'
                                min_weight = path_weight
                        if good_adj_cell == 'south' and (x, y + 1) not in path and (x, y + 1) not in visited:
                            path_weight = self.calculate_path_weight(x, y + 1)
                            if path_weight < min_weight:
                                go = 'south'
                                min_weight = path_weight
                        if good_adj_cell == 'east' and (x + 1, y) not in path and (x + 1, y) not in visited:
                            path_weight = self.calculate_path_weight(x + 1, y)
                            if path_weight < min_weight:
                                go = 'east'
                                min_weight = path_weight
                        if good_adj_cell == 'west' and (x - 1, y) not in path and (x - 1, y) not in visited:
                            path_weight = self.calculate_path_weight(x - 1, y)
                            if path_weight < min_weight:
                                go = 'west'

            else:
                path.pop()

        print 'A*'
        print 'Cells traversed: %s' % traversed_cells_count
        print 'Cells traversed total weight: %s' % traversed_cells_total_weight

    def a_star(self):
        x, y = self.maze.start[0], maze.start[1]
        path = [(x, y)]
        visited = []
        traversed_cells_count = 0
        traversed_cells_total_weight = 0

        while (x, y) != self.maze.end:
            good_adj_cells = []
            min_weight = sys.maxsize
            go = None

            x, y = path[len(path) - 1][0], path[len(path) - 1][1]
            visited.append((x, y))
            traversed_cells_count += 1
            traversed_cells_total_weight += self.maze.cells[x][y].weight

            if self.maze.exists(x, y - 1) and not self.maze.cells[x][y].north:
                good_adj_cells.append('north')
            if self.maze.exists(x, y + 1) and not self.maze.cells[x][y].south:
                good_adj_cells.append('south')
            if self.maze.exists(x + 1, y) and not self.maze.cells[x][y].east:
                good_adj_cells.append('east')
            if self.maze.exists(x - 1, y) and not self.maze.cells[x][y].west:
                good_adj_cells.append('west')

            if good_adj_cells:
                for good_adj_cell in good_adj_cells:
                    if good_adj_cell == 'north' and (x, y - 1) not in path and (x, y - 1) not in visited:
                        path_weight = self.calculate_path_weight(x, y - 1)
                        if path_weight < min_weight:
                            go = 'north'
                            min_weight = path_weight
                    if good_adj_cell == 'south' and (x, y + 1) not in path and (x, y + 1) not in visited:
                        path_weight = self.calculate_path_weight(x, y + 1)
                        if path_weight < min_weight:
                            go = 'south'
                            min_weight = path_weight
                    if good_adj_cell == 'east' and (x + 1, y) not in path and (x + 1, y) not in visited:
                        path_weight = self.calculate_path_weight(x + 1, y)
                        if path_weight < min_weight:
                            go = 'east'
                            min_weight = path_weight
                    if good_adj_cell == 'west' and (x - 1, y) not in path and (x - 1, y) not in visited:
                        path_weight = self.calculate_path_weight(x - 1, y)
                        if path_weight < min_weight:
                            go = 'west'

                if go == 'north':
                    path.append((x, y - 1))
                elif go == 'south':
                    path.append((x, y + 1))
                elif go == 'east':
                    path.append((x + 1, y))
                elif go == 'west':
                    path.append((x - 1, y))
                else:
                    path.pop()
            else:
                path.pop()

        print 'A*'
        print 'Cells traversed: %s' % traversed_cells_count
        print 'Cells traversed total weight: %s' % traversed_cells_total_weight

    def calculate_path_weight(self, x, y):
        delta_x = self.maze.end[0] - x
        delta_y = self.maze.end[1] - y

        total_weight = 0
        for i in range(0, abs(delta_x)):
            x = x + 1 if delta_x > 0 else x - 1
            total_weight += self.maze.cells[x][y].weight

        for j in range(0, abs(delta_y)):
            y = y + 1 if delta_y > 0 else y - 1
            total_weight += self.maze.cells[x][y].weight

        return total_weight


if __name__ == '__main__':
    maze = Maze(width=8, height=8, cell_width=50)
    maze.generate()
    maze.render()

    ai = AI(maze)
    ai.a_star()
