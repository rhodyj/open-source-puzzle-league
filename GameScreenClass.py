import pygame

import GameClass


class GameScreen:
    
    def __init__(self, filearray):
        
        f = open(filearray[0], "r")
        for x in f:
            splitline = x.split(" ")
            if splitline[0] == "cell_dimension": #size of square cells (in pixels)
                self.cell_dimension = int(splitline[1])
            elif splitline[0] == "cells_per_row": #how many cells per row?
                self.cells_per_row = int(splitline[1])
            elif splitline[0] == "cells_per_column": #how many cells per column?
                self.cells_per_column = int(splitline[1])
            elif splitline[0] == "cell_between": #space between cells (in pixels)
                self.cell_between = int(splitline[1])
            elif splitline[0] == "border_dimension": #size of border tiles (in pixels)
                self.border_dimension = int(splitline[1])
            elif splitline[0] == "combo_fade_time": #how many ticks does it take for a combo'd cell to be erased
                self.combo_fade_time = int(splitline[1])
            elif splitline[0] == "cell_drop_speed": #how fast to cell drop?
                self.cell_drop_speed = int(splitline[1])
            elif splitline[0] == "cell_swap_speed": #how fast to cells swap?
                self.cell_swap_speed = int(splitline[1])
        
        
        self.numplay = len(filearray[1]) #number of players
        self.games = [] #stores the actual game objects
        self.gameover = [] #which players have had a game over?
        self.timer = 0
        self.border_tile = pygame.image.load("Blocks/brick.png")

        for i in range(self.numplay): #each player gets their own instance of the game
            g = GameClass.Game(filearray[1][i], i, self.cell_dimension, self.cells_per_row, self.cells_per_column, self.cell_between, self.combo_fade_time, self.cell_drop_speed, self.cell_swap_speed) #pass a lot of data
            self.gameover.append(False) #the ith player has not had a game over yet
            self.games.append(g) #add the newly made game to the list of active games
            
        self.base_width = self.cells_per_row*(self.cell_dimension + self.cell_between) + self.cell_between #width of board
        self.base_height = self.cells_per_column*(self.cell_dimension + self.cell_between) + self.cell_dimension #height of board
        
        self.actual_width = (1+2*self.numplay)*self.base_width #actual width of game screen
        self.actual_height = self.base_height #actual height of game screen
        
        self.window_size = [self.actual_width, self.actual_height]
        
        self.gamescreen = pygame.display.set_mode(self.window_size)
        
        pygame.display.set_caption("Open Source Puzzle League")
        
        self.gameclock = pygame.time.Clock()


        
    def draw_border(self):
        for x in range(self.actual_width // self.border_dimension+ 1): #How many border tiles to draw horizontally?
            for y in range(self.actual_height // self.border_dimension + 1): #How many border tiles to draw vertically??
                if x == 0 or y == 0 or x == self.actual_width // 48 or y == self.actual_height // 48: #draw only at the border
                    self.gamescreen.blit(self.border_tile, (self.border_dimension*x, self.border_dimension*y)) #put the tiles on the screen

    def draw_screen(self):
        self.gamescreen.fill((0, 0, 0))
        # Draw the grid
        for p in range(len(self.games)):
            self.games[p].draw_board(self.gamescreen, self.timer)
            
        self.draw_border()

    def play(self):
        
        #Handle Time
        self.timer = self.timer % 60 #reset every 60 ticks
        self.timer += 1 #increment timer
        
        for i in range(len(self.games)):
            game = self.games[i]
            isgameover = self.gameover[i]
            if isgameover == False:
                if game.playertype == "player": 
                    if game.button_logic(pygame.event.get()) == -1: #handle player input; calls the function and stops if there's an error
                        return True
                    self.gameover[i] = game.gameloop(self.timer) #has the player lost?
                elif game.playertype == "ai":
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
                
                
                