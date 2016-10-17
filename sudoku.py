#!/usr/bin/python

import argparse
import random
import copy

from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

BOARDS = ['debug', 'n00b', 'l33t', 'error']  # Available sudoku boards
MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell.
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9  # Width and height of the whole board

class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    
    def __init__(self, parent, game):
        self.game = game
        Frame.__init__(self, parent)
        self.parent = parent

        self.row, self.col = -1, -1

        self.__initUI()
    # End def

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self,
                              text="Clear answers",
                              command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
    # End def

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in xrange(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)
        # End for
    # End def

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in xrange(9):
            for j in xrange(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]
                    color = "black" if answer == original else "sea green"
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color
                    )
                # End if
            # End for
        # End for
    # End def

    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", tags="cursor"
            )
        # End if
    # End def

    def __draw_victory(self):
        # create an oval (which will be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="victory",
            fill="white", font=("Arial", 32)
        )
    # End def

    def __cell_clicked(self, event):
        if self.game.game_over:
            return
        # End if
        
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            #elif self.game.puzzle[row][col] == 0:
            elif self.game.start_puzzle[row][col] == 0:
            #elif True:
                self.row, self.col = row, col
            # End if/else block
        else:
            self.row, self.col = -1, -1
        # End if/else block

        self.__draw_cursor()
    # End def

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        # End if
        
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
            if self.game.check_win():
                self.__draw_victory()
            # End if
        # End if
    # End def

    def __clear_answers(self):
        self.game.start()
        self.canvas.delete("victory")
        self.__draw_puzzle()
    # End def
# End class


class SudokuBoard(object):
    """
    Sudoku Board representation
    """
    
    def __init__(self, board_file):
        self.board = self.__create_board(board_file)
    # End def

    def __create_board(self, board_file):
        board = []
        
        for line in board_file:
            if len(line) != 9:
                raise SudokuError(
                    "Each line in the sudoku puzzle must be 9 chars long."
                )
            # End if
            board.append([])

            for c in line:
                if c == None:
                    c = 0
                # End if
                
                board[-1].append(c)
            # End for
        # End for

        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")
        # End if
        
        return board
    # End def
# End class


class SudokuGame(object):
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """
    def __init__(self, board_file, board_solution):
        self.board_file = board_file
        self.board_solution = board_solution
        self.start_puzzle = SudokuBoard(board_file).board
    # End def

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in xrange(9):
            self.puzzle.append([])
            for j in xrange(9):
                self.puzzle[i].append(self.start_puzzle[i][j])
            # End for
        # End for
    # End def

    def check_win(self):
        for row in xrange(9):
            if not self.__check_row(row):
                return False
            # End If
        # End for
        
        for column in xrange(9):
            if not self.__check_column(column):
                return False
            # End if
        # End for
        
        for row in xrange(3):
            for column in xrange(3):
                if not self.__check_square(row, column):
                    return False
                # End if
            # End for
        # End for
        
        if self.puzzle != self.board_solution:
            return False
        else:
            self.game_over = True
            return True
        # End 
    # End def

    def __check_block(self, block):
        return set(block) == set(range(1, 10))
    # End def

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])
    # End def

    def __check_column(self, column):
        return self.__check_block(
            [self.puzzle[row][column] for row in xrange(9)]
        )
    # End def

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in xrange(row * 3, (row + 1) * 3)
                for c in xrange(column * 3, (column + 1) * 3)
            ]
        )
    # End def
# End class

def make_board(m=3, diff=1):
    """Return a random filled m**2 x m**2 Sudoku board."""
    n = m**2
    board = [[None for _ in range(n)] for _ in range(n)]

    def search(c=0):
        i, j = divmod(c, n)
        i0, j0 = i - i % 3, j - j % 3 # Origin of mxm block
        numbers = list(range(1, n + 1))
        random.shuffle(numbers)
        
        for x in numbers:
            if (x not in board[i]                     # row
                and all(row[j] != x for row in board) # column
                and all(x not in row[j0:j0+m]         # block
                        for row in board[i0:i])): 
                board[i][j] = x
                
                if c + 1 >= n**2 or search(c + 1):
                    return board
                # End if
            # End if
            
        else:
            # No number is valid in this cell: backtrack and try again.
            board[i][j] = None
            return None
        # End for/else block
    # End def
    
    filled_board = search()
    sol = copy.deepcopy(filled_board)
    
    # Randomly remove numbers from every line
    for lst in filled_board:
        rand = range(m**2)
        random.shuffle(rand)
        
        for i in range(diff):
            lst[rand[i]] = None
        # End for
    # End for
    
    return filled_board, sol
# End def

def parse_arguments():
    """
    Parses arguments of the form:
        sudoku.py <difficulty level>
    """
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--difficulty",
                            help="Desired board difficulty",
                            type=int,
                            choices=[1, 2, 3])

    # Creates a dictionary of keys = argument flag, and value = argument
    args = vars(arg_parser.parse_args())
    return args["difficulty"]
# End def

if __name__ == '__main__':
    diff = parse_arguments()
    
    new_board, solution = make_board(diff=diff)

    game = SudokuGame(new_board, solution)
    game.start()

    root = Tk()
    SudokuUI(root, game)
    root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
    root.mainloop()
# End if