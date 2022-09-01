import pygame
import random
import GameScreenClass


random.seed(1000) #the random seed is ONLY set for debugging to make things more predictable
# Initialize pygame
pygame.init()

gamescreen = GameScreenClass.GameScreen(["config.txt", ["player_diff_config.txt"]])
done = False

# -------- Main Program Loop -----------
while not done:
    
    done = gamescreen.play()
 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
print("Thanks for Playing!")
pygame.quit()