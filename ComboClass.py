class Combo:
    
    def __init__(self):
        self.colors = set() #the number of colors in the combo, each represented by a number (see CellClass.py and "Important Implementation Detail" in GameClass.py)
        self.numblocks = 0 #how many blocks in the combo?
        self.numTX = 0 #how many TX combos? Again, see GameClass.py
        self.locations = set() #a set of tuples of (column, row)
        self.ischain = False