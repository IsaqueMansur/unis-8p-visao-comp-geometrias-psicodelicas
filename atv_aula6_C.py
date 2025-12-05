import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def desenhar_esfera(tempo, raio=1.8, div_long=40, div_lat=28):
    for i in range(div_lat):
        phi1 = math.pi * (-0.5 + i / float(div_lat))
        z1 = math.sin(phi1) * raio
        r1 = math.cos(phi1) * raio

        phi2 = math.pi * (-0.5 + (i + 1) / float(div_lat))
        z2 = math.sin(phi2) * raio
        r2 = math.cos(phi2) * raio

        glBegin(GL_QUAD_STRIP)
        for j in range(div_long + 1):
            t_cor = (i / div_lat) + (j / div_long) + tempo * 0.7
            r = 0.5 + 0.5 * math.sin(t_cor * 3.1)
            g = 0.5 + 0.5 * math.sin(t_cor * 4.3 + 1.5)
            b = 0.5 + 0.5 * math.cos(t_cor * 2.7 + 0.7)

            theta = 2 * math.pi * j / float(div_long)
            x2 = math.cos(theta) * r2
            y2 = math.sin(theta) * r2
            glColor3f(r, g, b)
            glNormal3f(x2 / raio, y2 / raio, z2 / raio)
            glVertex3f(x2, y2, z2)

            x1 = math.cos(theta) * r1
            y1 = math.sin(theta) * r1
            glColor3f(b, r, g)
            glNormal3f(x1 / raio, y1 / raio, z1 / raio)
            glVertex3f(x1, y1, z1)
        glEnd()

def configurar_luz():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (3, 7, 5, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.15, 1))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 60.0)

def executar():
    pygame.init()
    tamanho = (1000, 700)
    pygame.display.set_mode(tamanho, DOUBLEBUF | OPENGL)
    gluPerspective(55, tamanho[0] / tamanho[1], 0.1, 150.0)
    glTranslatef(0.0, 0.0, -10.0)
    glEnable(GL_DEPTH_TEST)

    glClearColor(0.02, 0.02, 0.05, 1.0)

    configurar_luz()

    relogio = pygame.time.Clock()
    ativo = True

    while ativo:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ativo = False
            if evento.type == KEYDOWN and evento.key == K_ESCAPE:
                ativo = False

        t = pygame.time.get_ticks() / 1000.0

        ang_x = math.sin(t * 0.9) * 60
        ang_y = math.cos(t * 0.7) * 90
        ang_z = math.sin(t * 1.3) * 45

        escala = 1.0 + 0.25 * math.sin(t * 2.0)
        deslocamento_z = -10.0 + 1.0 * math.sin(t * 0.6)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glTranslatef(0.0, 0.0, deslocamento_z + 10.0)
        glScalef(escala, escala, escala)
        glRotatef(ang_x, 1, 0, 0)
        glRotatef(ang_y, 0, 1, 0)
        glRotatef(ang_z, 0, 0, 1)

        desenhar_esfera(t)

        glPopMatrix()
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()

if __name__ == "__main__":
    executar()
