import pygame
import warnings

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
        assert not missingkeys, f"Missing difficult info: {missingkeys}" #Truth Value Testing to assert that missingkeys is empty

    # Store the info
        self.player_number = playernumber #the number of the player, zero-indexed: Player 0, Player 1, Player 2, etc.
        self.player_type = self.difficulty_info["player_type"] #0 is human, 1 is ai

    # Make some useful objects
        self.setup = SetupClass.Setup(display_info, self.difficulty_info)
        self.grid = GridClass.Grid(self.setup)
        self.buffer = BufferClass.Buffer(self.setup)
        self.cursor = CursorClass.Cursor(self.difficulty_info["cursor_starting_x"], self.difficulty_info["cursor_starting_y"])
        self.board_raise_flag = False #Is the player holding the button that raises the board?
        self.active_chains = [] #a list of all combos, i.e. everything marked for deletion
        self.total_combos = 0 #the total number of combos made in this game. Used to assign each combo a unique ID number, which is to be used in some flags
        self.total_chains = 0 #the total number of combo chains made in the game. Similar to total_combos, but a chain is a list of combos performed in a timed sequence
        self.active_combo_length = 0
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
            
            #move the board up
            if self.board_raise_flag:
                boff = boff + 5 #if the button is held, go up faster
            else:
                boff = boff + 1
            
            #if the board was raised enough to add a new row
            if boff >= self.setup.cell_dimension:

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
                if self.cursor.get_y() > 1:
                    self.cursor.move_down()


                #Once all blocks have been moved up, refill the buffer
                self.buffer.spawn_blocks(self.setup)
        
            self.grid.set_board_offset(boff % self.setup.cell_dimension) #sets the board offset correctly. The modulo handles the case where boff >= cell_dimension
        
        #check if any cell in the top row is not empty (i.e. if any column is touching the top of the board)
        for column in range(self.setup.cells_per_row):
            if self.grid.get_type(column, 0) != "empty":
                fooflag = True

        if fooflag: #if the board is too full
            self.graceperiod -= 1 #start counting down until GAME OVER
        else: #but if the top row is clear now
            self.graceperiod = self.setup.grace_period_full #reset the GAME OVER countdown. This would "refill the health bar"


    '''This will remove any invalid combos from the combo list of possible combos. A combo may be invalid because its cells are moving (i.e.
    a falling block is in a space that would be a combo), its cells are part of another combo, or other issues. This combo also merges combos
    that meet, such as a vertical and horizontal combo that make a plus shape'''
    def clean(self, combolist):
        
        newcombolist = set()

        for c in combolist:
            isbad = False
            for chain in self.active_chains:
                for combo in chain:
                    if len(c.locationdata & combo.locationdata) > 0: #make sure no cell in combolist are already a part of an active combo
                        isbad = True
            for loc in c.locationdata: #make sure all cells in the combo are on solid ground (i.e. none can drop)
                x,y = loc
                if self.grid.can_drop(x,y):
                    isbad = True
            if not isbad:
                newcombolist.add(c) #don't add redundant, falling, short, or non-block combos
    

        
        #some combos can be combined if they meet at a point. For example, a vertical and horizontal combo may combine to make an L or a T. We count this as one combo, a TX-combo
        tx = True
        while tx:
            tx = False #is there a TX Combo?
            combolistcopy = newcombolist.copy() #we plan on iterating through newcombolist and editing the values as we go. To make sure we hit everything, we iterate throgu ha copy of newcombolist instead
            for c1 in combolistcopy:
                for c2 in combolistcopy:
                    if c1 != c2 and c1.locationdata.isdisjoint(c2.locationdata): #combine two distinct combos who have at least one block in common
                        
                        txcombo = ComboClass.ProtoCombo()
                        txcombo.colors = c1.colors | c2.colors
                        txcombo.locationdata = c1.locationdata | c2.locationdata
                        txcombo.numblocks = len(txcombo.locationdata)
                        txcombo.numTX = c1.numTX + c2.numTX + 1 #for the sake of scoring in the future, we count the number of such combos
                        #no need to edit default value of txcombo.ischain, but that may prove useful later
                        
                        #WARNING: Iterating through sets in Python might work differently than how I think/hope want it to. This implementation requires further testing
                        newcombolist.discard(c1)
                        newcombolist.discard(c2)
                        newcombolist.add(txcombo)

        '''IMPORTANT IMPLEMENTATION DETAIL: any blocks that connect within the same tick are counted as the same combo, even if they are not touching.
        This means it is possible to have a combo consisting of multiple disconnected lines and crosses. This may change based on playtesting, but
        the code reflects this choice'''

        '''Finally, put all the contents of newcombolist into a single proper combo, fully pruned and cleaned. This also orders it for deletion:
        top row to bottom row; within the same row, left to right'''

        #first, check if this is a continuation of an existing chain OR the start of a new chain

        chain_flag = False

        for c in newcombolist: #check if the combo is a chain
            for loc in c.locationdata:
                x,y = loc
                if self.grid.get_just_dropped(x,y):
                    chain_flag = True

        #We update the values of total_combos and total_chains later, but we use their new and past values now
        if chain_flag:
            tmpcombo = ComboClass.Combo(self.total_combos, self.total_chains) #If this combo resulted from a non-falling block, it end the chain and creates a new one
        else:
            tmpcombo = ComboClass.Combo(self.total_combos, self.total_chains+1) #If this combo resulted from a falling block, it continues the chain

        for c in newcombolist:
            tmpcombo.colors.update(c.colors)
            tmpcombo.numblocks += c.numblocks
            tmpcombo.numTX += c.numTX
            tmpcombo.locationdata.update(c.locationdata)

        for row in range(self.setup.cells_per_column):
            for column in range(self.setup.cells_per_row):
                for c in newcombolist:
                    if (column, row) in c.locationdata:
                        tmpcombo.locations.append((column, row))

        return tmpcombo


    def find_matches(self):
        
        comboqueue = set()
        
        #Check for Vertical Combos
        for column in range(self.setup.cells_per_row): #check for combos in each column, one by one

            tmpcombo = ComboClass.ProtoCombo() #keep track of the line of same-colored blocks
            tmpcombo.colors.add(self.grid.get_color(column, 0))
            
            for row in range(self.setup.cells_per_column):
                if self.grid.get_color(column, row) in tmpcombo.colors: #since the colors attribute is a set (see IMPORTANT IMPLEMENTATION DETAILS), we check for membership instead of equality
                    tmpcombo.locationdata.add((column, row))
                    tmpcombo.numblocks += 1
                else: #or if the next block is a different color
                    if tmpcombo.numblocks > 2 and -1 not in tmpcombo.colors: #only add combos of sufficient length and type
                        comboqueue.add(tmpcombo) #if the new colored block would break the combo, add the previously made combo to the comboqueue
                    tmpcombo = ComboClass.ProtoCombo()
                    tmpcombo.colors.add(self.grid.get_color(column, row))
                    tmpcombo.locationdata.add((column, row))
                    tmpcombo.numblocks = 1

            #when we've gone through the entire column, the last combo won't trigger the "change" flag, so we add whatever's left
            if tmpcombo.numblocks > 2 and -1 not in tmpcombo.colors:
                comboqueue.add(tmpcombo)
                            
        #Check for horizontal columns. Same setup with different indexing   
        for row in range(self.setup.cells_per_column): #check for combos in each row

            tmpcombo = ComboClass.ProtoCombo()
            tmpcombo.colors.add(self.grid.get_color(0, row)) #sample the first cell in the ROW this time
            
            for column in range(self.setup.cells_per_row):
                if self.grid.get_color(column, row) in tmpcombo.colors: 
                    tmpcombo.locationdata.add((column, row))
                    tmpcombo.numblocks += 1
                else:
                    if tmpcombo.numblocks > 2 and -1 not in tmpcombo.colors:
                        comboqueue.add(tmpcombo)
                    tmpcombo = ComboClass.ProtoCombo()
                    tmpcombo.colors.add(self.grid.get_color(column, row))
                    tmpcombo.locationdata.add((column, row))
                    tmpcombo.numblocks = 1

            if tmpcombo.numblocks > 2 and -1 not in tmpcombo.colors:
                comboqueue.add(tmpcombo)

        '''At this point, "comboqueue" is just a set of all things on the board that could be considered a combo based on number of consecutive cells
        and their color. It does not check for whether these combos are valid within the game. Examples of invalid combos include cells that are falling
        or cells that are already marked for deletion (i.e. part of an active combo). We use the "clean" function to check these, and to combine all of these
        pieces into a single combo. This means that two vertical columns that are not touching each other count as one single "combo" when determining
        the length of a combo chain. This was a conscious design choice.'''
        #clean up the queue
        newbigcombo = self.clean(comboqueue)
        
        return newbigcombo
    
    def move_blocks(self): #Handles moving blocks side-to-side when swapped by the cursor
        for column in range(self.setup.cells_per_row):
            for row in range(self.setup.cells_per_column):
                #we want swap_offset 0 to be neutral, so we have to count up and down and then set back to 0 when the swapping is done
                if self.grid.get_swap_offset(column, row) > 0: #positive swap offset means the block is moving to the right
                    self.grid.set_swap_offset(column, row, self.grid.get_swap_offset(column, row) + self.setup.cell_swap_speed) #increment the offset
                elif self.grid.get_swap_offset(column, row) < 0: #negative swap offset means the block is moving to the left
                    self.grid.set_swap_offset(column, row, self.grid.get_swap_offset(column, row) - self.setup.cell_swap_speed)

                if self.grid.get_swap_offset(column, row) > self.setup.cell_dimension: #when the cell has moved enough visually, we swap the data in the cells
                    self.swap_blocks((column, row), (column+1, row))
                    self.grid.set_swap_offset(column, row, 0)
                elif self.grid.get_swap_offset(column, row) < -1*self.setup.cell_dimension:
                    self.grid.set_swap_offset(column, row, 0)

    def pop_combos(self, combo): #Handles the fade-out of the combos listed in "combo"
        
        for loc in combo.locations: #We first mark everything for deletion
            x,y = loc
            if self.grid.get_curr_fade(x, y) == 0:
                self.grid.mark_for_deletion(x, y) #mark all combos to be popped

        for loc in combo.locations: #Remember: Combos are ordered bottom-up, then left-right
            x,y = loc
            if self.grid.get_curr_fade(x, y) < self.setup.combo_fade_time:
                #If a particular cell is starting its animation, play a sound
                if self.grid.get_curr_fade(x, y) == 1:
                    pygame.mixer.Sound.play(self.setup.action_sounds[0])

                #Increase the fade value. Higher fade means further into the deletion animation.
                self.grid.fade(x, y)
                break #and only incrementation per loop
                
    def combo_blocks(self):
        
        newcombos = self.find_matches()
        
        if newcombos.numblocks > 0:
            print("New combo detected")
            self.total_combos += 1

            #if the combo was dropped or if there were no active combos to begin with, we make a new chain. Otherwise, we just add the combo to the last chain in active_chains
            if newcombos.chain_id > self.total_chains or not self.active_chains: #Truth Value Testing on self.active_chains
                print("It's a new chain")
                self.active_chains.append([newcombos])
                self.total_chains += 1
                self.active_combo_length = 0
            else:
                self.active_chains[-1].append(newcombos) #add to the end of the last item in the list of lists
                self.active_combo_length += 1
                print("It's a continuation fo a chain")

            #REMARK: Realistically, active_chains will probably never be more than 3 elements long. This approach, however, allows the code to handle multiple "big blob" combos that may take a while to disappear
                
        tmp_active_chains = [] #We want to prune any finished combos from active_chains, so we make a copy and ADD the UNFINISHED combos to it

        for chain in self.active_chains:
            tmp_chain = []
            for combo in chain:
                combo_completed = True

                '''We raise a flag if any of the cells set to be deleted have not been deleted. There are three cases: 
                    (a) If curr_fade is 0, then the cell hasn't been marked for deletion
                    (b) If curr_fade is less than combo_fade_timer, then the cell is partially deleted
                    (c) If curr_fade is equal to combo_fade_timer, then the cell is totally deleted
                We need ALL of the cells in a combo to be in case (c) before we can remove the cell from the chain''' 
                for cell in combo.locations:
                    x,y = cell
                    if self.grid.get_curr_fade(x, y) != self.setup.combo_fade_time:
                        combo_completed = False
                    
                if not combo_completed:
                    self.pop_combos(combo)
                    tmp_chain.append(combo)
                else:
                    print("MARKING FOR DELETION")
                    for cell in combo.locations:
                        x,y = cell
                        self.grid.set_to_empty(x, y)

            if tmp_chain: #If tmp_chain is not empty, add it to tmp_active_chains. LESSON FOR MYSELF: Don't get arrogant with built-in types.
                tmp_active_chains.append(tmp_chain)

        self.active_chains = tmp_active_chains
            
                        
                  
    def drop_blocks(self):
        
        for column in range(self.setup.cells_per_row):
            for row in range(self.setup.cells_per_column-1, 0, -1): #go from bottom to top

                if self.grid.get_just_dropped(column, row): #update this flag for combo timing
                    self.grid.set_just_dropped(column, row, False)

                #drop any block that is allowed
                if self.grid.can_drop(column, row):
                    if self.grid.get_drop_offset(column, row) == 0:

                        '''Same explanation as in the "button logic" section in the next function'''
                        initialoffset = self.setup.cell_dimension % self.setup.cell_drop_speed
                        if initialoffset == 0:
                            initialoffset = self.setup.cell_drop_speed
                    
                        self.grid.set_drop_offset(column, row, initialoffset)

                    elif self.grid.get_drop_offset(column, row) >= self.setup.cell_dimension: #if the block has dropped enough

                        self.grid.set_drop_offset(column, row, 0)
                        if not self.grid.can_drop(column, row): #if the block lands on solid ground, set the "just dropped" flag for the rest of the code TO-DO Test this added check
                            self.grid.set_just_dropped(column, row, True)
                        self.swap_blocks((column, row), (column, row+1)) #another use of swap_blocks, and this should ALWAYS functionally swap a cell and an empty block

                    elif self.grid.get_drop_offset(column, row) > 0:
                        self.grid.set_drop_offset(column, row, self.grid.get_drop_offset(column, row) + self.setup.cell_drop_speed)


    def button_logic(self, eventqueue):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.cursor.get_x() > 0:
                    self.cursor.move_left()
                elif event.key == pygame.K_RIGHT and self.cursor.get_x() < self.setup.cells_per_row-2: #since the cursor extends to the right, cursor.get_x() MUST NOT be in the last column
                    self.cursor.move_right()
                elif event.key == pygame.K_UP and self.cursor.get_y() > 0:
                    self.cursor.move_up()
                elif event.key == pygame.K_DOWN and self.cursor.get_y() < self.setup.cells_per_column-1:
                    self.cursor.move_down()
                elif event.key == pygame.K_SPACE: #Swap the cells
                    if self.grid.can_swap(self.cursor.get_x(), self.cursor.get_y()) and self.grid.can_swap(self.cursor.get_x()+1, self.cursor.get_y()):
                        if self.grid.get_type(self.cursor.get_x(), self.cursor.get_y()) == "block" or self.grid.get_type(self.cursor.get_x()+1, self.cursor.get_y()) == "block": #at least one of the target cells must be a block (e.g. don't swap two empty cells)
                            
                            '''This part deserves explanation: initialoffset is intended to be "spatial padding" to make sure that adding cell_swap_speed
                            repeatedly results in a sum of exactly cell_dimension at some point. For example, if cell_swap_speed is 7 and cell_dimension is 25,
                            initialoffset is 4 because 4 + 7 + 7 + 7 = 25. However, since a grid space with swap_offset of 0 is in its "normal state" and not
                            flagged to be swapped, if cell_dimension is divisible by cell_swap_speed, we risk not properly setting the flag. If cell_swap_speed
                            is 5 and cell_dimension is 25, this would cause an error since no padding is needed. Hence, if initialoffset is 0, we pad it with the
                            value of cell_swap_speed so properly raise the flag. TO-DO: MAKE THIS BETTER. IMPLEMENT ACTUAL FLAGS
                            '''
                            initialoffset = self.setup.cell_dimension % self.setup.cell_swap_speed
                            if initialoffset == 0:
                                initialoffset = self.setup.cell_swap_speed

                            self.grid.set_swap_offset(self.cursor.get_x(), self.cursor.get_y(), initialoffset)
                            self.grid.set_swap_offset(self.cursor.get_x()+1, self.cursor.get_y(), -1*initialoffset)

            if pygame.event == pygame.KEYUP:
                if event.key == pygame.LSHIFT:
                    self.board_raise_flag = False

        if not (self.board_raise_flag == pygame.key.get_pressed()[pygame.K_LSHIFT]):
            warnings.warn("board_raise_flag out of sync with keyboard input. Correcting...")
            self.board_raise_flag = pygame.key.get_pressed()[pygame.K_LSHIFT]
                
        return 0
    
    #CURRENTLY NOT USED

    def ai_logic(self, eventqueue, timer):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
            
        if timer % 5 == 0:
            command = self.vgame.v_find_move()
            if command == "MOVELEFT" and self.cursor.get_x() != 0:
                self.cursor.move_left()
            elif command == "MOVERIGHT" and self.cursor.get_x() != self.setup.cells_per_row-2:
                self.cursor.move_right()
            elif command == "MOVEUP" and self.cursor.get_y() != 1:
                self.cursor.move_up()
            elif command == "MOVEDOWN" and self.cursor.get_y() != self.setup.cells_per_column-1:
                self.cursor.move_down()
            elif command == "SWAP":
                if self.grid.can_swap(self.cursor.get_x(), self.cursor.get_y()) and self.grid.can_swap(self.cursor.get_x()+1, self.cursor.get_y()):
                    initialoffset = self.setup.cell_dimension % self.setup.cell_swap_speed
                    if initialoffset == 0:
                        initialoffset = self.setup.cell_swap_speed
                    self.grid.set_swap_offset(self.cursor.get_x(), self.cursor.get_y(), initialoffset)
                    self.grid.set_swap_offset(self.cursor.get_x()+1, self.cursor.get_y(), -1*initialoffset)
    
                    self.vgame.vgrid.set_swap_offset(self.cursor.get_x(), self.cursor.get_y(), initialoffset)
                    self.vgame.vgrid.set_swap_offset(self.cursor.get_x()+1, self.cursor.get_y(), -1*initialoffset)  
            #elif command == "WANDER": #WIP 
                
        return 0
        
    def quit_check(self, eventqueue):
        for event in eventqueue:  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                return -1
 
    def gameloop(self, timer):
        self.move_blocks()
        self.drop_blocks()
        self.combo_blocks()
        
        #If there are no chains, the grace period is not set, and the board is set to raise
        if not self.active_chains and self.graceperiod != 0 and timer % self.setup.board_raise_rate == 0:
            self.raise_board()
            
        if self.graceperiod == 0:
            return True
        else:
            return False
        
    def draw_cursor(self, screen):
        hoff = self.setup.display_width*(1+2*self.player_number)
        
        pygame.draw.rect(screen,
            self.setup.WHITE,
            [(self.setup.cell_between + self.setup.cell_dimension) * self.cursor.get_x() + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
            (self.setup.cell_between + self.setup.cell_dimension) * self.cursor.get_y() + self.setup.cell_between - self.grid.get_board_offset() + self.setup.cell_dimension//2,
            2*self.setup.cell_dimension+self.setup.cell_between,
            self.setup.cell_dimension],
            self.setup.cell_between*5)
        pygame.draw.lines(screen,
            self.setup.WHITE,
            False,
            (((self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.get_x() +1) + self.setup.cell_between//2 + self.setup.cell_dimension//2 + hoff,
                (self.setup.cell_between + self.setup.cell_dimension) * self.cursor.get_y() + 2*self.setup.cell_between- self.grid.get_board_offset() + self.setup.cell_dimension//2),
                ((self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.get_x() +1) + self.setup.cell_between//2 + self.setup.cell_dimension//2 + hoff,
                (self.setup.cell_between + self.setup.cell_dimension) * (self.cursor.get_y()+1) - self.setup.cell_between- self.grid.get_board_offset() + self.setup.cell_dimension//2)),
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
        
        #Set the Horizontal Offset. Used to pad the border and the result should be something like _[]_[]_[]_ or just _[]_ for one player
        hoff = self.setup.display_width*(1+2*self.player_number)
        
        #draw the cells before the border for layering

        for column in range(self.setup.cells_per_row):
            #draw the buffer
            index = self.buffer.get_color(column)
            sprite = self.setup.cell_type_array[index]        
            screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.setup.cell_dimension//2 + hoff,
                                 (self.setup.cell_between + self.setup.cell_dimension) * (self.setup.cells_per_column) + self.setup.cell_between + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
            
            #draw each row
            for row in range(self.setup.cells_per_column-1, -1, -1):
                index = self.grid.get_color(column, row)
                explode = self.grid.get_curr_fade(column, row)

                #if any cells are exploding, update their sprites
                if explode > 0:
                    index = (5*(explode-1))//(self.setup.combo_fade_time)
                    sprite = self.setup.explode_array[index]
                    screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.grid.get_swap_offset(column, row) + self.setup.cell_dimension//2 + hoff,
                                     (self.setup.cell_between + self.setup.cell_dimension) * (row) + self.setup.cell_between + self.grid.get_drop_offset(column, row) + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
                elif index > -1:
                    sprite = self.setup.cell_type_array[index]
                    screen.blit(sprite, ((self.setup.cell_between + self.setup.cell_dimension) * (column) + self.setup.cell_between + self.grid.get_swap_offset(column, row) + self.setup.cell_dimension//2 + hoff,
                                     (self.setup.cell_between + self.setup.cell_dimension) * (row) + self.setup.cell_between + self.grid.get_drop_offset(column, row) + self.setup.cell_dimension//2 - self.grid.get_board_offset()))
        
        #Display Active Combo Count
        pygame.draw.circle(screen, self.setup.WHITE, [hoff + self.setup.display_width + 2*self.setup.cell_dimension, 2*self.setup.cell_dimension], self.setup.cell_dimension)
        multiplier = self.setup.font.render("x" + str(self.active_combo_length), True, self.setup.PURPLE)
        screen.blit(multiplier, [hoff + self.setup.display_width + int(1.5*self.setup.cell_dimension), int(1.5*self.setup.cell_dimension)])
        #Obsolte code for displaying a combo number next to the active combo. No longer useful in this code right now, but may prove useful later. Commented out for now.
        '''pos = []
        
        for c in range(len(self.tempchainplaceholder)):
            pos.append((self.setup.cells_per_row, self.setup.cells_per_column,-1))
            for loc in self.tempchainplaceholder[c].locations:
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
        '''

        #WIP: Display Score
        '''
        if timer < 30:
            font = pygame.font.Font(pygame.font.get_default_font(), 16)          
            sbs = "Score: " + str(self.scoreboard.total_score)
            text = font.render(sbs, True, self.setup.GREEN, self.setup.BLACK)
            textRect = text.get_rect()  
            textRect.center = (self.setup.display_width//2 + hoff, self.setup.display_height) 
            screen.blit(text, textRect)
        '''

        # Draw the Cursor
        if timer < 45:
            self.draw_cursor(screen)
            
        self.draw_frame(screen)
        

        
        
        
        
                
        
        
