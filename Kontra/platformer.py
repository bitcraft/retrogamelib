import os
import sys
from math import *
import random

import pygame

sys.path.insert(0, "..")
import retrogamelib
from retrogamelib.gameobject import Object
from retrogamelib import display
from retrogamelib import button
from retrogamelib.constants import *
from retrogamelib import geometry
from retrogamelib import clock
from retrogamelib.util import play_music, play_sound
from retrogamelib.camera import Camera

level = """
......................................................................................................................................................
............................................h.........................................................................................................
TTTTTTTTTTTTTr........................................................................................................................................
BBB........BBB......LTR..............................................................................................................................
TTB........BBB......BBB....................................................................h..........................................................
BBB........BBBTTTTTTTTTTTTTTr.........................................................................................................................
BBB........BBB.....BBB......BT........................................................................................................................
BTT.......LTTT....BBB.......BB........................................................................................................................
BBB.......BBBBT...BBB.....LTTB........................................................................................................................
BBB.......BBBBB..BBB.....LBBBB........................................................................................................................
TTTR......BBBBTTTTTTTTTTTTT..B........................................................................................................................
BBBBR...LTTBBBBBBBBBBBBBBBBR.B........................................................................................................................
BBBBBR.LBBBBBBBBBBBBB........................................................................................................................
------------------............--------------------------------------------------------------------------------"""

