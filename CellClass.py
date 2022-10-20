class Cell:
    def __init__(self, ctype, col, xoffset, yoffset, comtimer, jd):
        self.cell_type = ctype #types are border, block, empty, grey
        self.color = col #color is represented by a number which is used to call an image from an array, with -1 being a catch-all "color" for non-blocks
        self.swap_offset = xoffset
        self.drop_offset = yoffset
        self.combo_timer = comtimer
        self.just_dropped = jd