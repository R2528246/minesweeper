import random


class Minesweeper:
    """
    Minesweeper game representation.
    """

    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty board.
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly.
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation of where mines are located.
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
        Returns the number of mines neighboring the given cell.
        """
        count = 0
        i, j = cell

        for r in range(i - 1, i + 2):
            for c in range(j - 1, j + 2):
                if (r, c) == cell:
                    continue
                if 0 <= r < self.height and 0 <= c < self.width:
                    if self.board[r][c]:
                        count += 1
        return count

    def won(self):
        """
        Checks whether all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of cells and a count of how many are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return (
            isinstance(other, Sentence)
            and self.cells == other.cells
            and self.count == other.count
        )

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """Return all cells in the sentence known to be mines."""
        if self.cells and len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """Return all cells in the sentence known to be safe."""
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """Update the sentence after a cell is known to be a mine."""
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """Update the sentence after a cell is known to be safe."""
        self.cells.discard(cell)


class MinesweeperAI:
    """
    Minesweeper game player that makes moves using logical inference.
    """

    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        """Mark a cell as a mine and update all knowledge sentences."""
        if cell in self.mines:
            return
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """Mark a cell as safe and update all knowledge sentences."""
        if cell in self.safes:
            return
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Record a safe move and its neighboring mine count, then infer
        every conclusion available from the current knowledge base.
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        i, j = cell
        neighbors = set()
        remaining_count = count

        for r in range(i - 1, i + 2):
            for c in range(j - 1, j + 2):
                neighbor = (r, c)
                if neighbor == cell:
                    continue
                if not (0 <= r < self.height and 0 <= c < self.width):
                    continue
                if neighbor in self.mines:
                    remaining_count -= 1
                elif neighbor not in self.safes:
                    neighbors.add(neighbor)

        if neighbors:
            new_sentence = Sentence(neighbors, remaining_count)
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        self.update_knowledge()

    def update_knowledge(self):
        """
        Repeatedly mark known mines and safes, remove empty sentences,
        and infer new sentences using subset relationships.
        """
        while True:
            changed = False

            # Collect deductions before changing the knowledge base.
            known_mines = set()
            known_safes = set()
            for sentence in self.knowledge:
                known_mines.update(sentence.known_mines())
                known_safes.update(sentence.known_safes())

            for cell in known_mines - self.mines:
                self.mark_mine(cell)
                changed = True

            for cell in known_safes - self.safes:
                self.mark_safe(cell)
                changed = True

            # Remove empty sentences and duplicate sentences.
            cleaned = []
            for sentence in self.knowledge:
                if sentence.cells and sentence not in cleaned:
                    cleaned.append(sentence)
            if len(cleaned) != len(self.knowledge):
                changed = True
            self.knowledge = cleaned

            # Infer sentences where one set is a proper subset of another.
            inferred_sentences = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1.cells < sentence2.cells:
                        inferred = Sentence(
                            sentence2.cells - sentence1.cells,
                            sentence2.count - sentence1.count
                        )
                        if (
                            inferred.cells
                            and inferred not in self.knowledge
                            and inferred not in inferred_sentences
                        ):
                            inferred_sentences.append(inferred)

            if inferred_sentences:
                self.knowledge.extend(inferred_sentences)
                changed = True

            if not changed:
                break

    def make_safe_move(self):
        """Return an unplayed cell known to be safe, or None."""
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """Return a random unplayed cell not known to be a mine, or None."""
        choices = [
            (i, j)
            for i in range(self.height)
            for j in range(self.width)
            if (i, j) not in self.moves_made and (i, j) not in self.mines
        ]
        if not choices:
            return None
        return random.choice(choices)
