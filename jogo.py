import pygame
import random
import os
import json 

pygame.init()
pygame.mixer.init()

# ---------------- CONFIGURAÇÃO ----------------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Star Wars Battle – Starter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 35)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_FILE = os.path.join(BASE_DIR, "ranking.json")

# Sons
som_laser = pygame.mixer.Sound(os.path.join(BASE_DIR, "corte.wav"))
som_explosao = pygame.mixer.Sound(os.path.join(BASE_DIR, "morrer.mp3"))

# ---------------- FUNÇÕES LEADERBOARD ----------------
def carregar_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def salvar_leaderboard(scores):
    scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(scores, f, indent=4)

# ---------------- CLASSES ----------------
class Personagem(pygame.sprite.Sprite):
    def __init__(self, nome, x, y, vida, sprite):
        super().__init__()
        self.nome = nome
        self.vida = vida
        self.vida_max = vida
        self.image = pygame.image.load(os.path.join(BASE_DIR, sprite)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

    def sofrer_dano(self, dano):
        self.vida -= dano

class Jedi(Personagem):
    def __init__(self):
        super().__init__("Jedi", WIDTH // 2, HEIGHT - 60, 100, "Ruca.jpeg")
        self.vidas = 5  # DESAFIO 4

class Sith(Personagem):
    def __init__(self):
        x = random.randint(40, WIDTH - 40)
        y = random.randint(-300, -40)
        super().__init__("Sith", x, y, 60, "barbear.jpg")
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.bottom = 0
            self.rect.x = random.randint(40, WIDTH - 40)

    # DESAFIO 1 – Barra dinâmica
    def desenhar_barra_vida(self, superficie):
        largura = 40
        altura = 6
        percentagem = max(0, self.vida / self.vida_max)

        x = self.rect.centerx - largura // 2
        y = self.rect.top - 10

        if percentagem > 0.6:
            cor = (0, 255, 0)
        elif percentagem > 0.3:
            cor = (255, 255, 0)
        else:
            cor = (255, 0, 0)

        pygame.draw.rect(superficie, (60, 60, 60), (x, y, largura, altura))
        pygame.draw.rect(superficie, cor, (x, y, largura * percentagem, altura))

class Boss(Personagem):
    def __init__(self):
        super().__init__("Boss", WIDTH // 2, -100, 300, "barbeiro.jpg")
        self.speed = 2
        self.pontuacao_valor = 100

    def update(self):
        if self.rect.top < 50:
            self.rect.y += self.speed
        else:
            self.rect.x += self.speed
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.speed *= -1

    def desenhar_barra_vida(self, superficie):
        largura = 100
        altura = 10
        percentagem = max(0, self.vida / self.vida_max)
        x = self.rect.centerx - largura // 2
        y = self.rect.top - 20

        pygame.draw.rect(superficie, (0, 0, 0), (x, y, largura, altura))
        pygame.draw.rect(superficie, (255, 0, 0), (x, y, largura * percentagem, altura))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 16))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -7

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# ---------------- MENU SIMPLES ----------------
def pedir_nome():
    nome = ""
    ativo = True
    while ativo:
        screen.fill((255, 255, 255))
        texto = font.render("Insere o teu nome:", True, (0, 0, 0))
        nome_texto = small_font.render(nome, True, (255, 0, 0))
        screen.blit(texto, (WIDTH//2 - texto.get_width()//2, HEIGHT//3))
        screen.blit(nome_texto, (WIDTH//2 - nome_texto.get_width()//2, HEIGHT//2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and nome.strip() != "":
                    return nome
                elif event.key == pygame.K_BACKSPACE:
                    nome = nome[:-1]
                elif len(nome) < 10:
                    nome += event.unicode

nome_jogador = pedir_nome()

# ---------------- JOGO ----------------
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

jedi = Jedi()
all_sprites.add(jedi)

for _ in range(5):
    s = Sith()
    enemies.add(s)
    all_sprites.add(s)

pontuacao = 0
nivel = 1
boss = None
proximo_boss = 200
running = True
game_over = False

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # DESAFIO 2 – limite 3 tiros
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                if len(bullets) < 3:
                    tiro = Bullet(jedi.rect.centerx, jedi.rect.top)
                    bullets.add(tiro)
                    all_sprites.add(tiro)
                    som_laser.play()

    if not game_over:

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and jedi.rect.left > 0:
            jedi.rect.x -= jedi.speed
        if keys[pygame.K_RIGHT] and jedi.rect.right < WIDTH:
            jedi.rect.x += jedi.speed

        all_sprites.update()

        # Spawn Boss
        if pontuacao >= proximo_boss and boss is None:
            boss = Boss()
            all_sprites.add(boss)
            proximo_boss += 200

        # Tiro vs Sith
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy in hits:
            enemy.sofrer_dano(25)
            if enemy.vida <= 0:
                pontuacao += 10  # DESAFIO 5
                som_explosao.play()
                enemy.kill()
                novo = Sith()
                enemies.add(novo)
                all_sprites.add(novo)

        # Tiro vs Boss
        if boss:
            boss_hits = pygame.sprite.spritecollide(boss, bullets, True)
            for b in boss_hits:
                boss.sofrer_dano(25)
                if boss.vida <= 0:
                    pontuacao += boss.pontuacao_valor
                    som_explosao.play()
                    boss.kill()
                    boss = None

        # DESAFIO 3 – Colisão Jedi vs Sith
        colisao = pygame.sprite.spritecollide(jedi, enemies, True)
        for inimigo in colisao:
            jedi.vidas -= 1
            jedi.rect.center = (WIDTH // 2, HEIGHT - 60)
            novo = Sith()
            enemies.add(novo)
            all_sprites.add(novo)

        # Colisão Jedi vs Boss
        if boss and pygame.sprite.collide_rect(jedi, boss):
            jedi.vidas -= 1
            jedi.rect.center = (WIDTH // 2, HEIGHT - 60)

        # DESAFIO 4 – GAME OVER
        if jedi.vidas <= 0:
            game_over = True
            scores = carregar_leaderboard()
            scores.append({"nome": nome_jogador, "score": pontuacao})
            salvar_leaderboard(scores)

        # DESAFIO 8 – Sistema de níveis
        if pontuacao >= nivel * 100:
            nivel += 1
            for enemy in enemies:
                enemy.speed += 1

    # ---------------- DESENHO ----------------
    screen.fill((255, 255, 255))
    all_sprites.draw(screen)

    for enemy in enemies:
        enemy.desenhar_barra_vida(screen)

    if boss:
        boss.desenhar_barra_vida(screen)

    score_texto = small_font.render(f"Score: {pontuacao}", True, (0, 0, 0))
    vidas_texto = small_font.render(f"Vidas: {jedi.vidas}", True, (255, 0, 0))
    nivel_texto = small_font.render(f"Nível: {nivel}", True, (0, 0, 255))

    screen.blit(score_texto, (10, 10))
    screen.blit(vidas_texto, (10, 50))
    screen.blit(nivel_texto, (10, 90))

    # Mostrar GAME OVER + Ranking
    if game_over:
        go = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//3))

        ranking = carregar_leaderboard()
        y_offset = HEIGHT//2

        for i, s in enumerate(ranking):
            texto_rank = small_font.render(
                f"{i+1}. {s['nome']} - {s['score']}",
                True,
                (0, 0, 0)
            )
            screen.blit(texto_rank, (WIDTH//2 - texto_rank.get_width()//2, y_offset))
            y_offset += 30

    pygame.display.flip()

pygame.quit()