import pygame

import CursorClass
import SetupClass
import GridClass
import BufferClass
import ScoreboardClass

import VirtualGameClass

import ComboClass

difficultyparamlist = [
    "player_type", #player name
    "board_raise_rate", #default speed or screen rise
    "cursor_starting_x", #default cursor x position
    "cursor_starting_y", #default cursor y position
    "initial_height_offset", #how many blocks from the top will not spawn?
    "grace_period" #how long can the board be full before the game ends?
    ]

class Game:
    
    def __init__(self, playerinfo, playernumber, display_info):
    # Collect info about the difficulty, such as the raise at which the board raises   

        f = open(playerinfo, "r")

        self.difficulty_info = {}
        for x in f:
            splitline = x.split(" ")
            self.difficulty_info[splitline[0]] = int(splitline[1])    
        f.close()

        #make sure all the necessary parameters were loaded from the file
        allkeys = self.difficulty_info.keys()
        missingkeys = []
        for key in difficultyparamlist:
            if key not in allkeys:
                missingkeys.append(key)

        #if any parameter is missing, end the program and report the error
        assert len(missingkeys) == 0, f"Missing difficult info: {missingkeys}"

    # Store the info
        self.player_number = playernumber #the number of the player, zero-indexed: Player 0, Player 1, Player 2, etc.
        self.player_type = self.difficulty_info["player_type"] #0 is human, 1 is ai

    # Make some useful objects
        self.setup = SetupClass.Setup(display_info, self.difficulty_info)
        self.grid = GridClass.Grid(self.setup)
        self.buffer = BufferClass.Buffer(self.setup)
        self.cursor = CursorClass.Cursor(self.difficulty_info["cursor_starting_x"], self.difficulty_info["cursor_starting_y"])
        self.gcq = set()
        self.combodata = []
        self.activecombo = 1
        self.scoreboard = ScoreboardClass.Scoreboard()
        self.graceperiod = self.difficulty_info["grace_period"]
        
        """
        self.vgame = VirtualGameClass.VirtualGame(self.setup, self.cursor, self.player_number) #used 
        if self.playertype == 1:
            self.vgame.v_copy_grid(self.grid)
        """    

    #swap_debuf_check is CURRENTLY UNUSED but may find use later
    def swap_debug_check(self, cellcoords): #debug statement to be called when trying to swap two cells. Gives descriptive error messages.
        x = cellcoords[0]
        y = cellcoords[1]
        assert self.grid.get_curr_fade(x, y) == 0, f"Cell at {cellcoords} is trying to swap while fading/being deleted"
        assert self.grid.get_drop_offset(x, y) == 0, f"Cell at {cellcoords} is trying to swap while falling"
        assert self.grid.get_swap_offset(x, y) == 0, f"Cell at {cellcoords} is trying to swap while already swapping"
        assert self.grid.get_type(x,y) == "block" or self.grid.get_type(x,y) == "empty", f"Cell at {cellcoords} is an invalid type: {self.grid.get_type(x,y)}"

    #when two cells have finished moving past each other visually, swap their values
    def swap_blocks(self, b1, b2): #input is two tuples representing the coordinates of the two cells to be swapped

        #take the coordinates from the tuples; mainly for code readability
        x1 = b1[0]
        y1 = b1[1]

        x2 = b2[0]
        y2 = b2[1]

        #swap the colors and the types of the cells
        # Other parts of the program should ensure that, when this process is called, the cells have the same drop/swap offset and combo timer (which should all be 0)
        foo1 = self.grid.get_color(x1, y1)
        foo2 = self.grid.get_color(x2, y2)
        self.grid.set_color(x1, y1, foo2) #make cell 1 the color of cell 2
        self.grid.set_color(x2, y2, foo1) #make cell 2 the old color of cell 1
        
        foo1 = self.grid.get_type(x1, y1)
        foo2 = self.grid.get_type(x2, y2)
        self.grid.set_type(x1, y1, foo2) #make cell 1 the type of cell 2
        self.grid.set_type(x2, y2, foo1) #make cell 2 the old type of cell 1
        
    def raise_board(self):
        fooflag = False #is there a cell in the very top row? Should we start counting down until game over/board full/"top out"?
        boff = self.grid.get_board_offset() #boff stands for "board offset"
        
        if self.graceperiod == self.setup.grace_period_full: #if the grace period "health bar" is "full" (see SetupClass.py), we can raise the board
            
            #move the board up one pixel
            boff = (boff + 1) % self.setup.cell_dimension
            self.grid.set_board_offset(boff)
            
            #if the board was raised enough to add a new row
            if boff == 0:

                #Move every cell up one position
                for column in range(self.setup.cells_per_row):

                    #for every row except the bottom row, copy the data from the cell below it
                    for row in range(self.setup.cells_per_column-1):
                        self.grid.set_color(column, row, self.grid.get_color(column, row+1))
                        self.grid.set_swap_offset(column, row, self.grid.get_swap_offset(column, row+1))
                        self.grid.set_drop_offset(column, row, self.grid.get_drop_offset(column, row+1))
                        self.grid.set_curr_fade(column, row, self.grid.get_curr_fade(column, row+1))
                        self.grid.set_type(column, row, self.grid.get_type(column, row+1))

                    #since the border is below the bottom row, we instead copy the buffer data to the bottom row
                    #the buffer hasn't been touched before, so all offsets/timers are 0
                    self.grid.set_color(column, self.setup.cells_per_column-1, self.buffer.get_color(column))
                    self.grid.set_swap_offset(column, self.setup.cells_per_column-1, 0) 
                    self.grid.set_drop_offset(column, self.setup.cells_per_column-1, 0)
                    self.grid.set_curr_fade(column, self.setup.cells_per_column-1, 0)
                    self.grid.set_type(column, self.setup.cells_per_column-1, "block")
                
                #move the cursor's position up one, so that it remains on the blocks it was on previously
                if self.cursor.y > 1:
                    self.cursor.y -= 1

                #Once all blocks have been moved up, refill the buffer
                self.buffer.spawn_blocks(self.setup)
                
                '''
                if self.playertype == 1:
                    self.vgame.v_copy_grid(self.grid)
                    self.vgame.reset_goals()
                '''
        #check if any cell in the top row is not empty (i.e. if any column is touching the top of the board)
        for column in range(self.setup.cells_per_row):
            if self.grid.get_type(column, 0) != "empty":
                fooflag = True

        if fooflag: #if the board is too full
            self.graceperiod -= 1 #start counting down until GAME OVER
        else: #but if the top row is clear now
            self.graceperiod = self.setup.grace_period_full #reset the GAME OVER countdown. This would "refill the health bar"
        

    #TO-DO: Continue from here.


    def clean(self, combolist):
        
        tmpcombo = ComboClass.Combo()
        
        for c0 in combolist.copy(): #for each combo in the list of combos
            isbad = False
            for c1 in self.gcq:
                if len(c0.locations & c1.locations) > 0:
                    isbad = True
            for loc in c0.locations:
                if self.grid.can_drop(loc[0], loc[1]):
                    isbad = True
            if c0.numblocks < 3 or c0.color == -1 or isbad:
                combolist.remove(c0) #remove small, "black/white", or redundant combos
    
        tx = True
        while tx:
            tx = False #is there a TX Combo?
            for c1 in combolist.copy():
                for c2 in combolist.copy():
                    if c1 != c2 and len(c1.locations) > 2 and len(c2.locations) > 2:
                        
                        txcombo = ComboClass.Combo()
                        txcombo.colors = c1.colors | c2.colors
                        txcombo.locations = c1.locations | c2.locations
                        txcombo.numblocks = len(txcombo.locations)
                        
                        if txcombo.numblocks < c1.numblocks + c2.numblocks:
                            tx = True
                            if c1 in combolist:
                                combolist.remove(c1)
                            if c2 in combolist:
                                combolist.remove(c2)
                            combolist.add(txcombo)
                            tmpcombo.numTX += 1
    
        for c0 in combolist.copy():
            tmpcombo.numblocks += c0.numblocks
            for loc in c0.locations:
                tmpcombo.colors.add(self.grid.get_color(loc[0], loc[1]))
                tmpcombo.locations.add((loc[0], loc[1], self.grid.get_color(loc[0], loc[1])))
        
        for c0 in combolist.copy(): #check if the combo is a chain
            for loc in c0.locations:
                if self.grid.get_just_dropped(loc[0], loc[1]):
                    tmpcombo.ischain = True
                    
        return tmpcombo

    def combo_check(self):
        self.swap_blocks((self.cursor.x, self.cursor.y), (self.cursor.x+1, self.cursor.y))
        foo = self.find_matches()
        
        color1 = self.grid.get_color(self.cursor.x, self.cursor.y)
        color2 = self.grid.get_color(self.cursor.x+1, self.cursor.y)
        if (self.cursor.x, self.cursor.y, color1) in foo.locations or (self.cursor.x+1, self.cursor.y, color2) in foo.locations:
            self.swap_blocks((self.cursor.x, self.cursor.y), (self.cursor.x+1, self.cursor.y))
            return True
        else:
            self.swap_blocks((self.cursor.x, self.cursor.y), (self.cursor.x+1, self.cursor.y))
            return False
        
        
    def find_matches(self):
        
        comboqueue = set()
        
        #Check for Vertical Combos
        for column in range(self.setup.cells_per_row):
            contiguous_blocks_matched = 0
            tmpcombo0 = ComboClass.Combo()
            current_color = self.grid.get_color(column,0)
            
            for row in range(self.setup.cells_per_column):
                if current_color == self.grid.get_color(column, row):
                    contiguous_blocks_matched += 1
                else: #or if the next block is a different color
                    tmpcombo0.numblocks = contiguous_blocks_matched
                    for i in range(contiguous_blocks_matched):
                        tmpcombo0.locations.add((column, row-i-1, current_color))
                    tmpcombo0.color = current_color
                    comboqueue.add(tmpcombo0)
                        
                    current_color = self.grid.get_color(column,row)
                    contiguous_blocks_matched = 1
                    tmpcombo0 = ComboClass.Combo()
                            
            tmpcombo0.numblocks = contiguous_blocks_matched
            for i in range(contiguous_blocks_matched):
                tmpcombo0.locations.add((column, row - i, self.grid.get_color(column, row)))
            tmpcombo0.color = self.grid.get_color(column, row)
            comboqueue.add(tmpcombo0)
            
        #Check for Horizontal Combos    
        for row in range(self.setup.cells_per_column):
            contiguous_blocks_matched = 0
            tmpcombo0 = ComboClass.Combo()
            current_color = self.grid.get_color(0, row)
            
            for column in range(self.setup.cells_per_row):
                if current_color == self.grid.get_color(column, row):
                    contiguous_blocks_matched += 1
                else: #or if the next block is a different color
                    tmpcombo0.numblocks = contiguous_blocks_matched
                    for i in range(contiguous_blocks_matched):
                        tmpcombo0.locations.add((column-i-1, row, current_color))
                    tmpcombo0.color = current_color
                    comboqueue.add(tmpcombo0)
                        
                    current_color = self.grid.get_color(column,row)
                    contiguous_blocks_matched = 1
                    tmpcombo0 = ComboClass.Combo()
                            
            tmpcombo0.numblocks = contiguous_blocks_matched
            for i in range(contiguous_blocks_matched):
                tmpcombo0.locations.add((column-i, row, self.grid.get_color(column, row)))
            tmpcombo0.color = self.grid.get_color(column, row)
            comboqueue.add(tmpcombo0)
    
    
        newbigcombo = self.clean(comboqueue)
        
        return newbigcombo
    
    def move_blocks(self):
        for column in range(self.setup.cells_per_row):
            for row in range(self.setup.cells_per_column):
                if self.grid.get_swap_offset(column, row) > 0:
                    self.grid.set_swap_offset(column, row, self.grid.get_swap_offset(column, row) + self.setup.cell_swap_speed)
                elif self.grid.get_swap_offset(column, row) < 0:
                    self.grid.set_swap_offset(column, row, self.grid.get_swap_offset(column, row) - self.setup.cell_swap_speed)
                if self.grid.get_swap_offset(column, row) > self.setup.cell_dimension:
                    self.swap_blocks((column, row), (column+1, row))
                    self.grid.set_swap_offset(column, row, 0)
                    
                elif self.grid.get_swap_offset(column, row) < -1*self.setup.cell_dimension:
                    self.grid.set_swap_offset(column, row, 0)
                        

                
                        

    def pop_combos(self, combo):
        pop = False        
        for row in range(0, self.setup.cells_per_column,1):
            for column in range(self.setup.cells_per_row):
                #if column in combo.locations[0] and row in combo.locations[1]:
                if (column, row, self.grid.get_color(column, row)) in combo.locations:
                    if self.grid.get_curr_fade(column, row) == 0 and self.grid.get_type(column, row) != "grey":
                        self.grid.set_curr_fade(column, row, 1) #mark all combos to be popped
                        self.grid.set_type(column, row, "grey")
                        #print("Marking for deletion: " + str((column, row))) 
                    
                    if self.grid.get_curr_fade(column, row) < self.setup.combo_fade_time and pop == False:
        
                        if self.grid.get_curr_fade(column, row) == 1:
                            pygame.mixer.Sound.play(self.setup.action_sounds[0])#PLAY EXPLOSION SOUND
        
                        self.grid.set_curr_fade(column, row, self.grid.get_curr_fade(column, row) + 1)
                            #print("Fully deleted: " + str((column, row)))
        
                            #print(str(self.grid.get_curr_fade(column, row)) + " tics left for " + str((column, row)))
                        pop = True
                
    def combo_blocks(self):
        
        newcombos = self.find_matches()
        
        
        
        if newcombos.numblocks > 0:
            
            #print(newcombos.locations)
            self.gcq.add(newcombos)
              
            if newcombos.ischain:    
                self.activecombo = self.activecombo+1
                print("Combo x" + str(self.activecombo))
                self.combodata.append(newcombos)
            else:
                if self.activecombo > 1:
                    print("Combo Dropped due to Asynch")
                self.activecombo = 1
                self.combodata = [newcombos]

            '''
            if self.player_type == 1:
                self.vgame.v_copy_gcq(self.gcq)
            '''

        if not self.grid.has_falling_blocks(self.setup) and len(self.gcq) == 0:
            if self.activecombo > 1:
                print("Combo Dropped due to inactivity")
            self.activecombo = 1
            self.combodata = []
                
        to_be_removed = set()
        
        for combo in self.gcq: 
            fooflag = False
            for cell in combo.locations:
                if self.grid.get_curr_fade(cell[0], cell[1]) != self.setup.combo_fade_time:
                    fooflag = True
                    
            if fooflag:
                self.pop_combos(combo)
            else:
                for cell in combo.locations:
                    self.grid.set_curr_fade(cell[0], cell[1], 0)
                    self.grid.set_type(cell[0], cell[1], "empty")
                    self.grid.set_color(cell[0], cell[1], -1)
                    if self.player_type == 1:
                        if (cell[0], cell[1]) in self.vgame.goals:
                            self.vgame.goals.remove((cell[0], cell[1]))
                to_be_removed.add(combo)
        
        for tbr in to_be_removed:
            self.gcq.remove(tbr)
            

                        
                  
    def drop_blocks(self):
        
        for column in range(self.setup.cells_per_row):
            for row in range(self.setup.cells_per_column-1, 0, -1): #go from bottom to top
                if self.grid.get_just_dropped(column, row):
                    self.grid.set_just_dropped(column, row, False)
                if self.grid.can_drop(column, row): #if the next lowest block is empty, but not a part of a combo
                    if self.grid.get_drop_offset(column, row) == 0:
                        initialoffset = self.setup.cell_dimension % self.setup.cell_drop_speed
                        if initialoffset == 0:
                            initialoffset = self.setup.cell_drop_speed
                        self.grid.set_drop_offset(column, row, initialoffset)
                    elif self.grid.get_drop_offset(column, row) >= self.setup.cell_dimension:
                        self.grid.set_drop_offset(column, row, 0)
                        self.swap_blocks((column, row), (column, row+1))
                        self.grid.set_just_dropped(column, row+1, True)
                    elif self.grid.get_drop_offset(column, row) > 0:
                        self.grid.set_drop_offset(column, row, self.grid.get_drop_offset(column, row) + self.setup.cell_drop_speed)


    def button_logic(self, eventqueue):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.cursor.x != 0:
                    self.cursor.x -= 1
                elif event.key == pygame.K_RIGHT and self.cursor.x != self.setup.cells_per_row-2:
                    self.cursor.x += 1
                elif event.key == pygame.K_UP and self.cursor.y != 1:
                    self.cursor.y -= 1
                elif event.key == pygame.K_DOWN and self.cursor.y != self.setup.cells_per_column-1:
                    self.cursor.y += 1
                elif event.key == pygame.K_SPACE:
                    if self.grid.can_swap_right(self.cursor.x, self.cursor.y) and self.grid.can_swap_left(self.cursor.x+1, self.cursor.y):
                        if self.grid.get_type(self.cursor.x, self.cursor.y) == "block" or self.grid.get_type(self.cursor.x+1, self.cursor.y) == "block":
                            initialoffset = self.setup.cell_dimension % self.setup.cell_swap_speed
                            if initialoffset == 0:
                                initialoffset = self.setup.cell_swap_speed
                            self.grid.set_swap_offset(self.cursor.x, self.cursor.y, initialoffset)
                            self.grid.set_swap_offset(self.cursor.x+1, self.cursor.y, -1*initialoffset)
                            '''
                            if self.player_type == 1:
                                self.vgame.vgrid.set_swap_offset(self.cursor.x, self.cursor.y, initialoffset)
                                self.vgame.vgrid.set_swap_offset(self.cursor.x+1, self.cursor.y, -1*initialoffset)
                            '''
        return 0
    
    def ai_logic(self, eventqueue, timer):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
            
        if timer % 5 == 0:
            command = self.vgame.v_find_move()
            if command == "MOVELEFT" and self.cursor.x != 0:
                self.cursor.x -= 1
            elif command == "MOVERIGHT" and self.cursor.x != self.setup.cells_per_row-2:
                self.cursor.x += 1
            elif command == "MOVEUP" and self.cursor.y != 1:
                self.cursor.y -= 1
            elif command == "MOVEDOWN" and self.cursor.y != self.setup.cells_per_column-1:
                self.cursor.y += 1
            elif command == "SWAP":
                if self.grid.can_swap_right(self.cursor.x, self.cursor.y) and self.grid.can_swap_left(self.cursor.x+1, self.cursor.y):
                    initialoffset = self.setup.cell_dimension % self.setup.cell_swap_speed
                    if initialoffset == 0:
                        initialoffset = self.setup.cell_swap_speed
                    self.grid.set_swap_offset(self.cursor.x, self.cursor.y, initialoffset)
                    self.grid.set_swap_offset(self.cursor.x+1, self.cursor.y, -1*initialoffset)
    
                    self.vgame.vgrid.set_swap_offset(self.cursor.x, self.cursor.y, initialoffset)
                    self.vgame.vgrid.set_swap_offset(self.cursor.x+1, self.cursor.y, -1*initialoffset)  
            elif command == "WANDER":
                if self.cursor.x == self.setup.cells_per_row - 2 and self.cursor.y <= self.setup.cells_per_column - 2:
                    self.cursor.y += 1
                elif self.cursor.y == self.setup.cells_per_column - 1:
                    if self.cursor.x == 0:
                        self.cursor.y -= 1
                    else:
                        self.cursor.x -= 1
                elif self.cursor.x % 2 == 0:
                    if self.cursor.y == 1:
                        self.cursor.x += 1
                    else:
                        self.cursor.y -= 1
                elif self.cursor.x % 2 == 1:
                    if self.cursor.y == self.setup.cells_per_column - 2:
                        self.cursor.x += 1
                    else:
                        self.cursor.y += 1             
                
        return 0
        
    def quit_check(self, eventqueue):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
 
    def gameloop(self, timer):
        self.move_blocks()
        self.drop_blocks()
        self.combo_blocks()
        
        '''
        if self.player_type == 1:
            self.vgame.v_gameloop()
        '''
        if len(self.gcq) == 0 and self.graceperiod != 0 and timer % self.setup.board_raise_rate == 0:
            self.raise_board()
            
        if self.graceperiod == 0:
            return True
        else:
            return False
        
    def draw_cursor(self, screen):
        hoff = self.setup.display_width*(1+2*self.player_number)
        
        pygame.draw.rect(screen,
            self.setup.WHITE,
            [(self.setup.cell_between + self.setup.cell_dimension) * self.cursor.x + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
            (self.setup.cell_between + self.setup.cell_dimension) * self.cursor.y + self.setup.cell_between - self.grid.get_board_offset() + self.setup.cell_dimension//2,
            2*self.setup.cell_dimension+self.setup.cell_between,
            self.setup.cell_dimension],
            self.setup.cell_between*5)
        pygame.draw.lines(screen,
            self.setup.WHITE,
            False,
            (((self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.x +1) + self.setup.cell_between//2 + self.setup.cell_dimension//2 + hoff,
                (self.setup.cell_between + self.setup.cell_dimension) * self.cursor.y + 2*self.setup.cell_between- self.grid.get_board_offset() + self.setup.cell_dimension//2),
                ((self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.x +1) + self.setup.cell_between//2 + self.setup.cell_dimension//2 + hoff,
                (self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.y+1) - self.setup.cell_between- self.grid.get_board_offset() + self.setup.cell_dimension//2)),
            self.setup.cell_between*5) 
        
    def draw_frame(self, screen):
        hoff = self.setup.display_width*(1+2*self.player_number)
        
        pygame.draw.rect(screen,
                         self.setup.WHITE,
                         [self.setup.cell_dimension//2 + hoff,
                          self.setup.cell_dimension//2,
                          (self.setup.cell_between + self.setup.cell_dimension)*(self.setup.cells_per_row) + self.setup.cell_between,
                          (self.setup.cell_between + self.setup.cell_dimension)*(self.setup.cells_per_column)],
                         self.setup.cell_between)
         
    def draw_board(self, screen, timer):
        '''
        if self.playertype == 1:
            self.vgame.v_draw_board(screen, timer)
        '''

        hoff = self.setup.display_width*(1+2*self.player_number)
        
        for column in range(self.setup.cells_per_row):
            index = self.buffer.get_color(column)

            sprite = self.setup.cell_type_array[index]
            
            screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
                                 (self.setup.cell_between + self.setup.cell_dimension) * (self.setup.cells_per_column) + self.setup.cell_between + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
            
            
            #color = self.setup.cell_type_array[self.buffer.get_color(column)]
            #pygame.draw.rect(screen,
            #                 color,
            #                 [(self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
            #                  (self.setup.cell_between + self.setup.cell_dimension) * (self.setup.cells_per_column) + self.setup.cell_between + self.setup.cell_dimension//2 - self.grid.get_board_offset(),
            #                  self.setup.cell_dimension,
            #                  self.setup.cell_dimension])
            
            for row in range(self.setup.cells_per_column-1, -1, -1):
                index = self.grid.get_color(column, row)
                explode = self.grid.get_curr_fade(column, row)
                if explode > 0:
                    index = (5*(explode-1))//(self.setup.combo_fade_time)
                    sprite = self.setup.explode_array[index]
                    screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.grid.get_swap_offset(column, row) + self.setup.cell_dimension//2 + hoff,
                                     (self.setup.cell_between + self.setup.cell_dimension) * (row) + self.setup.cell_between + self.grid.get_drop_offset(column, row) + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
                elif index > -1:
                    sprite = self.setup.cell_type_array[index]
                    screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.grid.get_swap_offset(column, row) + self.setup.cell_dimension//2 + hoff,
                                     (self.setup.cell_between + self.setup.cell_dimension) * (row) + self.setup.cell_between + self.grid.get_drop_offset(column, row) + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
            
                #if self.grid.can_drop(column, row):
                #    pygame.draw.rect(screen,
                #                 self.setup.WHITE,
                #                 [(self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.grid.get_swap_offset(column, row) + self.setup.cell_dimension//2 + hoff,
                #                  (self.setup.cell_between + self.setup.cell_dimension) * (row) + self.setup.cell_between + self.grid.get_drop_offset(column, row) + self.setup.cell_dimension//2 - self.grid.get_board_offset(), #draw from bottom up
                #                  self.setup.cell_dimension//2,
                #                  self.setup.cell_dimension//2])
        
        pos = []
        
        for c in range(len(self.combodata)):
            pos.append((self.setup.cells_per_row, self.setup.cells_per_column,-1))
            for loc in self.combodata[c].locations:
                if loc[1] < pos[c][1] or (loc[1] == pos[c][1] and loc[0] < pos[c][0]):
                    pos[c] = loc
                    
            pygame.draw.circle(screen,
                             self.setup.WHITE,
                             [(self.setup.cell_between + self.setup.cell_dimension) * (pos[c][0]) + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
                             (self.setup.cell_between + self.setup.cell_dimension) * (pos[c][1]) + self.setup.cell_between + self.setup.cell_dimension//2 - self.grid.get_board_offset()], #draw from bottom up
                             self.setup.cell_dimension//4)
            
            multi = self.setup.font.render(str(c+1) + "x", True, self.setup.PURPLE)
            screen.blit(multi, [(self.setup.cell_between + self.setup.cell_dimension) * (pos[c][0]) + self.setup.cell_between + self.setup.cell_dimension//2 + hoff - self.setup.fontsize//2,
                             (self.setup.cell_between + self.setup.cell_dimension) * (pos[c][1]) + self.setup.cell_between + self.setup.cell_dimension//2 - self.grid.get_board_offset() - self.setup.fontsize//2])
        
        if timer < 30:
            font = pygame.font.Font(pygame.font.get_default_font(), 16)          
            sbs = "Score: " + str(self.scoreboard.total_score)
            text = font.render(sbs, True, self.setup.GREEN, self.setup.BLACK)
            textRect = text.get_rect()  
            textRect.center = (self.setup.display_width//2 + hoff, self.setup.display_height) 
            screen.blit(text, textRect)
                    
        # Draw the Cursor
        if timer < 45:
            self.draw_cursor(screen)
            
        self.draw_frame(screen)
        

        
        
        
        
                
        
        
