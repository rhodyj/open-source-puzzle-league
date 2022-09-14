import pygame

import GameClass

configparamlist = [
    "cell_dimension", #size of square cells (in pixels)
    "cells_per_row", #how many cells per row?
    "cells_per_column", #how many cells per column?
    "cell_bewteen", #space between cells (in pixels)
    "border_dimension", #size of square border tiles (in pixels)
    "combo_fade_time", #how many ticks does it take for a combo'd cell to be erased
    "cell_drop_speed", #how fast to cell drop?
    "cell_swap_speed" #how fast to cells swap?
]

class GameScreen:
    
    def __init__(self, filearray): #filearray is structured as ["config.txt", ["player1_diff_config.txt", "player2_diff_config.txt", ... , ]]
 
        f = open(filearray[0], "r")

        self.config_info = {} #package some data into a dict to pass on
        for x in f:
            splitline = x.split(" ")
            self.config_info[splitline[0]] = int(splitline[1])
            #TO-DO: Throw exception if not everything in configparamlist is filled in properly

        f.close()
        
        self.numplay = len(filearray[1]) #the length of the second list in filearray is the number of players
        self.games = [] #stores the actual game objects
        self.gameover = [] #which players have had a game over?
        self.timer = 0
        self.border_tile = pygame.image.load("Blocks/brick.png")

        for i in range(self.numplay): #each player gets their own instance of the game
            g = GameClass.Game(filearray[1][i], i, self.config_info) #pass a lot of data
            self.gameover.append(False) #the i-th player has not had a game over yet
            self.games.append(g) #add the newly made game to the list of active games

    # Values from the dictionary that are useful to have immediately
        self.cells_per_row = self.config_info["cells_per_row"]
        self.cells_per_column = self.config_info["cells_per_column"]
        self.cell_dimension = self.config_info["cell_dimension"]
        self.cell_between = self.config_info["cell_between"]
        self.border_dimension = self.config_info["border_dimension"]

    # Calculate dimension of player screens and total dimension of game screen
        self.base_width = self.cells_per_row*(self.cell_dimension + self.cell_between) + self.cell_between #width of board
        self.base_height = self.cells_per_column*(self.cell_dimension + self.cell_between) + self.cell_dimension #height of board
        
        self.actual_width = (1+2*self.numplay)*self.base_width #actual width of game screen
        self.actual_height = self.base_height #actual height of game screen
        self.window_size = [self.actual_width, self.actual_height]
        
    # Draw the board
        self.gamescreen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Open Source Puzzle League")
        
    # Initialize the timer
        self.gameclock = pygame.time.Clock()


        
    def draw_border(self):
        for x in range(self.actual_width // self.border_dimension + 1): #How many border tiles to draw horizontally, rounded up
            for y in range(self.actual_height // self.border_dimension + 1): #How many border tiles to draw vertically, rounded up
                if x == 0 or y == 0 or x == self.actual_width // self.border_dimension or y == self.actual_height // self.border_dimension: #draw only at the border
                    self.gamescreen.blit(self.border_tile, (self.border_dimension*x, self.border_dimension*y)) #put the tiles on the screen

    def draw_screen(self):
    # Add background fill
        self.gamescreen.fill((0, 0, 0))

    # Draw each player's board
        for p in range(len(self.games)):
            self.games[p].draw_board(self.gamescreen, self.timer)

    # Draw the border    
        self.draw_border()

    def play(self):
        
        # Handle Time
        self.timer = self.timer % 60 #reset every 60 ticks
        self.timer += 1 #increment timer
        
        for i in range(len(self.games)):

            # Get the corresponding game and whether or not that game has finished
            game = self.games[i]
            isgameover = self.gameover[i]

            if isgameover == False:
                if game.player_type == 0: #if the player is a human 
                    if game.button_logic(pygame.event.get()) == -1: #handle player input; calls the function and stops if there's an error
                        return True
                    self.gameover[i] = game.gameloop(self.timer) #has the player lost?
                elif game.player_type == 1: #if the player is an ai
                    if game.ai_logic(pygame.event.get(), self.timer) == -1: #handle AI input; calls the function and stops if there's an error
                        return True
                    self.gameover[i] = game.gameloop(self.timer) #has the AI lost?
            else:
                if game.quit_check(pygame.event.get()) == -1:
                    return True
        
        # Set the screen background
        self.draw_screen()
                
        # Limit to 60 frames per second
        self.gameclock.tick(60)
           
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
        
        return False
                
                
                