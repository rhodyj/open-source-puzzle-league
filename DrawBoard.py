import pygame

def draw_cursor(cursor, setup, screen, grid):
    pygame.draw.rect(screen,
                setup.WHITE,
                [(setup.cell_between + setup.cell_dimension) * cursor.cursor_x + setup.cell_between + setup.cell_dimension//2,
                (setup.cell_between + setup.cell_dimension) * cursor.cursor_y + setup.cell_between - grid.get_board_offset() + setup.cell_dimension//2,
                2*setup.cell_dimension+setup.cell_between,
                setup.cell_dimension],
                setup.cell_between)
    pygame.draw.lines(screen,
                setup.WHITE,
                False,
                (((setup.cell_between + setup.cell_dimension) * (cursor.cursor_x +1) + setup.cell_between//2 + setup.cell_dimension//2,
                    (setup.cell_between + setup.cell_dimension) * cursor.cursor_y + 2*setup.cell_between- grid.get_board_offset() + setup.cell_dimension//2),
                    ((setup.cell_between + setup.cell_dimension) * (cursor.cursor_x +1) + setup.cell_between//2 + setup.cell_dimension//2,
                    (setup.cell_between + setup.cell_dimension) * (cursor.cursor_y+1) - setup.cell_between- grid.get_board_offset() + setup.cell_dimension//2)),
                setup.cell_between)


def draw_frame(setup, screen):
        pygame.draw.rect(screen,
                         setup.WHITE,
                         [setup.cell_dimension//2,
                          setup.cell_dimension//2,
                          (setup.cell_between + setup.cell_dimension)*(setup.cells_per_row) + setup.cell_between,
                          (setup.cell_between + setup.cell_dimension)*(setup.cells_per_column)],
                         setup.cell_between)
        
def draw_border(setup, screen):
        pygame.draw.rect(screen,
                         setup.GREY,
                         [0,
                          0,
                          setup.display_width,
                          setup.display_height],
                         setup.cell_dimension - setup.cell_between)
        

def draw_board(setup, screen, grid, buffer, cursor, timer, scoreboard):
    screen.fill(setup.BLACK)
    # Draw the grid
    for column in range(setup.cells_per_row):

        color = setup.cell_type_array[buffer.get_color(column)]
        pygame.draw.rect(screen,
                         color,
                         [(setup.cell_between + setup.cell_dimension) * (column) + setup.cell_between + setup.cell_dimension//2,
                          (setup.cell_between + setup.cell_dimension) * (setup.cells_per_column) + setup.cell_between + setup.cell_dimension//2 - grid.get_board_offset(),
                          setup.cell_dimension,
                          setup.cell_dimension])
        
        for row in range(setup.cells_per_column):
            color = setup.cell_type_array[grid.get_color(column,row)]
            
        
            
            if color != setup.BLACK:
                pygame.draw.rect(screen,
                             color,
                             [(setup.cell_between + setup.cell_dimension) * (column) + setup.cell_between + grid.get_swap_offset(column, row) + setup.cell_dimension//2,
                              (setup.cell_between + setup.cell_dimension) * (row) + setup.cell_between + grid.get_drop_offset(column, row) + setup.cell_dimension//2 - grid.get_board_offset(), #draw from bottom up
                              setup.cell_dimension,
                              setup.cell_dimension])
            #if grid.can_drop(column, row):
            #    pygame.draw.rect(screen,
            #                 setup.WHITE,
            #                 [(setup.cell_between + setup.cell_dimension) * column + setup.cell_between + grid.get_swap_offset(column, row),
            #                  (setup.cell_between + setup.cell_dimension) * row + setup.cell_between + grid.get_drop_offset(column, row), #draw from bottom up
            #                  setup.cell_dimension//2,
            #                 setup.cell_dimension//2])
                
        
    
    if timer < 30:
        font = pygame.font.Font(pygame.font.get_default_font(), 16)          
        sbs = "Score: " + str(scoreboard.total_score)
        for pts in scoreboard.score_array:
            sbs = sbs + "\n\t" + str(pts[0]) + ": " + str(pts[1]) + " x" + str(pts[2]) 
        text = font.render(sbs, True, setup.GREEN, setup.BLACK)
        textRect = text.get_rect()  
        textRect.center = (3*setup.display_width/4, setup.display_height//10) 
        screen.blit(text, textRect)
                
    # Draw the Cursor
    if timer < 45:
        draw_cursor(cursor, setup, screen, grid)
        
    draw_frame(setup, screen)
    draw_border(setup, screen)
        