"""
Game constants and configuration (TSIS 4)
"""
import pygame

# Grid & Display
CELL_SIZE   = 20
COLS        = 30
ROWS        = 25
WIDTH       = COLS * CELL_SIZE
HEIGHT      = ROWS * CELL_SIZE
HUD_HEIGHT  = 40

# Gameplay Mechanics
FOOD_PER_LEVEL   = 3
BASE_FPS         = 8
FPS_STEP         = 2
MAX_FPS          = 30
MAX_FOODS        = 3
SPAWN_INTERVAL   = 5.0

# Power‑ups
POWERUP_LIFESPAN = 8000          # ms on field
POWERUP_DURATION = 5000          # ms effect duration
MAX_POWERUPS     = 1

# Obstacles
OBSTACLES_START_LEVEL = 3
OBSTACLE_COUNT_BASE   = 5

# Colours
BLACK       = (  0,   0,   0)
DARK_GREEN  = ( 20,  60,  20)
GREEN       = ( 50, 200,  50)
BRIGHT_GRN  = (100, 255, 100)
WHITE       = (255, 255, 255)
GRAY        = (100, 100, 100)
YELLOW      = (255, 215,   0)
WALL_COLOR  = ( 40,  40,  40)
HUD_BG      = ( 15,  15,  15)
GRID_COLOR  = ( 60,  60,  60)   # line grid color
POISON_COLOR= (139,   0,   0)

# Fonts
FONT_HUD   = ("Courier New", 20, True)
FONT_BIG   = ("Courier New", 42, True)
FONT_SMALL = ("Courier New", 22, False)
FONT_TINY  = ("Courier New", 13, False)
FONT_TIMER = ("Courier New", 11, True)

# Food Types – includes Poison
FOOD_TYPES = [
    {"name": "Normal", "points": 10, "grow": 1, "color": (220, 50, 50),   "timer": None,  "chance": 50},
    {"name": "Bonus",  "points": 30, "grow": 1, "color": (255, 165, 0),   "timer": 8.0,   "chance": 25},
    {"name": "Rare",   "points": 60, "grow": 2, "color": (180, 0, 220),    "timer": 5.0,   "chance": 15},
    {"name": "Golden", "points": 100,"grow": 3, "color": (255, 215, 0),    "timer": 3.0,   "chance": 10},
    {"name": "Poison", "points": 0,  "grow": -2,"color": POISON_COLOR,      "timer": 7.0,   "chance": 12},
]

FOOD_POOL = []
for ft in FOOD_TYPES:
    FOOD_POOL.extend([ft] * ft["chance"])

# Game States
STATE_START   = "START"
STATE_RUNNING = "RUNNING"
STATE_PAUSED  = "PAUSED"
STATE_DEAD    = "DEAD"

# Controls
KEY_START    = (pygame.K_SPACE, pygame.K_RETURN)
KEY_PAUSE    = pygame.K_p
KEY_UP       = (pygame.K_UP, pygame.K_w)
KEY_DOWN     = (pygame.K_DOWN, pygame.K_s)
KEY_LEFT     = (pygame.K_LEFT, pygame.K_a)
KEY_RIGHT    = (pygame.K_RIGHT, pygame.K_d)