#!/usr/bin/env python3
"""
Snake Modern - Juego de la serpiente con diseño minimalista y moderno
Para usar dentro del Gaming OS, con alternancia de temas (claro/oscuro)
"""

import pygame
import random
import sys
import time
import math # Not strictly needed for this version, but good practice if more animations were added

class SnakeModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración de pantalla
        self.cell_size = 24 # Slightly smaller cells for a sleeker look
        self.grid_width = 25 # Adjusted grid size
        self.grid_height = 20 # Adjusted grid size
        self.game_area_padding = 40 # Padding around the main game grid
        
        self.game_width_px = self.grid_width * self.cell_size
        self.game_height_px = self.grid_height * self.cell_size
        
        self.width = self.game_width_px + self.game_area_padding * 2 # Total width including padding
        self.height = self.game_height_px + self.game_area_padding + 120 # Extra for UI at bottom
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Modern")
        
        # Sistema de temas (inspirado en TetrisModern)
        self.dark_mode = False
        self.themes = {
            'light': {
                'bg': (248, 249, 250),       # Gris muy claro
                'card_bg': (255, 255, 255),  # Blanco para tarjetas
                'grid_line': (233, 236, 239),# Gris claro para líneas de grid
                'border': (206, 212, 218),   # Gris medio para bordes
                'text_primary': (33, 37, 41),# Casi negro para texto principal
                'text_secondary': (108, 117, 125), # Gris para texto secundario
                'accent': (0, 123, 255),     # Azul de acento (Score, New High Score)
                'snake_head': (76, 175, 80), # Verde vivo para cabeza
                'snake_body': (102, 187, 106),# Verde más suave para cuerpo
                'food': (255, 193, 7),       # Amarillo anaranjado para comida
                'overlay': (255, 255, 255, 200), # Overlay claro
                'shadow_light': (0, 0, 0, 20), # Sombra sutil
                'shadow_dark': (0, 0, 0, 40)  # Sombra más intensa
            },
            'dark': {
                'bg': (18, 18, 18),          # Negro suave
                'card_bg': (33, 37, 41),     # Gris oscuro para tarjetas
                'grid_line': (52, 58, 64),   # Gris medio para líneas de grid
                'border': (73, 80, 87),      # Gris claro para bordes
                'text_primary': (248, 249, 250), # Blanco para texto principal
                'text_secondary': (173, 181, 189), # Gris claro para texto secundario
                'accent': (13, 202, 240),    # Cyan más vibrante (Score, New High Score)
                'snake_head': (32, 201, 151), # Verde azulado vibrante
                'snake_body': (80, 216, 178), # Verde azulado más claro
                'food': (255, 212, 59),      # Amarillo más brillante para comida
                'overlay': (33, 37, 41, 220), # Overlay oscuro
                'shadow_light': (0, 0, 0, 40), # Sombra sutil
                'shadow_dark': (0, 0, 0, 60)  # Sombra más intensa
            }
        }
        
        # Colores actuales (empezar en modo claro)
        self.colors = self.themes['light'].copy()
        
        # Fuentes modernas
        self.fonts = {
            'title': pygame.font.Font(None, 42),
            'large': pygame.font.Font(None, 32),
            'medium': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18),
            'tiny': pygame.font.Font(None, 14)
        }
        
        # Estado del juego
        self.reset_game()
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        self.game_speed = 6  # Velocidad inicial (FPS) - Reduced from 8 to make it slower
        
        # Animaciones
        self.food_blink_timer = 0
        self.food_blink_interval = 15 # Blink every 15 frames (half a second at 30 FPS)
        
    def reset_game(self):
        """Reiniciar estado del juego"""
        # Serpiente inicial (centro de la pantalla)
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        
        # Dirección inicial
        self.direction = (1, 0)  # Derecha
        self.next_direction = (1, 0) # Allows for quick turns without conflicting with current direction
        
        # Comida
        self.food = self.generate_food()
        
        # Puntuación
        self.score = 0
        self.high_score = self.load_high_score()
        
        # Estado
        self.game_over = False
        self.paused = False
        
        # Reset animation timer
        self.food_blink_timer = 0
        
    def load_high_score(self):
        """Cargar puntuación máxima"""
        try:
            with open("games/builtin/snake_highscore.txt", "r") as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0
        except ValueError: # Handle corrupted file
            return 0
    
    def save_high_score(self):
        """Guardar puntuación máxima"""
        try:
            with open("games/builtin/snake_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception as e: # Catch any potential file writing errors
            print(f"Error saving high score: {e}")
            pass
    
    def generate_food(self):
        """Generar nueva comida en posición aleatoria"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def play_beep(self, frequency=800, duration=100, volume=0.08):
        """Reproducir sonido beep suave"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            for i in range(frames):
                # Simple sine wave for a soft beep
                amplitude = 16383 * volume * math.sin(2 * math.pi * frequency * i / sample_rate)
                arr.append([int(amplitude)] * 2) # Stereo sound
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            # print(f"Error playing sound: {e}") # For debugging, can be removed
            pass  # Fail silently if there's no audio or an error
    
    def draw_rounded_rect(self, surface, color, rect, radius=8):
        """Dibujar rectángulo con bordes redondeados"""
        if radius > 0:
            pygame.draw.rect(surface, color, rect, border_radius=radius)
        else:
            pygame.draw.rect(surface, color, rect)
    
    def draw_shadow_rect(self, surface, rect, radius=8, shadow_offset=2, alpha=20):
        """Dibujar rectángulo con sombra sutil"""
        shadow_rect = rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        # Create a surface for the shadow with alpha channel
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))

    def handle_events(self):
        """Manejar eventos de entrada"""
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
                    self.play_beep(600, 50)
                
                elif event.key == pygame.K_t: # Toggle theme
                    self.toggle_theme()
                
                elif not self.game_over and not self.paused:
                    # Directional controls (prevents immediate reverse)
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                        self.play_beep(700, 20)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                        self.play_beep(700, 20)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                        self.play_beep(700, 20)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)
                        self.play_beep(700, 20)
        
        return True
    
    def toggle_theme(self):
        """Alternar entre modo claro y oscuro"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_beep(800, 80)
        
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.paused:
            return
        
        # Update current direction to the buffered next_direction
        self.direction = self.next_direction
        
        # Mover serpiente
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Verificar colisiones con paredes
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.game_over = True
            self.play_beep(200, 500) # Game over sound
            return
        
        # Verificar colisión consigo misma
        if new_head in self.snake:
            self.game_over = True
            self.play_beep(200, 500) # Game over sound
            return
        
        # Agregar nueva cabeza
        self.snake.insert(0, new_head)
        
        # Verificar si comió
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.play_beep(1000, 100) # Food eaten sound
            
            # Aumentar velocidad gradualmente (max 20 FPS)
            if self.score % 50 == 0 and self.game_speed < 20:
                self.game_speed += 1
            
            # Actualizar high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        else:
            # Quitar cola si no comió
            self.snake.pop()
        
        # Actualizar timer para animación de comida
        self.food_blink_timer = (self.food_blink_timer + 1) % (self.food_blink_interval * 2) # Cycle for blink
    
    def draw_game_area_background(self):
        """Dibuja el fondo principal del área de juego con el grid sutil"""
        self.screen.fill(self.colors['bg'])
        
        game_rect_padded = pygame.Rect(self.game_area_padding // 2, 
                                       self.game_area_padding // 2, 
                                       self.game_width_px + self.game_area_padding, 
                                       self.game_height_px + self.game_area_padding)
        
        # Draw a subtle shadow behind the main game area
        self.draw_shadow_rect(self.screen, game_rect_padded, radius=12, shadow_offset=6, alpha=40)
        
        # Draw the main game area card
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], game_rect_padded, 12)
        pygame.draw.rect(self.screen, self.colors['border'], game_rect_padded, 1, border_radius=12)

        # Calculate the actual playable grid area for drawing purposes
        game_grid_offset_x = self.game_area_padding
        game_grid_offset_y = self.game_area_padding
        
        # Draw subtle grid lines
        for x in range(0, self.grid_width):
            start_x = game_grid_offset_x + x * self.cell_size
            end_x = start_x
            start_y = game_grid_offset_y
            end_y = game_grid_offset_y + self.game_height_px
            pygame.draw.line(self.screen, self.colors['grid_line'], (start_x, start_y), (end_x, end_y), 1)

        for y in range(0, self.grid_height):
            start_x = game_grid_offset_x
            end_x = game_grid_offset_x + self.game_width_px
            start_y = game_grid_offset_y + y * self.cell_size
            end_y = start_y
            pygame.draw.line(self.screen, self.colors['grid_line'], (start_x, start_y), (end_x, end_y), 1)

        # Return the top-left coordinate of the actual game grid
        return (game_grid_offset_x, game_grid_offset_y)
    
    def draw_snake(self, grid_offset_x, grid_offset_y):
        """Dibujar serpiente con estilo moderno"""
        for i, (x, y) in enumerate(self.snake):
            # Calculate actual screen coordinates
            cell_x = grid_offset_x + x * self.cell_size
            cell_y = grid_offset_y + y * self.cell_size
            
            # Use slightly smaller rectangles for a gap effect
            rect_margin = 2
            segment_rect = pygame.Rect(cell_x + rect_margin, cell_y + rect_margin, 
                                       self.cell_size - 2 * rect_margin, 
                                       self.cell_size - 2 * rect_margin)
            
            if i == 0:  # Head
                color = self.colors['snake_head']
                # Add a subtle glow/highlight effect for the head
                self.draw_shadow_rect(self.screen, segment_rect, radius=6, shadow_offset=2, alpha=60)
                self.draw_rounded_rect(self.screen, color, segment_rect, 6)
                # Head highlight
                highlight_rect = pygame.Rect(segment_rect.x + 1, segment_rect.y + 1, 
                                             segment_rect.width - 2, segment_rect.height // 3)
                highlight_color = tuple(min(255, c + 30) for c in color)
                self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 4)
            else:  # Body
                color = self.colors['snake_body']
                # Subtle shadow for body segments
                self.draw_shadow_rect(self.screen, segment_rect, radius=6, shadow_offset=1, alpha=30)
                self.draw_rounded_rect(self.screen, color, segment_rect, 6)
                # Body highlight (optional, but adds depth)
                highlight_rect = pygame.Rect(segment_rect.x + 1, segment_rect.y + 1, 
                                             segment_rect.width - 2, segment_rect.height // 4)
                highlight_color = tuple(min(255, c + 20) for c in color)
                self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 4)
    
    def draw_food(self, grid_offset_x, grid_offset_y):
        """Dibujar comida con efecto parpadeante y estilo moderno"""
        x, y = self.food
        
        # Calculate actual screen coordinates
        food_x = grid_offset_x + x * self.cell_size
        food_y = grid_offset_y + y * self.cell_size
        
        # Blink effect: change color slightly
        base_color = self.colors['food']
        if self.food_blink_timer < self.food_blink_interval:
            color = base_color
        else:
            # Lighter version of the food color for blinking
            color = tuple(min(255, c + 50) for c in base_color)
            
        # Draw food as a rounded square
        food_rect_margin = 4 # Make it slightly smaller than the cell for more breathing room
        food_rect = pygame.Rect(food_x + food_rect_margin, food_y + food_rect_margin, 
                                self.cell_size - 2 * food_rect_margin, 
                                self.cell_size - 2 * food_rect_margin)
        
        self.draw_shadow_rect(self.screen, food_rect, radius=4, shadow_offset=2, alpha=50)
        self.draw_rounded_rect(self.screen, color, food_rect, 4)
        
    def draw_ui(self):
        """Dibujar interfaz de usuario moderna en la parte inferior"""
        ui_y = self.game_height_px + self.game_area_padding * 2 # Below the game grid + its padding
        
        # UI Background (card-like)
        ui_card_rect = pygame.Rect(self.game_area_padding // 2, ui_y, 
                                   self.width - self.game_area_padding, 
                                   self.height - ui_y - self.game_area_padding // 2)
        self.draw_shadow_rect(self.screen, ui_card_rect, radius=12, shadow_offset=6, alpha=40)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], ui_card_rect, 12)
        pygame.draw.rect(self.screen, self.colors['border'], ui_card_rect, 1, border_radius=12)
        
        # Positioning for UI elements within the card
        text_padding_x = 20
        text_padding_y = 15

        # --- Left Section: Score, High Score, Speed, Length ---
        col1_x = ui_card_rect.x + text_padding_x
        col2_x_offset = 180 # Increased offset for better spacing

        # Score
        score_label = self.fonts['small'].render("SCORE", True, self.colors['text_secondary'])
        score_value = self.fonts['large'].render(f"{self.score:04d}", True, self.colors['accent'])
        self.screen.blit(score_label, (col1_x, ui_card_rect.y + text_padding_y))
        self.screen.blit(score_value, (col1_x, ui_card_rect.y + text_padding_y + 18))
        
        # High Score
        high_score_label = self.fonts['small'].render("HIGH", True, self.colors['text_secondary'])
        high_score_value = self.fonts['medium'].render(f"{self.high_score:04d}", True, self.colors['text_primary'])
        self.screen.blit(high_score_label, (col1_x + col2_x_offset, ui_card_rect.y + text_padding_y))
        self.screen.blit(high_score_value, (col1_x + col2_x_offset, ui_card_rect.y + text_padding_y + 18))
        
        # Speed and Length
        speed_text = self.fonts['tiny'].render(f"SPEED: {self.game_speed}", True, self.colors['text_secondary'])
        length_text = self.fonts['tiny'].render(f"LENGTH: {len(self.snake)}", True, self.colors['text_secondary'])
        self.screen.blit(speed_text, (col1_x, ui_card_rect.y + text_padding_y + 55))
        self.screen.blit(length_text, (col1_x + col2_x_offset, ui_card_rect.y + text_padding_y + 55))
        
        # --- Right Section: Controls ---
        controls = [
            "ARROWS: Move",
            "SPACE: Pause/Restart",
            f"T: Theme ({'Dark' if self.dark_mode else 'Light'})",
            "ESC: Exit"
        ]
        
        control_y_start = ui_card_rect.y + text_padding_y # Align controls top with stats top
        
        # Calculate max width of controls to right-align properly
        max_control_width = 0
        for control in controls:
            max_control_width = max(max_control_width, self.fonts['tiny'].render(control, True, self.colors['text_secondary']).get_width())

        for i, control in enumerate(controls):
            text_render = self.fonts['tiny'].render(control, True, self.colors['text_secondary'])
            # Right align within the UI card, with 20px padding from the right edge
            text_x = ui_card_rect.right - text_render.get_width() - text_padding_x 
            self.screen.blit(text_render, (text_x, control_y_start + i * 18))
            
    def draw_overlay(self, title, subtitle="", action_text=""):
        """Dibujar overlay moderno (copiado de TetrisModern)"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        self.screen.blit(overlay, (0, 0))
        
        # Card principal
        card_width = 400
        card_height = 200
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_shadow_rect(self.screen, card_rect, radius=12, shadow_offset=8, alpha=60)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], card_rect, 12)
        
        # Título
        title_text = self.fonts['title'].render(title, True, self.colors['text_primary'])
        title_x = card_x + (card_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, card_y + 40))
        
        # Subtítulo (si existe)
        if subtitle:
            subtitle_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            subtitle_x = card_x + (card_width - subtitle_text.get_width()) // 2
            self.screen.blit(subtitle_text, (subtitle_x, card_y + 85))
            
        # Texto de acción (si existe)
        if action_text:
            action_font = self.fonts['large'] if not subtitle else self.fonts['medium']
            action_text_render = action_font.render(action_text, True, self.colors['accent'])
            action_x = card_x + (card_width - action_text_render.get_width()) // 2
            action_y = card_y + (130 if not subtitle else 150)
            self.screen.blit(action_text_render, (action_x, action_y))
    
    def run(self):
        """Loop principal del juego"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar juego
            self.update_game()
            
            # Dibujar todo
            # Get the top-left coordinates of the game grid (inside the card)
            grid_offset_x, grid_offset_y = self.draw_game_area_background() 
            self.draw_snake(grid_offset_x, grid_offset_y)
            self.draw_food(grid_offset_x, grid_offset_y)
            self.draw_ui()
            
            if self.game_over:
                self.draw_overlay("GAME OVER", f"FINAL SCORE: {self.score}", "PRESS SPACE TO PLAY AGAIN")
                # Optional: Show new high score message
                if self.score == self.high_score and self.score > 0:
                    new_high_score_text = self.fonts['medium'].render("NEW HIGH SCORE!", True, self.colors['food'])
                    new_high_score_x = (self.width - new_high_score_text.get_width()) // 2
                    new_high_score_y = self.height // 2 + 70 # Adjust positioning as needed
                    self.screen.blit(new_high_score_text, (new_high_score_x, new_high_score_y))
                    
            elif self.paused:
                self.draw_overlay("PAUSED", "Game is on hold", "PRESS SPACE TO RESUME")
            
            pygame.display.flip()
            self.clock.tick(self.game_speed) # Control FPS based on game speed
        
        pygame.quit()
        sys.exit() # Ensure clean exit

def main():
    """Función principal para iniciar el juego"""
    game = SnakeModern()
    game.run()

if __name__ == "__main__":
    main()
