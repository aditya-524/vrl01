import pygame
import neat
import time
import os
import random

WIN_WIDTH = 500 # Window width
WIN_HEIGHT = 800 # Window height

# Load images for sprites
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

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
    

def draw_window(win, bird): # Draw the window
    win.blit(BG_IMG, (0,0)) # Draw the background
    bird.draw(win) # Draw the bird
    pygame.display.update() # Update the display, refreshes it 

def main(): # Main function
    bird = Bird(200, 200) # Create a bird object
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # Create a window
    clock = pygame.time.Clock() # Create a clock
    
    run = True # Run the game
    while run: # While we are running
        clock.tick(30) # Tick the clock 30 times per second
        for event in pygame.event.get(): # Get all events
            if event.type == pygame.QUIT: # If we quit
                run = False # Stop running
        bird.move() # Move the bird
        draw_window(win, bird) # Draw the window
    pygame.quit() # Quit pygame
    quit() # Quit the program

main() # Run the main function





    

