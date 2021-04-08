import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # Check if the number of cells is equal to the count of mines - if so, return known mines
        if len(self.cells) <= self.count:
            return self.cells.copy()
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells.copy()
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # check if cell is in sentence
        if cell in self.cells:
            # reduce known mine count
            self.count -= 1
            # remove cell
            self.cells.remove(cell)
        return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # check if cell in sentence
        if cell in self.cells:
            # remove cell
            self.cells.remove(cell)
        return


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        Cell is provided as a tuple(i,j)

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) add cell to self.moves
        self.moves_made.add(cell)
        # 2) mark as safe
        self.mark_safe(cell)

        # 3) create a new sentence
        newCells = set()

        # 3a) Find all empty cells around this cell
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # skip instances that are off of the board
                if i < 0 or i > self.height-1 or j < 0 or j > self.width - 1:
                    continue
                locationToTest = (i, j)
                if locationToTest == cell:
                    continue
                if locationToTest not in self.moves_made and locationToTest not in self.mines and locationToTest not in self.safes:
                    newCells.add(locationToTest)
        # 3b) if there are empty cells near this cell add a new sentence to knowledge base
        if len(newCells) != 0:
            newSentence = Sentence(newCells, count)
            self.knowledge.append(newSentence)
            print("new sentence added")
            print(newCells, count)

        ## Cycle through all known knowledge seeing if any sentences became resolved by new data.
        ## Each time something is resolved it could have knock on effects, so cycle through all sencents again.
        cycles = 1
        while cycles > 0:
            # 4) look for new leads
            for sentence in self.knowledge:
                safes = sentence.known_safes()
                if safes != None:
                    for cell in safes:
                        print("marking safe cells from sentence:", sentence)
                        self.mark_safe(cell)
                    cycles = 2
                    self.knowledge.remove(sentence)
                else:
                    mines = sentence.known_mines()
                    if mines != None:
                        print("marking known mines from sentence:", sentence)
                        for cell in mines:
                            self.mark_mine(cell)
                        self.knowledge.remove(sentence)
                        cycles = 2
            # 5) Inference new sentences
            for sentenceA in self.knowledge:
                for sentenceB in self.knowledge:
                    if sentenceA == sentenceB:
                        continue
                    if len(sentenceA.cells) == 0 or len(sentenceB.cells) == 0:
                        continue
                    AB = sentenceA.cells - sentenceB.cells
                    BA = sentenceB.cells - sentenceA.cells
                    if len(BA) == 0:
                        if len(AB) != 0:
                            if sentenceA.count - sentenceB.count > 0:
                                newSentence = Sentence(AB, sentenceA.count - sentenceB.count)
                                if newSentence not in self.knowledge:
                                    print("sentence inferred", newSentence)
                                    self.knowledge.append(newSentence)
                                    cycles = 2
                    if len(AB) == 0:
                        if len(BA) != 0:
                            if sentenceB.count - sentenceA.count > 0:
                                newSentence = Sentence(BA, sentenceB.count - sentenceA.count)
                                if newSentence not in self.knowledge:
                                    print("sentence inferred", newSentence)
                                    self.knowledge.append(newSentence)
                                    cycles = 2
            cycles -= 1

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        availableSafeMoves = self.safes - self.moves_made - self.mines
        if len(availableSafeMoves) == 0:
            return None
        safeMove = availableSafeMoves.pop()
        return safeMove


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Generate all options
        allMoves = set()
        for i in range(self.height):
            for j in range(self.width):
                allMoves.add((i,j))
        availableMoves = allMoves - self.mines - self.moves_made
        if len(availableMoves) == 0:
            return None
        randomMove = availableMoves.pop()
        return randomMove
        
        
