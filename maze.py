import random
import sys
import os
import shutil

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
        self.start = (int(width / 2), 0)
        self.end = (int(width / 2), height - 1)
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

    def render(self, greedy, a_star):
        canvas_width, canvas_height = int(self.cell_width * self.height * 1.1), int(self.cell_width * self.height * 1.1)
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

        # Render AI paths
        fpath = 'images'
        if os.path.exists(fpath):
            shutil.rmtree(fpath)
        os.mkdir(fpath)
        images = []
        names = ['img{:02d}.gif'.format(i) for i in range(max(len(greedy), len(a_star)))]
        pos = 0
        for f, n in enumerate(names):
            print('Processing frame %s of %s' % (f, len(names)))
            
            frame = im.copy()
            draw = ImageDraw.Draw(frame)
            draw.text((0, self.cell_width * self.height + 10), 'STEP %s' % f, fill=(255, 255, 255, 255))

            # Render greedy path
            try:
                x = greedy[f][0] * self.cell_width + self.cell_width / 4
                y = greedy[f][1] * self.cell_width + self.cell_width / 4
                w = self.cell_width / 2
                draw.ellipse((x, y, w + x, w + y), 'red')
            except IndexError:
                pass

            # Render a star path
            try:
                x = a_star[f][0] * self.cell_width + self.cell_width / 4
                y = a_star[f][1] * self.cell_width + self.cell_width / 4
                w = self.cell_width / 2
                draw.ellipse((x, y, w + x, w + y), 'green')
            except IndexError:
                pass

            frame.save(os.path.join(fpath, n))
            pos += 25

        for n in names:
            frame = Image.open(os.path.join(fpath, n))
            images.append(frame)

        # Save the frames as an animated GIF
        images[0].save(os.path.join(fpath, 'rendered.gif'),
                       save_all=True,
                       append_images=images[1:],
                       duration=100,
                       loop=0)


class AI:

    def __init__(self, maze):
        self.maze = maze

    def is_path_better(self, path, x, y, direction):
        look_ahead = 3
        path_t = list(path)
        if direction == 'north':
            path_t.append((x, y - 1))
        if direction == 'south':
            path_t.append((x, y + 1))
        if direction == 'east':
            path_t.append((x + 1, y))
        if direction == 'west':
            path_t.append((x - 1, y))

        path_weight_t = 0

        for l in range(look_ahead):  # Find minimum path from adjacent cell
            go_t = None
            good_adj_cells_t = []
            min_weight_t = sys.maxsize
            x_t, y_t = path_t[len(path_t) - 1][0], path_t[len(path_t) - 1][1]
            path_weight_t += self.maze.cells[x_t][y_t].weight

            if self.maze.exists(x_t, y_t - 1) and not self.maze.cells[x_t][y_t].north:
                good_adj_cells_t.append('north')
            if self.maze.exists(x_t, y_t + 1) and not self.maze.cells[x_t][y_t].south:
                good_adj_cells_t.append('south')
            if self.maze.exists(x_t + 1, y_t) and not self.maze.cells[x_t][y_t].east:
                good_adj_cells_t.append('east')
            if self.maze.exists(x_t - 1, y_t) and not self.maze.cells[x_t][y_t].west:
                good_adj_cells_t.append('west')

            # Find minimum next step
            if good_adj_cells_t:
                for good_adj_cell_t in good_adj_cells_t:
                    if good_adj_cell_t == 'north' and (x_t, y_t - 1) not in path_t:
                        if self.maze.cells[x_t][y_t - 1].weight < min_weight_t:
                            go_t = 'north'
                            min_weight_t = self.maze.cells[x_t][y_t - 1].weight
                    if good_adj_cell_t == 'south' and (x_t, y_t + 1) not in path_t:
                        if self.maze.cells[x_t][y_t + 1].weight < min_weight_t:
                            go_t = 'south'
                            min_weight_t = self.maze.cells[x_t][y_t + 1].weight
                    if good_adj_cell_t == 'east' and (x_t + 1, y_t) not in path_t:
                        if self.maze.cells[x_t + 1][y_t].weight < min_weight_t:
                            go_t = 'east'
                            min_weight_t = self.maze.cells[x_t + 1][y_t].weight
                    if good_adj_cell_t == 'west' and (x_t - 1, y_t) not in path_t:
                        if self.maze.cells[x_t - 1][y_t].weight < min_weight_t:
                            go_t = 'west'
                            min_weight_t = self.maze.cells[x_t - 1][y_t].weight

                if go_t == 'north':
                    path_t.append((x_t, y_t - 1))
                elif go_t == 'south':
                    path_t.append((x_t, y_t + 1))
                elif go_t == 'east':
                    path_t.append((x_t + 1, y_t))
                elif go_t == 'west':
                    path_t.append((x_t - 1, y_t))
                else:
                    pass

        return path_weight_t

    def greedy(self):
        x, y = self.maze.start[0], maze.start[1]
        path = [(x, y)]
        visited = []
        traversed_cells_count = 0
        traversed_cells_total_weight = 0

        while (x, y) != self.maze.end:
            go = None
            x, y = path[len(path) - 1][0], path[len(path) - 1][1]
            visited.append((x, y))
            traversed_cells_count += 1
            traversed_cells_total_weight += self.maze.cells[x][y].weight

            # Find valid adjacent cells
            path_weight_min_t = sys.maxsize  # Minimum path weight of all available choice paths

            if self.maze.exists(x, y - 1) and not self.maze.cells[x][y].north and (x, y - 1) not in visited:
                calculated_temp_path = self.is_path_better(path, x, y, 'north')
                if calculated_temp_path < path_weight_min_t:
                    path_weight_min_t = calculated_temp_path
                    go = 'north'
            if self.maze.exists(x, y + 1) and not self.maze.cells[x][y].south and (x, y + 1) not in visited:
                calculated_temp_path = self.is_path_better(path, x, y, 'south')
                if calculated_temp_path < path_weight_min_t:
                    path_weight_min_t = calculated_temp_path
                    go = 'south'
            if self.maze.exists(x + 1, y) and not self.maze.cells[x][y].east and (x + 1, y) not in visited:
                calculated_temp_path = self.is_path_better(path, x, y, 'east')
                if calculated_temp_path < path_weight_min_t:
                    path_weight_min_t = calculated_temp_path
                    go = 'east'
            if self.maze.exists(x - 1, y) and not self.maze.cells[x][y].west and (x - 1, y) not in visited:
                calculated_temp_path = self.is_path_better(path, x, y, 'west')
                if calculated_temp_path < path_weight_min_t:
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

        print('Greedy')
        print('Cells traversed: %s' % traversed_cells_count)
        print('Cells traversed total weight: %s' % traversed_cells_total_weight)

        return visited

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

        print('A*')
        print('Cells traversed: %s' % traversed_cells_count)
        print('Cells traversed total weight: %s' % traversed_cells_total_weight)

        return visited

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
    maze = Maze(width=15, height=15, cell_width=50)
    maze.generate()

    ai = AI(maze)
    greedy = ai.greedy()
    a_star = ai.a_star()

    maze.render(greedy, a_star)
