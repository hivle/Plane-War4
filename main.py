import pygame
import os
import random

# --- 1. SETUP & CONFIGURATION ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Screen Dimensions
WIDTH, HEIGHT = 450, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Plane War Remastered")

# FPS Control
clock = pygame.time.Clock()
FPS = 60

# --- 2. ASSET LOADING ---
# Helper function to load images safely
def load_img(path, size=None):
    try:
        # Check if file exists to avoid hard crashes
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing: {path}")
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"Asset Warning: {e}")
        # Create a colored placeholder if image fails
        surf = pygame.Surface(size if size else (30,30))
        surf.fill((255, 0, 255)) # Magenta placeholder
        return surf

# Load Images (Using your file structure)
bg_img = load_img(os.path.join('resources','background.jpg'), (WIDTH, HEIGHT))
menu_bg = load_img(os.path.join('resources','menupicture.jpg'), (WIDTH, HEIGHT))

# Player Images
plane_img_normal = load_img(os.path.join('resources','plane.png'), (50, 50))
plane_img_turn = load_img(os.path.join('resources','plane.png'), (43, 50)) 

# Bullet & Enemy
bullet_img = load_img(os.path.join('resources','sprites','b7.png'), (15, 15))
enemy_img = load_img(os.path.join('resources','HENRY.png'), (50, 50))

# Fonts
try:
    arcadefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 10)
    titlefont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 50)
    btnfont = pygame.font.Font(os.path.join('resources','Fonts','ka1.ttf'), 30)
except:
    print("Custom font not found. Using system default.")
    arcadefont = pygame.font.SysFont('arial', 15)
    titlefont = pygame.font.SysFont('arial', 50, bold=True)
    btnfont = pygame.font.SysFont('arial', 30)

# Music
try:
    pygame.mixer.music.load(os.path.join('resources','sound','Street Fighter - Guile Stage.mp3'))
    pygame.mixer.music.play(-1, 0)
    pygame.mixer.music.set_volume(0.3)
except:
    print("Music file not found.")

# --- 3. CLASSES (With Delta Time Logic) ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = plane_img_normal
        self.rect = self.image.get_rect()
        
        # FLOAT POSITIONS (Crucial for Delta Time smooth movement)
        self.pos_x = WIDTH // 2
        self.pos_y = HEIGHT - 100
        self.rect.center = (self.pos_x, self.pos_y)
        
        # Stats
        self.speed = 300 # Pixels per Second
        self.energy = 100
        self.health = 100
        
        # Shooting Timer
        self.last_shot = 0
        self.shoot_delay = 0.2 # 0.2 seconds between shots

    def update(self, dt):
        keys = pygame.key.get_pressed()
        
        # Movement Amount: Speed * Time passed
        move_amount = self.speed * dt
        
        # Sprint Logic
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.energy > 0:
            move_amount *= 1.5 # 50% faster
            self.energy -= 30 * dt # Drain energy over time
        elif self.energy < 100:
            self.energy += 10 * dt # Regenerate

        # Direction Checks
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= move_amount
        if keys[pygame.K_s]: dy += move_amount
        if keys[pygame.K_a]: 
            dx -= move_amount
            self.image = plane_img_turn
        if keys[pygame.K_d]: 
            dx += move_amount
            self.image = plane_img_turn
            
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            self.image = plane_img_normal

        # Apply Movement to Float Position
        self.pos_x += dx
        self.pos_y += dy

        # Boundary Checks
        if self.pos_x < 0: self.pos_x = 0
        if self.pos_x > WIDTH: self.pos_x = WIDTH
        if self.pos_y < 0: self.pos_y = 0
        if self.pos_y > HEIGHT: self.pos_y = HEIGHT

        # Update Rect (Round to nearest pixel for drawing)
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

    def shoot(self):
        # Logic handled in main loop for simplicity
        pass 

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        
        # SNAPSHOT: Capture exact spawn location
        self.pos_x = x
        self.pos_y = y
        self.rect.centerx = x
        self.rect.bottom = y
        
        # SPEED: 600 px/sec (Faster than player's 300)
        self.speed = -600 

    def update(self, dt):
        # Move up independent of player
        self.pos_y += self.speed * dt
        self.rect.centery = int(self.pos_y)
        
        # Cleanup
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        
        self.pos_x = random.randint(0, WIDTH - self.rect.width)
        self.pos_y = random.randint(-100, -40)
        
        self.rect.x = self.pos_x
        self.rect.y = self.pos_y
        
        # Random speed for each enemy
        self.speed = random.randint(100, 250) 

    def update(self, dt):
        self.pos_y += self.speed * dt
        self.rect.y = int(self.pos_y)
        
        if self.rect.top > HEIGHT:
            self.kill()