class Player(Object):
    
    def __init__(self):
        super(Player, self).__init__(self.groups)
        self.base = pygame.image.load(os.path.join("data",
            "gunner.png"))
        self.image = self.base.copy()
        self.rect = self.image.get_rect(midtop = (64, 8))
        self.head_pics = [pygame.image.load(os.path.join("data",x))
                                for x in ["head-normal.png", "head-upright.png",
                                    "head-downright.png"]]
        self.normal_leg_pic = pygame.image.load(os.path.join("data","legs-normal.png"))
        self.leg_pics = [pygame.image.load(os.path.join("data",x))
                                for x in ["legs-run-1.png", "legs-run-2.png"]]
        self.leg_pic = self.normal_leg_pic
        self.image_flipped = False
        self.walk_speed = 0
        self.walk_frame_next = 3
        self.jump_speed = 0
        self.can_fall = False
        self.direction = geometry.Vector(1,0)
        self.shot_vector = self.direction.copy()
        self.fall_through = 0  #frames of fall_through
        self.jumping = False
        self.jump_angle = 0
        self.on_floor = False
        self.take_damage = "player"
        self.health = 1
        self.flashing = 0
        self.choose_images()
        
    def choose_images(self):
        self.image = self.normal_leg_pic.copy()
        self.image.fill([0, 0, 0, 0])
        legpic = self.leg_pic
        if self.direction.x<0:
            legpic = pygame.transform.flip(legpic, 1, 0)
        self.image.blit(legpic, [0, 0])
        headpic = self.head_pics[0]
        if self.shot_vector.y<0:
            headpic = self.head_pics[1]
        elif self.shot_vector.y>0:
            headpic = self.head_pics[2]
        if self.direction.x<0:
            headpic = pygame.transform.flip(headpic, 1, 0)
        self.image.blit(headpic, [0, -1])
        
    def offscreen(self, camera):
        """Called when this object is moved offscreen"""
        pass
        
    def controls(self):
        if button.is_pressed(A_BUTTON):
            self.jump()
        if button.is_pressed(B_BUTTON):
            self.shoot()
        self.control_walk()
        self.aim_shot()
        self.choose_images()
    
    def jump(self):
        if not self.on_floor:
            return
        if not self.jumping:
            self.jumping = True
            if button.is_held(DOWN):
                self.jump_speed = 7
                self.fall_through = 4
            else:
                self.jump_speed = -11
                
    def control_walk(self):
        self.walk_speed = 0
        if button.is_held(LEFT):
            self.walk_speed -= 3
        if button.is_held(RIGHT):
            self.walk_speed += 3
        if self.walk_speed:
            self.walk_frame_next -= 1
            if self.walk_frame_next <= 0:
                self.leg_pics.append(self.leg_pics.pop(0))
                self.leg_pic = self.leg_pics[0]
                self.walk_frame_next = 3
        else:
            self.leg_pic = self.normal_leg_pic
            
    def aim_shot(self):
        self.shot_vector = self.direction.copy()
        x = int(button.is_held(RIGHT)-button.is_held(LEFT))
        y = int(button.is_held(DOWN)-button.is_held(UP))
        if not x and y>0 and not self.jumping:
            y = 0
        if y:
            self.shot_vector.x = x
        self.shot_vector.y = y
    
    def do_walk(self):
        if self.walk_speed:
            self.rect.x += self.walk_speed
            self.direction.x = self.walk_speed/abs(self.walk_speed)
    
    def update(self):
        
        if self.jump_speed < 7:
            self.jump_speed += 1
        self.rect.y += self.jump_speed

        self.do_walk()
        self.flip_image()
        
        self.on_floor = False
        self.collide_with_floors()
        if self.fall_through > 0:
            self.fall_through -= 1

        self.hit_stuff()

        if self.jumping:
            self.image = pygame.transform.rotozoom(self.base, self.jump_angle, 1)
            self.jump_angle += 15
        else:
            if self.jump_angle:
                self.image = self.base.copy()
                self.image_flipped = 0
                self.jump_angle = 0
        
        self.do_flash()
        
    def do_flash(self):
        if self.flashing:
            newi = self.base.copy()
            newi.fill([255, 255, 255])
            self.image = newi
            self.flashing -= 1
            if self.flashing == 0:
                self.image = self.base
    
    def hit_stuff(self):
        for o in self.objects:
            if getattr(o, "damage", None) == self.take_damage:
                if o.rect.colliderect(self.rect):
                    if getattr(o, "die_on_hit", None):
                        o.kill()
                    self.health -= 1
                    self.flashing = 3
                    if self.health <= 0:
                        self.kill()
            
    def flip_image(self):
        if not self.image_flipped and self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.image_flipped = True
        elif self.image_flipped and self.direction.x > 0:
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.image_flipped = False
        
    def collide_with_floors(self):
        for platform in self.platforms:
            if self.fall_through and platform.allow_fall_through and self.jump_speed > 3:
                continue
            if self.rect.colliderect(platform.rect):
                if self.jump_speed >= 0:
                    if platform.is_slope:
                        m = sin(radians(platform.slope))/cos(radians(platform.slope))
                        x = self.rect.centerx - platform.rect.centerx
                        if platform.slope > -2:
                            x -= 8
                        else:
                            x += 8
                        y = m*x
                        if y < -platform.rect.height:
                            y = -16
                        if y > 8:
                            y = 8
                        y += platform.rect.bottom + platform.slope_offset
                        if self.rect.bottom < y+(self.jump_speed*2):
                            while self.rect.bottom > y:
                                self.rect.y -= 1
                                self.hit_floor()
                    else:
                        if self.rect.bottom < platform.rect.top+(self.jump_speed*2):
                            self.rect.bottom = platform.rect.top
                            self.hit_floor()
        
    def hit_floor(self):
        self.jump_speed = 3
        self.on_floor = True
        self.jumping = False

    def shoot(self):
        emit = list(self.rect.center)
        emit[1]-=1
        direction = self.shot_vector*5
        play_sound("data/shot.ogg")
        b = Bullet(emit, direction)
        b.damage_alien = True
        return b
        
class NPC(Player):
    
    def __init__(self):
        super(NPC, self).__init__()
        self.base = pygame.image.load(os.path.join("data",
            "alien.png"))
        self.image = self.base
        self.take_damage = "alien"
        self.damage = "player"
            
    def update(self):
        super(NPC, self).update()
        self.ai()
    
        
