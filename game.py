import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (34, 139, 34)
SILVER = (192, 192, 192)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
SNOW_WHITE = (255, 250, 250)
ICE_BLUE = (176, 224, 230)

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        return self.lifetime > 0
        
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        color = tuple(int(c * alpha) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)

class Bullet:
    def __init__(self, x, y, angle, speed, damage, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.radius = 4
        self.alive = True
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.alive = False
            
    def draw(self, screen):
        color = YELLOW if self.owner == 'player' else ORANGE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.health = 1027
        self.max_health = 1027
        self.speed = 5
        self.angle = 0
        self.alive = True
        self.score = 0
        self.kills = 0
        self.last_shot = 0
        self.last_damage_time = 0
        
    def move(self, keys, obstacles):
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed
            
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        if 20 <= new_x <= SCREEN_WIDTH - self.width - 20:
            collision = False
            for obs in obstacles:
                if pygame.Rect(new_x, self.y, self.width, self.height).colliderect(obs):
                    collision = True
                    break
            if not collision:
                self.x = new_x
                
        if 20 <= new_y <= SCREEN_HEIGHT - self.height - 20:
            collision = False
            for obs in obstacles:
                if pygame.Rect(self.x, new_y, self.width, self.height).colliderect(obs):
                    collision = True
                    break
            if not collision:
                self.y = new_y
                
    def update_angle(self, mouse_x, mouse_y):
        dx = mouse_x - (self.x + self.width//2)
        dy = mouse_y - (self.y + self.height//2)
        self.angle = math.atan2(dy, dx)
        
    def shoot(self, current_time):
        if current_time - self.last_shot >= 300:
            self.last_shot = current_time
            x = self.x + self.width//2 + math.cos(self.angle) * 20
            y = self.y + self.height//2 + math.sin(self.angle) * 20
            return Bullet(x, y, self.angle, 15, 35, 'player')
        return None
        
    def take_damage(self, damage, current_time):
        if current_time - self.last_damage_time > 500:
            self.health -= damage
            self.last_damage_time = current_time
            if self.health <= 0:
                self.alive = False
            return True
        return False
        
    def draw(self, screen, climate):
        player_center = (self.x + self.width//2, self.y + self.height//2)
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, (100, 150, 255), player_center, 18)
        
        # Eyes
        left_eye = (player_center[0] + math.cos(self.angle - 0.3) * 8,
                   player_center[1] + math.sin(self.angle - 0.3) * 8)
        right_eye = (player_center[0] + math.cos(self.angle + 0.3) * 8,
                    player_center[1] + math.sin(self.angle + 0.3) * 8)
        pygame.draw.circle(screen, WHITE, (int(left_eye[0]), int(left_eye[1])), 4)
        pygame.draw.circle(screen, WHITE, (int(right_eye[0]), int(right_eye[1])), 4)
        pygame.draw.circle(screen, BLACK, (int(left_eye[0]), int(left_eye[1])), 2)
        pygame.draw.circle(screen, BLACK, (int(right_eye[0]), int(right_eye[1])), 2)
        
        # Gun
        gun_end = (player_center[0] + math.cos(self.angle) * 35,
                  player_center[1] + math.sin(self.angle) * 35)
        pygame.draw.line(screen, GRAY, player_center, gun_end, 5)
        
        # Health bar
        bar_width = 60
        bar_height = 8
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, bar_width * health_percent, bar_height))
        
    def draw_hud(self, screen, level, climate, boss_defeated=False):
        # Health
        pygame.draw.rect(screen, RED, (20, 20, 200, 30))
        pygame.draw.rect(screen, GREEN, (20, 20, 200 * (self.health/self.max_health), 30))
        self.draw_text(screen, f"HP: {int(self.health)}/{self.max_health}", 20, WHITE, 120, 35)
        
        # Score and kills
        self.draw_text(screen, f"Score: {self.score}", 30, WHITE, 150, 80)
        self.draw_text(screen, f"Kills: {self.kills}", 30, WHITE, 150, 115)
        
        # Level and climate
        climate_names = ["Summer", "Rain", "Winter", "Spring", "Boss Battle"]
        self.draw_text(screen, f"Level {level}: {climate_names[level-1]}", 25, YELLOW, SCREEN_WIDTH//2, 30)
        
        if boss_defeated:
            self.draw_text(screen, "BOSS DEFEATED! Level Complete!", 25, GREEN, SCREEN_WIDTH//2, 70)
        
        # Controls
        self.draw_text(screen, "WASD: Move | Mouse: Aim | Click: Shoot | Buildings block bullets!", 18, GRAY, SCREEN_WIDTH//2, 65)
        
    def draw_text(self, screen, text, size, color, x, y, center=True):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)

class Enemy:
    def __init__(self, x, y, enemy_type, level):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.width = 30
        self.height = 30
        self.health = 200
        self.speed = 2 + (level * 0.2)
        self.angle = 0
        self.alive = True
        self.last_shot = 0
        self.damage = 25 + (level * 2)
        self.thinking_timer = 0
        self.patrol_x = x
        self.patrol_y = y
        self.state = "patrol"  # patrol, chase, retreat
        
        if enemy_type == "normal":
            self.color = RED
        elif enemy_type == "heavy":
            self.health = 200
            self.speed = 1.2
            self.width = 40
            self.height = 40
            self.color = (150, 50, 50)
            self.damage = 35
        elif enemy_type == "fast":
            self.health = 200
            self.speed = 4
            self.color = ORANGE
            self.damage = 20
        elif enemy_type == "sniper":
            self.health = 200
            self.speed = 1.5
            self.color = PURPLE
            self.damage = 45
            
    def update(self, player, obstacles, current_time):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # AI Thinking - Smart enemy behavior
        self.thinking_timer += 1
        
        if self.state == "patrol":
            if distance < 250:
                self.state = "chase"
            else:
                # Patrol around spawn point
                if self.thinking_timer % 120 < 60:
                    target_x = self.patrol_x + 80
                else:
                    target_x = self.patrol_x - 80
                dx = target_x - self.x
                dy = self.patrol_y - self.y
                distance = math.sqrt(dx**2 + dy**2)
                
        elif self.state == "chase":
            if distance > 350:
                self.state = "patrol"
            elif self.health < 100:
                self.state = "retreat"
                
        elif self.state == "retreat":
            if distance > 450:
                self.state = "patrol"
            elif self.health > 150:
                self.state = "chase"
            else:
                # Retreat away from player
                dx = -dx
                dy = -dy
        
        if distance > 0 and self.state != "retreat":
            dx /= distance
            dy /= distance
        elif distance > 0 and self.state == "retreat":
            dx = -dx / distance
            dy = -dy / distance
            
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        can_move = True
        for obs in obstacles:
            if pygame.Rect(new_x, new_y, self.width, self.height).colliderect(obs):
                can_move = False
                break
        if can_move:
            self.x = new_x
            self.y = new_y
            
        self.angle = math.atan2(player.y - self.y, player.x - self.x)
        
    def shoot(self, current_time):
        fire_rate = 1.5 if self.type == "sniper" else 2
        if current_time - self.last_shot >= 1000 / fire_rate:
            self.last_shot = current_time
            x = self.x + self.width//2 + math.cos(self.angle) * 20
            y = self.y + self.height//2 + math.sin(self.angle) * 20
            bullet_speed = 15 if self.type == "sniper" else 10
            return Bullet(x, y, self.angle, bullet_speed, self.damage, 'enemy')
        return None
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
        
    def draw(self, screen, climate):
        screen_x = self.x
        screen_y = self.y
        enemy_center = (screen_x + self.width//2, screen_y + self.height//2)
        
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))
        pygame.draw.circle(screen, self.color, enemy_center, 15)
        
        # Eyes
        left_eye = (enemy_center[0] + math.cos(self.angle - 0.3) * 8,
                   enemy_center[1] + math.sin(self.angle - 0.3) * 8)
        right_eye = (enemy_center[0] + math.cos(self.angle + 0.3) * 8,
                    enemy_center[1] + math.sin(self.angle + 0.3) * 8)
        pygame.draw.circle(screen, WHITE, (int(left_eye[0]), int(left_eye[1])), 4)
        pygame.draw.circle(screen, WHITE, (int(right_eye[0]), int(right_eye[1])), 4)
        pygame.draw.circle(screen, BLACK, (int(left_eye[0]), int(left_eye[1])), 2)
        pygame.draw.circle(screen, BLACK, (int(right_eye[0]), int(right_eye[1])), 2)
        
        # Health bar
        bar_width = self.width
        bar_height = 5
        health_percent = self.health / 200
        pygame.draw.rect(screen, RED, (screen_x, screen_y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, screen_y - 10, bar_width * health_percent, bar_height))
        
        # State indicator
        if self.state == "chase":
            pygame.draw.circle(screen, YELLOW, (int(enemy_center[0]), int(enemy_center[1] - 15)), 5)
        elif self.state == "retreat":
            pygame.draw.circle(screen, BLUE, (int(enemy_center[0]), int(enemy_center[1] - 15)), 5)

class Boss:
    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 100
        self.health = 900
        self.max_health = 900
        self.speed = 1.2
        self.angle = 0
        self.alive = True
        self.last_shot = 0
        self.damage = 50
        self.phase = 1
        self.last_ability = 0
        
        # Boss colors based on level
        if level == 1:
            self.color = (255, 100, 0)  # Fire boss
        elif level == 2:
            self.color = (0, 100, 200)  # Water boss
        elif level == 3:
            self.color = (200, 200, 255)  # Ice boss
        elif level == 4:
            self.color = (100, 200, 100)  # Nature boss
        else:
            self.color = (150, 0, 150)  # Shadow boss
            
    def update(self, player, obstacles, current_time):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            can_move = True
            for obs in obstacles:
                if pygame.Rect(new_x, new_y, self.width, self.height).colliderect(obs):
                    can_move = False
                    break
            if can_move:
                self.x = new_x
                self.y = new_y
                
        self.angle = math.atan2(player.y - self.y, player.x - self.x)
        
        # Phase change
        if self.health < self.max_health * 0.5:
            self.phase = 2
            self.speed = 1.8
            self.damage = 60
            
    def shoot(self, current_time):
        fire_rate = 1.2 if self.phase == 2 else 0.8
        if current_time - self.last_shot >= 1000 / fire_rate:
            self.last_shot = current_time
            bullets = []
            if self.phase == 2:
                # Phase 2: Triple shot + spread
                for angle_offset in [-0.4, -0.2, 0, 0.2, 0.4]:
                    x = self.x + self.width//2 + math.cos(self.angle + angle_offset) * 50
                    y = self.y + self.height//2 + math.sin(self.angle + angle_offset) * 50
                    bullets.append(Bullet(x, y, self.angle + angle_offset, 13, self.damage, 'enemy'))
            else:
                # Phase 1: Single shot
                x = self.x + self.width//2 + math.cos(self.angle) * 50
                y = self.y + self.height//2 + math.sin(self.angle) * 50
                bullets.append(Bullet(x, y, self.angle, 12, self.damage, 'enemy'))
            return bullets
        return []
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True
        return False
        
    def draw(self, screen, climate):
        screen_x = self.x
        screen_y = self.y
        boss_center = (screen_x + self.width//2, screen_y + self.height//2)
        
        # Boss body
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))
        pygame.draw.circle(screen, self.color, boss_center, 45)
        
        # Eyes
        eye_offset = 20
        left_eye = (boss_center[0] + math.cos(self.angle - 0.5) * eye_offset,
                   boss_center[1] + math.sin(self.angle - 0.5) * eye_offset)
        right_eye = (boss_center[0] + math.cos(self.angle + 0.5) * eye_offset,
                    boss_center[1] + math.sin(self.angle + 0.5) * eye_offset)
        pygame.draw.circle(screen, RED, (int(left_eye[0]), int(left_eye[1])), 10)
        pygame.draw.circle(screen, RED, (int(right_eye[0]), int(right_eye[1])), 10)
        pygame.draw.circle(screen, BLACK, (int(left_eye[0]), int(left_eye[1])), 5)
        pygame.draw.circle(screen, BLACK, (int(right_eye[0]), int(right_eye[1])), 5)
        
        # Crown/Horns
        pygame.draw.polygon(screen, GOLD, 
                           [(screen_x + self.width//2, screen_y - 25),
                            (screen_x + self.width//2 - 20, screen_y),
                            (screen_x + self.width//2 + 20, screen_y)])
        
        # Health bar
        bar_width = 300
        bar_height = 20
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - bar_width//2, 100, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH//2 - bar_width//2, 100, bar_width * health_percent, bar_height))
        
        # Phase indicator
        phase_color = YELLOW if self.phase == 1 else ORANGE
        self.draw_boss_text(screen, f"BOSS - Phase {self.phase}", 35, phase_color, SCREEN_WIDTH//2, 85)
        self.draw_boss_text(screen, f"HP: {int(self.health)}/{self.max_health}", 25, WHITE, SCREEN_WIDTH//2, 125)
        
    def draw_boss_text(self, screen, text, size, color, x, y, center=True):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        screen.blit(text_surface, text_rect)

class Building:
    def __init__(self, x, y, btype):
        self.x = x
        self.y = y
        self.type = btype
        self.width = 80
        self.height = 80
        self.health = 500
        
        if btype == "house":
            self.width = 70
            self.height = 60
            self.color = (160, 120, 80)
        elif btype == "chinese":
            self.width = 90
            self.height = 70
            self.color = (180, 100, 60)
        elif btype == "building":
            self.width = 100
            self.height = 120
            self.color = (100, 100, 120)
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen, climate):
        screen_x = self.x
        screen_y = self.y
        rect = pygame.Rect(screen_x, screen_y, self.width, self.height)
        
        if self.type == "house":
            pygame.draw.rect(screen, self.color, rect)
            pygame.draw.polygon(screen, (139, 69, 19), 
                               [(screen_x, screen_y), 
                                (screen_x + self.width//2, screen_y - 25),
                                (screen_x + self.width, screen_y)])
            pygame.draw.rect(screen, (101, 67, 33), 
                            (screen_x + self.width//2 - 8, screen_y + self.height - 25, 16, 25))
            
        elif self.type == "chinese":
            pygame.draw.rect(screen, self.color, rect)
            points = [(screen_x, screen_y), 
                     (screen_x + self.width//4, screen_y - 20),
                     (screen_x + self.width//2, screen_y - 25),
                     (screen_x + 3*self.width//4, screen_y - 20),
                     (screen_x + self.width, screen_y)]
            pygame.draw.polygon(screen, (200, 50, 50), points)
            pygame.draw.rect(screen, RED, 
                            (screen_x + self.width//2 - 5, screen_y + 10, 10, 20))
            
        elif self.type == "building":
            pygame.draw.rect(screen, self.color, rect)
            for i in range(2):
                for j in range(3):
                    pygame.draw.rect(screen, (200, 200, 200), 
                                    (screen_x + 15 + i*40, screen_y + 20 + j*30, 20, 20))
        
        # Draw building health bar
        bar_width = self.width
        bar_height = 5
        pygame.draw.rect(screen, RED, (screen_x, screen_y - 8, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (screen_x, screen_y - 8, bar_width, bar_height))

class Tree:
    def __init__(self, x, y, climate):
        self.x = x
        self.y = y
        self.climate = climate
        
    def get_rect(self):
        return pygame.Rect(self.x - 15, self.y - 15, 30, 30)
        
    def draw(self, screen):
        screen_x = self.x
        screen_y = self.y
        pygame.draw.rect(screen, BROWN, (screen_x - 5, screen_y, 10, 20))
        
        # Different tree colors based on climate
        if self.climate == "summer":
            leaf_color = DARK_GREEN
        elif self.climate == "rain":
            leaf_color = (0, 150, 0)
        elif self.climate == "winter":
            leaf_color = SNOW_WHITE
        elif self.climate == "spring":
            leaf_color = (100, 200, 100)
        else:
            leaf_color = DARK_GREEN
            
        pygame.draw.circle(screen, leaf_color, (screen_x, screen_y - 10), 15)
        pygame.draw.circle(screen, leaf_color, (screen_x, screen_y - 18), 12)

def create_world(climate):
    buildings = []
    trees = []
    obstacles = []
    
    # Create buildings
    building_positions = [
        (150, 150, "house"), (500, 200, "chinese"), (800, 400, "building"),
        (300, 500, "house"), (650, 550, "chinese"), (400, 300, "building"),
        (700, 100, "house"), (200, 400, "chinese"), (550, 450, "building"),
        (900, 600, "house"), (1000, 200, "building"), (100, 600, "chinese"),
        (1100, 500, "house"), (850, 150, "building"), (450, 650, "chinese")
    ]
    
    for x, y, btype in building_positions:
        building = Building(x, y, btype)
        buildings.append(building)
        obstacles.append(building.get_rect())
    
    # Create trees
    num_trees = 50
    for _ in range(num_trees):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)
        valid = True
        for building in buildings:
            if abs(x - building.x) < 60 and abs(y - building.y) < 60:
                valid = False
                break
        if valid:
            tree = Tree(x, y, climate)
            trees.append(tree)
            obstacles.append(tree.get_rect())
    
    return buildings, trees, obstacles

def draw_climate_effects(screen, climate, particles):
    if climate == "rain":
        for particle in particles:
            particle.draw(screen)
    elif climate == "winter":
        for particle in particles:
            particle.draw(screen)
    elif climate == "spring":
        for particle in particles:
            particle.draw(screen)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Battle Royale - Strategic Shooter")
    clock = pygame.time.Clock()
    
    # Level data
    levels = [
        {"name": "Summer", "bg_color": (135, 206, 235), "ground": (34, 139, 34), "enemies": 8},
        {"name": "Rain", "bg_color": (100, 100, 150), "ground": (50, 100, 50), "enemies": 10},
        {"name": "Winter", "bg_color": (200, 220, 255), "ground": (200, 210, 220), "enemies": 12},
        {"name": "Spring", "bg_color": (200, 220, 180), "ground": (100, 150, 100), "enemies": 14},
        {"name": "Boss", "bg_color": (50, 50, 80), "ground": (80, 80, 100), "enemies": 0}
    ]
    
    current_level = 1
    player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    climate = levels[current_level-1]["name"].lower()
    buildings, trees, obstacles = create_world(climate)
    bullets = []
    enemies = []
    particles = []
    boss = None
    level_complete = False
    boss_defeated = False
    level_complete_timer = 0
    all_enemies_defeated = False
    
    game_over = False
    game_started = False
    
    pygame.mouse.set_visible(False)
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and (game_over or not game_started):
                    # Restart game
                    current_level = 1
                    player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                    climate = levels[0]["name"].lower()
                    buildings, trees, obstacles = create_world(climate)
                    bullets = []
                    enemies = []
                    particles = []
                    boss = None
                    level_complete = False
                    boss_defeated = False
                    all_enemies_defeated = False
                    game_over = False
                    game_started = True
                    level_complete_timer = 0
                    
                    # Spawn initial enemies
                    for _ in range(levels[0]["enemies"]):
                        x = random.randint(50, SCREEN_WIDTH - 50)
                        y = random.randint(50, SCREEN_HEIGHT - 50)
                        enemy_type = random.choice(["normal", "fast", "heavy", "sniper"])
                        enemies.append(Enemy(x, y, enemy_type, current_level))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_started and not game_over and not level_complete:
                    bullet = player.shoot(current_time)
                    if bullet:
                        bullets.append(bullet)
        
        if game_started and not game_over and not level_complete:
            # Update player
            keys = pygame.key.get_pressed()
            player.move(keys, obstacles)
            player.update_angle(mouse_x, mouse_y)
            
            # Check if all enemies are defeated
            if current_level < 5 and len(enemies) == 0 and not all_enemies_defeated:
                all_enemies_defeated = True
                level_complete = True
                level_complete_timer = current_time
                
            # Update enemies
            for enemy in enemies[:]:
                enemy.update(player, obstacles, current_time)
                enemy_bullet = enemy.shoot(current_time)
                if enemy_bullet:
                    bullets.append(enemy_bullet)
                if not enemy.alive:
                    enemies.remove(enemy)
                    player.score += 20
                    player.kills += 1
                    
            # Boss level - spawn boss only after all enemies are defeated
            if current_level == 5 and boss is None and not level_complete and len(enemies) == 0:
                boss = Boss(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 - 100, current_level)
                
            if boss and boss.alive:
                boss.update(player, obstacles, current_time)
                boss_bullets = boss.shoot(current_time)
                bullets.extend(boss_bullets)
                if not boss.alive:
                    player.score += 200
                    player.kills += 1
                    boss_defeated = True
                    level_complete = True
                    level_complete_timer = current_time
            
            # Update bullets with building collision
            for bullet in bullets[:]:
                bullet.update()
                
                # Check collision with buildings (bullets hit buildings)
                hit_building = False
                for building in buildings:
                    if pygame.Rect(building.x, building.y, building.width, building.height).colliderect(
                        pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, 
                                   bullet.radius * 2, bullet.radius * 2)):
                        hit_building = True
                        bullets.remove(bullet)
                        break
                
                if hit_building:
                    continue
                
                # Check collision with player
                if bullet.owner == 'enemy':
                    if (player.x < bullet.x < player.x + player.width and
                        player.y < bullet.y < player.y + player.height):
                        player.take_damage(bullet.damage, current_time)
                        if bullet in bullets:
                            bullets.remove(bullet)
                        
                # Check collision with enemies
                elif bullet.owner == 'player':
                    hit = False
                    for enemy in enemies[:]:
                        if (enemy.x < bullet.x < enemy.x + enemy.width and
                            enemy.y < bullet.y < enemy.y + enemy.height):
                            if enemy.take_damage(bullet.damage):
                                if bullet in bullets:
                                    bullets.remove(bullet)
                            hit = True
                            break
                    # Check boss hit
                    if not hit and boss and boss.alive:
                        if (boss.x < bullet.x < boss.x + boss.width and
                            boss.y < bullet.y < boss.y + boss.height):
                            if boss.take_damage(bullet.damage):
                                if bullet in bullets:
                                    bullets.remove(bullet)
                            
                if bullet in bullets and not bullet.alive:
                    bullets.remove(bullet)
            
            # Climate effects
            if climate == "rain":
                if random.randint(0, 3) == 0:
                    particles.append(Particle(random.randint(0, SCREEN_WIDTH), 0,
                                            random.uniform(-1, 1), random.uniform(3, 6),
                                            (173, 216, 230), 60))
            elif climate == "winter":
                if random.randint(0, 4) == 0:
                    particles.append(Particle(random.randint(0, SCREEN_WIDTH), 0,
                                            random.uniform(-1, 1), random.uniform(2, 4),
                                            WHITE, 80))
            elif climate == "spring":
                if random.randint(0, 5) == 0:
                    particles.append(Particle(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT,
                                            random.uniform(-2, 2), random.uniform(-5, -3),
                                            (255, 192, 203), 70))
            
            # Update particles
            particles = [p for p in particles if p.update()]
            
            # Check game over
            if not player.alive:
                game_over = True
        
        # Level transition
        if level_complete and current_time - level_complete_timer > 2500:
            if current_level < 5:
                current_level += 1
                climate = levels[current_level-1]["name"].lower()
                buildings, trees, obstacles = create_world(climate)
                player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                bullets = []
                enemies = []
                boss = None
                level_complete = False
                all_enemies_defeated = False
                boss_defeated = False
                
                # Spawn enemies for new level
                if current_level < 5:
                    for _ in range(levels[current_level-1]["enemies"]):
                        x = random.randint(50, SCREEN_WIDTH - 50)
                        y = random.randint(50, SCREEN_HEIGHT - 50)
                        enemy_type = random.choice(["normal", "heavy", "fast", "sniper"])
                        enemies.append(Enemy(x, y, enemy_type, current_level))
            else:
                # Game completed - victory
                game_over = True
                victory = True
                level_complete = False
        
        # Draw everything
        bg_color = levels[current_level-1]["bg_color"]
        ground_color = levels[current_level-1]["ground"]
        screen.fill(bg_color)
        
        # Draw ground pattern
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(screen, ground_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(screen, ground_color, (0, y), (SCREEN_WIDTH, y), 1)
        
        # Draw trees
        for tree in trees:
            tree.draw(screen)
        
        # Draw buildings
        for building in buildings:
            building.draw(screen, climate)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen, climate)
        
        # Draw boss
        if boss and boss.alive:
            boss.draw(screen, climate)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        
        # Draw climate effects
        draw_climate_effects(screen, climate, particles)
        
        # Draw player
        if player.alive:
            player.draw(screen, climate)
        
        # Draw HUD
        if game_started and not game_over:
            player.draw_hud(screen, current_level, climate, boss_defeated)
            
            # Show enemy count
            if current_level < 5:
                font = pygame.font.Font(None, 30)
                enemy_text = font.render(f"Enemies Remaining: {len(enemies)}", True, WHITE)
                enemy_rect = enemy_text.get_rect(center=(SCREEN_WIDTH//2, 100))
                screen.blit(enemy_text, enemy_rect)
        
        # Draw crosshair
        if game_started and not game_over:
            pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 8, 2)
            pygame.draw.line(screen, WHITE, (mouse_x - 15, mouse_y), (mouse_x - 5, mouse_y), 2)
            pygame.draw.line(screen, WHITE, (mouse_x + 5, mouse_y), (mouse_x + 15, mouse_y), 2)
            pygame.draw.line(screen, WHITE, (mouse_x, mouse_y - 15), (mouse_x, mouse_y - 5), 2)
            pygame.draw.line(screen, WHITE, (mouse_x, mouse_y + 5), (mouse_x, mouse_y + 15), 2)
        
        # Level complete message
        if level_complete and current_level < 5:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 60)
            complete_text = font.render(f"LEVEL {current_level} COMPLETE!", True, GREEN)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(complete_text, complete_rect)
            font = pygame.font.Font(None, 30)
            next_text = font.render("Next Level Loading...", True, WHITE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            screen.blit(next_text, next_rect)
        
        # Start screen
        if not game_started:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 70)
            title = font.render("BATTLE ROYALE", True, YELLOW)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
            screen.blit(title, title_rect)
            
            font = pygame.font.Font(None, 28)
            controls = [
                "5 Epic Levels with Unique Climates!",
                "",
                "FEATURES:",
                "✓ Buildings block bullets - Use them for cover!",
                "✓ Smart enemies with Patrol, Chase & Retreat AI",
                "✓ Player HP: 1027 | Enemy HP: 200 | Boss HP: 900",
                "✓ Defeat all enemies to face the Final Boss!",
                "✓ Each level has unique weather effects",
                "",
                "CONTROLS:",
                "WASD / Arrows - Move",
                "Mouse - Aim",
                "Left Click - Shoot",
                "",
                "STRATEGY:",
                "Use buildings for cover from enemy fire!",
                "Enemies think and adapt to your playstyle!",
                "",
                "Press SPACE to Start Your Adventure!"
            ]
            
            y = SCREEN_HEIGHT//2 - 60
            for text in controls:
                text_surface = font.render(text, True, WHITE)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, y))
                screen.blit(text_surface, text_rect)
                y += 32
        
        # Game over screen
        if game_over and game_started:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 70)
            if current_level >= 5 and boss_defeated:
                game_over_text = font.render("VICTORY!", True, GREEN)
            else:
                game_over_text = font.render("GAME OVER!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(game_over_text, game_over_rect)
            
            font = pygame.font.Font(None, 40)
            score_text = font.render(f"Final Score: {player.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(score_text, score_rect)
            
            level_text = font.render(f"Levels Completed: {current_level if current_level <= 5 else 5}", True, WHITE)
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            screen.blit(level_text, level_rect)
            
            kills_text = font.render(f"Enemies Killed: {player.kills}", True, WHITE)
            kills_rect = kills_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
            screen.blit(kills_text, kills_rect)
            
            font = pygame.font.Font(None, 35)
            restart_text = font.render("Press SPACE to Play Again", True, GREEN)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 180))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
