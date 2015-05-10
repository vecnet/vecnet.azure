# Natalie Sanders
# PyGame Primer

import pygame
from math import pi, atan2, sin, cos
import sys

class GameSpace:
    def main(self):
    
        # BASIC INITIALIZATION
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.init()
        
        self.url = "/afs/nd.edu/user37/cmc/Public/cse332_sp15/pygame_primer/media/"
        self.size = self.width, self.height = 640, 480
        self.black = 0, 0, 0
        
        # INITIALIZE MUSIC/SOUNDS
        pygame.mixer.music.load("./imperialmarch.wav")                       # LOAD MUSIC
        self.beamSound = pygame.mixer.Sound(self.url + "screammachine.wav")  # LOAD LASER BEAM SOUND
        self.explodeSound = pygame.mixer.Sound(self.url + "explode.wav")     # LOAD EXPLOSION SOUND        
        
        self.screen = pygame.display.set_mode(self.size)
        pygame.key.set_repeat(1, 50)
        
        # SET UP GAME OBJECTS
        self.clock = pygame.time.Clock()
        self.player = Player(self)
        self.target = Target(self)
        self.explosion = Explosion(self)
        
        # PLAY MUSIC
        pygame.mixer.music.play(-1)
        
        # START GAME LOOP
        running = True
        while running:
            # CLOCK TICK REGULATION (FRAMERATE)
            self.clock.tick(60)
            
            # HANDLE USER INPUTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    self.player.keyDown(event.key)  
                    
                if event.type == pygame.KEYUP:
                    self.player.keyUp(event.key)
            
            
            # SEND TICK TO ALL GAME OBJECTS
            
            self.player.tick()
            
            for laser in self.player.lasers:    # GIVE TICK TO ALL CURRENT LASER OBJECTS
                laser.tick()
                
            if self.target.life:                # GIVE TICK TO TARGET IF IT STILL HAS LIVES
                self.target.tick()
            elif not self.explosion.done:
                self.explosion.tick()           # GIVE TICK TO EXPLOSION IF TARGET HAS NO LIVES
            
            
            # DISPLAY GAME OBJECTS
            
            self.screen.fill(self.black)                                        # CLEAR SCREEN
            
            for laser in self.player.lasers:
                self.screen.blit(laser.image, laser.rect)                       # BLIT ALL CURRENT LASTERS TO SCREEN
                
            self.screen.blit(self.player.image, self.player.rect)               # BLIT PLAYER TO SCREEN
            
            if self.target.life:
                self.screen.blit(self.target.image, self.target.rect)           # BLIT TARGET TO SCREEN IF TARGET HAS LIVES LEFT
            elif not self.explosion.done:
                self.screen.blit(self.explosion.image, self.explosion.rect)     # BLIT EXPLOSION TO SCREEN IF TARGET HAS NO LIVES LEFT

            pygame.display.flip()
        
        
            
class Laser(pygame.sprite.Sprite):
    def __init__(self, pl=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.pl = pl
        self.onscreen = True
                
        self.image = pygame.image.load(self.pl.gs.url + "laser.png")
        self.rect = self.image.get_rect()
        self.orig_image = self.image
                           
        # CALCULATE LASER ANGLE
        mx, my = pygame.mouse.get_pos()
        self.lcx, self.lcy = self.rect.center
        #+ 2*self.dy
        self.angle = atan2(my - self.pl.pcy, mx - self.pl.pcx)
        
        self.dy = 10*sin(self.angle)
        self.dx = 10*cos(self.angle)
        
        # POSITION LASER
        self.rect = self.rect.move(self.pl.pcx-10, self.pl.pcy-10)
        self.angle = 0        
        
    def tick(self):        
        self.rect = self.rect.move(self.dx, self.dy)

    def move(self, dx, dy):
        new_rect = self.rect.move(dx, dy)
    
        if new_rect.right  < 640 or \
           new_rect.left   > 0   or \
           new_rect.bottom < 480 or \
           new_rect.top    > 0:
           
            self.rect = new_rect
        else:
            self.offscreen = True
    
    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, angle)
        
        
        
