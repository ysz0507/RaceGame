from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pygame
from Element import Element
from Object import Object

vertex_shader = """
varying vec3 vN;
varying vec3 v;
varying vec2 fTexcoords;

void main(void)
{
   v = vec3(gl_ModelViewMatrix * gl_Vertex);
   vN = normalize(gl_NormalMatrix * gl_Normal);

   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
   fTexcoords = gl_MultiTexCoord0.xy;

}
"""

fragment_shader = """
varying vec3 vN;
varying vec3 v;
uniform sampler2D image;
varying vec2 fTexcoords;

#define MAX_LIGHTS 1
void main (void)
{
   vec3 N = normalize(vN);
   vec4 finalColor = vec4(0.0, 0.0, 0.0, 0.0);

   for (int i=0;i<MAX_LIGHTS;i++)
   {
      vec3 L = normalize(gl_LightSource[i].position.xyz - v);
      vec3 E = normalize(-v); // we are in Eye Coordinates, so EyePos is (0,0,0)
      vec3 R = normalize(-reflect(L,N));

      vec4 Iamb = gl_LightSource[i].ambient;
      vec4 Idiff = gl_LightSource[i].diffuse * max(dot(N,L), 0.0);
      Idiff = clamp(Idiff, 0.0, 1.0);
      vec4 Ispec = gl_LightSource[i].specular * pow(max(dot(R,E),0.0),0.3*gl_FrontMaterial.shininess);
      Ispec = clamp(Ispec, 0.0, 1.0);

      finalColor += Iamb + Idiff + Ispec;
   }
   vec4 color = texture2D(image, fTexcoords);
   //vec4 color = vec4(1,0,0, 0);
   gl_FragColor = color * finalColor;
}
"""

class Scene():

    def __init__(self, fullscreen, display=(1680, 1050)):

        self.position = [0.0, 0.0, -5.0]
        self.rotation = [180.0, 0.0, 0.0]

        self.objects = {}

        pygame.init()
        pygame.display.set_mode(display, pygame.DOUBLEBUF|pygame.OPENGL)
        self.clock = pygame.time.Clock()
        if fullscreen:
            pygame.display.toggle_fullscreen()

        self.program = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER))

        glMatrixMode(GL_PROJECTION)
        OpenGL.GLU.gluPerspective(45, (display[0]/display[1]), 1.2071 * display[1] - 500, 1.2071 * display[1] + 100)
        glMatrixMode(GL_MODELVIEW)
        OpenGL.GL.glRotatef(180, 1, 0, 0)
        OpenGL.GL.glTranslatef(0.0, 0.0, 1.2071 * display[1])

        glLight(GL_LIGHT0, GL_POSITION,  (20, 20, -300, 0.9))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.7, 0.7, 0.7, 0.33))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 0.5))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (0.8, 0.8, 0.8, 0.5))


        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_COLOR_MATERIAL)

    def addObject(self, url, file, name, scale=1.0):
        a = Object()
        a.loadByUrl(url, file, scale)
        e = Element()
        self.objects[name] = (a, e)

    def getObject(self, name):
        return self.objects[name][1]

    def refresh(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            self.position[2] -= 0.1
        if keys[pygame.K_r]:
            self.position[2] += 0.1
        if keys[pygame.K_d]:
            self.position[0] -= 13
        if keys[pygame.K_a]:
            self.position[0] += 13
        if keys[pygame.K_w]:
            self.position[1] += 13
        if keys[pygame.K_s]:
            self.position[1] -= 13

        glClearColor(0.53, 0.63, 0.98, 1) 
        OpenGL.GL.glClear(OpenGL.GL.GL_COLOR_BUFFER_BIT|OpenGL.GL.GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glTranslatef(*self.position)
        glLight(GL_LIGHT0, GL_POSITION,  (20, 20, -300, 0.9))

        for name, object in self.objects.items():
            print(name + " wird gezeichnet bei " + str((*object[1].getPosition(), "")))

            glPushMatrix()
            glTranslatef(*object[1].getPosition(), 0)
            glRotatef(object[1].getOffRotationForAllAxes()[0], 1, 0, 0)
            glRotatef(object[1].getOffRotationForAllAxes()[1], 0, 1, 0)
            glRotatef(object[1].getOffRotationForAllAxes()[2], 0, 0, 1)
            glRotatef(object[1].getRotation(), 0, 0, 1)
            object[0].drawTexture(self.program)
            #object[0].draw()
            glPopMatrix()

        glPopMatrix()

        print("pos: ", self.position)
        pygame.display.flip()
        self.clock.tick(30)


    def getKeys(self):
        return pygame.key.get_pressed()

    def quit(self):
        pygame.quit()

if __name__ == '__main__':
    s = Scene()
    #self.a.loadByUrl("C:\\Users\\Simon Zeulner\\Desktop\\Atom\\workspace\\KlassenOpenGL\\block\\", "block.obj")
    #self.a.loadByUrl("/Users/simonzeulner/Documents/privat/programmierung/pythonworkspace/KlassenOpenGL/block/", "block.obj")

    s.addObject("/Users/simonzeulner/Documents/privat/programmierung/pythonworkspace/KlassenOpenGL/block/", "block.obj", "block")

    while True:
        s.refresh()
