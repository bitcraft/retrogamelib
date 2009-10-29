import pygame
import os
import sys
import math

sys.path.insert(0, "..")
from retrogamelib import gameobject
from retrogamelib import button
from retrogamelib.constants import *
from retrogamelib.util import *

class Collidable(gameobject.Object):
    
    def __init__(self):
        gameobject.Object.__init__(self, self.groups)
        self.offsetx = 0
        self.offsety = 0
        self.always_update = False
    
    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.x + self.offsetx, 
            self.rect.y - camera.y + self.offsety))
            
    def on_collision(self, dx, dy):
        pass
    
    def get_surrounding(self, pos):
        center = (pos[0], pos[1])
        topleft     = (pos[0]-1, pos[1]-1)
        midtop      = (pos[0],   pos[1]-1)
        topright    = (pos[0]+1, pos[1]-1)
        midleft     = (pos[0]-1, pos[1])
        midright    = (pos[0]+1, pos[1])
        bottomleft  = (pos[0]-1, pos[1]+1)
        midbottom   = (pos[0],   pos[1]+1)
        bottomright = (pos[0]+1, pos[1]+1)
        return (topleft, midtop, topright, midleft, midright,
            bottomleft, midbottom, bottomright, center)
    
    def move(self, dx, dy, tiles):
        sides = [0, 0, 0, 0]
        tile_pos = (self.rect.centerx//16, self.rect.centery//16)
        
        coltiles = []
        for pos in self.get_surrounding(tile_pos):
            if pos[0] > -1 and pos[0] < len(tiles[0]) and \
                pos[1] > -1 and pos[1] < len(tiles):
                tile = tiles[pos[1]][pos[0]]
                if isinstance(tile, Platform):
                    coltiles.append(tile)
        
        if dx != 0:
            self.__move(dx, 0, coltiles)
        if dy != 0:
            self.__move(0, dy, coltiles)
    
    def __move(self, dx, dy, tiles):
        self.rect.x += dx
        self.rect.y += dy
        collided = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if tile.slant == 0:
                    self.rect_respond(dx, dy, tile)
                else:
                    self.slant_respond(dx, dy, tile)
    
    def rect_respond(self, dx, dy, tile):
        if dx > 0:
            self.rect.right = tile.rect.left
        elif dx < 0:
            self.rect.left = tile.rect.right
        if dy > 0:
            self.rect.bottom = tile.rect.top
        elif dy < 0:
            self.rect.top = tile.rect.bottom
        self.on_collision(dx, dy)
    
    def slant_respond(self, dx, dy, tile):
        top = None
        if tile.slant < 0:
            if self.rect.left >= tile.rect.left:
                x = self.rect.left - tile.rect.left
                top = tile.rect.top+x-1
        if tile.slant > 0:
            if self.rect.right <= tile.rect.right:
                x = tile.rect.right - self.rect.right
                top = tile.rect.top+x-1
        if top:
            if self.rect.bottom > top:
                self.rect.bottom = top
                self.on_collision(0, dy)

class Player(Collidable):
    
    def __init__(self):
        Collidable.__init__(self)
       
        self.right_images = [
            load_image("data/bubbman-1.png"),
            load_image("data/bubbman-2.png"),
            load_image("data/bubbman-4.png"),
            load_image("data/bubbman-5.png"),
        ]
        self.left_images = []
        for img in self.right_images:
            self.left_images.append(pygame.transform.flip(img, 1, 0))
       
        self.images = self.right_images
        self.image = self.images[0]
        self.rect = pygame.Rect(8, 16, 6, 16)
       
        self.facing = 1
        self.jump_speed = 0
        self.frame = 0
        self.jumping = True
        self.punch_time = 0
        self.offsetx = -5
        self.z = 0
    
    def punch(self):
        if self.punch_time <= 0:
            self.punch_time = 5
    
    def on_collision(self, dx, dy):        
        if dy > 0 or dy < 0:            
            self.jump_speed = 2       
        if dy > 0:            
            self.jumping = False    

    def update(self, tiles):
        self.frame += 1
        imgframe = 0
        if self.punch_time > 0:
            self.punch_time -= 1
        
        moving = False
        if button.is_held(LEFT) and self.punch_time <= 0:
            self.facing = -1
            moving = True
            self.move(-2, 0, tiles)
        if button.is_held(RIGHT) and self.punch_time <= 0:
            self.facing = 1
            moving = True
            self.move(2, 0, tiles)
        if button.is_pressed(A_BUTTON) and self.punch_time <= 0:
            if not self.jumping:
                play_sound("data/jump.ogg")
                self.jump_speed = -5
                self.jumping = True
        if button.is_pressed(B_BUTTON):
            self.punch()
        
        if self.facing < 0:
            self.images = self.left_images
        else:
            self.images = self.right_images
        
        if moving:
            imgframe = self.frame/3%2
        if self.jumping:
            imgframe = 1
        if self.punch_time > 0:
            imgframe = 3
        if self.punch_time == 3:
            Punch(self)
            play_sound("data/swoosh.ogg")
        if self.punch_time > 3:
            imgframe = 2
        
        self.image = self.images[imgframe]
        
        if button.is_held(A_BUTTON):
            self.jump_speed += 0.4
        else:
            self.jump_speed += 0.8
        if self.jump_speed > 5:
            self.jump_speed = 5
        
        if self.punch_time <= 0:
            self.move(0, self.jump_speed, tiles)
        if self.jump_speed > 3:
            self.jumping = True

class Punch(Collidable):
    
    def __init__(self, player):
        Collidable.__init__(self)
        self.image = pygame.Surface((1, 1))
        self.image.set_alpha(0)
        self.rect = pygame.Rect(0, 0, 12, 12)
        self.life = 2
        self.player = player
        self.always_update = True
    
    def update(self, tiles):
        gameobject.Object.update(self)
        self.rect.center = (self.player.rect.centerx + (8*self.player.facing), self.player.rect.centery)
        self.life -= 1
        if self.life <= 0:
            self.rect.centerx += self.player.facing*4
            Poof(self.rect.center)
            self.kill()

class Platform(Collidable):
    
    def __init__(self, pos, imagepos, slant=0):
        Collidable.__init__(self)
        self.sheet = load_image("data/platform.png")
        self.image = pygame.Surface((16, 16))
        self.image.set_colorkey((0, 0, 0), pygame.RLEACCEL)
        self.image.blit(self.sheet, (-imagepos[0]*16, 
            -imagepos[1]*16, 16, 16))
        self.rect = self.image.get_rect(topleft = pos)
        self.slant = slant  #1 for up slope right, -1 for down slope right
        self.z = -3
        
    def update(self, tiles):
        gameobject.Object.update(self)

class Baddie(Collidable):
    
    def __init__(self, pos):
        Collidable.__init__(self)
        self.left_images = [
            load_image("data/baddie-1.png"), 
            load_image("data/baddie-2.png"),
        ]
        self.right_images = []
        for img in self.left_images:
            self.right_images.append(pygame.transform.flip(img, 1, 0))
        self.images = self.left_images
        
        self.image = self.images[0]
        self.rect = pygame.Rect(pos[0], pos[1], 8, 11)
        self.offsetx = -2
        self.frame = 0
        self.dx = -1
        self.z = -1
    
    def update(self, tiles):
        self.frame += 1
        self.image = self.images[self.frame/4%2]
        self.move(self.dx, 3, tiles)
        if self.dx > 0:
            self.images = self.right_images
        else:
            self.images = self.left_images
        
    def on_collision(self, dx, dy):
        if dx < 0 or dx > 0:
            self.dx = -self.dx

class Coin(Collidable):
    
    def __init__(self, pos):
        Collidable.__init__(self)
        self.images = [
            load_image("data/coin-1.png"), load_image("data/coin-2.png"),
            load_image("data/coin-3.png"), load_image("data/coin-4.png"),
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame = 0
        self.always_update = True
        self.z = -2
    
    def update(self, tiles):
        self.frame += 1
        self.image = self.images[self.frame/4%4]

class Points(Collidable):
    
    def __init__(self, score, pos, font):
        Collidable.__init__(self)
        self.image = font.render("%d" % score)
        self.rect = self.image.get_rect(center = pos)
        self.life = 20
        self.z = 10
    
    def update(self, tiles):
        self.life -= 1
        if self.life <= 0:
            self.kill()
        self.rect.move_ip(0, -1)

class Poof(Collidable):
    
    def __init__(self, pos):
        Collidable.__init__(self)
        self.images = [
            load_image("data/poof-1.png"), load_image("data/poof-2.png"),
            load_image("data/poof-3.png"),
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
        self.frame = 0
    
    def update(self, tiles):
        self.frame += 1
        self.image = self.images[self.frame/2%3]
        if self.frame >= 6:
            self.kill()

class BaddieDeath(Collidable):
    
    def __init__(self, baddie, pos):
        Collidable.__init__(self)
        self.image = pygame.transform.flip(baddie.image, 0, 1)
        self.rect = self.image.get_rect(center = pos)
        self.frame = 0
        self.dy = -3
    
    def update(self, tiles):
        self.dy += 0.5
        self.rect.y += self.dy
        if self.rect.y > 200:
            self.kill()

class Death(Collidable):
    
    def __init__(self, pos):
        Collidable.__init__(self)
        self.image = load_image("data/bubbman-3.png")
        self.rect = self.image.get_rect(center = pos)
        self.x = self.rect.centerx
        self.jump_speed = -10
        self.life = 100
    
    def update(self, tiles):
        if self.rect.top > 200:
            self.kill()
        self.jump_speed += 0.5
        self.rect.move_ip(0, self.jump_speed)

class Spring(Collidable):
    
    def __init__(self, pos):
        Collidable.__init__(self)
        self.images = [
            load_image("data/spring-1.png"), load_image("data/spring-2.png"),
        ]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.bouncing = 0
    
    def bounce(self):
        self.bouncing = 2
    
    def update(self, tiles):
        if self.bouncing > 0:
            self.bouncing -= 1
            self.image = self.images[1]
        else:
            self.image = self.images[0]