class Player(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.gs = gs
        self.image = pygame.image.load(self.gs.url + "deathstar.png")
        self.rect = self.image.get_rect()
        self.lasers = list()
        
        # KEEP ORIGINAL IMAGE TO LIMIT RESIZE ERRORS
        self.orig_image = self.image
        self.angle = 0
        
        # LASER FIRING FLAG
        self.tofire = False
        
    def tick(self):
        # GET MOUSE X AND Y POSITION ON SCREEN
        mx, my = pygame.mouse.get_pos()
        self.pcx, self.pcy = self.rect.center
        
        # PREVENT MOVEMENT WHILE FIRING
        if self.tofire:
            # EMIT LASER BEAM
            self.lasers.append(Laser(self))

        else:
            # CALCULATE ANGLE BTW CURRENT DIRECTION & MOUSE POSITION
            self.angle = -1*(atan2(my - self.pcy, mx - self.pcx)*(180/pi) + 45)
            
            # ROTATE IMAGE TO FACE MOUSE
            self.image = pygame.transform.rotate(self.orig_image, self.angle)
            self.rect = self.image.get_rect(center=[self.pcx, self.pcy])

            
    def updateLasers(self, update, move=False, rotate=False):
        if move:
            dx = update[0]
            dy = update[1]
            
            for l in self.lasers:
                l.move(dx, dy)
                
        if rotate:
            angle = rotate
            
            for l in self.lasers:
                l.rotate(angle)
            
    def keyDown(self, key):
            
        if key == pygame.K_DOWN: # down key
            new_rect = self.rect.move(0, 5)
            
            if not new_rect.bottom > 480:
                self.rect = new_rect
            
        elif key == pygame.K_UP: # up key
            new_rect = self.rect.move(0, -5)
            
            if not new_rect.top < 0:
                self.rect = new_rect
            
        elif key == pygame.K_RIGHT: # right key
            new_rect = self.rect.move(5, 0)
            
            if not new_rect.right > 640:
                self.rect = new_rect
            
        elif key == pygame.K_LEFT: # left key
            new_rect = self.rect.move(-5, 0)
            
            if not new_rect.left < 0:
                self.rect = new_rect
        
        elif key == pygame.K_SPACE:
            self.tofire = True
            self.gs.beamSound.play()
            
    def keyUp(self, key):
        
        if key == pygame.K_SPACE:
            self.tofire = False
        
            
class Target(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.gs = gs
        self.image = pygame.image.load(self.gs.url + "globe.png")
        self.rect = self.image.get_rect()
        self.rect.move_ip(300, 200)
        
        # KEEP TRACK OF HITS:
        self.life = 1000
        
        
    def tick(self):
    
        if self.life  <= 100:
            self.image = pygame.image.load(self.gs.url + "globe_red100.png")
    
        for laser in self.gs.player.lasers:
            collide = self.rect.colliderect(laser.rect)
            if collide:
                #del self.gs.player.lasers[collide_index]
                self.life = self.life - 1
                
            if not self.life:
                self.gs.explodeSound.play()
                break
                
class Explosion(pygame.sprite.Sprite):
    def __init__(self, gs=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.gs = gs
        self.image = pygame.image.load(self.gs.url + "explosion/frames000a.png")
        self.image
        self.rect = self.image.get_rect()
        self.rect.move_ip(300, 200)
        
        self.imageNo = 0
        self.done = False
        
    def tick(self):
        self.imageNo = self.imageNo + 1
        
        if self.imageNo > 16:
            self.done = True
        else:
            imageStr = "frames" + str(self.imageNo).zfill(3) + "a.png"
            self.image = pygame.image.load(self.gs.url + "explosion/" + imageStr)
        
        
        
        
        
                
        
if __name__ == '__main__':
    gs = GameSpace()
    gs.main()
    