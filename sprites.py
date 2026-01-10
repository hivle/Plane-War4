import pygame
import os
import random  # <--- Added this back!

# --- 1. FORCE INIT ---
pygame.init()

# --- CONSTANTS ---
WIDTH, HEIGHT = 450, 700

# --- ASSET LOADING HELPER ---
def load_img(path, size=None):
    try:
        if not os.path.exists(path):
            surf = pygame.Surface(size if size else (50,50))
            surf.fill((255, 0, 255)) 
            return surf
        img = pygame.image.load(path) 
        if size: img = pygame.transform.scale(img, size)
        return img
    except:
        return pygame.Surface(size if size else (50,50))

# --- SLICING HELPERS ---
def slice_4x4(sheet):
    """Slices a 4x4 sheet (like the explosion)"""
    frames = []
    sheet_w, sheet_h = sheet.get_size()
    frame_w = sheet_w // 4
    frame_h = sheet_h // 4
    
    for row in range(4):
        for col in range(4):
            x = col * frame_w
            y = row * frame_h
            rect = pygame.Rect(x, y, frame_w, frame_h)
            try:
                image = sheet.subsurface(rect)
                image = pygame.transform.scale(image, (60, 60))
                frames.append(image)
            except:
                pass
    return frames

def slice_row(sheet, total_frames):
    """Slices a single row sheet (like the bullet)"""
    frames = []
    sheet_w, sheet_h = sheet.get_size()
    frame_w = sheet_w // total_frames
    
    for i in range(total_frames):
        x = i * frame_w
        # Cut the frame from the sheet
        rect = pygame.Rect(x, 0, frame_w, sheet_h)
        try:
            image = sheet.subsurface(rect)
            # Scale to 30x30 for the game
            image = pygame.transform.scale(image, (30, 30))
            frames.append(image)
        except:
            pass
    return frames

# --- LOAD SPRITE ASSETS ---
plane_img = load_img(os.path.join('resources','plane.png'), (50, 50))
enemy_img = load_img(os.path.join('resources','HENRY.png'), (50, 50))

# 1. Explosion Sheet (4x4)
explosion_sheet = load_img(os.path.join('resources','explosion.png')) 
explosion_anim = slice_4x4(explosion_sheet)

# 2. Bullet Sheet (1 Row, 7 Frames)
bullet_sheet = load_img(os.path.join('resources', 'sprites', 'bullet.png'))
all_bullet_frames = slice_row(bullet_sheet, 7)

# Split the frames:
# First 4 frames = Travel (b1-b4)
travel_frames = all_bullet_frames[:4] 
# Last 3 frames = Hit (b5-b7)
hit_frames = all_bullet_frames[4:]


# --- CLASSES ---

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
        
        self.anim_timer += dt
        threshold = 0.05 if self.exploding else 0.50
        
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
        self.speed = random.randint(200, 300) 
        self.hp = 2
        
        self.dying = False
        self.explosion_frames = explosion_anim
        self.current_frame = 0
        self.anim_timer = 0

    def die(self):
        if not self.dying:
            self.dying = True
            self.current_frame = 0
            self.speed = 0

    def update(self, dt):
        if not self.dying:
            self.pos_y += self.speed * dt
            self.rect.y = int(self.pos_y)
        else:
            self.anim_timer += dt
            if self.anim_timer >= 0.05: 
                self.anim_timer = 0
                self.current_frame += 1
                
                if self.current_frame >= len(self.explosion_frames):
                    self.kill()
                    return
                
                center = self.rect.center 
                self.image = self.explosion_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

        if self.rect.top > HEIGHT: self.kill()
        