import pygame
import neat
import time
import os
import random
import graphviz #To visuliaze the neural network
import visualize #To visuliaze the neural network
pygame.font.init() # Initialize pygame font

WIN_WIDTH = 500 # Window width
WIN_HEIGHT = 800 # Window height

GEN = 0 # Generation

# Load images for sprites
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50) # Font for the score


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
    


def draw_window(win, birds, pipes, base, score, gen): # Draw the window
    win.blit(BG_IMG, (0,0)) # Draw the background

    for pipe in pipes: # For each pipe
        pipe.draw(win) # Draw the pipe
    
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255)) # Create the score text
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10)) # Draw the score text

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255)) # Create the generation text
    win.blit(text, (10, 10)) # Draw the generation text

    base.draw(win) # Draw the base
    for bird in birds:
        bird.draw(win) # Draw the bird

    pygame.display.update() # Update the display, refreshes it 

def main(genomes, config): # Main function
    global GEN # Global generation
    GEN += 1 # Increment generation
    nets = [] # List of neural networks
    ge = [] # List of genomes
    birds = [] # List of birds]
    
    for _, g in genomes: # For each genome
        g.fitness = 0 # Set the fitness to 0
        net = neat.nn.FeedForwardNetwork.create(g, config) # Create a neural network
        nets.append(net) # Add the neural network to the list of neural networks
        birds.append(Bird(230,350)) # Add a bird
        ge.append(g) # Add the genome to the list of genomes

    base = Base(730) # Create a base object
    pipes = [Pipe(700)] # Create a pipe object
    score = 0 # Starting score
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) # Create a window
    clock = pygame.time.Clock() # Create a clock
    
    run = True # Run the game
    while run and len(birds) > 0: # While we are running
        clock.tick(30) # Tick the clock 30 times per second

        for event in pygame.event.get(): # Get all events
            if event.type == pygame.QUIT: # If we quit
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0 # Index of the pipe
        if len(birds) > 0: # If there are birds
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # If the bird has passed the first pipe
                pipe_ind = 1 # Set the pipe index to 1
        else: # If there are no birds #TODO check if this is irrelevant, i think it is cause we aare checcking in line 186 for 0 birds
            run = False # Stop running
            break            

        for x, bird in enumerate(birds): # For each bird
            ge[x].fitness += 0.1 # Increase the fitness of the bird
            bird.move() # Move the bird
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5: # If the output is greater than 0.5
                bird.jump() # Make the bird jump

        base.move() # Move the base

        rem = [] # List of pipes to remove
        add_pipe = False # Add a pipe
        
        for pipe in pipes: # For each pipe
            pipe.move() # Move the pipe
            for x, bird in enumerate(birds): # For each bird
                if pipe.collide(bird): # If the bird collides with the pipe
                    ge[x].fitness -= 1 # Decrease the fitness of the bird
                    birds.pop(x) # Remove the bird
                    nets.pop(x) # Remove the neural network
                    ge.pop(x) # Remove the genome
                        
            if not pipe.passed and pipe.x < bird.x: # If the bird has passed the pipe
                pipe.passed = True # Set passed to true
                add_pipe = True # Add a pipe

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # If the pipe is off the screen
                rem.append(pipe) # Add the pipe to the list of pipes to remove

        if add_pipe:
            score += 1
            for g in ge: # For each genome
                g.fitness += 5 # Increase the fitness of the bird

            pipes.append(Pipe(WIN_WIDTH)) # Add a pipe

        
        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds): # For each bird
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: # If the bird hits the ground
                birds.pop(x) # Remove the bird
                nets.pop(x) # Remove the neural network
                ge.pop(x) # Remove the genome
        
        draw_window(win, birds, pipes, base, score, GEN) # Draw the window
        visualize.draw_net(config, g, filename=f'neural_net_{GEN}.png')

def draw_net(config, genome, filename):
    """ Receives a genome and draws a neural network with arbitrary topology. """
    # Create a PyDot graph object
    dot = graphviz.Digraph(comment='Neural Network')

    # Add nodes for each neuron in the genome
    for node in genome.nodes:
        if node.type == 'INPUT':
            dot.node(str(node.id), shape='circle', style='filled', fillcolor='lightblue')
        elif node.type == 'OUTPUT':
            dot.node(str(node.id), shape='doublecircle', style='filled', fillcolor='lightblue')
        else:
            dot.node(str(node.id), shape='circle')

    # Add edges for each connection in the genome
    for conn in genome.connections.values():
        if conn.enabled:
            dot.edge(str(conn.in_node), str(conn.out_node), label=str(round(conn.weight, 2)))

    # Save the graph to a file
    dot.render(filename, format='png')
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, 
                                config_path) # Get the config file
    p = neat.Population(config) # Create a population
    p.add_reporter(neat.StdOutReporter(True)) # Add a reporter, optional to give out output in the console #TODO check for visual 
    stats = neat.StatisticsReporter() # Create a statistics reporter
    p.add_reporter(stats) # Add the statistics reporter

    winner = p.run(main, 50) # Run the main function 50 times, return the winner
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner)) # Print the best genome
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) # Get the directory of the current file
    config_path = os.path.join(local_dir, "config-feedforward.txt") # Get the path to the config file
    run(config_path) # Run the config file





    

