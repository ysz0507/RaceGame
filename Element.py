
class Element():

    def __init__(self):
        self.rot = 0.0
        self.x = 0.0
        self.y = 0.0
        self.xoff = 0.0
        self.yoff = 0.0
        self.xrotation = 0.0
        self.yrotation = 0.0
        self.zrotation = 0.0

    def getPosition(self):
        return (self.x + self.xoff, self.y + self.yoff)

    def getRotation(self):
        return (self.rot)

    def getOffRotationForAllAxes(self):
        return self.xrotation, self.yrotation, self.zrotation

    def setOffRotationForAllAxes(self, x, y, z):
        self.xrotation = x
        self.yrotation = y
        self.zrotation = z

    def setRotation(self, rot):
        self.rot = rot

    def setPosition(self, xpos, ypos):
        self.x = xpos
        self.y = ypos

    def setOffPosition(self, xpos, ypos):
        self.xoff = xpos
        self.yoff = ypos