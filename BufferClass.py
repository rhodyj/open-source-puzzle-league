import random

class Buffer:
    def __init__(self, setup):
        self.colorarray = []
        for column in range(setup.cells_per_column+2):
            self.colorarray.append(0)
        self.spawn_blocks(setup)
    
    def get_color(self, x):
        return self.colorarray[x+1]
    
    def spawn_blocks(self, setup):
        for column in range(setup.cells_per_row+2):
            if column == 0 or column == setup.cells_per_row+1:
                self.colorarray[column] = -1
            else:
                self.colorarray[column] = random.randint(0,4)
    

        
