import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def gerar_centros_flor(raio_base, alcance_hex=2):
    centros = []
    raiz3 = math.sqrt(3)
    for q in range(-alcance_hex, alcance_hex + 1):
        for r in range(-alcance_hex, alcance_hex + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= alcance_hex:
                x = raiz3 * (q + r / 2.0) * raio_base
                y = 1.5 * r * raio_base
                centros.append((x, y))
    return centros

def cor_vermelho_azul(t, ang, idx):
    base = t * 1.7 + ang * 2.4 + idx * 0.6

    vermelho = (1.0, 0.1, 0.1)
    magenta  = (1.0, 0.0, 0.7)
    roxo     = (0.7, 0.1, 0.9)
    azul     = (0.1, 0.2, 1.0)
    ciano    = (0.1, 1.0, 1.0)

    random.seed(idx * 777 + int(ang * 30) + int(t * 4))
    jitter = (random.random() - 0.5) * 0.2

    w1 = 0.35 + 0.25 * math.sin(base * 1.1) + jitter       # vermelho
    w2 = 0.20 + 0.20 * math.sin(base * 1.4 + 0.7)          # magenta
    w3 = 0.15 + 0.15 * math.sin(base * 1.7 + 1.5)          # roxo
    w4 = 0.15 + 0.15 * math.sin(base * 2.0 + 2.4)          # azul
    w5 = max(0.0, 1.0 - (w1 + w2 + w3 + w4))               # ciano

    r = (vermelho[0] * w1 + magenta[0] * w2 +
         roxo[0] * w3 + azul[0] * w4 + ciano[0] * w5)
    g = (vermelho[1] * w1 + magenta[1] * w2 +
         roxo[1] * w3 + azul[1] * w4 + ciano[1] * w5)
    b = (vermelho[2] * w1 + magenta[2] * w2 +
         roxo[2] * w3 + azul[2] * w4 + ciano[2] * w5)

    sat = 1.25
    r = min(1.0, r * sat)
    g = min(1.0, g * sat)
    b = min(1.0, b * sat)

    brilho = 0.8 + 0.2 * math.sin(base * 1.9)
    r *= brilho
    g *= brilho
    b *= brilho

    return r, g, b

def desenhar_anel_random(cx, cy, raio, t, idx, passos=110, espessura=0.30):
    random.seed(idx * 1234 + int(t * 5))
    ruido_global = (random.random() - 0.5) * 0.35

    glBegin(GL_TRIANGLE_STRIP)
    for i in range(passos + 1):
        frac = i / float(passos)
        ang = frac * 2.0 * math.pi
        cos_ang = math.cos(ang)
        sin_ang = math.sin(ang)

        deform = 1.0 + 0.2 * math.sin(ang * 6.0 + t * 2.3 + idx * 0.6)
        deform += 0.08 * math.sin(ang * 9.0 - t * 3.2 + idx * 0.4)
        deform += ruido_global * 0.4
        deform = max(0.75, deform)

        raio_int = raio * deform * (1.0 - espessura)
        raio_ext = raio * deform * (1.0 + espessura)

        x_int = cx + cos_ang * raio_int
        y_int = cy + sin_ang * raio_int
        x_ext = cx + cos_ang * raio_ext
        y_ext = cy + sin_ang * raio_ext

        r, g, b = cor_vermelho_azul(t, ang, idx)

        rand_alpha = 0.8 + 0.2 * (random.random() - 0.5)
        a_ext = max(0.4, min(1.0, rand_alpha))
        a_int = a_ext * 0.5

        glColor4f(r, g, b, a_ext)
        glVertex3f(x_ext, y_ext, 0.0)

        glColor4f(r, g, b, a_int)
        glVertex3f(x_int, y_int, 0.0)
    glEnd()

def desenhar_flor_random(centros, t, raio_base):
    for i, (cx, cy) in enumerate(centros):
        fase = i * 0.22
        pulso = 1.0 + 0.2 * math.sin(t * 1.5 + fase)
        raio = raio_base * pulso
        desenhar_anel_random(cx, cy, raio, t, i)

def cor_texto_rb(t):
    base = t * 1.7
    r = 200 + 55 * math.sin(base * 1.1)
    g = 40 + 30 * math.sin(base * 1.6 + 1.1)
    b = 200 + 55 * math.cos(base * 1.3)
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    return (r, g, b)

def executar_flor():
    pygame.init()
    tamanho = (600, 600)
    pygame.display.set_mode(tamanho, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Flor da Vida Vermelho ↔ Azul")

    pygame.font.init()
    fonte = pygame.font.SysFont("Arial", 22, bold=True)

    gluPerspective(45, tamanho[0] / tamanho[1], 0.1, 200.0)
    glTranslatef(0.0, 0.0, -32.0)
    glEnable(GL_DEPTH_TEST)

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_LIGHTING)

    raio_base = 2.2
    centros = gerar_centros_flor(raio_base, alcance_hex=2)

    relogio = pygame.time.Clock()
    ativo = True

    while ativo:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ativo = False
            if evento.type == KEYDOWN and evento.key == K_ESCAPE:
                ativo = False

        t = pygame.time.get_ticks() / 1000.0

        if int(t * 2.3) % 2 == 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        ang_z = (t * 20.0) % 360
        escala = 1.05 + 0.22 * math.sin(t * 1.3)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()

        glRotatef(ang_z, 0, 0, 1)
        glScalef(escala, escala, escala)

        desenhar_flor_random(centros, t, raio_base)

        glPopMatrix()

        texto = "Obrigado pela força, professor"
        cor_txt = cor_texto_rb(t)
        cor_sombra = (10, 0, 30)

        texto_surface = fonte.render(texto, True, cor_txt)
        sombra_surface = fonte.render(texto, True, cor_sombra)

        tela = pygame.display.get_surface()
        rect = texto_surface.get_rect()
        rect.center = (tamanho[0] // 2, tamanho[1] - 28)

        wobble_y = int(4 * math.sin(t * 2.7))
        wobble_x = int(3 * math.sin(t * 3.1 + 1.0))
        rect.y += wobble_y
        rect.x += wobble_x

        sombra_rect = rect.copy()
        sombra_rect.move_ip(2, 2)

        tela.blit(sombra_surface, sombra_rect)
        tela.blit(texto_surface, rect)

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()

if __name__ == "__main__":
    executar_flor()
