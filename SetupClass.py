import pygame

class Setup:
    
    def __init__(self, cd, cpr, cpc, cb, cds, css, cft, brr, iho, gp): #store constants
    # Define some colors
        self.WHITE = (255, 255, 255)
        self.GREY = (123, 123, 123)
        self.BLACK= (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.PURPLE = (255, 0, 255)
    
        self.fontsize = 20
        self.font = pygame.font.SysFont('Consolas', self.fontsize, True, False)
        
        self.cell_type_array = ["Blocks/block1.png", "Blocks/block2.png", "Blocks/block3.png", "Blocks/block4.png", "Blocks/block5.png"]
        for fn in range(len(self.cell_type_array)):
            self.cell_type_array[fn] = pygame.image.load(self.cell_type_array[fn])        
        
        self.explode_array = ["Blocks/explode0.png", "Blocks/explode1.png", "Blocks/explode2.png", "Blocks/explode3.png", "Blocks/explode4.png"]
        for fn in range(len(self.explode_array)):
            self.explode_array[fn] = pygame.image.load(self.explode_array[fn])
            
        self.action_sounds = ["SFX/sfx_exp_shortest_hard5.wav", "SFX/sfx_exp_shortest_soft7.wav"]
        for sfx in range(len(self.action_sounds)):
            self.action_sounds[sfx] = pygame.mixer.Sound(self.action_sounds[sfx])
    
        self.cell_dimension = cd
        self.cells_per_row = cpr
        self.cells_per_column = cpc
        self.cell_between = cb
 
        self.display_width = self.cells_per_row*(self.cell_dimension + self.cell_between) + self.cell_between #width of window
        self.display_height = self.cells_per_column*(self.cell_dimension + self.cell_between) + self.cell_dimension #height of window
     
        self.cell_swap_speed = css
        self.cell_drop_speed = cds
        self.combo_fade_time = cft
        
        self.initial_height_offset = iho
        self.board_raise_rate = brr

        self.grace_period_counter = gp