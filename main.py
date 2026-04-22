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
    arcadefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 15)
    titlefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 40)
    btnfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 25)
except (pygame.error, OSError):
    arcadefont = pygame.font.SysFont('arial', 15, bold=True)
    titlefont = pygame.font.SysFont('arial', 40, bold=True)
    btnfont = pygame.font.SysFont('arial', 25, bold=True)

# Audio
try:
    pygame.mixer.music.load(os.path.join('resources','sound','Street Fighter - Guile Stage.mp3'))
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)
except (pygame.error, OSError):
    pass

def draw_text(text, font, color, surface, x, y, align="left"):
    textobj = font.render(text, True, color)
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
spawn_timer = 0
shoot_timer = 0
bg_y = 0

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
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_p, pygame.K_ESCAPE):
            paused = not paused

    if not paused:
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
                running = False

        # Draw Background
        bg_y += 100 * dt
        if bg_y >= HEIGHT: bg_y = 0

    screen.blit(bg_img, (0, int(bg_y)))
    screen.blit(bg_img, (0, int(bg_y) - HEIGHT))

    all_sprites.draw(screen)

    # UI
    if player.energy <= 0 and (pygame.time.get_ticks() // 300) % 2 == 0:
        draw_text("LOW ENERGY", arcadefont, (255, 60, 60), screen, 70, 650, "center")
    else:
        draw_text("ENERGY", arcadefont, (255,255,255), screen, 70, 650, "center")
    pygame.draw.rect(screen, (0,0,255), (20, 670, int(player.energy), 20))
    pygame.draw.rect(screen, (255,255,255), (18, 668, 104, 24), 2)
    draw_text("HEALTH", arcadefont, (255,255,255), screen, 370, 650, "center")
    pygame.draw.rect(screen, (255,0,0), (320, 670, int(player.health), 20))
    pygame.draw.rect(screen, (255,255,255), (318, 668, 104, 24), 2)

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        draw_text("PAUSED", titlefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 - 20, "center")
        draw_text("Press P to resume", arcadefont, (255,255,255), screen, WIDTH//2, HEIGHT//2 + 30, "center")

    pygame.display.flip()

pygame.quit()
