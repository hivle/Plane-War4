import pygame
import os
import random

# --- 1. SETUP ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 450, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane War Arcade")
clock = pygame.time.Clock()

# --- 2. ASSETS ---
def load_img(path, size=None):
    try:
        if not os.path.exists(path):
            return pygame.Surface(size if size else (50,50)) 
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.scale(img, size)
        return img
    except:
        return pygame.Surface(size if size else (50,50))

bg_img = load_img(os.path.join('resources','background.jpg'), (WIDTH, HEIGHT))
menu_bg = load_img(os.path.join('resources','menupicture.jpg'), (WIDTH, HEIGHT))
plane_img = load_img(os.path.join('resources','plane.png'), (50, 50))
enemy_img = load_img(os.path.join('resources','HENRY.png'), (50, 50))

# --- LOAD ANIMATIONS ---
travel_frames = []
for i in range(1, 5): 
    img = load_img(os.path.join('resources', 'sprites', f'b{i}.png'), (30, 30))
    travel_frames.append(img)

hit_frames = []
for i in range(5, 8): 
    img = load_img(os.path.join('resources', 'sprites', f'b{i}.png'), (30, 30))
    hit_frames.append(img)

# Fonts & Audio
try:
    arcadefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 15)
    titlefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 40)
    btnfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 25)
    pygame.mixer.music.load(os.path.join('resources','sound','Street Fighter - Guile Stage.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
except:
    arcadefont = pygame.font.SysFont('arial', 15, bold=True)
    titlefont = pygame.font.SysFont('arial', 40, bold=True)
    btnfont = pygame.font.SysFont('arial', 25, bold=True)

# --- 3. CLASSES ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = plane_img
        self.rect = self.image.get_rect()
        self.pos_x = WIDTH // 2
        self.pos_y = HEIGHT - 100
        self.rect.center = (self.pos_x, self.pos_y)
        self.speed = 400 
        self.energy = 100
        self.health = 100

    def update(self, dt):
        keys = pygame.key.get_pressed()
        move = self.speed * dt
        
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.energy > 0:
            move *= 1.5 
            self.energy -= 30 * dt 
        elif self.energy < 100:
            self.energy += 10 * dt 

        if keys[pygame.K_w] or keys[pygame.K_UP]: self.pos_y -= move
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.pos_y += move
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.pos_x -= move
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.pos_x += move

        self.pos_x = max(0, min(self.pos_x, WIDTH))
        self.pos_y = max(0, min(self.pos_y, HEIGHT))
        self.rect.center = (int(self.pos_x), int(self.pos_y))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.travel_anim = travel_frames
        self.hit_anim = hit_frames
        self.frames = self.travel_anim 
        
        self.current_frame = 0
        self.anim_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        
        self.pos_y = y
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -250 
        self.exploding = False

    def explode(self):
        if not self.exploding:
            self.exploding = True
            self.frames = self.hit_anim
            self.current_frame = 0
            self.speed = 0

    def update(self, dt):
        if not self.exploding:
            self.pos_y += self.speed * dt
            self.rect.centery = int(self.pos_y)
        
        # --- ANIMATION SPEED CONTROL ---
        self.anim_timer += dt
        
        # 0.05 = Super fast (Explosion)
        # 0.50 = Super slow (Travel)
        threshold = 0.05 if self.exploding else 0.5
        
        if self.anim_timer >= threshold: 
            self.anim_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.exploding:
                    self.kill()
                    return
                else:
                    self.current_frame = 0 
            self.image = self.frames[self.current_frame]

        if self.rect.bottom < 0: self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.pos_y = -50
        self.rect.x = random.randint(0, WIDTH - 50)
        self.rect.y = self.pos_y
        self.speed = random.randint(200, 400) 
        self.hp = 3

    def update(self, dt):
        self.pos_y += self.speed * dt
        self.rect.y = int(self.pos_y)
        if self.rect.top > HEIGHT: self.kill()

def draw_text(text, font, color, surface, x, y, align="left"):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if align == "center":
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- 4. INIT ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

running = True
in_menu = True
spawn_timer = 0
shoot_timer = 0
bg_y = 0

# --- 5. MAIN LOOP ---
while running:
    dt = clock.tick(60) / 1000.0 

    if in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 175 < mx < 295 and 400 < my < 430: in_menu = False
                if 180 < mx < 300 and 600 < my < 630: running = False

        screen.blit(menu_bg, (0,0))
        draw_text("PLANE WAR", titlefont, (255,255,255), screen, WIDTH//2, 100, "center")
        draw_text("PLAY", btnfont, (200,200,200), screen, WIDTH//2, 415, "center")
        draw_text("EXIT", btnfont, (200,200,200), screen, WIDTH//2, 615, "center")
        pygame.display.flip()
        continue 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    shoot_timer += dt
    if shoot_timer > 0.6: 
        b = Bullet(player.rect.centerx, player.rect.top)
        all_sprites.add(b)
        bullets.add(b)
        shoot_timer = 0

    spawn_timer += dt
    if spawn_timer > 1.0:
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)
        spawn_timer = 0

    all_sprites.update(dt)

    hits = pygame.sprite.groupcollide(enemies, bullets, False, False)
    for enemy, bullet_list in hits.items():
        for b in bullet_list:
            if not b.exploding:
                b.explode() 
                enemy.hp -= 1 
                if enemy.hp <= 0:
                    enemy.kill() 

    if pygame.sprite.spritecollide(player, enemies, True):
        player.health -= 20
        if player.health <= 0: running = False

    bg_y += 100 * dt
    if bg_y >= HEIGHT: bg_y = 0
    screen.blit(bg_img, (0, int(bg_y)))
    screen.blit(bg_img, (0, int(bg_y) - HEIGHT))
    
    all_sprites.draw(screen)

    pygame.draw.rect(screen, (0,0,255), (20, 670, int(player.energy), 20)) 
    pygame.draw.rect(screen, (255,255,255), (18, 668, 104, 24), 2) 
    pygame.draw.rect(screen, (255,0,0), (320, 670, int(player.health), 20)) 
    pygame.draw.rect(screen, (255,255,255), (318, 668, 104, 24), 2) 
    
    pygame.display.flip()

pygame.quit()
