
from math import sin, cos, radians, atan, degrees
import time
import json
from SpielElemente import Auto
from SpielElemente import Renderer
import pygame.key

class Rennspiel():

    import enum
    class Dimension(enum.Enum):
        TwoDmode = 2
        ThreeDmode = 3

    def __init__(self, dimension, fullscreen, mapName):
        self.dimension = dimension
        self.rennzeit = time.time()
        laenge = 100

        self.renderer = Renderer(laenge, dimension, fullscreen, mapName)

        self.car = Auto(self.renderer.SCREEN_WIDTH / 2, self.renderer.SCREEN_HEIGHT / 2, laenge)

        self.kamera = [0.0, 0.0]
        self.kamera_speed = [0.0, 0.0]

    def pythagoras(self, i = 0.0, i2 = 0.0):
        return (i**2 + i2**2)**0.5

    def kameraRichten(self):
        mitte = [0, 0]
        mitte[0] = self.car.vorn[0] + (self.car.vorn[0] - self.car.hinten[0])*1.5
        mitte[1] = self.car.vorn[1] + (self.car.vorn[1] - self.car.hinten[1])*1.5

        #pygame.draw.circle(self.screen, (255, 255, 255), (0, 0),10)

        entfernung = self.pythagoras(mitte[0] - self.renderer.SCREEN_WIDTH/2 - self.kamera[0], mitte[1] - self.renderer.SCREEN_HEIGHT/2 - self.kamera[1])

        if entfernung > 0:
            self.kamera_speed[0] = (mitte[0] - self.renderer.SCREEN_WIDTH/2 - self.kamera[0]) * 0.02
            self.kamera_speed[1] = (mitte[1] - self.renderer.SCREEN_HEIGHT/2 - self.kamera[1]) * 0.02
        else:
            self.kamera_speed[0] = 0.0
            self.kamera_speed[1] = 0.0

        self.kamera_speed[0] = self.kamera_speed[0]**3
        self.kamera_speed[1] = self.kamera_speed[1]**3
        if (self.kamera_speed[0]**2 + self.kamera_speed[1]**2)**0.5 > 0.6:
            self.kamera[0] += self.kamera_speed[0]
            self.kamera[1] += self.kamera_speed[1]

    def reset(self):
        with open("sources2D/maps/spawns.json", "r") as file:
            data = json.load(file).get(self.renderer.MAP)

        self.car.geschwindigkeit = data.get("geschwindigkeit")
        self.orientierung = data.get("orientierung")
        self.car.richtung = data.get("richtung")
        self.car.vorn = data.get("vorn")
        self.car.hinten = data.get("hinten")
        self.car.blickrichtung = data.get("blickrichtung")
        self.kamera = data.get("kamera")

        print("reset")

    def setSpawnPoint(self):
        current = {
            self.renderer.MAP: {
                "geschwindigkeit": self.car.geschwindigkeit,
                "orientierung": self.car.orientierung,
                "richtung": self.car.richtung,
                "vorn": self.car.vorn,
                "hinten": self.car.hinten,
                "blickrichtung": self.car.blickrichtung,
                "kamera": self.kamera
            }
        }
        with open("sources2D/maps/spawns.json", "r") as file:
            data = json.load(file)
        data.update(current)
        with open("sources2D/maps/spawns.json", "w") as file:
            json.dump(data, file, indent = "    ")

    def movement(self):
        keys = self.renderer.getKeys()
        if keys[pygame.K_RIGHT]:
            self.car.rechtsLenken()
        if keys[pygame.K_LEFT]:
            self.car.linksLenken()
        if (keys[pygame.K_LEFT] == False) & (keys[pygame.K_RIGHT] == False):
            self.car.lenkradziehen()
        if keys[pygame.K_UP]:
            self.car.beschleunigen()
        if keys[pygame.K_DOWN]:
            self.car.bremsen()
        if (keys[pygame.K_UP] == False) & (keys[pygame.K_DOWN] == False):
            self.car.ausrollen()
            
        if keys[pygame.K_SPACE]:
            self.reset()
        if keys[pygame.K_ESCAPE]:
            return False
        if keys[pygame.K_p]:
            self.setSpawnPoint()

        self.car.spielerBewegen()
        self.kameraRichten()

        if self.renderer.detectCollision(self.car.vorn):
            self.reset()
        return True


    def mainLoop(self):
        start_time = time.time()
        spielt = True
        while spielt:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    spielt = False
            spielt = self.movement()
            
            #self.renderer.log("FPS: " + str(1.0 / (time.time() - start_time)))
            self.renderer.refresh(self.kamera, self.car.blickrichtung, self.car.vorn, self.car.hinten)
            start_time = time.time()
        self.renderer.quit()

if __name__ == '__main__':
    pygame.init()
    spiel = Rennspiel(Rennspiel.Dimension.TwoDmode, True, "Strand")
    #spiel = Rennspiel(Rennspiel.Dimension.ThreeDmode, False, "Strand")
    spiel.mainLoop()
    pygame.quit()