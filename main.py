import pygame
import os
from sprites import Player, Bullet, Enemy, load_img, WIDTH, HEIGHT

# --- SETUP ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane War Arcade")
clock = pygame.time.Clock()

# --- LOAD BACKGROUNDS ---
bg_img = load_img(os.path.join('resources','background.jpg'), (WIDTH, HEIGHT))
menu_bg = load_img(os.path.join('resources','menupicture.jpg'), (WIDTH, HEIGHT))

# Fonts
try:
    # ka1 is a pixel font. Small HUD sizes look crispest with AA off (handled
    # where they're rendered). Larger title/button sizes look smoother with AA
    # on, which draw_text does by default.
    arcadefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 16)
    energyfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 10)
    healthfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 8)
    titlefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 40)
    btnfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 24)
    font_is_pixel = True
except (pygame.error, OSError):
    arcadefont = pygame.font.SysFont('arial', 16, bold=True)
    energyfont = pygame.font.SysFont('arial', 10, bold=True)
    healthfont = pygame.font.SysFont('arial', 8, bold=True)
    titlefont = pygame.font.SysFont('arial', 40, bold=True)
    btnfont = pygame.font.SysFont('arial', 24, bold=True)
    font_is_pixel = False

# Audio
try:
    pygame.mixer.music.load(os.path.join('resources','sound','Street Fighter - Guile Stage.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
except (pygame.error, OSError):
    pass

def draw_text(text, font, color, surface, x, y, align="left", aa=True):
    # Large pixel-font sizes (title, buttons) look best with AA on. HUD text
    # renders inline with AA off where pixel-perfect crispness matters.
    textobj = font.render(text, aa, color)
    textrect = textobj.get_rect()
    if align == "center":
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- INIT GROUPS ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

running = True
in_menu = True
paused = False
game_over = False
spawn_timer = 0
shoot_timer = 0
bg_y = 0

# HUD: both bars stacked on the right, health on top (smaller), energy below
ENERGY_FILL_W = 100
ENERGY_FILL_H = 12
ENERGY_BOX_W = ENERGY_FILL_W + 4
ENERGY_BOX_H = ENERGY_FILL_H + 4
# Health bar is 75% of the energy bar — same aspect ratio, smaller overall.
HEALTH_FILL_W = int(ENERGY_FILL_W * 0.75)
HEALTH_FILL_H = int(ENERGY_FILL_H * 0.75)
HEALTH_BOX_W = HEALTH_FILL_W + 4
HEALTH_BOX_H = HEALTH_FILL_H + 4
HUD_X = WIDTH - ENERGY_BOX_W - 16
ENERGY_BOX_Y = HEIGHT - ENERGY_BOX_H - 8
HEALTH_BOX_Y = ENERGY_BOX_Y - HEALTH_BOX_H - 4
HEALTH_BOX = pygame.Rect(HUD_X, HEALTH_BOX_Y, HEALTH_BOX_W, HEALTH_BOX_H)
ENERGY_BOX = pygame.Rect(HUD_X, ENERGY_BOX_Y, ENERGY_BOX_W, ENERGY_BOX_H)
HUD_FADE_SPEED = 1000  # alpha units per second
energy_alpha = 255.0
health_alpha = 255.0

def reset_game():
    global player, spawn_timer, shoot_timer, bg_y, game_over, energy_alpha, health_alpha
    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    player = Player()
    all_sprites.add(player)
    spawn_timer = 0
    shoot_timer = 0
    bg_y = 0
    energy_alpha = 255.0
    health_alpha = 255.0
    game_over = False

# --- MAIN LOOP ---
while running:
    # Cap dt so a long pause (window drag, GC) can't teleport sprites through each other.
    dt = min(clock.tick(60) / 1000.0, 1 / 30.0)

    # --- MENU LOOP ---
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

    # --- GAME LOOP ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_m:
                    reset_game()
                    in_menu = True
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                paused = not paused

    if not paused and not game_over:
        # Shoot
        shoot_timer += dt
        if shoot_timer > 0.6:
            b = Bullet(player.rect.centerx, player.rect.top)
            all_sprites.add(b)
            bullets.add(b)
            shoot_timer -= 0.6

        # Spawn
        spawn_timer += dt
        if spawn_timer > 1.2:
            e = Enemy()
            all_sprites.add(e)
            enemies.add(e)
            spawn_timer -= 1.2

        all_sprites.update(dt)

        # --- COLLISION: BULLETS vs ENEMIES ---
        hits = pygame.sprite.groupcollide(enemies, bullets, False, False)
        for enemy, bullet_list in hits.items():
            if enemy.dying:
                continue

            for b in bullet_list:
                if not b.exploding:
                    b.explode()
                    enemy.hp -= 1
                    if enemy.hp <= 0:
                        enemy.die()

        # --- COLLISION: PLAYER vs ENEMIES (UPDATED) ---
        # Change True to False so the enemy stays alive to play animation
        hit_player = pygame.sprite.spritecollide(player, enemies, False)

        if hit_player:
            for e in hit_player:
                # Only trigger damage if the enemy isn't ALREADY exploding
                if not e.dying:
                    player.health -= 20
                    e.die() # Trigger the explosion animation

            if player.health <= 0:
                player.health = 0
                game_over = True

        # Draw Background
        bg_y += 100 * dt
        if bg_y >= HEIGHT: bg_y = 0

    screen.blit(bg_img, (0, int(bg_y)))
    screen.blit(bg_img, (0, int(bg_y) - HEIGHT))

    all_sprites.draw(screen)

    # UI: fade each HUD box out when the plane flies over it
    energy_target = 0 if player.rect.colliderect(ENERGY_BOX) else 255
    health_target = 0 if player.rect.colliderect(HEALTH_BOX) else 255
    step = HUD_FADE_SPEED * dt
    if energy_alpha < energy_target:
        energy_alpha = min(energy_alpha + step, energy_target)
    elif energy_alpha > energy_target:
        energy_alpha = max(energy_alpha - step, energy_target)
    if health_alpha < health_target:
        health_alpha = min(health_alpha + step, health_target)
    elif health_alpha > health_target:
        health_alpha = max(health_alpha - step, health_target)

    aa = not font_is_pixel

    # Energy bar (bottom)
    energy_fill = int(max(0, min(player.energy, 100)) / 100 * ENERGY_FILL_W)
    energy_surf = pygame.Surface((ENERGY_BOX_W, ENERGY_BOX_H), pygame.SRCALPHA)
    pygame.draw.rect(energy_surf, (0,0,255), (2, 2, energy_fill, ENERGY_FILL_H))
    pygame.draw.rect(energy_surf, (255,255,255), (0, 0, ENERGY_BOX_W, ENERGY_BOX_H), 2)
    if player.energy < 30 and (pygame.time.get_ticks() // 300) % 2 == 0:
        label = energyfont.render("LOW ENERGY", aa, (255, 60, 60))
    else:
        label = energyfont.render("ENERGY", aa, (255,255,255))
    energy_surf.blit(label, label.get_rect(center=(ENERGY_BOX_W // 2, ENERGY_BOX_H // 2)))
    energy_surf.set_alpha(int(energy_alpha))
    screen.blit(energy_surf, ENERGY_BOX.topleft)

    # Health bar (top, 75% size, smaller label to match)
    health_fill = int(max(0, min(player.health, 100)) / 100 * HEALTH_FILL_W)
    health_surf = pygame.Surface((HEALTH_BOX_W, HEALTH_BOX_H), pygame.SRCALPHA)
    pygame.draw.rect(health_surf, (255,0,0), (2, 2, health_fill, HEALTH_FILL_H))
    pygame.draw.rect(health_surf, (255,255,255), (0, 0, HEALTH_BOX_W, HEALTH_BOX_H), 2)
    label = healthfont.render("HEALTH", aa, (255,255,255))
    health_surf.blit(label, label.get_rect(center=(HEALTH_BOX_W // 2, HEALTH_BOX_H // 2)))
    health_surf.set_alpha(int(health_alpha))
    screen.blit(health_surf, HEALTH_BOX.topleft)

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", titlefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 - 20, "center")
        draw_text("Press P to resume", arcadefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 + 30, "center")

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        draw_text("GAME OVER", titlefont, (255, 60, 60), screen, WIDTH//2, HEIGHT//2 - 40, "center")
        draw_text("R - RESTART", arcadefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 + 20, "center")
        draw_text("M - MAIN MENU", arcadefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 + 50, "center")

    pygame.display.flip()

pygame.quit()
