
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import os

class Object():
    import enum
    class Category(enum.Enum):
        vertices = 0
        tex_vertices = 1
        normals = 2

        vert_surfaces = 3
        tex_surfaces = 4
        norm_surfaces = 5
        openGLmode = 6
        material_surfaces = 7
        materials = 8

    def __init__(self):
        self.vertices = []
        self.tex_vertices = []
        self.normals = []

        self.vert_surfaces = []
        self.tex_surfaces = []
        self.norm_surfaces = []
        self.material_surfaces = []

        self.materials = {}
        return

    def loadByUrl(self, url, objFile, scale=1.0):
        material = ""
        file = open(os.path.join(url, objFile), "r").readlines()
        for line in file:
            keyWord = line.split()[0]
            if(keyWord == "mtllib"):
                self.loadMtl(url, line.split()[1])
            elif(keyWord == "v"):
                self.vertices.append(list(map(float, line.split()[1:])))
            elif(keyWord == "vt"):
                self.tex_vertices.append(list(map(float, line.split()[1:])))
            elif(keyWord == "vn"):
                self.normals.append(list(map(float, line.split()[1:])))
            elif(keyWord == "usemtl"):
                material = line.split(" ", 1)[1].rstrip()
            elif(keyWord == "f"):
                packs = line.split()[1:]

                if len(packs) == 4:
                    self.mode = GL_QUADS
                else:
                    self.mode = GL_TRIANGLES

                temp = [[],[],[]]
                for i in range(len(packs[0].split("/"))):
                    for pack in packs:
                        temp[i].append(int(pack.split("/")[i].rstrip()))
                self.vert_surfaces.append(temp[0])
                self.tex_surfaces.append(temp[1])
                if len(temp) == 3:
                    self.norm_surfaces.append(temp[2])
                self.material_surfaces.append(material)
            elif(keyWord == "#"):
                continue
            else:
                print("OBJ: I still do not know: " + line.rstrip())
        
        for i, vert in enumerate(self.vertices):
            for i2, x in enumerate(vert):
                self.vertices[i][i2] = x*scale

    def loadMtl(self, url, file):
        material = {}
        file = open(os.path.join(url, file), "r").readlines()
        for line in file:
            if len(line.split()) == 0:
                continue
            keyWord = line.split()[0]
            if(keyWord == "#"):
                continue
            elif(keyWord == "map_Kd"):
                material["id"] = self.bindImage(os.path.join(url, line.split(" ", 1)[1].rstrip()))
                self.materials[name] = material
                material = {}
            elif(keyWord == "newmtl"):
                name = line.split()[1]
            elif(keyWord == "Ns" or keyWord == "Ni" or keyWord == "d" or keyWord == "illum"):
                material[keyWord] = float(line.split()[1])
            elif(keyWord == "Ka" or keyWord == "Kd" or keyWord == "Ks" or keyWord == "Ke"):
                material[keyWord] = list(map(float, line.split()[1:]))
            else:
                print("MTL: I still do not know: " + line.rstrip())

    def bindImage(self, url):
        print(url)
        textureSurface = pygame.image.load(open(url, "r"))
        textureData = pygame.image.tostring(textureSurface, "RGB")
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        OpenGL.GL.glEnable(GL_TEXTURE_2D)
        id = OpenGL.GL.glGenTextures(1)
        OpenGL.GL.glBindTexture(GL_TEXTURE_2D, id)
        OpenGL.GL.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, textureData)

        #OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        #OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        OpenGL.GL.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        OpenGL.GL.glDisable(GL_TEXTURE_2D)

        return id

    def getData(self, type = 0):
        data = (self.vertices, self.tex_vertices, self.normals, self.vert_surfaces, self.tex_surfaces, self.norm_surfaces, self.mode, self.material_surfaces, self.materials)
        return data[type.value]

    def draw(self):
        glBegin(self.mode)
        for i, surface in enumerate(self.vert_surfaces):
            glNormal3fv(self.normals[self.norm_surfaces[i][0] - 1])
            for vertex in surface:
                glVertex3fv(self.vertices[vertex - 1])
        glEnd()

    def drawTexture(self, shader):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.materials[self.material_surfaces[0]]["id"])

        glUseProgram(shader)
        glBegin(self.mode)

        for i, surface in enumerate(self.vert_surfaces):
            if i == 0 or self.material_surfaces[i] != self.material_surfaces[i - 1]:
                if i != 0:
                    glEnd()
                    glBindTexture(GL_TEXTURE_2D, self.materials[self.material_surfaces[i]]["id"])
                    glBegin(self.mode)
                glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, *self.materials[self.material_surfaces[i]]["Ka"], 1.0)
                glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, *self.materials[self.material_surfaces[i]]["Kd"], 1.0)
                glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, *self.materials[self.material_surfaces[i]]["Ks"], 1.0)
                glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.materials[self.material_surfaces[i]]["Ns"] * 0.128)
            glNormal3fv(self.normals[self.norm_surfaces[i][0] - 1])
            for x, vertex in enumerate(surface):
                glTexCoord2fv((self.tex_vertices[self.tex_surfaces[i][x] - 1][0], 1 - self.tex_vertices[self.tex_surfaces[i][x] - 1][1]))
                glVertex3fv(self.vertices[vertex - 1])

        glEnd()
        glUseProgram(0)
        glDisable(GL_TEXTURE_2D)
