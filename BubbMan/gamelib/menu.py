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
from nesgamelib import dialog
from nesgamelib.constants import *

from game import *
from levels import *
from nesgamelib.util import *

def run_menu():
        
    timer = 0
    play_music("data/title.ogg")
    game = Game()
    set_global_sound_volume(0.75)
    
    while 1:
        clock.tick()
        button.handle_input()
        
        # If we pressed start, begin the game
        if button.is_pressed(START):

            play_music("data/algar-orka.xm", -1)
            whitefont = font.Font(GAMEBOY_FONT, GB_SCREEN_COLOR)
            box = dialog.DialogBox((152, 46), (50, 50, 50), 
                GB_SCREEN_COLOR, whitefont)
            box.set_dialog([
                "bubbman was on his way to oliland,",
                "when his car broke down in the dododu mountains!",
                "can bubbman cross the monster-infested mountain range?"
            ])
            box.set_scrolldelay(2)
            while not box.over():
                clock.tick()
                button.handle_input()
                if button.is_pressed(A_BUTTON):
                    box.progress()
                screen = display.get_surface()
                screen.fill(GB_SCREEN_COLOR)
                screen.blit(game.background, (0, 0))
                box.draw(screen, (4, 4))
                display.update()
            
            
            game.won = True
            game.level = 1
            game.lives = 5
            game.score = 0

            # Play each level
            for lvl in LEVELS:
                game.start_level(lvl)
                game.level += 1
                game.loop()
                if not game.player.alive():
                    break
            
            # If we got to the end of the game, display credits
            if game.won:
                pos = 144
                credits = [
                    "Credits",
                    "",
                    "",
                    "Programmers",
                    "pymike",
                    "saluk",
                    "",
                    "",
                    "Sound Mixing",
                    "pymike",
                    "",
                    "",
                    "Music",
                    "ModArchive.org",
                    "DrPetter",
                    "",
                    "",
                    "Special Thanks To",
                    "SFXR by DrPetter",
                    "The Gimp 2",
                    "Geany",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    " Thanks for playing!!"]
                while pos > -144-(len(credits)*7):
                    button.handle_input()
                    if button.is_pressed(START):
                        break
                    screen = display.get_surface()
                    screen.fill(GB_SCREEN_COLOR)
                    screen.blit(game.background, (0, 0))
                    
                    clock.tick()
                    pos -= 0.5
                    y = 0
                    for c in credits:
                        ren = game.font.render(c)
                        screen.blit(ren, (80-ren.get_width()/2, pos+y))
                        y += 10
                    display.update()
           
            play_music("data/title.ogg")
        
        # Draw the main menu
        screen = display.get_surface()
        screen.fill(GB_SCREEN_COLOR)
        screen.blit(load_image("data/bubbman-menu.png"), (0, 0))
        ren = game.font.render("Press Start")
        timer += 1
        timer = timer % 30
        if timer < 15:
            screen.blit(ren, (80-ren.get_width()/2, 
                104-ren.get_height()/2))
        display.update()
