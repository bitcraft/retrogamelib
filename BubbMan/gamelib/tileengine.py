from objects import *

class TileEngine(object):
    
    def get_at(self, x, y):
        try:
            char = self.raw[y][x]
            return char
        except:
            return ""

    def parse_level(self, level):
        self.raw = level[:]
        self.tiles = [x[:] for x in level]
        platforms = ("P", "", "L", "R")
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                char = self.tiles[y][x]
                if char == "L":
                    self.tiles[y][x] = Platform((x*16, y*16), [3, 0], 1)
                if char == "R":
                    self.tiles[y][x] = Platform((x*16, y*16), [3, 1], -1)
                if char == "Q":
                    self.tiles[y][x] = Platform((x*16, y*16), [3, 2])
                if char == "P":
                    imgpos = [1, 1]
                    if self.get_at(x-1, y) not in platforms:
                        imgpos = [0, 1]
                    if self.get_at(x+1, y) not in platforms:
                        imgpos = [2, 1]
                    if self.get_at(x, y-1) not in platforms:
                        imgpos[1] = 0
                    if self.get_at(x, y+1) not in platforms:
                        imgpos[1] = 2
                    if imgpos == [1, 1]:
                        if self.get_at(x, y-1) == "L":
                            imgpos = [4, 0]
                        if self.get_at(x, y-1) == "R":
                            imgpos = [4, 1]
                        if self.get_at(x, y-1) == "P":
                            if self.get_at(x-1, y-1) not in platforms:
                                if self.get_at(x-1, y) == "P":
                                    imgpos = [4, 2]
                            if self.get_at(x+1, y-1) not in platforms:
                                if self.get_at(x+1, y) == "P":
                                    imgpos = [5, 0]
                        if self.get_at(x, y+1) == "P":
                            if self.get_at(x-1, y+1) not in platforms:
                                if self.get_at(x-1, y) == "P":
                                    imgpos = [5, 1]
                            if self.get_at(x+1, y+1) not in platforms:
                                if self.get_at(x+1, y) == "P":
                                    imgpos = [5, 2]
                                
                    self.tiles[y][x] = Platform((x*16, y*16), imgpos)
                if char == "C":
                    Coin((x*16 + 4, y*16 + 4))
                if char == "B":
                    Baddie((x*16 + 4, y*16 + 4))
                if char == "S":
                    Spring((x*16, y*16))
