#! /usr/bin/env python

# example.py - an example for NESGameLib
# Example code released to the public domain
# Art is Copyright (C) 2009.

import pygame
import os

# Import the modules we'll use from NESGameLib
from nesgamelib import display
from nesgamelib import button
from nesgamelib import clock
from nesgamelib import font
from nesgamelib import dialog
from nesgamelib import util
from nesgamelib.constants import *

class Player(object):
    
    def __init__(self):
        self.image = util.load_image("data/bubbman-nes.png")
        self.pos = [32, 112]
        self.jump_speed = 0
    
    def update(self):
        
        # Increase the y position by the jump speed
        self.pos[1] += self.jump_speed
        self.jump_speed += 0.4
        
        # If we're at ground level, stop.
        if self.pos[1] > 192:
            self.pos[1] = 192
            self.jump_speed = 0
        
        # Keep the player in-bounds
        if self.pos[0] < 0:
            self.pos[0] = 0
        if self.pos[0] > 240:
            self.pos[0] = 240

# Initalise the display
display.init(scale=2.0, caption="NES Demo", res=NESRES)
player = Player() # Create the player

# Create a font
nesfont = font.Font(NES_FONT, (255, 255, 255))

dialogbox = dialog.DialogBox((240, 51), (0, 0, 0), 
    (255, 255, 255), nesfont)
dialogbox.set_dialog([
"This is a dialog box! Press the a button to go to the next page.", 
"Press it again and this box will close."])
menu = dialog.Menu(nesfont, ["Close", "Pause", "Exit"])
#dialogbox.close()

while 1:
    
    # Tick, tock, at 30 frames per second
    clock.tick()
    
    # Handle button and key input
    button.handle_input()
    
    # If displaying dialog, do events for dialog!
    if not dialogbox.over():
        if button.is_pressed(A_BUTTON):
            dialogbox.progress()
    
    # Otherwise, play the "game"
    else:
        
        # Move if LEFT or RIGHT is being pressed.
        if button.is_held(LEFT):
            player.pos[0] -= 3
        if button.is_held(RIGHT):
            player.pos[0] += 3
        
        # Move the menu cursor if you press up or down    
        if button.is_pressed(UP):
            menu.move_cursor(-1)
        if button.is_pressed(DOWN):
            menu.move_cursor(1)
        
        # If you press start, check which option you're on!
        if button.is_pressed(START):
            option, text = menu.get_option()
            print "You pressed '%s'" % text
            if option == 2:
                raise SystemExit
        
        # Jump if the player taps the A button
        if button.is_pressed(A_BUTTON):
            player.jump_speed = -5
            
        # Update the player
        player.update()
    
    # Get the surface from the NES game library
    screen = display.get_surface()
    
    # Call normal pygame draw functions
    screen.fill((200, 200, 255))
    pygame.draw.rect(screen, (50, 100, 0), (0, 208, 256, 32))
    pygame.draw.rect(screen, (255, 200, 185), (0, 209, 256, 1), 1)
    screen.blit(player.image, player.pos)
    
    # Render text with the font
    ren = nesfont.render("Score        Time        World")
    screen.blit(ren, (8, 8))
    ren = nesfont.render("000000        99          1-1")
    screen.blit(ren, (8, 18))
    
    # Draw the dialog and menu boxes
    menu.draw(screen, (8, 202), background=(0, 0, 0), 
        border=(255, 255, 255))
    dialogbox.draw(screen, (8, 8))
    
    # Update and draw the display
    display.update()
