import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ------------ PALETA PRISMÁTICA (HSV → RGB) ------------ #

def hsv_para_rgb(h, s=1.0, v=1.0):
    h = h % 1.0
    i = int(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return r, g, b

def cor_prismatica(t, ang, idx, ganho_brilho=1.0):
    # fase prismática contínua: tempo + ângulo + índice
    fase = t * 0.25 + ang / (2.0 * math.pi) * 0.6 + idx * 0.013
    h = fase % 1.0
    r, g, b = hsv_para_rgb(h, s=1.0, v=1.0)

    # leve modulação de brilho pra dar vida
    brilho = 0.8 + 0.2 * math.sin(t * 0.7 + idx * 0.17)
    r *= brilho * ganho_brilho
    g *= brilho * ganho_brilho
    b *= brilho * ganho_brilho

    return min(1.0, r), min(1.0, g), min(1.0, b)

# ------------------ FLOR 3D ------------------ #

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

def centro_flor_3d(cx, cy, t, morph):
    r = math.sqrt(cx*cx + cy*cy)
    z_wave = math.sin(r * 1.1 - t * 0.5) * 1.3
    depth_factor = 1.0 - 0.3 * morph
    cz = z_wave * depth_factor
    return cx, cy, cz

def desenhar_anel_multicamadas(cx, cy, raio, t, idx, strength, morph,
                               passos=110, espessura=0.30,
                               camadas=5, dist_z=0.5):
    if strength <= 0:
        return

    cx3, cy3, cz3 = centro_flor_3d(cx, cy, t, morph)

    for k in range(camadas):
        offset = (k - (camadas - 1) / 2.0) * dist_z
        z_layer = cz3 + offset

        random.seed(idx * 1234 + int(t * 4) + k * 31)
        ruido_global = (random.random() - 0.5) * 0.3

        glBegin(GL_TRIANGLE_STRIP)
        for i in range(passos + 1):
            frac = i / float(passos)
            ang = frac * 2.0 * math.pi
            cos_ang = math.cos(ang)
            sin_ang = math.sin(ang)

            deform = 1.0 + 0.18 * math.sin(ang * 6.0 + t * 1.4 + idx * 0.6)
            deform += 0.07 * math.sin(ang * 9.0 - t * 1.9 + idx * 0.4)
            deform += ruido_global * 0.35
            deform = max(0.75, deform)

            raio_int = raio * deform * (1.0 - espessura)
            raio_ext = raio * deform * (1.0 + espessura)

            x_int = cx3 + cos_ang * raio_int
            y_int = cy3 + sin_ang * raio_int
            x_ext = cx3 + cos_ang * raio_ext
            y_ext = cy3 + sin_ang * raio_ext

            r, g, b = cor_prismatica(t, ang, idx + k * 10)

            rand_alpha = 0.7 + 0.2 * (random.random() - 0.5)
            a_ext = max(0.35, min(1.0, rand_alpha)) * strength
            a_int = a_ext * 0.5

            glColor4f(r, g, b, a_ext)
            glVertex3f(x_ext, y_ext, z_layer)

            glColor4f(r, g, b, a_int)
            glVertex3f(x_int, y_int, z_layer)
        glEnd()

def desenhar_flor_random(centros, t, raio_base, strength, morph):
    if strength <= 0:
        return
    for i, (cx, cy) in enumerate(centros):
        fase = i * 0.22
        pulso = 1.0 + 0.06 * math.sin(t * 0.4 + fase)  # flor bem lenta
        raio = raio_base * pulso
        desenhar_anel_multicamadas(cx, cy, raio, t, i, strength, morph)

# ------------------ TRIÂNGULO DARK SIDE ------------------ #

def desenhar_triangulo_dark_side(t, strength):
    if strength <= 0:
        return

    v0 = (-3.0, -1.8, 0.0)
    v1 = ( 3.0, -1.8, 0.0)
    v2 = ( 0.0,  2.3, 0.0)

    # interior escuro
    glBegin(GL_TRIANGLES)
    glColor4f(0.01, 0.01, 0.03, 0.6 * strength)
    glVertex3fv(v0)
    glVertex3fv(v1)
    glVertex3fv(v2)
    glEnd()

    # bordas prismáticas
    glLineWidth(2.5 + 1.5 * strength)
    glBegin(GL_LINE_LOOP)
    for i, (x, y, z) in enumerate((v0, v1, v2)):
        ang = math.atan2(y, x + 0.0001)
        r, g, b = cor_prismatica(t, ang, 300 + i, ganho_brilho=1.2)
        glColor4f(r, g, b, 0.95 * strength)
        glVertex3f(x, y, z)
    glEnd()

    # feixe branco entrando
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor4f(1.0, 1.0, 1.0, 0.95 * strength)
    glVertex3f(-6.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glEnd()

    # feixe prismático saindo
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    segmentos = 14
    for i in range(segmentos + 1):
        frac = i / float(segmentos)
        x = 0.0 + frac * 6.0
        y = 0.0 + frac * 1.0
        ang = frac * 2.0 * math.pi
        r, g, b = cor_prismatica(t + frac * 0.8, ang, 400 + i, ganho_brilho=1.3)
        glColor4f(r, g, b, 0.95 * strength)
        glVertex3f(x, y, 0.0)
    glEnd()

# ------------------ TEXTO ------------------ #

def cor_texto_prismatica(t):
    h = (t * 0.1) % 1.0
    r, g, b = hsv_para_rgb(h, s=1.0, v=1.0)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return (r, g, b)

# ------------------ LOOP PRINCIPAL ------------------ #

def executar_flor_triangulo():
    pygame.init()
    tamanho = (600, 600)
    pygame.display.set_mode(tamanho, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OBRIGADO | FROM PSYCHEDELIC IDEAS | BILL")

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

        # morph batimento lento
        morph = (math.sin(t * 0.6 - math.pi / 2) + 1.0) / 2.0
        flor_strength = 1.0 - morph
        tri_strength  = morph

        if int(t * 0.6) % 2 == 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        ang_y = (t * 18.0) % 360
        ang_x_base  = 12.0
        ang_x_extra = 18.0 * morph
        ang_x = ang_x_base + ang_x_extra

        escala_global = 1.03 + 0.06 * math.sin(t * 0.5)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glRotatef(ang_x, 1, 0, 0)
        glRotatef(ang_y, 0, 1, 0)
        glScalef(escala_global, escala_global, escala_global)

        # Flor volumétrica, agora prismática também
        desenhar_flor_random(centros, t, raio_base, flor_strength, morph)

        # Triângulo prismático “Dark Side”, conectado ao centro
        if tri_strength > 0:
            glPushMatrix()
            zoom_tri       = 1.0 + tri_strength * 1.1
            desloc_z_extra = tri_strength * 4.5
            glTranslatef(0.0, 0.0, desloc_z_extra)
            glScalef(zoom_tri, zoom_tri, zoom_tri)
            desenhar_triangulo_dark_side(t, tri_strength)
            glPopMatrix()

        glPopMatrix()

        texto = "Obrigado pela força, professor"
        cor_txt = cor_texto_prismatica(t)
        cor_sombra = (10, 0, 30)

        texto_surface = fonte.render(texto, True, cor_txt)
        sombra_surface = fonte.render(texto, True, cor_sombra)

        tela = pygame.display.get_surface()
        rect = texto_surface.get_rect()
        rect.center = (tamanho[0] // 2, tamanho[1] - 28)

        wobble_y = int(3 * math.sin(t * 1.3))
        wobble_x = int(2 * math.sin(t * 1.6 + 1.0))
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
    executar_flor_triangulo()
