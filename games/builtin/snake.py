#!/usr/bin/env python3
"""
Snake Modern - Juego de serpiente con diseño moderno y minimalista
Compatible con Gaming Modern OS
"""

import pygame
import random
import sys
import time
import math

class SnakeModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración moderna
        self.cell_size = 25
        self.grid_width = 24
        self.grid_height = 18
        self.padding = 50
        
        self.game_width = self.grid_width * self.cell_size
        self.game_height = self.grid_height * self.cell_size
        self.width = self.game_width + self.padding * 2
        self.height = self.game_height + self.padding * 2 + 100  # Extra para UI
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Modern")
        
        # Tema moderno - Dark mode por defecto
        self.dark_mode = True
        self.themes = {
            'dark': {
                'bg_primary': (26, 26, 26),          # #1a1a1a
                'bg_secondary': (45, 45, 45),        # #2d2d2d
                'bg_surface': (61, 61, 61),          # #3d3d3d
                'text_primary': (255, 255, 255),     # #ffffff
                'text_secondary': (160, 160, 160),   # #a0a0a0
                'accent': (0, 122, 255),             # #007AFF
                'success': (52, 199, 89),            # #34C759
                'warning': (255, 149, 0),            # #FF9500
                'danger': (255, 59, 48),             # #FF3B30
                'snake_head': (52, 199, 89),         # Verde moderno
                'snake_body': (80, 220, 120),        # Verde más claro
                'food': (255, 149, 0),               # Naranja moderno
                'grid': (40, 40, 40),                # Grid sutil
                'shadow': (0, 0, 0, 60)
            },
            'light': {
                'bg_primary': (248, 249, 250),       # #f8f9fa
                'bg_secondary': (255, 255, 255),     # #ffffff
                'bg_surface': (233, 236, 239),       # #e9ecef
                'text_primary': (33, 37, 41),        # #212529
                'text_secondary': (108, 117, 125),   # #6c757d
                'accent': (0, 122, 255),             # #007AFF
                'success': (40, 167, 69),            # #28a745
                'warning': (255, 193, 7),            # #ffc107
                'danger': (220, 53, 69),             # #dc3545
                'snake_head': (40, 167, 69),         # Verde
                'snake_body': (80, 200, 120),        # Verde claro
                'food': (255, 193, 7),               # Amarillo
                'grid': (220, 220, 220),             # Grid sutil
                'shadow': (0, 0, 0, 30)
            }
        }
        
        self.colors = self.themes['dark'].copy()
        
        # Fuentes modernas
        self.fonts = {
            'title': pygame.font.Font(None, 36),
            'large': pygame.font.Font(None, 28),
            'medium': pygame.font.Font(None, 22),
            'small': pygame.font.Font(None, 18),
            'tiny': pygame.font.Font(None, 14)
        }
        
        # Estado del juego
        self.reset_game()
        
        # Control
        self.clock = pygame.time.Clock()
        self.game_speed = 8
        self.animation_time = 0
        
        # Efectos
        self.food_pulse = 0
        self.score_display = 0
        
    def reset_game(self):
        """Reiniciar juego"""
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        
        self.snake = [(center_x, center_y), (center_x - 1, center_y)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False
        
        self.food_pulse = 0
        self.score_display = 0
        
    def load_high_score(self):
        """Cargar high score"""
        try:
            with open("games/builtin/snake_highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        """Guardar high score"""
        try:
            with open("games/builtin/snake_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def generate_food(self):
        """Generar comida"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def play_sound(self, sound_type):
        """Sonidos modernos"""
        try:
            frequencies = {
                'move': 800,
                'eat': 1200,
                'game_over': 300,
                'pause': 600,
                'theme': 1000
            }
            
            freq = frequencies.get(sound_type, 800)
            duration = 80 if sound_type != 'game_over' else 400
            
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            
            for i in range(frames):
                t = float(i) / sample_rate
                envelope = math.exp(-t * 6)
                wave = math.sin(2 * math.pi * freq * t) * envelope * 0.08
                arr.append([int(32767 * wave)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass
    
    def toggle_theme(self):
        """Cambiar tema"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_sound('theme')
    
    def draw_modern_card(self, surface, rect, color, radius=12, shadow=True):
        """Dibujar card moderna"""
        if shadow:
            # Sombra
            shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
            shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, self.colors['shadow'], 
                           (0, 0, rect.width, rect.height), border_radius=radius)
            surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Card principal
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_background(self):
        """Dibujar fondo moderno"""
        self.screen.fill(self.colors['bg_primary'])
        
        # Área de juego
        game_rect = pygame.Rect(self.padding, self.padding, 
                               self.game_width, self.game_height)
        
        self.draw_modern_card(self.screen, game_rect, self.colors['bg_secondary'])
        
        # Grid sutil
        for x in range(0, self.grid_width + 1):
            start_x = self.padding + x * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid'],
                           (start_x, self.padding),
                           (start_x, self.padding + self.game_height), 1)
        
        for y in range(0, self.grid_height + 1):
            start_y = self.padding + y * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid'],
                           (self.padding, start_y),
                           (self.padding + self.game_width, start_y), 1)
    
    def draw_snake(self):
        """Dibujar serpiente moderna"""
        for i, (x, y) in enumerate(self.snake):
            cell_x = self.padding + x * self.cell_size + 2
            cell_y = self.padding + y * self.cell_size + 2
            cell_size = self.cell_size - 4
            
            rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
            
            if i == 0:  # Cabeza
                color = self.colors['snake_head']
                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                
                # Highlight en la cabeza
                highlight_rect = pygame.Rect(cell_x + 2, cell_y + 2, 
                                           cell_size - 4, cell_size // 3)
                highlight_color = tuple(min(255, c + 40) for c in color)
                pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=6)
                
            else:  # Cuerpo
                # Efecto de degradado en el cuerpo
                fade_factor = 1.0 - (i / len(self.snake)) * 0.3
                color = self.colors['snake_body']
                faded_color = tuple(int(c * fade_factor) for c in color)
                
                pygame.draw.rect(self.screen, faded_color, rect, border_radius=6)
    
    def draw_food(self):
        """Dibujar comida con efecto pulso"""
        x, y = self.food
        cell_x = self.padding + x * self.cell_size + 3
        cell_y = self.padding + y * self.cell_size + 3
        
        # Efecto pulso
        pulse = 1.0 + 0.2 * math.sin(self.food_pulse * 0.2)
        size = int((self.cell_size - 6) * pulse)
        
        food_rect = pygame.Rect(
            cell_x + (self.cell_size - 6 - size) // 2,
            cell_y + (self.cell_size - 6 - size) // 2,
            size, size
        )
        
        # Sombra de la comida
        shadow_rect = pygame.Rect(food_rect.x + 2, food_rect.y + 2, 
                                 food_rect.width, food_rect.height)
        shadow_surface = pygame.Surface((food_rect.width, food_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, self.colors['shadow'], 
                          (0, 0, food_rect.width, food_rect.height))
        self.screen.blit(shadow_surface, shadow_rect.topleft)
        
        # Comida principal
        pygame.draw.ellipse(self.screen, self.colors['food'], food_rect)
        
        # Highlight
        highlight_size = size // 3
        highlight_rect = pygame.Rect(
            food_rect.x + size // 4,
            food_rect.y + size // 4,
            highlight_size, highlight_size
        )
        highlight_color = tuple(min(255, c + 60) for c in self.colors['food'])
        pygame.draw.ellipse(self.screen, highlight_color, highlight_rect)
    
    def draw_ui(self):
        """Dibujar UI moderna"""
        ui_y = self.padding + self.game_height + 20
        
        # Card de estadísticas
        ui_rect = pygame.Rect(self.padding, ui_y, self.game_width, 60)
        self.draw_modern_card(self.screen, ui_rect, self.colors['bg_secondary'])
        
        # Score animado
        target_score = self.score
        if self.score_display < target_score:
            self.score_display = min(target_score, self.score_display + 1)
        
        # Información del juego
        score_text = self.fonts['large'].render(f"SCORE: {self.score_display:04d}", 
                                               True, self.colors['accent'])
        self.screen.blit(score_text, (ui_rect.x + 20, ui_rect.y + 10))
        
        high_text = self.fonts['medium'].render(f"HIGH: {self.high_score:04d}", 
                                              True, self.colors['text_secondary'])
        self.screen.blit(high_text, (ui_rect.x + 20, ui_rect.y + 35))
        
        # Estadísticas de juego
        length_text = self.fonts['medium'].render(f"LENGTH: {len(self.snake)}", 
                                                True, self.colors['text_secondary'])
        self.screen.blit(length_text, (ui_rect.x + 200, ui_rect.y + 10))
        
        speed_text = self.fonts['medium'].render(f"SPEED: {self.game_speed}", 
                                               True, self.colors['text_secondary'])
        self.screen.blit(speed_text, (ui_rect.x + 200, ui_rect.y + 35))
        
        # Controles (derecha)
        controls = [
            "ARROWS: Move",
            "SPACE: Pause",
            f"T: Theme ({'Dark' if self.dark_mode else 'Light'})",
            "ESC: Exit"
        ]
        
        control_x = ui_rect.right - 200
        for i, control in enumerate(controls):
            control_text = self.fonts['tiny'].render(control, True, self.colors['text_secondary'])
            self.screen.blit(control_text, (control_x, ui_rect.y + 5 + i * 12))
    
    def draw_overlay(self, title, subtitle="", action=""):
        """Overlay modal moderno"""
        # Fondo semi-transparente
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Modal card
        modal_width = 400
        modal_height = 200
        modal_x = (self.width - modal_width) // 2
        modal_y = (self.height - modal_height) // 2
        
        modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)
        self.draw_modern_card(self.screen, modal_rect, self.colors['bg_secondary'], 
                             radius=16, shadow=True)
        
        # Contenido del modal
        title_text = self.fonts['title'].render(title, True, self.colors['text_primary'])
        title_x = modal_x + (modal_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, modal_y + 40))
        
        if subtitle:
            sub_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            sub_x = modal_x + (modal_width - sub_text.get_width()) // 2
            self.screen.blit(sub_text, (sub_x, modal_y + 80))
        
        if action:
            # Efecto pulso para el texto de acción
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * 0.1)
            action_color = tuple(int(c * pulse) for c in self.colors['accent'])
            
            action_text = self.fonts['large'].render(action, True, action_color)
            action_x = modal_x + (modal_width - action_text.get_width()) // 2
            self.screen.blit(action_text, (action_x, modal_y + 130))
    
    def handle_events(self):
        """Manejar eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.paused = not self.paused
                    self.play_sound('pause')
                
                elif event.key == pygame.K_t:
                    self.toggle_theme()
                
                elif not self.game_over and not self.paused:
                    # Controles direccionales
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                        self.play_sound('move')
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                        self.play_sound('move')
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                        self.play_sound('move')
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)
                        self.play_sound('move')
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.paused:
            return
        
        # Actualizar dirección
        self.direction = self.next_direction
        
        # Mover serpiente
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Verificar colisiones con paredes
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            self.play_sound('game_over')
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        
        # Verificar colisión consigo misma
        if new_head in self.snake:
            self.game_over = True
            self.play_sound('game_over')
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        
        # Agregar nueva cabeza
        self.snake.insert(0, new_head)
        
        # Verificar si comió
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.play_sound('eat')
            
            # Aumentar velocidad gradualmente
            if self.score % 50 == 0 and self.game_speed < 15:
                self.game_speed += 1
        else:
            # Quitar cola si no comió
            self.snake.pop()
    
    def run(self):
        """Loop principal"""
        running = True
        
        while running:
            # Eventos
            running = self.handle_events()
            
            # Lógica
            self.update_game()
            
            # Render
            self.draw_background()
            self.draw_snake()
            self.draw_food()
            self.draw_ui()
            
            # Overlays
            if self.game_over:
                if self.score == self.high_score and self.score > 0:
                    self.draw_overlay("GAME OVER", f"NEW HIGH SCORE: {self.score}!", 
                                    "PRESS SPACE TO PLAY AGAIN")
                else:
                    self.draw_overlay("GAME OVER", f"Final Score: {self.score}", 
                                    "PRESS SPACE TO PLAY AGAIN")
            elif self.paused:
                self.draw_overlay("PAUSED", "Game is on hold", 
                                "PRESS SPACE TO RESUME")
            
            # Actualizar animaciones
            self.animation_time += 1
            self.food_pulse += 1
            
            pygame.display.flip()
            self.clock.tick(self.game_speed)
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    game = SnakeModern()
    game.run()

if __name__ == "__main__":
    main()