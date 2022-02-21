from math import sin, cos, radians, atan, degrees
import pygame
import os
import time
import json
from Scene import Scene

class Auto():

    def __init__(self, xpos = 0, ypos = 0, laenge = 100):
        self.geschwindigkeit = 5
        self.orientierung = [0, -1]
        self.richtung = 270
        self.vorn = [xpos, ypos]
        self.LAENGE = laenge
        self.hinten = [xpos, ypos + self.LAENGE]
        self.blickrichtung = 270

    def getReifeneinschlag(self, winkel):
        if winkel - self.blickrichtung > 180:
            unser_winkel = self.blickrichtung + 360
        elif winkel - self.blickrichtung < - 180:
            unser_winkel = self.blickrichtung - 360
        else:
            unser_winkel = self.blickrichtung
        return winkel - unser_winkel

    def setRichtung(self, winkel):
        #max * 0.7
        wendigkeit = 20 - (self.geschwindigkeit*0.215)

        einschlag = self.getReifeneinschlag(winkel)
        if einschlag > wendigkeit:
            winkel = self.blickrichtung + wendigkeit
        elif einschlag < -wendigkeit:
            winkel = self.blickrichtung - wendigkeit
        self.orientierung[0] = cos(radians(winkel))
        self.orientierung[1] = sin(radians(winkel))
        
        self.richtung = winkel % 360

    def spielerBewegen(self):
        self.vorn[0] += self.orientierung[0] * self.geschwindigkeit
        self.vorn[1] += self.orientierung[1] * self.geschwindigkeit

        m = [self.vorn[0] - self.hinten[0], self.vorn[1] - self.hinten[1]]
        laenge = (m[0]**2 + m[1]**2)**0.5

        m[0] /= laenge
        m[1] /= laenge

        self.hinten[0] = self.vorn[0] - (self.LAENGE - 1) * m[0]
        self.hinten[1] = self.vorn[1] - (self.LAENGE - 1) * m[1]
        if self.vorn[0] - self.hinten[0] != 0:
            self.blickrichtung = degrees(atan((self.vorn[1] - self.hinten[1]) / (self.vorn[0] - self.hinten[0])))
            if self.blickrichtung < 0:
                self.blickrichtung += 180
            if self.vorn[1]- self.hinten[1] < 0:
                self.blickrichtung += 180
    
    def rechtsLenken(self):
        self.setRichtung(self.richtung + 5)
    def linksLenken(self):
        self.setRichtung(self.richtung - 5)
    def lenkradziehen(self):
        einschlag = self.getReifeneinschlag(self.richtung)
        if (einschlag >= 5):
            self.setRichtung(self.richtung - 5)
        elif einschlag <= -5:
            self.setRichtung(self.richtung + 5)
        elif einschlag != 0.0:
            self.setRichtung(self.richtung)
    def beschleunigen(self):
        if self.geschwindigkeit < 35:
            self.geschwindigkeit += (40-self.geschwindigkeit) * 0.04
        elif self.geschwindigkeit < 40:
            self.geschwindigkeit += (40-self.geschwindigkeit) * 0.01
    def bremsen(self):
        if self.geschwindigkeit < 5:
            self.geschwindigkeit = 0
        else:
            self.geschwindigkeit /= 1.045
    def ausrollen(self):
        if self.geschwindigkeit < 1.5:
            self.geschwindigkeit = 0
        else:
            self.geschwindigkeit /= 1.02


