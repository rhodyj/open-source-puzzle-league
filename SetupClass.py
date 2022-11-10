import pygame

class Setup:
    
    def __init__(self, displayinfo, difficultyinfo): #store constants
    # Define some colors
        self.WHITE = (255, 255, 255)
        self.GREY = (123, 123, 123)
        self.BLACK= (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (255, 0, 255)

    # Load the cell images  
        self.cell_type_array = ["Blocks/block1.png", "Blocks/block2.png", "Blocks/block3.png", "Blocks/block4.png", "Blocks/block5.png"]

        for fn in range(len(self.cell_type_array)):
            self.cell_type_array[fn] = pygame.image.load(self.cell_type_array[fn])        

    # Load the explosion animation    
        self.explode_array = ["Blocks/explode0.png", "Blocks/explode1.png", "Blocks/explode2.png", "Blocks/explode3.png", "Blocks/explode4.png"]
        for fn in range(len(self.explode_array)):
            self.explode_array[fn] = pygame.image.load(self.explode_array[fn])

    # Load the sound effects        
        self.action_sounds = ["SFX/sfx_exp_shortest_hard5.wav", "SFX/sfx_exp_shortest_soft7.wav"]
        for sfx in range(len(self.action_sounds)):
            self.action_sounds[sfx] = pygame.mixer.Sound(self.action_sounds[sfx])
    
    # Read information from the input dictionaries
        self.cell_dimension = displayinfo["cell_dimension"] #how many pixels is the (square) cell
        self.cells_per_row = displayinfo["cells_per_row"] #how many cells in each row
        self.cells_per_column = displayinfo["cells_per_column"] #how many cells in each column
        self.cell_between = displayinfo["cell_between"] #how many pixels between each cell
 
        self.display_width = self.cells_per_row*(self.cell_dimension + self.cell_between) + self.cell_between #width of window
        self.display_height = self.cells_per_column*(self.cell_dimension + self.cell_between) + self.cell_dimension #height of window
     
        self.cell_drop_speed = displayinfo["cell_drop_speed"]
        self.cell_swap_speed = displayinfo["cell_swap_speed"]
        self.combo_fade_time = displayinfo["combo_fade_time"]
        
        self.initial_height_offset = difficultyinfo["initial_height_offset"] #how many blocks does the 
        self.board_raise_rate = difficultyinfo["board_raise_rate"] #how fast does the board raise?

        self.grace_period_full = difficultyinfo["grace_period"] #how long can the board stay "topped out" before the game results in game over? Think of a bar that lowers when any column is full

        # Set up the font
        self.fontsize = self.cell_dimension
        self.font = pygame.font.SysFont('Consolas', self.fontsize, True, False)