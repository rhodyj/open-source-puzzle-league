import random
import CellClass
import warnings


class Grid:
    def __init__(self, setup):

        #set some empty values
        self.board_offset = 0
        self.cell_grid = []
        
        #make and populate the grid
        for column in range(setup.cells_per_row+2):
            
            self.cell_grid.append([]) #the grid should be an array of arrays (a 2-D array)
            
            for row in range(setup.cells_per_column+2):
                
                if row == 0 or row == setup.cells_per_column+1 or column == 0 or column == setup.cells_per_row + 1:
                    cell = CellClass.Cell("border", -1, 0, 0, 0, False) #"border" tiles are for bounding and behind-the-scenes thing; they are not usually drawn
                elif row > setup.initial_height_offset:
                    cell = CellClass.Cell("block", random.randint(0,4), 0, 0, 0, False) #initial height offset determines how high from the top the blocks start; used to adjust difficulty
                else:
                    cell = CellClass.Cell("empty", -1, 0, 0, 0, False) #a basic, unpopulated cell
                    
                self.cell_grid[column].append(cell) #once the cell is made, add it to the array
    
    '''board_offset is how much of the buffer has actually come into view. when board_offset meets 
    cell_dimension, the buffer is added to the grid. board_offset also visually affects the grid'''

    def get_board_offset(self):
        return self.board_offset
    
    def set_board_offset(self, boff):
        self.board_offset = boff
    
    '''access the cell data; since cell_grid[x][0] and cell_grid[0][y] are border tiles, this returns the position in the array
    ignoring the border tiles, hence the use of [x+1][y+1]. In other words, use indices from the sub-array of actual playable 
    (non-border) tiles'''
    def get_color(self, x, y): #color is usually keyed to a position in the cell sprite array. -1 is for things that can't combo, like empty cells
        return self.cell_grid[x+1][y+1].color
    
    def set_color(self, x, y, c):
        self.cell_grid[x+1][y+1].color = c

    def set_swap_offset(self, x, y, swoff): #swap offset is how far left/right from the neutral position the cell is; used to check if a cell is moving
        self.cell_grid[x+1][y+1].swap_offset = swoff
    
    def get_swap_offset(self, x, y):
        return self.cell_grid[x+1][y+1].swap_offset
    
    def set_drop_offset(self, x, y, doff): #drop offset is how far down from the neutral position the cell is; used to check if a cell is falling
        self.cell_grid[x+1][y+1].drop_offset = doff
        
    def get_drop_offset(self,x,y):
        return self.cell_grid[x+1][y+1].drop_offset
    
    def set_type(self, x, y, ct): #types are types are border, block, empty, grey
        self.cell_grid[x+1][y+1].cell_type = ct
        
    def get_type(self,x,y):
        return self.cell_grid[x+1][y+1].cell_type    
    
    def set_curr_fade(self, x, y, ct): #after being "combo'd", how far into the disappearing animation is the associated cell. Affects display and behavior
        self.cell_grid[x+1][y+1].combo_timer = ct
        
    def get_curr_fade(self,x,y):
        return self.cell_grid[x+1][y+1].combo_timer

    def fade(self, x, y):
        self.cell_grid[x+1][y+1].combo_timer += 1
    
    def set_just_dropped(self, x, y, jd): #has a cell just landed? Useful for combo windows
        self.cell_grid[x+1][y+1].just_dropped = jd
        
    def get_just_dropped(self,x,y):
        return self.cell_grid[x+1][y+1].just_dropped

    def mark_for_deletion(self, x, y): #mark a combo for deletion/"makes it grey"
        self.set_curr_fade(x, y, 1) #mark all combos to be popped
        self.set_type(x, y, "grey")
        self.set_color(x, y, -1)
        #Set up some warnings
        if self.get_drop_offset(x,y) != 0:
            self.set_drop_offset(x, y, 0)
            warnings.warn("Possible error: Cell at " + str((x,y)) + " is being set to grey despite falling")
        if self.get_swap_offset(x,y) != 0:
            self.set_swap_offset(x, y, 0)
            warnings.warn("Possible error: Cell at " + str((x,y)) + " is being set to grey despite swapping")


    def set_to_empty(self,x,y):
        self.set_curr_fade(x, y, 0)
        self.set_type(x, y, "empty")
        self.set_color(x, y, -1)
        #Set up some warnings
        if self.get_just_dropped(x,y):
            self.set_just_dropped(x, y, False)
            warnings.warn("Possible error: Cell at " + str((x,y)) + " is being set to black despite having just dropped")
        if self.get_drop_offset(x,y) != 0:
            self.set_drop_offset(x, y, 0)
            warnings.warn("Possible error: Cell at " + str((x,y)) + " is being set to black despite falling")
        if self.get_swap_offset(x,y) != 0:
            self.set_swap_offset(x, y, 0)
            warnings.warn("Possible error: Cell at " + str((x,y)) + " is being set to black despite swapping")
    
    '''check for valid moves within the grid. Cells drop automatically if they aren't on
    a stable surface (e.g. another cell that isn't moving, a boundary tile, garbage [once garbage is implemented]).
    These checks also determine when a player can swap the position of the two cells within the cursor'''
    
    def can_drop(self, x, y): #can a cell drop?

        c0 = self.get_type(x,y) == "block" #the cell must be a block, not an empty cell or a boundary
        c1 = self.get_curr_fade(x,y) == 0 and self.get_swap_offset(x,y) ==  0 #the cell must not be comboing or swapping        
        c2 = self.get_type(x,y+1) == "empty" #the cell below must be empty OR
        c3 = self.get_type(x, y+1) == "block" and self.get_drop_offset(x,y+1) > self.get_drop_offset(x, y) #the cell below has enough room above it
        
        return c0 and c1 and (c2 or c3)

    def can_swap(self, x, y): #can the cell in this position be swapped?
        c0 = False
        if self.get_type(x,y) == "block":
            c0 = not self.can_drop(x,y) #a "block" cell cannot be swapped if it is falling or able to fall. It must be on "solid ground."
        elif self.get_type(x,y) == "empty":
            c0 = self.get_drop_offset(x,y-1) == 0 #an "empty" cell cannot be swapped if there is anything falling into it. However, an empty cell doesn't need to be on "solid ground" to be swapped

        c1 = self.get_swap_offset(x,y) == 0 #the cell can't already be moving to the left or right

        return c0 and c1

    def has_falling_blocks(self, setup): #does the board have any falling blocks? Useful for detecting idle state, which helps in determining chains
        islooking = False
        for column in range(setup.cells_per_row):
            for row in range(setup.cells_per_column-1, -1, -1): #go from bottom to top
                if self.can_drop(column, row):
                    islooking = True
                    
        return islooking