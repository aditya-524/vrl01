import pygame
import neat
import time
import os
import random
pygame.font.init() # Initialize pygame font

WIN_WIDTH = 500 # Window width
WIN_HEIGHT = 800 # Window height

# Load images for sprites
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50) # Font for the score


#TODO Define Classes for different objects

class Bird:
    IMGS = BIRD_IMGS # Images for bird
    MAX_ROTATION = 25 # How much the bird will tilt
    ROT_VEL = 20 # How much we will rotate on each frame
    ANIMATION_TIME = 5 # How long each bird animation will last

    def __init__(self, x, y): # Initialize bird object
        self.x = x # Starting x position
        self.y = y # Starting y position
        self.tilt = 0 # Starting tilt
        self.tick_count = 0 # Keeps track of how many times we moved since last jump
        self.vel = 0 # Starting velocity
        self.height = self.y # Keeps track of where the bird is
        self.img_count = 0 # Keeps track of which image we are currently showing
        self.img = self.IMGS[0] # Starting image

    def jump(self): # Make the bird jump
        self.vel = -10.5 # Negative velocity because top left is (0,0)
        self.tick_count = 0 # Reset tick count
        self.height = self.y # Keep track of where the bird jumped from
    
    def move(self): # Move the bird
        self.tick_count += 1 # Increment tic by k count
        d = self.vel*self.tick_count + 1.5*self.tick_count**2 # How many pixels we are moving up or down this frame

        if d >= 16: # If we are moving down more than 16 pixels
            d = 16 # Set d to 16
        
        if d < 0: # If we are moving up
            d -= 2 # Move up a little more

        self.y = self.y + d # Update y position

        if d < 0 or self.y < self.height + 50: # If we are moving up or we are above where we jumped from
            if self.tilt < self.MAX_ROTATION: # If we are not tilted too far up
                self.tilt = self.MAX_ROTATION # Tilt up
        else: # If we are moving down
            if self.tilt > -90: # If we are not tilted too far down
                self.tilt -= self.ROT_VEL # Tilt down
    
    def draw(self, win): # Draw the bird
        self.img_count += 1 # Increment image count

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0] # Show first image
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] # Show second image
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2] # Show third image
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0 # Reset image count

        if self.tilt <= -80: # If we are tilted too far down
            self.img = self.IMGS[1] # Show second image
            self.img_count = self.ANIMATION_TIME*2 # Set image count to 2 times animation time

        rotated_image = pygame.transform.rotate(self.img, self.tilt) # Rotate the image
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center) # Rotate the image around the center    
        win.blit(rotated_image, new_rect.topleft) # Draw the rotated image
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img) # Get the mask for the current image

class Pipe: # Pipe class
    GAP = 200 # Space between pipes
    VEL = 5 # How fast the pipes move

    def __init__(self, x): # Initialize pipe object
        self.x = x # Starting x position
        self.height = 0 # Starting height
        self.top = 0 # Top of pipe
        self.bottom = 0 # Bottom of pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) # Top pipe image
        self.PIPE_BOTTOM = PIPE_IMG # Bottom pipe image
        
        self.passed = False # If the bird has passed the pipe
        self.set_height() # Set the height of the pipe
    
    def set_height(self): # Set the height of the pipe
        self.height = random.randrange(50, 450) # Random height
        self.top = self.height - self.PIPE_TOP.get_height() # Top of pipe
        self.bottom = self.height + self.GAP # Bottom of pipe

    def move(self): # Move the pipe
        self.x -= self.VEL # Move the pipe

    def draw(self, win): # Draw the pipe
        win.blit(self.PIPE_TOP, (self.x, self.top)) # Draw the top pipe
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) # Draw the bottom pipe

    def collide(self, bird): # Check if the bird collides with the pipe
        bird_mask = bird.get_mask() # Get the mask for the bird
        top_mask = pygame.mask.from_surface(self.PIPE_TOP) # Get the mask for the top pipe
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM) # Get the mask for the bottom pipe
        top_offset = (self.x - bird.x, self.top - round(bird.y)) # Offset for top pipe    
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y)) # Offset for bottom pipe

        b_point = bird_mask.overlap(bottom_mask, bottom_offset) # Point of collision with bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset) # Point of collision with top pipe

        if t_point or b_point: # If we collide with either pipe
            return True # Return true
        return False # Return false
    
class Base: # Base class
    VEL = 5 # How fast the base moves
    WIDTH = BASE_IMG.get_width() # Width of the base
    IMG = BASE_IMG # Image for the base

    def __init__(self, y): # Initialize base object
        self.y = y # Starting y position
        self.x1 = 0 # Starting x position 1
        self.x2 = self.WIDTH # Starting x position 2

    def move(self): # Move the base
        self.x1 -= self.VEL # Move the base
        self.x2 -= self.VEL # Move the base
    
        if self.x1 + self.WIDTH < 0: # If the first base is off the screen
            self.x1 = self.x2 + self.WIDTH # Move the first base to the right of the second base
        if self.x2 + self.WIDTH < 0: # If the second base is off the screen
            self.x2 = self.x1 + self.WIDTH # Move the second base to the right of the first base
    
    def draw(self, win): # Draw the base
        win.blit(self.IMG, (self.x1, self.y)) # Draw the first base
        win.blit(self.IMG, (self.x2, self.y)) # Draw the second base
    


def draw_window(win, bird, pipes, base, score): # Draw the window
    win.blit(BG_IMG, (0,0)) # Draw the background

    for pipe in pipes: # For each pipe
        pipe.draw(win) # Draw the pipe
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255)) # Create the score text
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) # Draw the score text


    base.draw(win) # Draw the base
    bird.draw(win) # Draw the bird
    pygame.display.update() # Update the display, refreshes it 

def main(): # Main function
    bird = Bird(230,350) # Create a bird object
    base = Base(730) # Create a base object
    pipes = [Pipe(600)] # Create a pipe object
    score = 0 # Starting score
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # Create a window
    clock = pygame.time.Clock() # Create a clock
    
    run = True # Run the game
    while run: # While we are running
        clock.tick(30) # Tick the clock 30 times per second
        for event in pygame.event.get(): # Get all events
            if event.type == pygame.QUIT: # If we quit
                run = False # Stop running
        # bird.move() # Move the bird
        rem = [] # List of pipes to remove
        add_pipe = False # Add a pipe
        for pipe in pipes: # For each pipe
            if pipe.collide(bird): # If the bird collides with the pipe
                pass # Do nothing
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # If the pipe is off the screen
                rem.append(pipe) # Add the pipe to the list of pipes to remove
                pipes.remove(pipe) # Remove the pipe
            
            if not pipe.passed and pipe.x < bird.x: # If the bird has passed the pipe
                pipe.passed = True # Set passed to true
                pipes.append(Pipe(600)) # Add a new pipe
                add_pipe = True # Add a pipe

            pipe.move() # Move the pipe

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
            add_pipe = False
        
        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() >= 730: # If the bird hits the ground
            pass

        base.move() # Move the base
        draw_window(win, bird, pipes, base, score) # Draw the window
    pygame.quit() # Quit pygame
    quit() # Quit the program

main() # Run the main function





    

