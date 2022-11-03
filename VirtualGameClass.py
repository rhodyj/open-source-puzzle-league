import pygame
import copy

import GridClass
import SetupClass
import CellClass


import ComboClass

#THIS CLASS IS NOT USED IN ANY WAY RIGHT NOW. Will probably be rewritten as a subclass when the overhaul has progressed enough

class VirtualGame:
    
    def __init__(self, actualsetup, actualcursor, playernumber):
        
        self.vsetup = SetupClass.Setup(copy.deepcopy(actualsetup.cell_dimension), copy.deepcopy(actualsetup.cells_per_row), copy.deepcopy(actualsetup.cells_per_column), copy.deepcopy(actualsetup.cell_between), 2, copy.deepcopy(actualsetup.cell_swap_speed), 2, 0, 0, 0)
        self.vsetup.combo_fade_time = 1
        self.vsetup.cell_drop_speed = 60 #BADBAD HARDCODE. REPLACE WITH framerate variable at some point
        self.vgrid = GridClass.Grid(self.vsetup)
        self.vcursor = actualcursor
        self.vplayernumber = playernumber
        self.goals = set()
        
        self.vgcq = set()
        
    def v_copy_grid(self, actualgrid):
        self.vgrid.set_board_offset(copy.deepcopy(actualgrid.get_board_offset()))
        
        for column in range(self.vsetup.cells_per_row+2): #white blocks for bounding
            
            for row in range(self.vsetup.cells_per_column+2):
                
                if row == 0 or row == self.vsetup.cells_per_column+1 or column == 0 or column == self.vsetup.cells_per_row + 1:
                    cell = CellClass.Cell("border",2, 0, 0, 0)
                else:
                    cell = CellClass.Cell(copy.deepcopy(actualgrid.get_type(column-1, row-1)), copy.deepcopy(actualgrid.get_color(column-1, row-1)), copy.deepcopy(actualgrid.get_offset(column-1, row-1)), copy.deepcopy(actualgrid.get_drop_offset(column-1, row-1)), copy.deepcopy(actualgrid.get_curr_fade(column-1, row-1)))
                    
                self.vgrid.cell_grid[column][row] = cell
                
    def v_copy_gcq(self, actualgcq):
        self.vgcq.queue = copy.deepcopy(actualgcq.queue)
        self.vgcq.active_combo = 1
        self.vgcq.time_buffer = 0
    
    def reset_goals(self):
        self.goals = set()

    def v_swap_blocks(self, b1, b2):
        foo = self.vgrid.get_color(b1[0], b1[1])
        foop1 = self.vgrid.get_color(b2[0], b2[1])

        for c in self.vgcq.queue:
            if (b1[0], b1[1], foo) in c.locations:
                c.locations.remove((b1[0], b1[1], foo))
                c.locations.add((b2[0], b2[1], foo))
            elif (b2[0], b2[1], foop1) in c.locations:
                c.locations.remove((b2[0], b2[1], foop1))
                c.locations.add((b1[0], b1[1], foop1))  
        
        self.vgrid.set_color(b1[0], b1[1], foop1)
        self.vgrid.set_color(b2[0], b2[1], foo)

    def v_clean(self, combolist):
        
        tmpcombo = ComboClass.Combo()
        
        for c0 in combolist.copy(): #for each combo in the list of combos
            isbad = False
            for loc in c0.locations:
                if self.vgrid.can_drop(loc[0], loc[1]):
                    isbad = True
            if c0.numblocks < 3 or c0.color < 3 or isbad:
                combolist.remove(c0) #remove small, "black/white", or redundant combos
    
        for c0 in combolist.copy():
            tmpcombo.numblocks += c0.numblocks
            for loc in c0.locations:
                tmpcombo.locations.add((loc[0], loc[1], self.vgrid.get_color(loc[0], loc[1])))
            
        tmpcombo.timeleft = tmpcombo.numblocks*self.vsetup.combo_fade_time
        
        return tmpcombo
    
    def v_can_hcombo(self, column, row):
        color = self.vgrid.get_color(column, row)
        
        numleft = 0
        counterleft = 1
        
        while (column-counterleft, row) not in self.goals and self.vgrid.can_swap(column-counterleft, row): #canswapright might need reworking
            if self.vgrid.get_color(column-counterleft, row) == color:
                numleft += 1
            counterleft += 1
        
        numright = 0
        counterright = 1
        while (column+counterright, row) not in self.goals and self.vgrid.can_swap(column+counterright, row): #canswapleft might need some reworking
            if self.vgrid.get_color(column+counterright, row) == color:
                numright += 1
            counterright += 1
                
        return (numleft, numright)
    
    def v_can_vcombo(self, column, row):
        color = self.vgrid.get_color(column, row)
        
        numdown = 1
        foundinrow = True
        
        while foundinrow:
            foundinrow = False
            
            leftdata = self.v_find_next_left_block((column, row+numdown), color)
            
            rightdata = self.v_find_next_right_block((column, row+numdown), color)
                
            if (leftdata != (-1, -1) or rightdata != (-1,-1) or self.vgrid.get_color(column,row+numdown) == color) and (column, row+numdown) not in self.goals:
                numdown += 1
                foundinrow = True
            
        return numdown - 1
    
    def v_find_next_left_block(self, comblo, tc):
        offsetcounter = 0
        
        while self.vgrid.get_color(comblo[0]-offsetcounter, comblo[1]) != tc and self.vgrid.get_color(comblo[0]-offsetcounter, comblo[1]) != 2 and (comblo[0]-offsetcounter, comblo[1]) not in self.goals:
            offsetcounter += 1
            
        if self.vgrid.get_color(comblo[0]-offsetcounter, comblo[1]) == tc and self.vgrid.get_color(comblo[0]-offsetcounter, comblo[1]) != 2 and (comblo[0]-offsetcounter, comblo[1]) not in self.goals:
            return (comblo[0]-offsetcounter, comblo[1])
        else:
            return (-1, -1)
        
    def v_find_next_right_block(self, comblo, tc):
        offsetcounter = 0
        
        while self.vgrid.get_color(comblo[0]+offsetcounter, comblo[1]) != tc and self.vgrid.get_color(comblo[0]+offsetcounter, comblo[1]) != 2 and (comblo[0] + offsetcounter, comblo[1]) not in self.goals:
            offsetcounter += 1
            
        if self.vgrid.get_color(comblo[0]+offsetcounter, comblo[1]) == tc and self.vgrid.get_color(comblo[0]+offsetcounter, comblo[1]) != 2 and (comblo[0] + offsetcounter, comblo[1]) not in self.goals:
            return (comblo[0]+offsetcounter, comblo[1])
        else:
            return (-1, -1)
    
    def v_find_next_left_move(self, comblo):
        targetcolor = self.vgrid.get_color(comblo[0], comblo[1])
        
        offsetcounter = 1
        numcolors = 1
        
        while self.vgrid.get_color(comblo[0]-offsetcounter, comblo[1]) == targetcolor:
            numcolors += 1
            offsetcounter += 1
            
        if numcolors >= 3:
            return "DONOTHING"
        else:
            tmpcomblo = (comblo[0] - offsetcounter, comblo[1])
            nextblockleft = self.v_find_next_left_block(tmpcomblo, targetcolor)
            
            if nextblockleft != (-1, -1):
                if self.vcursor.x > nextblockleft[0]:
                    return "MOVELEFT"
                elif self.vcursor.x < nextblockleft[0]:
                    return "MOVERIGHT"
                else:
                    return "SWAP"
            else:
                return "DONOTHING"
            
    def v_find_next_right_move(self, comblo):
        targetcolor = self.vgrid.get_color(comblo[0], comblo[1])
        
        offsetcounter = 1
        numcolors = 1
        
        while self.vgrid.get_color(comblo[0]+offsetcounter, comblo[1]) == targetcolor:
            numcolors += 1
            offsetcounter += 1
            
        if numcolors >= 3:
            return "DONOTHING"
        else:
            tmpcomblo = (comblo[0] + offsetcounter, comblo[1])
            nextblockright = self.v_find_next_right_block(tmpcomblo, targetcolor)
                
            if nextblockright != (-1, -1):
                if self.vcursor.x + 1 > nextblockright[0]:
                    return "MOVELEFT"
                elif self.vcursor.x + 1 < nextblockright[0]:
                    return "MOVERIGHT"
                else:
                    return "SWAP"
            else:
                return "DONOTHING"
            
    def v_find_next_down_move(self, comblo):
        targetcolor = self.vgrid.get_color(comblo[0], comblo[1])
        
        downoffset = 1
        
        while self.vgrid.get_color(comblo[0], comblo[1] + downoffset) == targetcolor:
            downoffset += 1
            
        if downoffset >= 3:
            return "DONOTHING"
        else:
            vdiff = self.vcursor.y - (comblo[1] + downoffset)
            if vdiff < 0:
                return "MOVEDOWN"
            elif vdiff > 0:
                return "MOVEUP"
            else:
                tmpcomblo = (comblo[0], comblo[1] + downoffset)
                nextblockleft = self.v_find_next_left_block(tmpcomblo, targetcolor)
                nextblockright = self.v_find_next_right_block(tmpcomblo, targetcolor)
                
                if nextblockleft != (-1,-1):
                    if self.vcursor.x > nextblockleft[0]:
                        return "MOVELEFT"
                    elif self.vcursor.x < nextblockleft[0]:
                        return "MOVERIGHT"
                    else:
                        return "SWAP"
                elif nextblockright != (-1,-1):
                    if self.vcursor.x + 1 > nextblockright[0]:
                        return "MOVELEFT"
                    elif self.vcursor.x +1 < nextblockright[0]:
                        return "MOVERIGHT"
                    else:
                        return "SWAP"
                else:
                    return "MOVEDOWN"

    def v_combo_scan(self):
        centralblock = (self.vcursor.x, self.vcursor.y, "null")
        
        for column in range(self.vsetup.cells_per_row):
            for row in range(self.vsetup.cells_per_column):
                if (column, row) in self.goals and self.vgrid.get_color(column, row) > 2:
                    cd = self.v_can_hcombo(column, row) #store an ordered pair
                    numleft = cd[0]
                    numright = cd[1]
                    numdown = self.v_can_vcombo(column,row)
                    if numleft >= 2:
                        centralblock = (column, row, "left")
                    elif numright >= 2:
                        centralblock = (column, row, "right")
                    elif numleft + numright >= 2:
                        centralblock = (column, row, "leftright")
                    elif numdown >= 2:
                        centralblock = (column, row, "down")
        
        if centralblock[2] == "null" and self.vgrid.get_color(self.vcursor.x, self.vcursor.y) > 2:
            cd = self.v_can_hcombo(self.vcursor.x, self.vcursor.y)
            numleft = cd[0]
            numright = cd[1]
            numdown = self.v_can_vcombo(self.vcursor.x, self.vcursor.y)
            if numleft >= 2:
                self.goals.add((self.vcursor.x, self.vcursor.y))
                centralblock = (self.vcursor.x, self.vcursor.y, "left")
            elif numright >= 2:
                self.goals.add((self.vcursor.x, self.vcursor.y))
                centralblock = (self.vcursor.x, self.vcursor.y, "right")
            elif numleft + numright >= 2:
                self.goals.add((self.vcursor.x, self.vcursor.y))
                centralblock = (self.vcursor.x, self.vcursor.y, "leftright")   
            elif numdown >= 2:
                self.goals.add((self.vcursor.x, self.vcursor.y))
                centralblock = (self.vcursor.x, self.vcursor.y, "down")
        
        if centralblock[2] == "left":
            vdiff = self.vcursor.y - centralblock[1]
            if vdiff < 0:
                return "MOVEDOWN"
            elif vdiff > 0:
                return "MOVEUP"
            else:
                return self.v_find_next_left_move(centralblock)
        elif centralblock[2] == "right":
            vdiff = self.vcursor.y - centralblock[1]
            if vdiff < 0:
                return "MOVEDOWN"
            elif vdiff > 0:
                return "MOVEUP"
            else:
                return self.v_find_next_right_move(centralblock)
        elif centralblock[2] == "leftright":
            vdiff = self.vcursor.y - centralblock[1]
            if vdiff < 0:
                return "MOVEDOWN"
            elif vdiff > 0:
                return "MOVEUP"
            else:
                foo = self.v_find_next_left_move(centralblock)
                if foo == "DONOTHING":
                    return self.v_find_next_right_move(centralblock)
                else:
                    return foo
        elif centralblock[2] == "down":
            foo = self.v_find_next_down_move(centralblock)
            return foo
        else:
            self.reset_goals()
            return "WANDER"
    
    def v_eval_board(self):
        griddata = []
        for column in range(self.vsetup.cells_per_row):
            griddata.append(0)
            for row in range(self.vsetup.cells_per_row-1, -1, -1):
                griddata[column] = row
        return 1
            
    def v_find_move(self):
        if self.v_eval_board() > 2:
            return self.v_fix_board()
        else:
            return self.v_combo_scan()
        
    def v_move_blocks(self):
        for column in range(self.vsetup.cells_per_row):
            for row in range(self.vsetup.cells_per_column):
                if self.vgrid.get_offset(column, row) > 0:
                    self.vgrid.set_swap_offset(column, row, self.vgrid.get_offset(column, row) + self.vsetup.cell_swap_speed)
                elif self.vgrid.get_offset(column, row) < 0:
                    self.vgrid.set_swap_offset(column, row, self.vgrid.get_offset(column, row) - self.vsetup.cell_swap_speed)
                if self.vgrid.get_offset(column, row) > self.vsetup.cell_dimension:
                    self.v_swap_blocks((column, row), (column+1, row))
                    self.vgrid.set_swap_offset(column, row, 0)
                    
                elif self.vgrid.get_offset(column, row) < -1*self.vsetup.cell_dimension:
                    self.vgrid.set_swap_offset(column, row, 0)
                        
    def v_pop_combos(self, combo):
        for row in range(self.vsetup.cells_per_column-1, -1, -1):
            for column in range(self.vsetup.cells_per_row):
                #if column in combo.locations[0] and row in combo.locations[1]:
                if (column, row, self.vgrid.get_color(column, row)) in combo.locations:
                    if self.vgrid.get_curr_fade(column, row) == 0 and self.vgrid.get_color(column, row) > 2:
                        self.vgrid.set_curr_fade(column, row, 1) #mark all combos to be popped
                        combo.timeleft -= 1
                        #print("Marking for deletion: " + str((column, row))) 
                    if self.vgrid.get_curr_fade(column, row) > 0:

                        if self.vgrid.get_curr_fade(column, row) == 1:
                            pygame.mixer.Sound.play(self.vsetup.action_sounds[0])#PLAY EXPLOSION SOUND
                            combo.locations.remove((column, row, self.vgrid.get_color(column,row)))
                            combo.locations.add((column, row, 1))
                            self.vgrid.set_color(column,row, 1)
                        

                        self.vgrid.set_curr_fade(column, row, self.vgrid.get_curr_fade(column, row) + 1)
                        combo.timeleft -= 1
                        if self.vgrid.get_curr_fade(column, row) == self.vsetup.combo_fade_time:
                            self.vgrid.set_curr_fade(column, row, 0)

                            #print(str(self.vgrid.get_curr_fade(column, row)) + " tics left for " + str((column, row)))

        #if combo.timeleft == 0:
        #    for x in combo.locations:
        #        print("\t" + str(self.vgrid.get_curr_fade(x[0], x[1])))
    def v_combo_blocks(self):
        for cq in self.vgcq.queue:  #pop blocks until they go black
            for c in cq.locations:
                self.vgrid.set_color(c[0], c[1], 0)
                self.vgrid.set_curr_fade(c[0], c[1], 0)
                self.goals.add((c[0], c[1]))
            self.vgcq.queue.remove(cq)
            
    
    def v_drop_blocks(self):
        for column in range(self.vsetup.cells_per_row):
            for row in range(self.vsetup.cells_per_column-1, -1, -1): #go from bottom to top
                if self.vgrid.can_drop(column, row): #if the next lowest block is empty, but not a part of a combo
                    if self.vgrid.get_drop_offset(column, row) == 0:
                        initialoffset = self.vsetup.cell_dimension % self.vsetup.cell_drop_speed
                        if initialoffset == 0:
                            initialoffset = self.vsetup.cell_swap_speed
                        self.vgrid.set_drop_offset(column, row, initialoffset)
                    elif self.vgrid.get_drop_offset(column, row) >= self.vsetup.cell_dimension:
                        self.vgrid.set_drop_offset(column, row, 0)
                        self.v_swap_blocks((column, row), (column, row+1))
                    elif self.vgrid.get_drop_offset(column, row) > 0:
                        self.vgrid.set_drop_offset(column, row, self.vgrid.get_drop_offset(column, row) + self.vsetup.cell_drop_speed)

        
    def v_draw_cursor(self, screen):
        hoff = self.vsetup.display_width*(2+2*self.vplayernumber)

        pygame.draw.rect(screen,
            self.vsetup.WHITE,
            [(self.vsetup.cell_between + self.vsetup.cell_dimension) * self.vcursor.x + self.vsetup.cell_between + self.vsetup.cell_dimension//2 + hoff,
            (self.vsetup.cell_between + self.vsetup.cell_dimension) * self.vcursor.y + self.vsetup.cell_between - self.vgrid.get_board_offset() + self.vsetup.cell_dimension//2,
            2*self.vsetup.cell_dimension+self.vsetup.cell_between,
            self.vsetup.cell_dimension],
            self.vsetup.cell_between)
        pygame.draw.lines(screen,
            self.vsetup.WHITE,
            False,
            (((self.vsetup.cell_between + self.vsetup.cell_dimension) * (self.vcursor.x +1) + self.vsetup.cell_between//2 + self.vsetup.cell_dimension//2 + hoff,
                (self.vsetup.cell_between + self.vsetup.cell_dimension) * self.vcursor.y + 2*self.vsetup.cell_between- self.vgrid.get_board_offset() + self.vsetup.cell_dimension//2),
                ((self.vsetup.cell_between + self.vsetup.cell_dimension) * (self.vcursor.x +1) + self.vsetup.cell_between//2 + self.vsetup.cell_dimension//2 + hoff,
                (self.vsetup.cell_between + self.vsetup.cell_dimension) * (self.vcursor.y+1) - self.vsetup.cell_between- self.vgrid.get_board_offset() + self.vsetup.cell_dimension//2)),
            self.vsetup.cell_between) 
        
    def v_draw_frame(self, screen):
        hoff = self.vsetup.display_width*(2+2*self.vplayernumber)
        
        pygame.draw.rect(screen,
                         self.vsetup.WHITE,
                         [self.vsetup.cell_dimension//2 + hoff,
                          self.vsetup.cell_dimension//2,
                          (self.vsetup.cell_between + self.vsetup.cell_dimension)*(self.vsetup.cells_per_row) + self.vsetup.cell_between,
                          (self.vsetup.cell_between + self.vsetup.cell_dimension)*(self.vsetup.cells_per_column)],
                         self.vsetup.cell_between)
         
    def v_draw_board(self, screen, timer):
        hoff = self.vsetup.display_width*(2*(self.vplayernumber+1))

        for column in range(self.vsetup.cells_per_row):
            for row in range(self.vsetup.cells_per_column):
                index = self.vgrid.get_color(column, row)
                if index > 2:
                        sprite = self.vsetup.cell_type_array[index-3]
                        screen.blit(sprite, ((self.vsetup.cell_between + self.vsetup.cell_dimension) * (column) + self.vsetup.cell_between + self.vgrid.get_offset(column, row) + self.vsetup.cell_dimension//2 + hoff,
                                         (self.vsetup.cell_between + self.vsetup.cell_dimension) * (row) + self.vsetup.cell_between + self.vgrid.get_drop_offset(column, row) + self.vsetup.cell_dimension//2 - self.vgrid.get_board_offset()))
                
                if (column, row) in self.goals:
                    pygame.draw.rect(screen,
                             self.vsetup.WHITE,
                             [(self.vsetup.cell_between + self.vsetup.cell_dimension) * (column) + self.vsetup.cell_between + self.vgrid.get_offset(column, row) + self.vsetup.cell_dimension//2 + hoff,
                                         (self.vsetup.cell_between + self.vsetup.cell_dimension) * (row) + self.vsetup.cell_between + self.vgrid.get_drop_offset(column, row) + self.vsetup.cell_dimension//2 - self.vgrid.get_board_offset(),
                              self.vsetup.cell_dimension//2,
                              self.vsetup.cell_dimension//2])
        # Draw the Cursor
        if timer < 45:
            self.v_draw_cursor(screen)
            
        self.v_draw_frame(screen)
        
    def v_gameloop(self):
        self.v_move_blocks()
        self.v_drop_blocks()
        self.v_combo_blocks()        
        
            

        
        
        
        
                
        
        
