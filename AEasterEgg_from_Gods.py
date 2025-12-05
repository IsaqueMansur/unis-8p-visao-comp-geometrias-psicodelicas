import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


# ----------------- CORES -----------------

def cor_neon_frio(t, u, v, idx):
    """
    Paleta psicodélica mais fria (azul / ciano / roxo).
    """
    base = t * 0.6 + u * 1.8 + v * 1.3 + idx * 0.29

    # componentes base
    b = 0.5 + 0.5 * math.sin(base + 0.0)          # azul
    g = 0.4 + 0.6 * math.sin(base + 2.4)          # ciano-esverdeado
    r = 0.2 + 0.3 * math.sin(base + 4.1)          # pouco vermelho só pra nuance

    # clamp pra evitar valores negativos antes do expoente fracionário
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))

    # puxar pra neon frio
    r = r ** 0.8
    g = g ** 0.6
    b = b ** 0.5

    return r, g, b


def cor_texto(t):
    base = t * 0.5
    r = int((0.6 + 0.3 * math.sin(base * 1.3)) * 255)
    g = int((0.8 + 0.2 * math.sin(base * 1.7 + 1.1)) * 255)
    b = int((0.9 + 0.1 * math.cos(base * 1.1)) * 255)
    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )


# ----------------- FUNDO / ESTRELAS / NEBULOSA -----------------

def desenhar_fundo_estrelas(t, strength):
    if strength <= 0:
        return

    glPushMatrix()
    glTranslatef(0.0, 0.0, -40.0)

    glPointSize(2.0)
    glBegin(GL_POINTS)

    random.seed(1234)
    num_estrelas = 450

    for i in range(num_estrelas):
        x = (random.random() - 0.5) * 80.0
        y = (random.random() - 0.5) * 60.0
        u = random.random()
        v = random.random() * 2 * math.pi

        r, g, b = cor_neon_frio(t * 0.3, u, v, i)

        twinkle = 0.4 + 0.6 * (
            0.5
            + 0.5 * math.sin(t * (1.0 + u * 2.0) + i * 0.37)
        )

        glColor4f(r, g, b, twinkle * 0.6 * strength)
        glVertex3f(x, y, 0.0)

    glEnd()
    glPopMatrix()


def desenhar_nebulosa_espiral(t, strength):
    if strength <= 0:
        return

    glPushMatrix()
    glTranslatef(0.0, 0.0, -20.0)

    num_espirais = 4
    passos = 220

    for s in range(num_espirais):
        ang_offset = s * (2.0 * math.pi / num_espirais) + t * 0.08
        glBegin(GL_LINE_STRIP)

        for i in range(passos):
            u = i / (passos - 1)
            ang = u * 7.0 * math.pi + ang_offset
            raio = 2.0 + 10.0 * u + 1.0 * math.sin(t * 0.4 + i * 0.05)

            x = math.cos(ang) * raio
            y = math.sin(ang) * raio * (0.7 + 0.1 * math.sin(t * 0.5))

            r, g, b = cor_neon_frio(t, u, ang, 1000 + s * 100 + i)
            alpha = (0.04 + 0.22 * (1.0 - u)) * strength

            glColor4f(r, g, b, alpha)
            glVertex3f(x, y, 0.0)

        glEnd()

    glPopMatrix()


# ----------------- ONDAS EM ESPIRAL (só elas) -----------------

def desenhar_ondas_espirais(t, strength):
    """
    Ondas em espiral (linhas) que aparecem/somem.
    Nada de formas centrais, só redemoinhos.
    """
    if strength <= 0:
        return

    glPushMatrix()
    glTranslatef(0.0, 0.0, -5.0)

    num_espirais = 7
    passos = 190

    for s in range(num_espirais):
        ang_offset = s * (2.0 * math.pi / num_espirais)
        fase_global = t * (0.7 + 0.12 * s)

        glLineWidth(1.3 + 0.5 * math.sin(t * 0.9 + s))

        glBegin(GL_LINE_STRIP)
        for i in range(passos):
            u = i / (passos - 1)

            # base da espiral
            ang = u * 6.5 * math.pi + ang_offset + 0.5 * math.sin(fase_global)
            raio = 1.2 + 9.0 * u

            # ondulação radial
            ond = 0.6 * math.sin(u * 18.0 + fase_global + s)
            raio_aj = raio + ond

            x = math.cos(ang) * raio_aj
            y = math.sin(ang) * raio_aj

            r, g, b = cor_neon_frio(t, u, ang, 2500 + s * 300 + i)

            # "aparecimento" ao longo da espiral
            mask = 0.5 + 0.5 * math.sin(fase_global + i * 0.2)
            mask = mask ** 1.7

            alpha = (0.2 + 0.6 * (1.0 - u)) * mask * strength

            if alpha < 0.02:
                alpha = 0.0

            glColor4f(r, g, b, alpha)
            glVertex3f(x, y, 0.0)
        glEnd()

    glPopMatrix()


# ----------------- LOOP PRINCIPAL -----------------

def executar_galaxia_psicodelica():
    pygame.init()
    tamanho = (800, 600)
    pygame.display.set_mode(tamanho, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("PSYCHEDELIC GALAXY BLACK HOLE | FROM THE DIVISION BELL")

    pygame.font.init()
    fonte = pygame.font.SysFont("Arial", 20, bold=True)

    gluPerspective(45, tamanho[0] / tamanho[1], 0.1, 200.0)
    glTranslatef(0.0, 0.0, -25.0)
    glEnable(GL_DEPTH_TEST)

    # fundo bem escuro com um toque roxo
    glClearColor(0.0, 0.0, 0.02, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_LIGHTING)

    relogio = pygame.time.Clock()
    ativo = True

    while ativo:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ativo = False
            if evento.type == KEYDOWN and evento.key == K_ESCAPE:
                ativo = False

        t = pygame.time.get_ticks() / 1000.0

        strength = 0.8 + 0.2 * math.sin(t * 0.5)

        ang_y = math.sin(t * 0.06) * 10.0
        ang_x = 9.0 + 4.0 * math.sin(t * 0.09)
        escala = 2.3 + 0.08 * math.sin(t * 0.3)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Fundo e nebulosa
        desenhar_fundo_estrelas(t, strength)
        desenhar_nebulosa_espiral(t, strength * 0.9)

        glPushMatrix()
        glRotatef(ang_x, 1, 0, 0)
        glRotatef(ang_y, 0, 1, 0)
        glScalef(escala, escala, escala)

        # Só espirais psicodélicas
        desenhar_ondas_espirais(t, strength * 0.95)

        glPopMatrix()

        # Texto
        texto = "Obrigado pela força, professor"
        cor_txt = cor_texto(t)
        cor_sombra = (0, 0, 0)

        tela = pygame.display.get_surface()
        texto_surface = fonte.render(texto, True, cor_txt)
        sombra_surface = fonte.render(texto, True, cor_sombra)

        rect = texto_surface.get_rect()
        rect.center = (tamanho[0] // 2, tamanho[1] - 28)

        wobble_y = int(3 * math.sin(t * 1.1))
        wobble_x = int(3 * math.sin(t * 1.5 + 1.0))
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
    executar_galaxia_psicodelica()
