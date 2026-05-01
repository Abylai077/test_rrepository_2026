"""
Core game loop, snake, food, power-ups, obstacles, rendering, and sound.
"""
import pygame
import sys
import random
from config import *
import db
import os

# -------------------------------------------------------------------
# Font cache
_fonts = {}
def get_font(name, size, bold=False):
    key = (name, size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]

# -------------------------------------------------------------------
# Sound manager
# -------------------------------------------------------------------
# Sound manager (with proper path detection)
import os

_script_dir = os.path.dirname(os.path.abspath(__file__))
_sounds = {}
_music_playing = False

def load_sounds():
    global _sounds
    sound_dir = os.path.join(_script_dir, "assets", "sounds")
    try:
        _sounds["eat"] = pygame.mixer.Sound(os.path.join(sound_dir, "eat.wav"))
        _sounds["game_over"] = pygame.mixer.Sound(os.path.join(sound_dir, "game_over.wav"))
        _sounds["powerup"] = pygame.mixer.Sound(os.path.join(sound_dir, "powerup.wav"))
    except Exception:
        pass  # Silently ignore missing sounds

def play_sound(sound_name, sound_enabled=True):
    if sound_enabled and sound_name in _sounds:
        _sounds[sound_name].play()

def play_music(sound_enabled=True):
    global _music_playing
    if not sound_enabled:
        pygame.mixer.music.stop()
        _music_playing = False
        return
    if not _music_playing:
        try:
            music_path = os.path.join(_script_dir, "assets", "sounds", "music.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            _music_playing = True
        except Exception:
            pass  # Silently ignore missing music

def stop_music():
    global _music_playing
    pygame.mixer.music.stop()
    _music_playing = False

# -------------------------------------------------------------------
# Drawing functions
def draw_cell(surface, col, row, color, margin=1, hud_offset=True):
    y_offset = HUD_HEIGHT if hud_offset else 0
    rect = pygame.Rect(
        col * CELL_SIZE + margin,
        row * CELL_SIZE + margin + y_offset,
        CELL_SIZE - margin * 2,
        CELL_SIZE - margin * 2,
    )
    pygame.draw.rect(surface, color, rect, border_radius=3)

def draw_walls(surface):
    for col in range(COLS):
        draw_cell(surface, col, 0,         WALL_COLOR, margin=0)
        draw_cell(surface, col, ROWS - 1,  WALL_COLOR, margin=0)
    for row in range(1, ROWS - 1):
        draw_cell(surface, 0,        row,  WALL_COLOR, margin=0)
        draw_cell(surface, COLS - 1, row,  WALL_COLOR, margin=0)

def draw_hud(surface, score, level, fps, personal_best=None):
    pygame.draw.rect(surface, HUD_BG, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(surface, DARK_GREEN, (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)
    font = get_font(*FONT_HUD)
    surface.blit(font.render(f"SCORE: {score}", True, GREEN), (14, 10))
    lv = font.render(f"LEVEL: {level}", True, YELLOW)
    surface.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 10))
    sp = font.render(f"SPD: {fps}", True, GRAY)
    surface.blit(sp, (WIDTH - sp.get_width() - 14, 10))
    if personal_best is not None:
        pb_text = font.render(f"BEST: {personal_best}", True, (150,150,150))
        surface.blit(pb_text, (14, HUD_HEIGHT - 20))

def draw_overlay(surface, title, subtitle=""):
    overlay = pygame.Surface((WIDTH, HEIGHT + HUD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    title_font = get_font(*FONT_BIG)
    sub_font   = get_font(*FONT_SMALL)
    title_surf = title_font.render(title, True, GREEN)
    surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, (HEIGHT + HUD_HEIGHT) // 2 - 50))
    if subtitle:
        sub_surf = sub_font.render(subtitle, True, WHITE)
        surface.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, (HEIGHT + HUD_HEIGHT) // 2 + 10))

def draw_background_grid(surface, enabled=True):
    """Draw a net (line grid) over the playable area if enabled."""
    if not enabled:
        return
    # Draw vertical lines
    for c in range(1, COLS - 1):
        x = c * CELL_SIZE
        pygame.draw.line(
            surface, GRID_COLOR,
            (x, HUD_HEIGHT + CELL_SIZE),
            (x, HEIGHT + HUD_HEIGHT - CELL_SIZE),
            1
        )
    # Draw horizontal lines
    for r in range(1, ROWS - 1):
        y = r * CELL_SIZE + HUD_HEIGHT
        pygame.draw.line(
            surface, GRID_COLOR,
            (CELL_SIZE, y),
            (WIDTH - CELL_SIZE, y),
            1
        )

def draw_legend(surface):
    x_start = WIDTH - 148
    y_start = HEIGHT + HUD_HEIGHT - len(FOOD_TYPES) * 18 - 6
    font = get_font(*FONT_TINY)
    for i, ft in enumerate(FOOD_TYPES):
        y = y_start + i * 18
        pygame.draw.circle(surface, ft["color"], (x_start + 6, y + 6), 5)
        timer_str = f"{ft['timer']}s" if ft["timer"] else "inf"
        label = f"{ft['name']}  +{ft['points']}  g:{ft['grow']}  t:{timer_str}"
        surface.blit(font.render(label, True, GRAY), (x_start + 16, y))

# -------------------------------------------------------------------
# Food Item
class FoodItem:
    def __init__(self, pos, food_type):
        self.pos = pos
        self.food_type = food_type
        self.time_left = food_type["timer"]
    @property
    def color(self): return self.food_type["color"]
    @property
    def points(self): return self.food_type["points"]
    @property
    def grow(self): return self.food_type["grow"]
    @property
    def name(self): return self.food_type["name"]
    def update(self, dt):
        if self.time_left is None:
            return False
        self.time_left -= dt
        return self.time_left <= 0
    def draw(self, surface):
        col, row = self.pos
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT
        if self.time_left is not None and self.time_left < 2.0:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                return
        pygame.draw.circle(surface, self.color, (cx, cy), CELL_SIZE // 2 - 2)
        hr = max(2, min(5, self.points // 20))
        pygame.draw.circle(surface, WHITE, (cx - 3, cy - 3), hr)
        if self.time_left is not None:
            secs = max(0, int(self.time_left) + 1)
            font = get_font(*FONT_TIMER)
            t_surf = font.render(str(secs), True, WHITE)
            surface.blit(t_surf, (cx - t_surf.get_width()//2, cy - CELL_SIZE//2 - 13))

def spawn_food(snake_body, existing_foods):
    occupied = set(snake_body) | {f.pos for f in existing_foods}
    free_cells = [(c, r) for c in range(1, COLS-1) for r in range(1, ROWS-1) if (c, r) not in occupied]
    if not free_cells:
        return None
    pos = random.choice(free_cells)
    food_type = random.choice(FOOD_POOL)
    return FoodItem(pos, food_type)

# -------------------------------------------------------------------
# Power‑up
class PowerUp:
    TYPES = ["speed_boost", "slow_motion", "shield"]
    def __init__(self, pos, power_type):
        self.pos = pos
        self.type = power_type
        self.spawn_time = pygame.time.get_ticks()
        self.lifespan = POWERUP_LIFESPAN
    @property
    def color(self):
        if self.type == "speed_boost": return (0, 255, 255)
        elif self.type == "slow_motion": return (255, 255, 0)
        else: return (100, 100, 255)
    def is_expired(self):
        return (pygame.time.get_ticks() - self.spawn_time) > self.lifespan
    def draw(self, surface):
        col, row = self.pos
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT
        pygame.draw.circle(surface, self.color, (cx, cy), CELL_SIZE // 2 - 2)
        font = pygame.font.SysFont("Arial", 12, bold=True)
        letter = "S" if self.type == "speed_boost" else ("M" if self.type == "slow_motion" else "H")
        text = font.render(letter, True, WHITE)
        surface.blit(text, (cx - 4, cy - 6))

def spawn_powerup(snake_body, foods, obstacles, existing_powerups):
    if existing_powerups: return None
    if random.random() > 0.01: return None
    occupied = set(snake_body) | {f.pos for f in foods} | set(obstacles) | {p.pos for p in existing_powerups}
    free_cells = [(c, r) for c in range(1, COLS-1) for r in range(1, ROWS-1) if (c, r) not in occupied]
    if not free_cells: return None
    pos = random.choice(free_cells)
    ptype = random.choice(PowerUp.TYPES)
    return PowerUp(pos, ptype)

# -------------------------------------------------------------------
# Obstacles
def generate_obstacles(level, snake_body, existing_foods, powerups):
    if level < OBSTACLES_START_LEVEL:
        return []
    count = min(OBSTACLE_COUNT_BASE + (level - OBSTACLES_START_LEVEL) // 2, (COLS-2)*(ROWS-2)//3)
    occupied = set(snake_body) | {f.pos for f in existing_foods} | {p.pos for p in powerups}
    free_cells = [(c, r) for c in range(1, COLS-1) for r in range(1, ROWS-1) if (c, r) not in occupied]
    head = snake_body[0]
    adj = [(head[0]+dx, head[1]+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] if 1 <= head[0]+dx < COLS-1 and 1 <= head[1]+dy < ROWS-1]
    free_for_head = [c for c in adj if c not in occupied]
    if not free_for_head:
        return []
    obstacles = []
    for _ in range(count):
        if not free_cells: break
        pos = random.choice(free_cells)
        obstacles.append(pos)
        free_cells.remove(pos)
        occupied.add(pos)
    return obstacles

# -------------------------------------------------------------------
# Snake
class Snake:
    def __init__(self, start_pos=None, snake_color=None):
        if start_pos is None:
            start_pos = (COLS // 2, ROWS // 2)
        self.body = [start_pos, (start_pos[0]-1, start_pos[1]), (start_pos[0]-2, start_pos[1])]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.base_color = snake_color or GREEN
    @property
    def head(self): return self.body[0]
    def set_direction(self, new_dir):
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.next_direction = new_dir
    def apply_direction(self): self.direction = self.next_direction
    def grow_by(self, count):
        for _ in range(count):
            self.body.append(self.body[-1])
    def shorten_by(self, count):
        for _ in range(min(count, len(self.body)-1)):
            self.body.pop()
        return len(self.body) < 1
    def check_wall_collision(self, pos):
        col, row = pos
        return col <= 0 or col >= COLS - 1 or row <= 0 or row >= ROWS - 1
    def check_self_collision(self, pos):
        return pos in self.body[1:]
    def get_color_for_segment(self, idx):
        if idx == 0: return self.base_color
        f = max(0.3, 1.0 - idx / len(self.body) * 0.6)
        return (int(self.base_color[0]*f), int(self.base_color[1]*f), int(self.base_color[2]*f))
    def draw(self, surface):
        for idx, (c, r) in enumerate(self.body):
            draw_cell(surface, c, r, self.get_color_for_segment(idx))
    def reset(self):
        start_pos = (COLS // 2, ROWS // 2)
        self.body = [start_pos, (start_pos[0]-1, start_pos[1]), (start_pos[0]-2, start_pos[1])]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
    def get_positions_set(self):
        return set(self.body)

# -------------------------------------------------------------------
# Main Game Loop
def game_loop(screen, clock, username, user_settings):
    sound_enabled = user_settings.get("sound", True)
    load_sounds()
    play_music(sound_enabled)

    snake = Snake(snake_color=user_settings["snake_color"])
    foods = []
    powerups = []
    obstacles = []
    first = spawn_food(snake.body, foods)
    if first: foods.append(first)

    score = 0
    level = 1
    food_eaten = 0
    current_fps = BASE_FPS
    spawn_timer = 0.0
    state = STATE_RUNNING
    active_effects = {}
    shield_active = False
    personal_best = db.get_personal_best(username)

    while True:
        dt = clock.tick(current_fps) / 1000.0
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == KEY_PAUSE:
                    if state == STATE_RUNNING: state = STATE_PAUSED
                    elif state == STATE_PAUSED: state = STATE_RUNNING
                if state == STATE_RUNNING:
                    if event.key in KEY_UP: snake.set_direction((0, -1))
                    elif event.key in KEY_DOWN: snake.set_direction((0, 1))
                    elif event.key in KEY_LEFT: snake.set_direction((-1, 0))
                    elif event.key in KEY_RIGHT: snake.set_direction((1, 0))
        # Logic
        if state == STATE_RUNNING:
            snake.apply_direction()
            head = snake.head
            new_head = (head[0] + snake.direction[0], head[1] + snake.direction[1])

            collision = False
            if snake.check_wall_collision(new_head) or snake.check_self_collision(new_head) or new_head in obstacles:
                if shield_active:
                    shield_active = False
                    if "shield" in active_effects: del active_effects["shield"]
                    collision = False
                else:
                    collision = True

            if collision:
                play_sound("game_over", sound_enabled)
                stop_music()
                db.save_game_result(username, score, level)
                return score, level

            snake.body.insert(0, new_head)

            # Food collision
            eaten = None
            for f in foods:
                if f.pos == new_head:
                    eaten = f
                    break

            if eaten:
                if eaten.grow < 0:
                    play_sound("eat", sound_enabled)   # poison also plays eat sound
                    if snake.shorten_by(-eaten.grow):
                        play_sound("game_over", sound_enabled)
                        stop_music()
                        db.save_game_result(username, score, level)
                        return score, level
                else:
                    play_sound("eat", sound_enabled)
                    score += eaten.points * level
                    food_eaten += 1
                    if eaten.grow > 1:
                        snake.grow_by(eaten.grow - 1)
                foods.remove(eaten)

                if food_eaten >= FOOD_PER_LEVEL:
                    level += 1
                    food_eaten = 0
                    current_fps = min(MAX_FPS, BASE_FPS + (level - 1) * FPS_STEP)
                    obstacles = generate_obstacles(level, snake.body, foods, powerups)

                replacement = spawn_food(snake.body, foods)
                if replacement: foods.append(replacement)
            else:
                snake.body.pop()

            # Power-up collection
            collected = None
            for p in powerups:
                if p.pos == new_head:
                    collected = p
                    break
            if collected:
                play_sound("powerup", sound_enabled)
                now = pygame.time.get_ticks()
                if collected.type == "speed_boost":
                    active_effects["speed_boost"] = now + POWERUP_DURATION
                elif collected.type == "slow_motion":
                    active_effects["slow_motion"] = now + POWERUP_DURATION
                elif collected.type == "shield":
                    shield_active = True
                    active_effects["shield"] = now + POWERUP_DURATION
                powerups.remove(collected)

            # Update active effects
            now_ticks = pygame.time.get_ticks()
            for effect in list(active_effects.keys()):
                if now_ticks >= active_effects[effect]:
                    if effect == "shield": shield_active = False
                    del active_effects[effect]

            speed_mult = 1.0
            if "speed_boost" in active_effects: speed_mult = 1.5
            elif "slow_motion" in active_effects: speed_mult = 0.6
            effective_fps = max(3, min(MAX_FPS, int(current_fps * speed_mult)))

            # Update food timers
            for f in foods[:]:
                if f.update(dt): foods.remove(f)

            # Auto-spawn food
            spawn_timer += dt
            if spawn_timer >= SPAWN_INTERVAL and len(foods) < MAX_FOODS:
                spawn_timer = 0.0
                extra = spawn_food(snake.body, foods)
                if extra: foods.append(extra)

            # Spawn power-up
            if len(powerups) < MAX_POWERUPS:
                new_power = spawn_powerup(snake.body, foods, obstacles, powerups)
                if new_power: powerups.append(new_power)

            powerups = [p for p in powerups if not p.is_expired()]

        # Rendering
        screen.fill(BLACK)
        draw_background_grid(screen, enabled=user_settings["grid_overlay"])
        draw_walls(screen)
        for obs in obstacles: draw_cell(screen, obs[0], obs[1], WALL_COLOR, margin=0)
        for f in foods: f.draw(screen)
        for p in powerups: p.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, effective_fps, personal_best)
        draw_legend(screen)

        if state == STATE_PAUSED:
            draw_overlay(screen, "PAUSED", "Press P to resume")
        elif state == STATE_DEAD:
            draw_overlay(screen, "GAME OVER", f"Score: {score}  Level: {level}")

        pygame.display.flip()