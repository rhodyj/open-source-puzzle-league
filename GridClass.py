import random
import CellClass


class Grid:
    def __init__(self, setup):
        
        self.board_offset = 0
        
        self.cell_grid = []
        
        for column in range(setup.cells_per_row+2): #white blocks for bounding
            
            self.cell_grid.append([])
            
            for row in range(setup.cells_per_column+2):
                
                if row == 0 or row == setup.cells_per_column+1 or column == 0 or column == setup.cells_per_row + 1:
                    cell = CellClass.Cell("border", -1, 0, 0, 0, False)
                elif row > setup.initial_height_offset:
                    cell = CellClass.Cell("block", random.randint(0,4), 0, 0, 0, False)
                else:
                    cell = CellClass.Cell("empty", -1, 0, 0, 0, False)
                    
                self.cell_grid[column].append(cell)
    
    def get_board_offset(self):
        return self.board_offset
    
    def set_board_offset(self, boff):
        self.board_offset = boff
    
    def get_color(self, x, y): #all functions offset appropriately
        return self.cell_grid[x+1][y+1].color
    
    def set_color(self, x, y, c):
        self.cell_grid[x+1][y+1].color = c

    def set_offset(self, x, y, swoff):
        self.cell_grid[x+1][y+1].swap_offset = swoff
    
    def get_swap_offset(self, x, y):
        return self.cell_grid[x+1][y+1].swap_offset
    
    def set_drop_offset(self, x, y, doff):
        self.cell_grid[x+1][y+1].drop_offset = doff
        
    def get_drop_offset(self,x,y):
        return self.cell_grid[x+1][y+1].drop_offset
    
    def set_type(self, x, y, ct):
        self.cell_grid[x+1][y+1].cell_type = ct
        
    def get_type(self,x,y):
        return self.cell_grid[x+1][y+1].cell_type    
    
    def set_curr_fade(self, x, y, ct):
        self.cell_grid[x+1][y+1].combo_timer = ct
        
    def get_curr_fade(self,x,y):
        return self.cell_grid[x+1][y+1].combo_timer
    
    def set_just_dropped(self, x, y, jd):
        self.cell_grid[x+1][y+1].just_dropped = jd
        
    def get_just_dropped(self,x,y):
        return self.cell_grid[x+1][y+1].just_dropped
    
    def can_drop(self, x, y):
        c0 = self.get_type(x,y) == "block" #the cell must be a block, not an empty cell or a boundary
        c1 = self.get_curr_fade(x,y) == 0 and self.get_swap_offset(x,y) ==  0 #the cell must not be comboing or swapping        
        c2 = self.get_type(x,y+1) == "empty" or self.get_drop_offset(x,y+1) > self.get_drop_offset(x, y) #the cell below must be empty or dropped further than 
        return c0 and c1 and c2

    def can_swap_right(self, x, y): #can the cell be swapped to the right?
        c0 = self.get_swap_offset(x,y) == 0 #the cell can't be swapping
        c1 = self.get_drop_offset(x, y-1) == 0 #there can't be anything dropping into the cell
        c2 = self.get_curr_fade(x+1,y) == 0
        return c0 and c1 and c2 and not self.can_drop(x,y)
    
    def can_swap_left(self, x, y): #can the cell be swapped to the left?
        c0 = self.get_swap_offset(x,y) == 0 #the cell can't be swapping
        c1 = self.get_drop_offset(x, y-1) == 0 #there can't be anything dropping into the cell
        c2 = self.get_curr_fade(x-1,y) == 0
        return c0 and c1 and c2 and not self.can_drop(x,y)
    
    def has_falling_blocks(self, setup):
        islooking = False
        for column in range(setup.cells_per_row):
            for row in range(setup.cells_per_column-1, -1, -1): #go from bottom to top
                if self.can_drop(column, row):
                    islooking = True
                    
        return islooking
        

                            
                        



        


        
        


        
        


        
                        
        
        
        
                
                        
                        
                        
                    
                    
        
                
        


        
