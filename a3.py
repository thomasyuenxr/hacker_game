from a3_support import *
import tkinter as tk
import random


class Entity(object):
    """Entity is an abstract class that is used to represent
    any element that can appear on the game's grid."""

    def display(self) -> str:
        """Return the character used to represent
        this entity in a text-based grid"""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return a representation of this entity"""
        return 'Entity()'


class Player(Entity):
    """A subclass of Entity representing a Player within the game"""

    def display(self) -> str:
        """Return the character representing a player"""
        return PLAYER

    def __repr__(self) -> str:
        """Return a representation of this entity"""
        return 'Player()'


class Destroyable(Entity):
    """A subclass of Entity representing a Destroyable within the game
    A destroyable can be destroyed by the player but not collected"""

    def display(self) -> str:
        """Return the character representing a destroyable"""
        return DESTROYABLE

    def __repr__(self) -> str:
        """Return a representation of this entity"""
        return 'Destroyable()'


class Collectable(Entity):
    """A subclass of Entity representing a Collectable within the game
    A collectable can be destroyed OR collected by the player"""

    def display(self) -> str:
        """Return the character representing a collectable"""
        return COLLECTABLE

    def __repr__(self) -> str:
        """Return a representation of this entity"""
        return 'Collectable()'


class Blocker(Entity):
    """A subclass of Entity representing a Blocker within the game
    A blocker cannot be destroyer or collected by the player"""

    def display(self) -> str:
        """Return the character representing a blocker"""
        return BLOCKER

    def __repr__(self) -> str:
        """Return a representation of this entity"""
        return 'Blocker()'


class Grid(object):
    """The Grid class is to represent the 2D grid of entities
    The top left position of the grid is indicated by (0, 0)"""

    def __init__(self, size: int) -> None:
        """A grid is constructed with a size representing the number of rows
        (equal to columns) in the grid.
        Initially a grid does not contain any entities.

        Parameters:
            size(int): the number of rows and columns of the grid
        """
        self._size = size
        self._entities = {}
        self._serialise_entities = {}

    def get_size(self) -> int:
        """Return the size of the grid"""
        return self._size

    def add_entity(self, position: Position, entity: Entity) -> None:
        """Add a given entity into the grid at a specified position
        The entity is only added if the position is valid.

        Parameters:
            position(Position): The specified position that
                the entity is adding to.
            entity (Entity): The adding kind of entity.
        """
        if self.in_bounds(position):  # position is valid
            self._entities[position] = entity

    def get_entities(self) -> Dict[Position, Entity]:
        """Return the dictionary containing grid entities."""
        return self._entities

    def get_entity(self, position: Position) -> Optional[Entity]:
        """Return a entity from the grid at a specified position
        or None if the position does not have a mapped entity.

        Parameters:
            position(Position): The specified position

        Returns:
            Entity at that specified position if exist or None.
        """
        return self._entities.get(position)

    def remove_entity(self, position: Position) -> None:
        """Remove an entity from the grid at a specified position.

        Parameters:
            position(Position): The specified position
        """
        del self._entities[position]

    def serialise(self) -> Dict[Tuple[int, int], str]:
        """Convert dictionary of Position and Entities into a simplified
        serialised dictionary mapping tuples to characters

        Returns:
            Dict[Tuple[int, int], str]: serialised mapping of
            position and character
        """
        for position in self._entities:
            # convert to get the simplified position tuple
            x, y = position.get_x(), position.get_y()
            character = self.get_entity(position).display()
            self._serialise_entities[(x, y)] = character
        return self._serialise_entities

    def in_bounds(self, position: Position) -> bool:
        """Return a boolean on whether the position is valid in terms of
        the dimensions of the grid

        Parameters:
            position(Position): The given specified position

        Returns(bool): True iff in the bound"""
        if (0 <= position.get_x() < self.get_size()
                and 1 <= position.get_y() < self.get_size()):
            return True
        return False

    def __repr__(self) -> str:
        """Return a representation of this Grid"""
        return f'Grid({self._size})'


class Game:
    """
    The Game handles the logic for controlling the actions
    of the entities within the grid.
    """

    def __init__(self, size: int) -> None:
        """
        A game is constructed with a size representing the dimensions
        of the playing grid.

        Parameters:
            size(int): the size of the game grid.
        """
        self._size = size
        self._flag = None  # True for won, False for lost
        self._num_collected = 0
        self._num_destroyed = 0
        self._total_shot = 0
        self._grid = Grid(self._size)

    def get_grid(self) -> Grid:
        """Return the instance of the grid held by the game"""
        return self._grid

    def get_player_position(self) -> Position:
        """
        Return the position of the player in the grid.
        (top row, centre column).
        This position should be constant.
        """
        return Position(GRID_SIZE // 2, 0)

    def get_num_collected(self) -> int:
        """Return the total of Collectables acquired."""
        return self._num_collected

    def get_num_destroyed(self) -> int:
        """Return the total of Destroyable removed with a shot."""
        return self._num_destroyed

    def get_total_shots(self) -> int:
        """Return the total of shots taken."""
        return self._total_shot

    def rotate_grid(self, direction: str) -> None:
        """
        Rotate the positions of the entities within the grid depending on
        the direction they are being rotated.

        Parameters:
            direction(str): The rotate direction.
        """
        after_rotated_entities = {}
        if direction == DIRECTIONS[0]:  # LEFT

            for pos, entity in self.get_grid().get_entities().items():
                # offset is (-1, 0)
                # ROTATIONS = ((-1, 0), (1, 0))
                new_pos = pos.add(Position(ROTATIONS[0][0], ROTATIONS[0][1]))
                if new_pos.get_x() < 0:  # out of LEFT bound
                    new_pos = new_pos.add(Position(GRID_SIZE, 0))
                after_rotated_entities[new_pos] = entity

            # clear the entities dict which contains entities before rotate
            self.get_grid().get_entities().clear()

        elif direction == DIRECTIONS[1]:  # RIGHT

            for pos, entity in self.get_grid().get_entities().items():
                # offset is (1, 0)
                # ROTATIONS = ((-1, 0), (1, 0))
                new_pos = pos.add(Position(ROTATIONS[1][0], ROTATIONS[1][1]))
                if new_pos.get_x() > GRID_SIZE - 1:  # out of RIGHT bound
                    new_pos = new_pos.subtract(Position(GRID_SIZE, 0))
                after_rotated_entities[new_pos] = entity

            # clear the entities dict which contains entities before rotate
            self.get_grid().get_entities().clear()

        # re-add entities with after rotate position
        for pos, entity in after_rotated_entities.items():
            self.get_grid().add_entity(pos, entity)

    def _create_entity(self, display: str) -> Entity:
        """
        Uses a display character to create an Entity.

        Parameters:
            display(str): The character of Entity to be created.
        Returns:
            (Entity): The entity on the game grid.
        """
        if display == PLAYER:
            return Player()
        elif display == COLLECTABLE:
            return Collectable()
        elif display == DESTROYABLE:
            return Destroyable()
        elif display == BLOCKER:
            return Blocker()
        # elif display == BOMB:
        # return Bomb()
        else:
            raise NotImplementedError

    def generate_entities(self) -> None:
        """
        Method given to the students to generate a random amount of entities to
        add into the game after each step
        """
        # Generate amount
        entity_count = random.randint(0, self.get_grid().get_size() - 3)
        entities = random.choices(ENTITY_TYPES, k=entity_count)

        # Blocker in a 1 in 4 chance
        blocker = random.randint(1, 4) % 4 == 0

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # bomb = False
        # if not blocker:
        #     bomb = random.randint(1, 4) % 4 == 0

        total_count = entity_count
        if blocker:
            total_count += 1
            entities.append(BLOCKER)

        # UNCOMMENT THIS FOR TASK 3 (CSSE7030)
        # if bomb:
        #     total_count += 1
        #     entities.append(BOMB)

        entity_index = random.sample(range(self.get_grid().get_size()),
                                     total_count)

        # Add entities into grid
        for pos, entity in zip(entity_index, entities):
            position = Position(pos, self.get_grid().get_size() - 1)
            new_entity = self._create_entity(entity)
            self.get_grid().add_entity(position, new_entity)

    def step(self) -> None:
        """Moves all entities on the board by an offset of (0, -1).
        Once entities have been moved, new entities are added to the grid.
        """
        after_step_entities = {}
        for pos, entity in self.get_grid().get_entities().items():
            new_pos = pos.add(Position(MOVE[0], MOVE[1]))
            # after step position is in bounds
            if self.get_grid().in_bounds(new_pos):
                after_step_entities[new_pos] = entity

        # clear the entities dict which contains entities before step
        self.get_grid().get_entities().clear()

        # re-add entities with after step position
        for pos, entity in after_step_entities.items():
            self.get_grid().add_entity(pos, entity)

        # generate a new row of entities
        self.generate_entities()

    def fire(self, shot_type: str) -> None:
        """
        Handles the firing/ collecting actions of a player towards
        an entity within the grid.
        A shot is fired from the players position and iteratively
        moves down the grid.

        Parameters:
            shot_type(str): refers to whether a collect or destroy shot
                has been fired.
        """
        closest_central_pos = Position(self.get_player_position().get_x(),
                                       self.get_grid().get_size())

        # find the closest to player entity in player column
        for pos in self.get_grid().get_entities():
            entity = self.get_grid().get_entities()[pos]
            if (pos.get_x() == self.get_player_position().get_x()
                    and pos < closest_central_pos
                    and entity.display() != BLOCKER):
                closest_central_pos = pos
        closest_entity = self.get_grid().get_entities().get(closest_central_pos)

        # shot_type is DESTROY
        if shot_type == SHOT_TYPES[0] and closest_entity is not None:
            # closest entity is Destroyable OR Collectable
            if closest_entity.display() in ENTITY_TYPES:
                self.get_grid().remove_entity(closest_central_pos)
                # closest entity is Destroyable
                if closest_entity.display() == DESTROYABLE:
                    self._num_destroyed += 1

        # shot_type is COLLECT
        elif shot_type == SHOT_TYPES[1] and closest_entity is not None:
            if closest_entity.display() == COLLECTABLE:
                self.get_grid().remove_entity(closest_central_pos)
                self._num_collected += 1

        self._total_shot += 1

    def has_won(self) -> bool:
        """Return Ture if the player has won the game."""
        if self._num_collected >= COLLECTION_TARGET:
            self._flag = True
            return True
        return False

    def has_lost(self) -> bool:
        """
        Return True if the game is lost.
        (i.e. a Destroyable has reached the top row).
        """
        for pos in self.get_grid().get_entities():
            entity = self.get_grid().get_entities()[pos]
            if pos.get_y() == 0 and entity.display() == DESTROYABLE:
                self._flag = False
                return True
        return False


class AbstractField(tk.Canvas):
    """An abstract view class which inherits from tk.Canvas
    and provides base functionality for other view class."""

    def __init__(self, master: tk.Tk, rows: int, cols: int,
                 width: int, height: int, **kwargs):
        """The AbstractField class is constructed from master canvas,
        number of rows and columns in the grid,
        width and height of the grid.

        Parameters:
            master: Window in which this canvas is to be drawn.
            rows(int): the number of rows in the grid.
            cols(int): the number of columns in the grid.
            width(int): width of the grid, measured in pixels.
            height(int): height of the grid, measured in pixel.
        """
        super().__init__(master, width=width, height=height, **kwargs)
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height

    def get_bbox(self, position: Position) -> Tuple[int, int, int, int]:
        """
        Return the bounding box for the position,
         i.e. tuple containing information about the pixel position of
         the edges of the shape, in the form(x_min, y_min, x_max, x_min)

         Parameters:
             position(Position): the position in grid.
        """
        x_min = position.get_x() * (self._width / GRID_SIZE)
        x_max = (position.get_x() + 1) * (self._width / GRID_SIZE)
        y_min = position.get_y() * (self._height / GRID_SIZE)
        y_max = (position.get_y() + 1) * (self._height / GRID_SIZE)
        return (x_min, y_min, x_max, y_max)

    def pixel_to_position(self, pixel: Tuple[int, int]) -> Position:
        """Convert the (x, y) pixel position to (row, column) position

        Parameters:
            pixel(Tuple[int, int]): The (x, y) graphics units position

        Returns:
            position(Position): The location in 2D grid."""
        x = pixel[0] // (self._width / GRID_SIZE)
        y = pixel[1] // (self._height / GRID_SIZE)
        return Position(x, y)

    def get_position_center(self, position: Position) -> Tuple[int, int]:
        """
        Get the graphics coordinate for the center of the cell
        at the given position.

        Parameters:
            position(Position): The location in 2D grid.

        Returns:
            (Tuple[int, int]): the pixel coordinates of the center of the cell.
        """
        x = (self.get_bbox(position)[0] + self.get_bbox(position)[2]) // 2
        y = (self.get_bbox(position)[1] + self.get_bbox(position)[3]) // 2
        return (x, y)

    def annotate_position(self, position: Position, text: str) -> None:
        """
        Annotate the center of the cell at the given Position
        with the provided text.

        Parameters:
            position(Position): The location in 2D grid.
            text(str): The text to annotate on the cell.
        """
        x, y = self.get_position_center(position)
        self.create_text(x, y, text=text)


class GameField(AbstractField):
    """A visual representation of the game grid."""

    def __init__(self, master: tk.Tk, size: int,
                 width: int, height: int, **kwargs):
        """
        Parameters:
            master: Window in which this canvas is to be drawn.
            size(int): The number of rows and columns of the grid.
            width(int): width of the grid, measured in pixels.
            height(int): height of the grid, measured in pixel.
        """
        super().__init__(master, size, size, width, height, **kwargs)
        self._size = size
        self._width = width
        self._height = height

    def draw_grid(self, entities: Dict[Position, Entity]) -> None:
        """
        Draws the entities (from Grid's entity dictionary) in the game grid
        at their given position using a coloured rectangle with
        superimposed identifying the entity.

        Parameters:
            entities(Dict[Position, Entity]): The dict that contain
                Position and Entity on the grid.
        """

        # create Player
        player_pos = Position(self._size // 2, 0)
        self.create_rectangle(self.get_bbox(player_pos),
                              fill=COLOURS[PLAYER])
        self.annotate_position(player_pos, PLAYER)

        # create other entity(Destroyable, Collectable, Blocker, Bomb)
        for pos, entity in entities.items():
            self.create_rectangle(self.get_bbox(pos),
                                  fill=COLOURS[entity.display()])
            self.annotate_position(pos, entity.display())

    def draw_player_area(self) -> None:
        """Draws the grey area a player is placed on."""

        self.create_rectangle(0,
                              0,
                              ((self._width - (self._width / self._size)) / 2),
                              self._height / self._size,
                              fill=PLAYER_AREA)
        self.create_rectangle(((self._width + (self._width / self._size)) / 2),
                              0,
                              self._width,
                              self._height / self._size,
                              fill=PLAYER_AREA)


class ScoreBar(AbstractField):
    """A visual representation of shot statistics from the player
    which inherits from AbstractField."""

    def __init__(self, master: tk.Tk, rows: int, **kwargs):
        """
        Parameters:
            master:Window in which this canvas is to be drawn.
            rows(int): The number of rows contained in the ScoreBar canvas.
        """
        super().__init__(master, rows, 2, SCORE_WIDTH, MAP_HEIGHT, **kwargs)
        self._rows = rows

    def draw_score_title(self) -> None:
        """Draw the labels of title in ScoreBar """
        self.create_text(SCORE_WIDTH / 2,
                         BAR_HEIGHT / 3,
                         text="Score",
                         font=('Arial', 22),
                         fill="white")

    def draw_score_subject(self) -> None:
        """Draw the text of subjects in ScoreBar"""

        # subject text
        self.create_text(SCORE_WIDTH / 4,
                         BAR_HEIGHT / 3 * 2,
                         text="Collected:",
                         fill="white")
        self.create_text(SCORE_WIDTH / 4,
                         BAR_HEIGHT,
                         text="Destroyed:",
                         fill="white")

    def draw_score_statistics(self, collect_num: int, destroy_num: int) -> None:
        """
        Draw the text of  statistics of collected and destroyed in the ScoreBar.

        Parameters:
            collect_num(int): The statistics of collected number.
            destroy_num(int): The statistics of destroyed number.
        """

        # collected number label
        self.create_text(SCORE_WIDTH / 4 * 3,
                         BAR_HEIGHT / 3 * 2,
                         text=collect_num,
                         fill="white")
        self.create_text(SCORE_WIDTH / 4 * 3,
                         BAR_HEIGHT,
                         text=destroy_num,
                         fill="white")


class HackerController:
    """The controller for the hacker game."""

    def __init__(self, master: tk.Tk, size: int):
        """

        Parameters:
            master:The master window of the hacker game
            size(int):  The number of rows (which is equal to column)
        """
        master.title("Hacker Game")
        self._master = master
        self._size = size
        self._game = Game(self._size)

        # HACKER title Label
        self._hacker_title = tk.Label(master,
                                      text=TITLE,
                                      bg=TITLE_BG,
                                      font=TITLE_FONT,
                                      fg="white")
        self._hacker_title.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # GameField Canvas
        self._game_field = GameField(master,
                                     self._size,
                                     MAP_WIDTH,
                                     MAP_HEIGHT,
                                     bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT, expand=True)

        # Draw Player and its area in GameField
        self._game_field.draw_player_area()
        self._game_field.draw_grid(self._game.get_grid().get_entities())

        # ScoreBar Canvas
        self._score_bar = ScoreBar(master, 2, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT, expand=True)

        # initial text in ScoreBar
        self._score_bar.draw_score_title()
        self._score_bar.draw_score_subject()
        self._score_bar.draw_score_statistics(0, 0)

        # apply step function per 2 seconds
        self._master.after(2000, self.step)

        # bind with keypress action
        self._master.bind('<KeyPress>', self.handle_keypress)

    def handle_keypress(self, event: tk.Event) -> None:
        """
        This method will be called when the user presses any key
        during the game.

        Parameters:
            event: Data about the event that has triggered this handle.
        """
        if event.keysym.upper() in DIRECTIONS:
            self.handle_rotate(event.keysym.upper())
        elif event.keysym.upper() in (COLLECT, DESTROY):
            self.handle_fire(event.keysym.upper())

    def draw(self, game: Game) -> None:
        """
        Clears and redraws the view based on the current game state.

        Parameters:
            game(Game): The current game model.
        """
        self._game_field.delete("all")
        self._game_field.draw_grid(game.get_grid().get_entities())
        # Draw Player area in GameField
        self._game_field.draw_player_area()

    def handle_rotate(self, direction: str) -> None:
        """
        Handles rotation of the entities and redrawing the game.

        Parameters:
            direction(str): The str that represents the rotate direction.
        """
        self._game.rotate_grid(direction)
        # redraw the game
        self.draw(self._game)

    def handle_fire(self, shot_type: str) -> None:
        """
        Handles thr firing of the specified shot type and redrawing the game.

        Parameters:
            shot_type(str): Refers to whether a collect or destroy shot
                            has been fired.
        """
        self._game.fire(shot_type)
        # redraw the game
        self.draw(self._game)
        # redraw the ScoreBar
        self._score_bar.delete("all")
        self._score_bar.draw_score_title()
        self._score_bar.draw_score_subject()
        self._score_bar.draw_score_statistics(self._game.get_num_collected(),
                                              self._game.get_num_destroyed())

    def step(self) -> None:
        """The step method is called every 2 seconds"""
        self._game.step()
        # redraw the game
        self.draw(self._game)
        # repeat step every 2 seconds
        self._master.after(2000, self.step)


class ImageGameField(AbstractField):
    """A visual representation with images of the game"""

    def __init__(self, master: tk.Tk, size: int,
                 width: int, height: int, **kwargs):
        """
        Parameters:
            master: Window in which canvas is to be drawn.
            size(int): The number of rows and columns of the grid.
            width(int): width of the grid, measured in pixels.
            height(int): height of the grid, measured in pixels.
        """
        super().__init__(master, size, size, width, height, **kwargs)
        self._size = size
        self._width = width
        self._height = height
        self._player_img = tk.PhotoImage(file="images/P.png")
        self._blocker_img = tk.PhotoImage(file="images/B.png")
        self._collectable_img = tk.PhotoImage(file="images/C.png")
        self._destroyable_img = tk.PhotoImage(file="images/D.png")
        self._bomb_img = tk.PhotoImage(file="images/O.png")

    def draw_grid(self, entities: Dict[Position, Entity]) -> None:
        """
        Draws the entities (from Grid's entity dictionary) in the game grid
        at their given position using a coloured rectangle with
        superimposed identifying the entity.

        Parameters:
            entities(Dict[Position, Entity]): The dict that contain
                Position and Entity on the grid.
        """

        # create Player
        player_pos = Position(self._size // 2, 0)
        self.create_image(self.get_position_center(player_pos),
                          image=self._player_img,
                          anchor=tk.CENTER)

        # create other entities(Destroyable, Collectable, Blocker, Bomb)
        for pos, entity in entities.items():
            if entity.display() == COLLECTABLE:
                entity_img = self._collectable_img
            elif entity.display() == DESTROYABLE:
                entity_img = self._destroyable_img
            elif entity.display() == BLOCKER:
                entity_img = self._blocker_img
            elif entity.display() == BOMB:
                entity_img = self._bomb_img
            self.create_image(self.get_position_center(pos),
                              image=entity_img,
                              anchor=tk.CENTER)

    def draw_player_area(self) -> None:
        """Draws the gray area a player is placed on."""
        self.create_rectangle(0,
                              0,
                              self._width,
                              self._height / self._size,
                              fill=PLAYER_AREA)


class StatusBar(tk.Frame):
    """A frame for StatusBar."""

    def __init__(self, master: tk.Tk, **kwargs):
        """
        Parameters:
            master: Window in which this frame is to be drawn.
        """
        super().__init__(master, **kwargs)
        self._master = master
        self._status_bar_frame = tk.Frame(self._master)
        self._status_bar_frame.pack(side=tk.BOTTOM)

    def draw_shot_frame(self) -> None:
        """Create the shot frame"""
        # Total Shots
        self._shot_frame = tk.Frame(self._status_bar_frame)
        self._shot_frame.pack(side=tk.LEFT)
        # Labels in Total Shots
        self._total_shot_text = tk.Label(self._shot_frame,
                                         text="Total Shots", )
        self._total_shot_text.pack(side=tk.TOP, expand=True)

    def draw_timer_frame(self) -> None:
        """Create the timer frame"""
        # Timer
        self._timer_frame = tk.Frame(self._status_bar_frame)
        self._timer_frame.pack(side=tk.LEFT)
        # Label in Timer
        self._timer = tk.Label(self._timer_frame,
                               text="Timer")
        self._timer.pack(side=tk.TOP, expand=True)

    def draw_pause(self) -> None:
        """Create the pause button"""
        # Pause button
        self._pause_button = tk.Button(self._status_bar_frame,
                                       text="Pause",
                                       command=self.pause)
        self._pause_button.pack(side=tk.LEFT)

    def pause(self) -> None:
        """Function on Pause Button"""
        pass

    def draw_shots(self, shots: int) -> None:
        """
        draw shots statistics in shots frame as a label.

        Parameters:
            shots(int): The number of total shots.
        """
        self.shot_num = tk.Label(self._shot_frame,
                                 text=shots)
        self.shot_num.pack(tk.TOP, expand=True)

    def draw_timer(self, min: int, sec: int) -> None:
        """
        Draw the timer label in timer frame.

        Parameters:
            min(int): The statistics of timer in minutes.
            sec(int): The statistics of timer in seconds.
        """
        self.timer_stat = tk.Label(self._timer_frame,
                                   text=f'{min}m{sec}s')
        self.timer_stat.pack(tk.TOP, expand=True)


class AdvancedHackerController:
    """The controller for hacker game task2."""

    def __init__(self, master: tk.Tk, size: int):
        """
        Parameters:
            master: The root window of the hacker game.
            size(int): The number of rows and columns of the game.
        """

        master.title("Hacker Task2")
        self._master = master
        self._size = size
        self._game = Game(self._size)

        # File Menu
        self._menu = tk.Menu(self._master)
        self._master.config(menu=self._menu)
        # sub-menu
        self._file_menu = tk.Menu(self._menu)
        self._menu.add_cascade(label="File", menu=self._file_menu)
        # cascade detail menu
        self._file_menu.add_command(label="New game", command=self.new_game)
        self._file_menu.add_command(label="Save game", command=self.save_game)
        self._file_menu.add_command(label="Load game", command=self.load_game)
        self._file_menu.add_command(label="Quit", command=self.quit_game)

        # HACKER title Label
        self._hacker_title = tk.Label(self._master,
                                      text=TITLE,
                                      bg=TITLE_BG,
                                      font=TITLE_FONT,
                                      fg="white")
        self._hacker_title.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Game Frame (gamefield + scorebar)
        self._game_frame = tk.Frame(self._master)
        self._game_frame.pack(side=tk.TOP)

        # GameField Canvas
        self._game_field = ImageGameField(self._game_frame,
                                          self._size,
                                          MAP_WIDTH,
                                          MAP_HEIGHT,
                                          bg=FIELD_COLOUR)
        self._game_field.pack(side=tk.LEFT, expand=True)

        # Draw Player and its area in GameField
        self._game_field.draw_player_area()
        self._game_field.draw_grid(self._game.get_grid().get_entities())

        # ScoreBar Canvas
        self._score_bar = ScoreBar(self._game_frame, 2, bg=SCORE_COLOUR)
        self._score_bar.pack(side=tk.LEFT, expand=True)

        # initial text in ScoreBar
        self._score_bar.draw_score_title()
        self._score_bar.draw_score_subject()
        self._score_bar.draw_score_statistics(0, 0)

        # Status Frame
        self._status_frame = tk.Frame(self._master)
        self._status_frame.pack(side=tk.TOP)

        # Status Bar
        self._status_bar = StatusBar(self._status_frame)
        self._status_bar.draw_shot_frame()
        self._status_bar.draw_timer_frame()
        self._status_bar.draw_pause()

        # apple step function per 2 seconds
        self._master.after(2000, self.step)

        # bind with keypress action
        self._master.bind('<KeyPress>', self.handle_keypress)

    def handle_keypress(self, event: tk.Event) -> None:
        """
        This method will be called when the user presses any key
        during the game.

        Parameters:
            event: Data about the event that has triggered this handle.
        """
        if event.keysym.upper() in DIRECTIONS:
            self.handle_rotate(event.keysym.upper())
        elif event.keysym.upper() in (COLLECT, DESTROY):
            self.handle_fire(event.keysym.upper())

    def draw(self, game: Game) -> None:
        """
        Clears and redraws the view based on the current game state.

        Parameters:
            game(Game): The current game model.
        """
        self._game_field.delete("all")
        self._game_field.draw_grid(game.get_grid().get_entities())

        # Draw Player and its area in GameField
        self._game_field.draw_player_area()
        self._game_field.draw_grid(self._game.get_grid().get_entities())

    def handle_rotate(self, direction: str) -> None:
        """
        Handles rotation of the entities and redrawing the game.

        Parameters:
            direction(str): The str that represents the rotate direction.
        """
        self._game.rotate_grid(direction)
        # redraw the game
        self.draw(self._game)

    def handle_fire(self, shot_type: str) -> None:
        """
        Handles thr firing of the specified shot type and redrawing the game.

        Parameters:
            shot_type(str): Refers to whether a collect or destroy shot
                            has been fired.
        """
        self._game.fire(shot_type)
        # redraw the game
        self.draw(self._game)
        # redraw the ScoreBar
        self._score_bar.delete("all")
        self._score_bar.draw_score_title()
        self._score_bar.draw_score_subject()
        self._score_bar.draw_score_statistics(self._game.get_num_collected(),
                                              self._game.get_num_destroyed())

    def step(self) -> None:
        """The step method is called every 2 seconds"""
        self._game.step()
        # redraw the game
        self.draw(self._game)
        # repeat step every 2 seconds
        self._master.after(2000, self.step)



    def new_game(self):
        pass

    def save_game(self):
        pass

    def load_game(self):
        pass

    def quit_game(self):
        pass


def start_game(root, TASK=TASK):
    controller = HackerController

    if TASK != 1:
        controller = AdvancedHackerController

    app = controller(root, GRID_SIZE)
    return app


def main():
    root = tk.Tk()
    root.title(TITLE)
    app = start_game(root)
    root.mainloop()


if __name__ == '__main__':
    main()
