import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

pontos_pira = (
    (1, -1, -1),
    (1, -1, 1),
    (-1, -1, 1),
    (-1, -1, -1),
    (0, 1, 0)
)

faces_pira = (
    (0, 1, 2, 3),
    (0, 1, 4),
    (1, 2, 4),
    (2, 3, 4),
    (3, 0, 4)
)

def cor_psico(a, b, c, t, o):
    s = t * 2.0 + a * 1.2 + b * 1.7 + c * 2.3 + o
    r = 0.5 + 0.5 * math.sin(s * 1.9)
    g = 0.5 + 0.5 * math.sin(s * 2.6 + 1.4)
    b = 0.5 + 0.5 * math.cos(s * 3.1 + 0.7)
    return r, g, b

def desenhar_piramide_psico(t):
    glBegin(GL_QUADS)
    for i, idx in enumerate(faces_pira[0]):
        x, y, z = pontos_pira[idx]
        r, g, b = cor_psico(x, y, z, t, i * 0.8)
        glColor3f(r, g, b)
        glVertex3f(x, y, z)
    glEnd()

    glBegin(GL_TRIANGLES)
    for f, face in enumerate(faces_pira[1:]):
        for v, idx in enumerate(face):
            x, y, z = pontos_pira[idx]
            r, g, b = cor_psico(x, y, z, t, f * 1.3 + v * 0.9)
            glColor3f(r, g, b)
            glVertex3f(x, y, z)
    glEnd()

def chama_a_piramide_psicodelica_de_jise():
    pygame.init()
    dimensao = (1000, 700)
    pygame.display.set_mode(dimensao, DOUBLEBUF | OPENGL)

    gluPerspective(65, dimensao[0] / dimensao[1], 0.1, 150.0)
    glTranslatef(0.0, 0.0, -12.0)
    glEnable(GL_DEPTH_TEST)

    glClearColor(0.01, 0.0, 0.05, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    relogio = pygame.time.Clock()
    ativo = True

    while ativo:
        for e in pygame.event.get():
            if e.type == QUIT:
                ativo = False
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                ativo = False

        t = pygame.time.get_ticks() / 1000.0

        if int(t * 3) % 2 == 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        ang_x = math.sin(t * 1.4) * 80
        ang_y = (t * 140.0) % 360
        ang_z = math.cos(t * 1.1) * 70

        escala = 1.2 + 0.3 * math.sin(t * 2.3)
        desl_z = -12.0 + 1.8 * math.sin(t * 0.9)
        desl_y = 0.4 * math.sin(t * 1.7)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glTranslatef(0.0, desl_y, desl_z + 12.0)
        glRotatef(ang_x, 1, 0, 0)
        glRotatef(ang_y, 0, 1, 0)
        glRotatef(ang_z, 0, 0, 1)
        glScalef(escala, escala, escala)

        desenhar_piramide_psico(t)

        glPopMatrix()
        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()

if __name__ == "__main__":
    chama_a_piramide_psicodelica_de_jise()
