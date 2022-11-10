class ProtoCombo:
    def __init__(self):
        self.colors = set() #the number of colors in the combo, each represented by a number (see CellClass.py and "Important Implementation Detail" in GameClass.py)
        self.numblocks = 0 #how many blocks in the combo?
        self.numTX = 0 #how many TX combos? Again, see GameClass.py
        self.locationdata = set()

class Combo(ProtoCombo):
    def __init__(self, comboid, chainid):
        super().__init__()
        self.locations = [] #a list of tuples of coordinates of the form (column, row)
        self.combo_id = comboid #an ID number for the combo. Used for planned uniqueness checking. A value of -1 is used for unprocessed combos as a placeholder
        self.chain_id = chainid #an ID for the chain the combo. Similar to above