class Alien(NPC):

    def __init__(self):
        super(Alien, self).__init__()
        self.base = pygame.image.load(os.path.join("data",
            "alien.png"))
        self.image = self.base
        self.take_damage = "alien"
        self.damage = "player"
        
    def offscreen(self, camera):
        self.kill()
        
    def ai(self):
        self.walk_speed = self.direction.x*2
        
class Helicopter(NPC):
    
    def __init__(self, pos):
        super(Helicopter, self).__init__()
        self.frames = [pygame.image.load(os.path.join("data",
            "helicopter-1.png")),
            pygame.image.load(os.path.join("data",
            "helicopter-2.png"))]
        self.base = self.frames[0]
        self.rect = self.base.get_rect()
        self.rect.topleft = pos
        self.image = self.base
        self.startx = pos[0]
        self.speed = 2
        self.health = 20
        self.camera = None
        
    def offscreen(self, camera):
        pass
        
    def onscreen(self, camera):
        if camera.translate(pygame.Rect([self.startx, self.rect.y, 
                                        self.rect.width, self.rect.height])).x<100:
            camera.freeze(self)
            self.camera = camera
            self.camera.offset[0] = -(self.startx-100)
        
    def kill(self):
        if self.camera:
            self.camera.unfreeze(self)
        super(Helicopter, self).kill()
        DeadHelicopter(self.rect.topleft)

    def update(self):
        self.frames.append(self.frames.pop(0))
        self.base = self.frames[0]
        self.image = self.base
        self.hit_stuff()
        self.rect.x += self.speed * self.direction.x
        if self.rect.x > self.startx + 100 or self.rect.x < self.startx - 100:
            self.direction.x = -self.direction.x
        self.do_flash()
        if random.randint(0, 100) > 94:
            Bomb(self.rect.midbottom, geometry.Vector(0, 5))
            
class DeadHelicopter(NPC):
    
    def __init__(self, pos):
        super(DeadHelicopter, self).__init__()
        self.frames = [pygame.image.load(os.path.join("data",
            "helicopter-1.png")),
            pygame.image.load(os.path.join("data",
            "helicopter-2.png"))]
        self.base = self.frames[0]
        self.rect = self.base.get_rect()
        self.rect.topleft = pos
        self.image = self.base
        self.explode_time = 10
        self.die_time = 0
        self.fall = 1

    def update(self):
        self.explode_time -= 1
        if self.explode_time == 0:
            play_sound("data/explosion.ogg")
            self.explode_time = random.randint(10, 30)
        self.rect.y += self.fall
        if self.fall < 7:
            self.fall += 1
        for platform in self.platforms:
            if platform.rect.colliderect(self.rect):
                self.rect.bottom = platform.rect.top
                self.die_time += 1
        if self.die_time > 120:
            self.kill()
                    
class Turret(Alien):
    
    def __init__(self):
        super(Turret, self).__init__()
        self.shot_timer = random.randint(30, 80)
        self.player = None
        
    def ai(self):
        self.walk_speed = 0
        self.shot_timer -= 1
        if not self.player:
            for o in self.objects:
                if getattr(o, "take_damage", None) == "player":
                    self.player = o
        if not self.player:
            return
        self.shot_vector.x = self.player.rect.centerx-self.rect.centerx
        self.shot_vector.y = self.player.rect.centery-self.rect.centery
        self.shot_vector = self.shot_vector.normalize()
        self.direction.x = self.shot_vector.x
        if self.shot_timer < 0:
            self.shot_timer = random.randint(30, 80)
            bullet = self.shoot()
            bullet.damage = "player"
            

class Bullet(Object):
    
    def __init__(self, pos, direction):
        Object.__init__(self, self.groups)
        self.image = pygame.image.load(os.path.join("data",
            "bullet.png"))
        self.rect = self.image.get_rect(center = pos)
        self.direction = direction
        self.z = -1
        self.damage = "alien"
        self.die_on_hit = True
        
    def offscreen(self, camera):
        self.kill()
    
    def update(self):
        self.rect.x += self.direction.x*2
        self.rect.y += self.direction.y*2
        if self.rect.y < -100:
            self.kill()
        elif self.rect.y > 400:
            self.kill()
            
