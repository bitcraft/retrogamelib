#! /usr/bin/env python

# Gamebub - a GameBoy type platformer
# All code and assets are Copyright (C) 2009.

import pygame
import os
import sys

sys.path.insert(0, "..")
from nesgamelib import display
from nesgamelib import button
from nesgamelib import clock
from nesgamelib import font
from nesgamelib import gameobject
from nesgamelib.constants import *

from nesgamelib.util import *
from objects import *
from tileengine import *
from levels import *

class Game(object):
    
    def __init__(self):
        
        self.objects = gameobject.Group()
        self.coins = gameobject.Group()
        self.baddies = gameobject.Group()
        self.dead = gameobject.Group()
        self.springs = gameobject.Group()
        
        Player.groups = [self.objects]
        Platform.groups = [self.objects]
        Coin.groups = [self.objects, self.coins]
        Points.groups = [self.objects]
        Poof.groups = [self.objects]
        Baddie.groups = [self.objects, self.baddies]
        Death.groups = [self.objects, self.dead]
        Spring.groups = [self.objects, self.springs]
        
        self.font = font.Font(GAMEBOY_FONT, (50, 50, 50))
        self.background = load_image("data/background.png")
        self.lifeicon = load_image("data/head.png")
        
        self.score = 0
        self.level = 1
        self.lives = 5
        self.show_win_screen = False
        
        self.engine = TileEngine()
        self.camera = pygame.Rect(0, 0, GBRES[0], GBRES[1])

    def start_level(self, level):
        self.show_win_screen = False
        if self.lives > 0:
            for obj in self.objects:
                obj.kill()
            self.player = Player()
            self.engine.parse_level(level)
            self.camera.centerx = self.player.rect.centerx
        else:
            self.won = False
            self.playing = False
            self.lose()

    def kill_player(self):
        if self.player.alive():
            self.lives -= 1
            self.player.kill()
            Death(self.player.rect.center)
            #pygame.mixer.music.stop()
            play_sound("data/die.ogg")

    def win(self):
        splash = display.get_surface().copy()
        pos = 0
        time = 50
        while 1:
            button.handle_input()
            clock.tick()
            if pos < 74:
                pos += 2
            else:
                time -= 1
                if time <= 0:
                    break
            screen = display.get_surface()
            screen.blit(splash, (0, 0))
            ren = self.font.render("You reached Oliland!")
            screen.blit(ren, (80-ren.get_width()/2, pos))
            display.update()
        self.playing = False

    def lose(self):
        splash = display.get_surface().copy()
        pos = 0
        time = 50
        while 1:
            button.handle_input()
            clock.tick()
            if pos < 74:
                pos += 2
            else:
                time -= 1
                if time <= 0:
                    break
            screen = display.get_surface()
            screen.blit(splash, (0, 0))
            ren = self.font.render("Game over!")
            screen.blit(ren, (80-ren.get_width()/2, pos))
            display.update()
        self.playing = False
        self.won = False

    def pause(self):
        pygame.mixer.music.pause()
        button.handle_input()
        play_sound("data/pause.ogg")
        while not button.is_pressed(START):
            button.handle_input()
            ren = self.font.render("PAUSED")
            screen = display.get_surface()
            screen.blit(ren, (80-ren.get_width()/2, 
                74-ren.get_height()/2))
            display.update()
        play_sound("data/pause.ogg")
        pygame.mixer.music.unpause()

    def loop(self):
        self.playing = True
        while self.playing:
            
           self.handle_input()
           self.update()
           self.draw()
    
    def handle_input(self):
        button.handle_input()
        if button.is_pressed(START):
            self.pause()
        if button.is_pressed(A_BUTTON) and button.is_held(SELECT):
            self.playing = False
            
    def update(self):
        clock.tick()
        for object in self.objects:
            if (object.rect.right >= self.camera.left and \
                object.rect.left <= self.camera.right) or \
                object.always_update == True:
                object.update(self.engine.tiles)
                object.always_update = True
        
        # Move the camera
        self.camera.centerx = self.player.rect.centerx
        if self.camera.left < 0:
            self.camera.left = 0
        if self.camera.right > len(self.engine.tiles[0])*16:
            self.camera.right = len(self.engine.tiles[0])*16
        
        # Check if we won the level
        if self.player.rect.left > len(self.engine.tiles[0])*16:
            if len(LEVELS) == self.level-1:
                self.win()
            else:
                self.playing = False
        
        # Check if we fell off a cliff
        if self.player.rect.top > len(self.engine.tiles)*16:
            self.kill_player()
        
        # Make sure we don't move off the far left of the level
        if self.player.rect.left < 0:
            self.player.rect.left = 0
        
        # Get rich quick!
        for c in self.coins:
            if self.player.rect.colliderect(c.rect):
                c.kill()
                self.score += 25
                Poof(c.rect.center)
                play_sound("data/coin.ogg")
        
        # Will you live, or die?
        for b in self.baddies:
            if self.player.rect.colliderect(b.rect):
                if self.player.jump_speed > 0 and \
                    self.player.rect.bottom < b.rect.top+10 and \
                    b.alive():
                    b.kill()
                    Poof(b.rect.center)
                    self.player.jump_speed = -3
                    self.player.rect.bottom = b.rect.top-1
                    play_sound("data/pounce.ogg")
                    self.score += 50
                    Points(50, b.rect.center, self.font)
                else:
                    if b.alive():
                        self.kill_player()
        
        # Boinnnng!
        for s in self.springs:
            if self.player.rect.colliderect(s.rect):
                if self.player.jump_speed > 0:
                    self.player.jump_speed = -8
                    if not s.bouncing:
                        play_sound("data/bounce.ogg")
                    s.bounce()
                    self.player.jumping = True
    
    def draw(self):
        screen = display.get_surface()

        screen.fill(GB_SCREEN_COLOR)
        screen.blit(self.background, ((-self.camera.x/2) % 160, 0))
        screen.blit(self.background, (((-self.camera.x/2) - 160) % -160, 0))
        screen.blit(self.background, (((-self.camera.x/2) + 160) % 160, 0))

        for object in self.objects:
            object.draw(screen, self.camera)
        
        ren = self.font.render("score    level      x%d" % self.lives)
        screen.blit(ren, (4, 4))
        ren = self.font.render("%06d    %d-1" % (self.score, self.level-1))
        screen.blit(ren, (4, 14))
        screen.blit(self.lifeicon, (160-30, 2))
        
        if not self.player.alive() and not self.dead:
            self.start_level(LEVELS[self.level-2])
        
        display.update()
