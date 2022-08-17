class Cell:
    def __init__(self, ctype, col, xoffset, yoffset, comtimer, jd):
        self.cell_type = ctype #types are border, block, empty, grey
        self.color = col
        self.swap_offset = xoffset
        self.drop_offset = yoffset
        self.combo_timer = comtimer
        self.just_dropped = jd
        
    