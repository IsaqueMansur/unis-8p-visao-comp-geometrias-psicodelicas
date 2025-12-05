import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

pontos_cubo = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

faces_cubo = (
    (0, 1, 2, 3),
    (4, 5, 1, 0),
    (7, 6, 4, 5),
    (2, 7, 5, 1),
    (3, 2, 7, 6),
    (6, 3, 0, 4)
)

def desenhar_cubo_psico(t):
    glBegin(GL_QUADS)
    total_faces = len(faces_cubo)
    for i, face in enumerate(faces_cubo):
        base = i / float(total_faces)
        for j, idx in enumerate(face):
            x, y, z = pontos_cubo[idx]
            u = j / 4.0
            s = t * 1.0 + base * 3.0 + u * 2.5 + (x + y + z) * 0.4
            r = 0.5 + 0.5 * math.sin(s * 2.1)
            g = 0.5 + 0.5 * math.sin(s * 2.7 + 1.3)
            b = 0.5 + 0.5 * math.cos(s * 3.2 + 0.8)
            glColor3f(r, g, b)
            glVertex3f(x, y, z)
    glEnd()

def configurar_luz_cubo():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (-3.0, 7.0, 5.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.16, 1.0))
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 65.0)

def executar_cubo():
    pygame.init()
    tamanho = (1000, 700)
    pygame.display.set_mode(tamanho, DOUBLEBUF | OPENGL)
    gluPerspective(60, tamanho[0] / tamanho[1], 0.1, 150.0)
    glTranslatef(0.0, 0.0, -10.0)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.01, 0.01, 0.04, 1.0)
    configurar_luz_cubo()

    relogio = pygame.time.Clock()
    ativo = True

    while ativo:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ativo = False
            if evento.type == KEYDOWN and evento.key == K_ESCAPE:
                ativo = False

        t = pygame.time.get_ticks() / 1000.0
        ang_x = math.sin(t * 0.8) * 70
        ang_y = math.cos(t * 1.1) * 110
        ang_z = math.sin(t * 1.6) * 50
        escala = 1.0 + 0.25 * math.sin(t * 1.9)
        desloc_z = -10.0 + 1.2 * math.sin(t * 0.7)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glTranslatef(0.0, 0.0, desloc_z + 10.0)
        glRotatef(ang_x, 1, 0, 0)
        glRotatef(ang_y, 0, 1, 0)
        glRotatef(ang_z, 0, 0, 1)
        glScalef(escala, escala, escala)

        desenhar_cubo_psico(t)

        glPopMatrix()
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()

if __name__ == "__main__":
    executar_cubo()