# --- 4. TEXT HELPER ---
def draw_text(text, font, color, surface, x, y, align="left"):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if align == "center":
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# --- 5. INITIALIZE OBJECTS ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Game Variables
bg_y1 = 0
bg_y2 = -HEIGHT
shoot_timer = 0
spawn_timer = 0

running = True
in_menu = True
game_over = False

# ==========================================
#              MAIN LOOP
# ==========================================
while running:
    # 1. CALCULATE DELTA TIME (Seconds passed since last frame)
    # This ensures consistent speed on all computers
    dt = clock.tick(FPS) / 1000.0 

    # --- MENU LOOP ---
    if in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 175 < mx < 295 and 400 < my < 430: # Play Button Area
                    in_menu = False
                if 180 < mx < 300 and 600 < my < 630: # Exit Button Area
                    running = False

        screen.blit(menu_bg, (0,0))
        draw_text("PLANE WAR!", titlefont, (255,255,255), screen, WIDTH//2, 100, "center")
        
        # Draw Buttons
        mx, my = pygame.mouse.get_pos()
        
        # Play Button Hover
        color = (100,100,100) if (175 < mx < 295 and 400 < my < 430) else (255,255,255)
        draw_text("PLAY", btnfont, color, screen, WIDTH//2, 415, "center")
        
        # Exit Button Hover
        color = (100,100,100) if (180 < mx < 300 and 600 < my < 630) else (255,255,255)
        draw_text("EXIT", btnfont, color, screen, WIDTH//2, 615, "center")
        
        pygame.display.flip()
        continue # Skip the rest of the loop while in menu

    # --- GAME OVER LOGIC ---
    if game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw_text("GAME OVER", titlefont, (255,0,0), screen, WIDTH//2, HEIGHT//2, "center")
        pygame.display.flip()
        continue

    # --- GAME LOOP ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # -- Spawning Logic (Time based) --
    spawn_timer += dt
    if spawn_timer > 1.0: # Spawn enemy every 1 second
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)
        spawn_timer = 0
        
    # -- Shooting Logic (Time based) --
    # Auto-shoot if Space or just automatic
    shoot_timer += dt
    if shoot_timer > 0.2: # Fire every 0.2 seconds
        # Create bullet at player's CURRENT position (Fire and Forget)
        b = Bullet(player.rect.centerx, player.rect.top)
        all_sprites.add(b)
        bullets.add(b)
        shoot_timer = 0

    # -- Update Everything --
    # We pass 'dt' to update() so sprites move smoothly
    all_sprites.update(dt)

    # -- Collisions --
    # Bullet hits Enemy
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    
    # Enemy hits Player
    hits = pygame.sprite.spritecollide(player, enemies, True)
    if hits:
        player.health -= 20
        if player.health <= 0:
            game_over = True

    # -- Drawing --
    # Scroll Background
    bg_y1 += 100 * dt # Scroll speed
    bg_y2 += 100 * dt
    
    if bg_y1 >= HEIGHT: bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT: bg_y2 = -HEIGHT
    
    screen.blit(bg_img, (0, int(bg_y1)))
    screen.blit(bg_img, (0, int(bg_y2)))

    # Draw Sprites
    all_sprites.draw(screen)

    # UI Bars
    # Energy
    pygame.draw.rect(screen, (0,0,255), (20, 670, int(player.energy), 20))
    pygame.draw.rect(screen, (255,255,255), (18, 668, 104, 24), 2)
    
    # Health
    pygame.draw.rect(screen, (255,0,0), (320, 670, int(player.health), 20))
    pygame.draw.rect(screen, (255,255,255), (318, 668, 104, 24), 2)
    draw_text("HP", arcadefont, (255,255,255), screen, 360, 675)

    if player.energy <= 0:
        draw_text("NO ENERGY", arcadefont, (255,0,0), screen, 25, 655)
    elif (pygame.key.get_pressed()[pygame.K_LSHIFT]) and player.energy > 0:
        draw_text("BOOST!", arcadefont, (0,255,255), screen, 25, 655)

    pygame.display.flip()

pygame.quit()

