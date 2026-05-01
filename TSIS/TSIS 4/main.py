"""
Main menu, username input, settings loading/saving, leaderboard, game over screen.
Full mouse + keyboard support.
"""
import pygame
import sys
import json
import os
from config import WIDTH, HEIGHT, HUD_HEIGHT, GREEN, WHITE, GRAY, BLACK
from game import get_font, game_loop
import db

DEFAULT_SETTINGS = {
    "snake_color": (50, 200, 50),
    "grid_overlay": True,
    "sound": True
}

def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r") as f:
            return json.load(f)
    else:
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=2)

def username_entry_screen(screen, clock):
    font = get_font("Courier New", 20, True)
    username = ""
    while True:
        screen.fill(BLACK)
        title = get_font("Courier New", 36, True).render("ENTER USERNAME", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        input_box = pygame.Rect(WIDTH//2 - 150, 200, 300, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        text_surf = font.render(username, True, WHITE)
        screen.blit(text_surf, (input_box.x + 5, input_box.y + 5))
        prompt = font.render("Press ENTER to confirm", True, GRAY)
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 300))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
        clock.tick(30)

def game_over_screen(screen, clock, final_score, final_level, username):
    font_big = get_font("Courier New", 36, True)
    font_med = get_font("Courier New", 22, True)
    personal_best = db.get_personal_best(username)
    retry_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 60, 100, 40)
    menu_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 60, 100, 40)
    selected = 0
    while True:
        screen.fill(BLACK)
        title = font_big.render("GAME OVER", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        info = font_med.render(f"Score: {final_score}   Level: {final_level}", True, WHITE)
        screen.blit(info, (WIDTH//2 - info.get_width()//2, 200))
        pb_text = font_med.render(f"Personal Best: {personal_best}", True, GRAY)
        screen.blit(pb_text, (WIDTH//2 - pb_text.get_width()//2, 250))
        retry_color = GREEN if selected == 0 else GRAY
        menu_color = GREEN if selected == 1 else GRAY
        pygame.draw.rect(screen, retry_color, retry_rect, 2)
        pygame.draw.rect(screen, menu_color, menu_rect, 2)
        retry_text = font_med.render("RETRY", True, WHITE)
        menu_text = font_med.render("MENU", True, WHITE)
        screen.blit(retry_text, (retry_rect.x + 20, retry_rect.y + 8))
        screen.blit(menu_text, (menu_rect.x + 20, menu_rect.y + 8))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = 0
                elif event.key == pygame.K_RIGHT:
                    selected = 1
                elif event.key == pygame.K_RETURN:
                    return "RETRY" if selected == 0 else "MENU"
            if event.type == pygame.MOUSEMOTION:
                if retry_rect.collidepoint(event.pos):
                    selected = 0
                elif menu_rect.collidepoint(event.pos):
                    selected = 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(event.pos):
                    return "RETRY"
                if menu_rect.collidepoint(event.pos):
                    return "MENU"
        clock.tick(30)

def main_menu(screen, clock):
    settings = load_settings()
    font = get_font("Courier New", 20, True)
    options = ["PLAY", "LEADERBOARD", "SETTINGS", "QUIT"]
    option_rects = []
    for i, opt in enumerate(options):
        text = font.render(opt, True, WHITE)
        rect = text.get_rect(center=(WIDTH//2, 200 + i*50))
        option_rects.append((opt, rect))
    selected = 0
    while True:
        screen.fill(BLACK)
        title = get_font("Courier New", 48, True).render("SNAKE", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        for i, (opt, rect) in enumerate(option_rects):
            color = GREEN if i == selected else GRAY
            text = font.render(opt, True, color)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    action = options[selected]
                    if action == "PLAY":
                        username = username_entry_screen(screen, clock)
                        final_score, final_level = game_loop(screen, clock, username, settings)
                        while True:
                            choice = game_over_screen(screen, clock, final_score, final_level, username)
                            if choice == "RETRY":
                                final_score, final_level = game_loop(screen, clock, username, settings)
                            else:
                                break
                    elif action == "LEADERBOARD":
                        leaderboard_screen(screen, clock)
                    elif action == "SETTINGS":
                        settings = settings_screen(screen, clock, settings)
                    else:
                        pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEMOTION:
                for i, (_, rect) in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = i
                        break
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, (opt, rect) in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        if opt == "PLAY":
                            username = username_entry_screen(screen, clock)
                            final_score, final_level = game_loop(screen, clock, username, settings)
                            while True:
                                choice = game_over_screen(screen, clock, final_score, final_level, username)
                                if choice == "RETRY":
                                    final_score, final_level = game_loop(screen, clock, username, settings)
                                else:
                                    break
                            break
                        elif opt == "LEADERBOARD":
                            leaderboard_screen(screen, clock)
                            break
                        elif opt == "SETTINGS":
                            settings = settings_screen(screen, clock, settings)
                            break
                        else:
                            pygame.quit(); sys.exit()
        clock.tick(30)

def leaderboard_screen(screen, clock):
    top = db.get_top_10()
    font_big = get_font("Courier New", 20, True)
    font_small = get_font("Courier New", 22, False)
    back_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT + HUD_HEIGHT - 60, 120, 40)
    while True:
        screen.fill(BLACK)
        title = font_big.render("TOP 10 SCORES", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        y = 100
        for idx, (name, score, lvl, played_at) in enumerate(top):
            line = f"{idx+1}. {name}  {score} pts  (lvl {lvl})  {played_at.strftime('%Y-%m-%d')}"
            text = font_small.render(line, True, WHITE)
            screen.blit(text, (50, y))
            y += 30
            if y > HEIGHT + HUD_HEIGHT - 100:
                break
        pygame.draw.rect(screen, GREEN, back_rect, 2)
        back_text = font_small.render("BACK", True, WHITE)
        screen.blit(back_text, (back_rect.x + 35, back_rect.y + 8))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        clock.tick(30)

def settings_screen(screen, clock, settings):
    font = get_font("Courier New", 20, True)
    font_small = get_font("Courier New", 22, False)
    grid_rect = pygame.Rect(WIDTH//2 - 100, 150, 200, 40)
    sound_rect = pygame.Rect(WIDTH//2 - 100, 220, 200, 40)
    color_rect = pygame.Rect(WIDTH//2 - 100, 290, 200, 40)
    save_rect = pygame.Rect(WIDTH//2 - 60, 380, 120, 40)
    color_presets = [(50,200,50), (255,100,100), (100,100,255), (255,200,50)]
    color_index = 0
    for i, col in enumerate(color_presets):
        if col == tuple(settings["snake_color"]):
            color_index = i
            break
    while True:
        screen.fill(BLACK)
        title = get_font("Courier New", 36, True).render("SETTINGS", True, GREEN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        # Grid toggle
        grid_status = "ON" if settings["grid_overlay"] else "OFF"
        pygame.draw.rect(screen, GRAY, grid_rect, 2)
        grid_text = font.render(f"Grid Overlay: {grid_status}", True, WHITE)
        screen.blit(grid_text, (grid_rect.x + 10, grid_rect.y + 10))
        # Sound toggle
        sound_status = "ON" if settings["sound"] else "OFF"
        pygame.draw.rect(screen, GRAY, sound_rect, 2)
        sound_text = font.render(f"Sound: {sound_status}", True, WHITE)
        screen.blit(sound_text, (sound_rect.x + 10, sound_rect.y + 10))
        # Color
        pygame.draw.rect(screen, GRAY, color_rect, 2)
        color_text = font.render("Snake Color", True, WHITE)
        screen.blit(color_text, (color_rect.x + 10, color_rect.y + 10))
        pygame.draw.circle(screen, color_presets[color_index], (color_rect.x + 170, color_rect.y + 20), 10)
        # Save button
        pygame.draw.rect(screen, GREEN, save_rect, 2)
        save_text = font_small.render("SAVE", True, WHITE)
        screen.blit(save_text, (save_rect.x + 35, save_rect.y + 8))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_rect.collidepoint(event.pos):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                elif sound_rect.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                elif color_rect.collidepoint(event.pos):
                    color_index = (color_index + 1) % len(color_presets)
                    settings["snake_color"] = color_presets[color_index]
                elif save_rect.collidepoint(event.pos):
                    save_settings(settings)
                    return settings
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return settings
        clock.tick(30)

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT + HUD_HEIGHT))
    pygame.display.set_caption("Snake TSIS 4")
    clock = pygame.time.Clock()
    main_menu(screen, clock)