class Renderer():
    def __init__(self, width, height, autoLaenge, dimension, fullscreen):
        pygame.init()
        self.GRID = False
        self.dimension = dimension

        self.SCREEN_WIDTH = width
        self.SCREEN_HEIGHT = height
        if fullscreen and dimension == 2:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Hier Map waehlen:
        self.MAP = "sachsenring"

        # Nur 2D:
        #self.MAP = "sachsenring_v2"

        if dimension.value == 2:
            self.clock = pygame.time.Clock()
        elif dimension.value == 3:
            self.scene = Scene(fullscreen, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.scene.addObject(os.path.join(os.getcwd(), "sources3D", "fahrzeuge", "Delorean"), "delorean.obj", "auto", 68.5)
            #self.scene.addObject(os.path.join(os.getcwd(), "sources3D", "fahrzeuge", "block"), "block.obj", "block", 68.0)
            
            self.scene.getObject("auto").setOffRotationForAllAxes(0, 0, 90)
            self.scene.addObject(os.path.join(os.getcwd(), "sources3D", "maps", self.MAP), "map.obj", "map", 1.0)
            self.scene.getObject("map").setOffRotationForAllAxes(90, 0, 0)
            self.scene.getObject("map").setOffPosition(3236.0 - self.SCREEN_WIDTH/2, 2024.0 - self.SCREEN_HEIGHT/2)

            self.scene.getObject("auto").setOffPosition(-self.SCREEN_WIDTH/2, -self.SCREEN_HEIGHT/2)

        self.MAP_PATH = os.path.join(os.getcwd(), "sources2D", "maps", self.MAP)

        self.rennzeit = 0
        self.ausgabe = "Test"

        self.map = pygame.image.load(os.path.join(self.MAP_PATH, 'optik.png')).convert()
        self.map = pygame.transform.smoothscale(self.map, (self.map.get_rect().width * 4, self.map.get_rect().height * 4))

        if self.dimension.value == 2:
            self.auto = pygame.image.load(os.path.join("sources2D", 'img', 'auto.png')).convert()
        else:
            self.auto = pygame.image.load(os.path.join("sources3D", "Fahrzeuge", 'Delorean', 'coll.png')).convert()
        self.auto.set_colorkey((0, 0, 0))
        self.auto = pygame.transform.smoothscale(self.auto, (int(self.auto.get_rect().width / self.auto.get_rect().height * (autoLaenge + 60)), autoLaenge + 60))
        self.auto_mask = pygame.mask.from_surface(self.auto)
        self.auto_mask_corner = [0, 0]

        self.collision = pygame.image.load(os.path.join(self.MAP_PATH, 'coll.png')).convert()
        self.collision.set_colorkey((0, 0, 0))
        self.collision = pygame.transform.smoothscale(self.collision, (self.collision.get_rect().width * 4, self.collision.get_rect().height * 4))
        self.collision_mask = pygame.mask.from_surface(self.collision)

        self.special = pygame.image.load(os.path.join(self.MAP_PATH, 'spec.png')).convert()
        self.special = pygame.transform.smoothscale(self.special, (self.special.get_rect().width * 4, self.special.get_rect().height * 4))
    
    def log(self, text=""):
        if self.dimension == 2:
            if(text==""):
                font = pygame.font.SysFont(None, 100)
                timer = font.render(self.ausgabe, True, (0, 0, 0), (255, 255, 255))
                self.screen.blit(timer, (100, 100))
            else:
                self.ausgabe = text
        else:
            print(text)

    def mapZeichnen(self, kamera):
        self.screen.fill((255, 255, 255))

        tileSize = 100

        self.screen.blit(self.map, (-kamera[0], -kamera[1], self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        #rote Striche
        if self.GRID:
            for i in range(1, int(self.SCREEN_WIDTH / tileSize) + 2):
                pygame.draw.line(self.screen, (255, 0, 0), (i * tileSize - kamera[0]%tileSize, 0), (i * tileSize - kamera[0]%tileSize, self.SCREEN_HEIGHT))

            for i in range(1, int(self.SCREEN_HEIGHT / tileSize) + 2):
                pygame.draw.line(self.screen, (255, 0, 0), (0, i * tileSize - kamera[1]%tileSize), (self.SCREEN_WIDTH, i * tileSize - kamera[1]%tileSize))

    def autoZeichnen(self, blickrichtung, kamera, vorn, hinten):
        rotated_image = pygame.transform.rotate(self.auto, 270 - blickrichtung)
        new_rect = rotated_image.get_rect(center = self.auto.get_rect(center = ((vorn[0] + hinten[0])/2 - kamera[0], (vorn[1] + hinten[1])/2 - kamera[1])).center)
        
        if self.dimension.value == 2:
            self.screen.blit(rotated_image, new_rect.topleft)

        self.auto_mask = pygame.mask.from_surface(rotated_image)
        self.auto_mask_corner[0] = new_rect.x + kamera[0]
        self.auto_mask_corner[1] = new_rect.y + kamera[1]

        if self.GRID and self.dimension.value == 2:
            pygame.draw.line(self.screen, (100, 100, 255), (vorn[0] - kamera[0], vorn[1] - kamera[1]), (hinten[0] - kamera[0], hinten[1] - kamera[1]), 4)



    def detectCollision(self, vorn):
        if(self.GRID):
            olist = self.auto_mask.outline()
            pygame.draw.polygon(self.screen,(200,150,150),olist,0)
            print(self.auto_mask_corner)

        dx = int(self.auto_mask_corner[0]) - self.map.get_rect().x
        dy = int(self.auto_mask_corner[1]) - self.map.get_rect().y

        if self.collision_mask.overlap(self.auto_mask, (dx, dy)):
            return True
        else:
            if self.special.get_at((int(vorn[0]), int(vorn[1]))) == (0, 0, 0, 255):
                print("Zeit: " + str(time.time() - self.rennzeit))
            elif self.special.get_at((int(vorn[0]), int(vorn[1]))) == (0, 255, 0, 255):
                print("Start 0:0")
                self.rennzeit = time.time()


    def drawOverlay(self, vorn):
            size = 20
            minimap = self.collision_mask.scale((int(self.collision_mask.get_rect().width / size), int(self.collision_mask.get_rect().height / size)))
            minimap.to_surface(self.screen, setcolor=None, unsetcolor=(50, 50, 50, 255), dest=(self.SCREEN_WIDTH - minimap.get_rect().width, self.SCREEN_HEIGHT - minimap.get_rect().height))
            pygame.draw.circle(self.screen, (100, 10, 250), (self.SCREEN_WIDTH - minimap.get_rect().width + vorn[0] / size, self.SCREEN_HEIGHT - minimap.get_rect().height + vorn[1]/size), 10)

            font = pygame.font.SysFont(None, 100)
            timer = font.render("%.3f"%(time.time() - self.rennzeit), True, (0, 0, 0), (200, 200, 200))
            self.screen.blit(timer, (self.SCREEN_WIDTH/2-timer.get_rect().width / 2, 70))
    
    def refresh(self, kamera, blickrichtung, vorn, hinten):

        if self.dimension.value == 2:
            self.mapZeichnen(kamera)
            
            self.autoZeichnen(blickrichtung, kamera, vorn, hinten)
            self.drawOverlay(vorn)
            if(self.GRID):
                self.log()

            pygame.display.update((0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.clock.tick(30)
        elif self.dimension.value == 3:
            self.autoZeichnen(blickrichtung, kamera, vorn, hinten)
            self.scene.getObject("auto").setPosition((vorn[0] + hinten[0])/2 - kamera[0], (vorn[1] + hinten[1])/2 - kamera[1])
            self.scene.getObject("auto").setRotation(blickrichtung)
            self.scene.getObject("map").setPosition(-kamera[0]/1.0, -kamera[1]/1.0)
            self.scene.refresh()


    def quit(self):
        pygame.quit()
        if self.dimension.value == 3:
            self.scene.quit()

    def getKeys(self):
        if self.dimension.value == 2:
            return pygame.key.get_pressed()
        elif self.dimension.value == 3:
            return self.scene.getKeys()