class Bomb(Bullet):
    
    def __init__(self, pos, direction):
        Bullet.__init__(self, pos, direction)
        self.image = pygame.image.load(os.path.join("data",
            "bomb.png"))
        self.rect = self.image.get_rect(center = pos)
        self.direction = direction
        self.z = -1
        self.damage = "player"
        self.die_on_hit = True
    
    def update(self):
        Bullet.update(self)
        for platform in self.platforms:
            if platform.rect.colliderect(self.rect):
                self.kill()
            
class Spread:

    def __init__(self, pos, direction):
        bullets.append(Bullet(pos, direction))
        bullets.append(Bullet(pos, direction.rotate(-15)))
        bullets.append(Bullet(pos, direction.rotate(15)))
        
    def update(self):
        bullets.remove(self)

class Platform(Object):
    
    def __init__(self, pos, slope=0):
        Object.__init__(self, self.groups)
        self.image = pygame.image.load("data/platform.png")
        self.rect = self.image.get_rect(topleft = pos)
        self.slope_offset = 0
        self.allow_fall_through = True
        if slope != 0:
            self.is_slope = True
            self.slope = slope
            if slope < 0:
                self.image = pygame.image.load("data/platform-left.png")
            elif slope<45:
                self.image = pygame.image.load("data/platform-shallow-right.png")
                self.slope_offset = -5
            else:
                self.image = pygame.image.load("data/platform-right.png")
        else:
            self.is_slope = False
            self.slope = 0
        self.z = -2

class Tile(Object):
    
    def __init__(self, pos):
        Object.__init__(self, self.groups)
        self.image = pygame.image.load("data/platform-middle.png")
        self.rect = self.image.get_rect(topleft = pos)
        self.z = -2

def main():
    display.init(3.0, "Kontra")
    play_music("data/nes6.xm")
    
    objects = retrogamelib.gameobject.Group()
    platforms = retrogamelib.gameobject.Group()
    bullets = retrogamelib.gameobject.Group()
    
    Bullet.groups = [objects, bullets]
    Player.groups = [objects]
    Player.platforms = platforms
    Player.objects = objects
    Platform.groups = [objects, platforms]
    Tile.groups = [objects]
    Bullet.platforms = platforms

    x = 0
    y = 0
    for row in level.split("\n"):
        for col in row:
            if col == "T":
                Platform((x, y))
            if col == "-":
                Platform((x, y))
                platforms[-1].allow_fall_through = False
            if col == "L":
                Platform((x, y), -45)
            if col == "R":
                Platform((x, y), 45)
            if col == "r":
                Platform((x, y), 30)
            if col == "B":
                Tile((x, y))
            if col == "h":
                Helicopter((x, y))
            x += 16
        x = 0
        y += 16
    player = Player()
    turret = Turret()
    turret.rect.topleft = [0, 100]
    camera = Camera()
    camera.follow(player)

    while 1:
        clock.tick()
        button.handle_input()
        aliencount = 0
        for o in objects:
            if isinstance(o, Alien):
                aliencount += 1
            o.update()
        
        player.controls()
        camera.update()

        surface = display.surface
        surface.fill((175, 200, 255))
        for object in objects:
            translated = camera.translate(object.rect)
            surface.blit(object.image, translated)
            if translated.x<-16 or translated.x>300:
                if hasattr(object, "offscreen"):
                    object.offscreen(camera)
            else:
                if hasattr(object, "onscreen"):
                    object.onscreen(camera)
        display.update()
        
        if aliencount<2:
            if random.randint(0, 100) > 95:
                if random.randint(0, 1) == 1:
                    alien = Alien()
                    alien.rect.topleft = [258-camera.offset[0], random.randint(0,200)]
                    alien.direction.x = -1
                else:
                    alien = Alien()
                    alien.rect.topleft = [-5-camera.offset[0], random.randint(0,200)]
                    alien.direction.x = 1

if __name__ == "__main__":
    main()
