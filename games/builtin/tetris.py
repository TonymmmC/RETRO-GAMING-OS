#!/usr/bin/env python3
"""
Tetris Modern - Juego de bloques con diseño moderno y minimalista
Compatible con Gaming Modern OS
"""

import pygame
import random
import sys
import time
import math

class TetrisModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración moderna
        self.cell_size = 30
        self.grid_width = 10
        self.grid_height = 20
        self.game_width = self.grid_width * self.cell_size + 40
        self.sidebar_width = 300
        self.width = self.game_width + self.sidebar_width
        self.height = self.grid_height * self.cell_size + 120
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris Modern")
        
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
                'grid': (40, 40, 40),                # Grid sutil
                'shadow': (0, 0, 0, 60),
                # Colores de tetrominos modernos
                'I': (0, 122, 255),      # Azul
                'O': (255, 149, 0),      # Naranja
                'T': (156, 39, 176),     # Púrpura
                'S': (52, 199, 89),      # Verde
                'Z': (255, 59, 48),      # Rojo
                'J': (63, 81, 181),      # Indigo
                'L': (255, 152, 0)       # Ámbar
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
                'grid': (220, 220, 220),             # Grid sutil
                'shadow': (0, 0, 0, 30),
                # Colores de tetrominos para tema claro
                'I': (52, 144, 220),     # Azul material
                'O': (255, 206, 84),     # Amarillo dorado
                'T': (156, 39, 176),     # Púrpura material
                'S': (76, 175, 80),      # Verde material
                'Z': (244, 67, 54),      # Rojo material
                'J': (63, 81, 181),      # Indigo
                'L': (255, 152, 0)       # Naranja material
            }
        }
        
        self.colors = self.themes['dark'].copy()
        
        # Fuentes modernas
        self.fonts = {
            'title': pygame.font.Font(None, 42),
            'large': pygame.font.Font(None, 32),
            'medium': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18),
            'tiny': pygame.font.Font(None, 14)
        }
        
        # Definir tetrominos
        self.tetrominos = {
            'I': [['.....',
                   '..#..',
                   '..#..',
                   '..#..',
                   '..#..'],
                  ['.....',
                   '.....',
                   '####.',
                   '.....',
                   '.....']],
            'O': [['.....',
                   '.....',
                   '.##..',
                   '.##..',
                   '.....']],
            'T': [['.....',
                   '.....',
                   '.#...',
                   '###..',
                   '.....'],
                  ['.....',
                   '.....',
                   '.#...',
                   '.##..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.....',
                   '###..',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.#...',
                   '##...',
                   '.#...']],
            'S': [['.....',
                   '.....',
                   '.##..',
                   '##...',
                   '.....'],
                  ['.....',
                   '.....',
                   '.#...',
                   '.##..',
                   '..#..']],
            'Z': [['.....',
                   '.....',
                   '##...',
                   '.##..',
                   '.....'],
                  ['.....',
                   '.....',
                   '..#..',
                   '.##..',
                   '.#...']],
            'J': [['.....',
                   '.....',
                   '.#...',
                   '.#...',
                   '##...'],
                  ['.....',
                   '.....',
                   '.....',
                   '#....',
                   '###..'],
                  ['.....',
                   '.....',
                   '.##..',
                   '.#...',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.....',
                   '###..',
                   '..#..']],
            'L': [['.....',
                   '.....',
                   '.#...',
                   '.#...',
                   '.##..'],
                  ['.....',
                   '.....',
                   '.....',
                   '###..',
                   '#....'],
                  ['.....',
                   '.....',
                   '##...',
                   '.#...',
                   '.#...'],
                  ['.....',
                   '.....',
                   '.....',
                   '..#..',
                   '###..']]
        }
        
        # Control del juego
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 500
        self.animation_time = 0
        
        # Estado del juego
        self.reset_game()
        
    def reset_game(self):
        """Reiniciar juego"""
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        self.current_piece = self.get_new_piece()
        self.piece_x = self.grid_width // 2 - 2
        self.piece_y = 0
        self.piece_rotation = 0
        
        self.next_piece = self.get_new_piece()
        
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.high_score = self.load_high_score()
        
        self.game_over = False
        self.paused = False
        
        self.line_clear_animation = []
        
    def get_new_piece(self):
        """Obtener nueva pieza aleatoria"""
        return random.choice(list(self.tetrominos.keys()))
        
    def get_piece_shape(self, piece, rotation):
        """Obtener forma de la pieza con rotación"""
        shapes = self.tetrominos[piece]
        return shapes[rotation % len(shapes)]
        
    def load_high_score(self):
        """Cargar high score"""
        try:
            with open("games/builtin/tetris_highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
        
    def save_high_score(self):
        """Guardar high score"""
        try:
            with open("games/builtin/tetris_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
            
    def toggle_theme(self):
        """Cambiar tema"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_sound('theme')
    
    def play_sound(self, sound_type):
        """Sonidos modernos"""
        try:
            frequencies = {
                'move': 800,
                'rotate': 1000,
                'drop': 600,
                'line_clear': 1200,
                'tetris': 1500,
                'game_over': 300,
                'theme': 900
            }
            
            freq = frequencies.get(sound_type, 800)
            duration = 100 if sound_type != 'game_over' else 500
            
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
    
    def is_valid_position(self, piece, x, y, rotation):
        """Verificar si la posición es válida"""
        shape = self.get_piece_shape(piece, rotation)
        
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    new_x = x + col_i
                    new_y = y + row_i
                    
                    if (new_x < 0 or new_x >= self.grid_width or 
                        new_y >= self.grid_height):
                        return False
                    
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return False
        
        return True
    
    def place_piece(self):
        """Colocar pieza en el grid"""
        shape = self.get_piece_shape(self.current_piece, self.piece_rotation)
        
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    x = self.piece_x + col_i
                    y = self.piece_y + row_i
                    if y >= 0:
                        self.grid[y][x] = self.current_piece
        
        # Verificar líneas completas
        lines_to_clear = []
        for y in range(self.grid_height):
            if all(cell is not None for cell in self.grid[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.clear_lines(lines_to_clear)
        
        # Nueva pieza
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        self.piece_x = self.grid_width // 2 - 2
        self.piece_y = 0
        self.piece_rotation = 0
        
        # Verificar game over
        if not self.is_valid_position(self.current_piece, self.piece_x, self.piece_y, self.piece_rotation):
            self.game_over = True
            self.play_sound('game_over')
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def clear_lines(self, lines):
        """Limpiar líneas completas"""
        for line in sorted(lines, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [None for _ in range(self.grid_width)])
        
        lines_count = len(lines)
        points = {1: 100, 2: 300, 3: 500, 4: 800}
        self.score += points.get(lines_count, 0) * self.level
        self.lines_cleared += lines_count
        
        self.level = (self.lines_cleared // 10) + 1
        self.fall_speed = max(50, 500 - (self.level - 1) * 30)
        
        if lines_count == 4:
            self.play_sound('tetris')
        else:
            self.play_sound('line_clear')
    
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
                    self.play_sound('move')
                
                elif event.key == pygame.K_t:
                    self.toggle_theme()
                
                elif not self.game_over and not self.paused:
                    if event.key == pygame.K_LEFT:
                        if self.is_valid_position(self.current_piece, self.piece_x - 1, 
                                                 self.piece_y, self.piece_rotation):
                            self.piece_x -= 1
                            self.play_sound('move')
                    
                    elif event.key == pygame.K_RIGHT:
                        if self.is_valid_position(self.current_piece, self.piece_x + 1, 
                                                 self.piece_y, self.piece_rotation):
                            self.piece_x += 1
                            self.play_sound('move')
                    
                    elif event.key == pygame.K_DOWN:
                        if self.is_valid_position(self.current_piece, self.piece_x, 
                                                 self.piece_y + 1, self.piece_rotation):
                            self.piece_y += 1
                            self.score += 1
                            self.play_sound('drop')
                    
                    elif event.key == pygame.K_UP:
                        new_rotation = (self.piece_rotation + 1) % len(self.tetrominos[self.current_piece])
                        if self.is_valid_position(self.current_piece, self.piece_x, 
                                                  self.piece_y, new_rotation):
                            self.piece_rotation = new_rotation
                            self.play_sound('rotate')
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.paused:
            return
        
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if self.is_valid_position(self.current_piece, self.piece_x, 
                                       self.piece_y + 1, self.piece_rotation):
                self.piece_y += 1
            else:
                self.place_piece()
            
            self.fall_time = current_time
        
        self.animation_time += 1
    
    def draw_background(self):
        """Dibujar fondo moderno"""
        self.screen.fill(self.colors['bg_primary'])
        
        # Área de juego
        game_rect = pygame.Rect(20, 20, self.grid_width * self.cell_size, 
                               self.grid_height * self.cell_size)
        
        self.draw_modern_card(self.screen, game_rect, self.colors['bg_secondary'])
        
        # Grid
        for x in range(0, self.grid_width + 1):
            start_x = game_rect.x + x * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid'],
                           (start_x, game_rect.y),
                           (start_x, game_rect.bottom), 1)
        
        for y in range(0, self.grid_height + 1):
            start_y = game_rect.y + y * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid'],
                           (game_rect.x, start_y),
                           (game_rect.right, start_y), 1)
    
    def draw_placed_pieces(self):
        """Dibujar piezas colocadas"""
        game_rect = pygame.Rect(20, 20, self.grid_width * self.cell_size, 
                               self.grid_height * self.cell_size)
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] is not None:
                    color = self.colors[self.grid[y][x]]
                    
                    cell_x = game_rect.x + x * self.cell_size + 2
                    cell_y = game_rect.y + y * self.cell_size + 2
                    cell_size = self.cell_size - 4
                    
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    
                    # Celda con bordes redondeados
                    pygame.draw.rect(self.screen, color, cell_rect, border_radius=6)
                    
                    # Highlight superior
                    highlight_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size // 3)
                    highlight_color = tuple(min(255, c + 30) for c in color)
                    pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=6)
    
    def draw_current_piece(self):
        """Dibujar pieza actual"""
        if self.game_over:
            return
            
        game_rect = pygame.Rect(20, 20, self.grid_width * self.cell_size, 
                               self.grid_height * self.cell_size)
        shape = self.get_piece_shape(self.current_piece, self.piece_rotation)
        color = self.colors[self.current_piece]
        
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    x = self.piece_x + col_i
                    y = self.piece_y + row_i
                    
                    if 0 <= x < self.grid_width and y >= 0:
                        cell_x = game_rect.x + x * self.cell_size + 2
                        cell_y = game_rect.y + y * self.cell_size + 2
                        cell_size = self.cell_size - 4
                        
                        cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                        
                        # Celda principal
                        pygame.draw.rect(self.screen, color, cell_rect, border_radius=6)
                        
                        # Highlight
                        highlight_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size // 3)
                        highlight_color = tuple(min(255, c + 40) for c in color)
                        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=6)
    
    def draw_sidebar(self):
        """Dibujar barra lateral moderna"""
        sidebar_x = self.game_width + 40
        
        # Título
        title_text = self.fonts['title'].render("TETRIS", True, self.colors['text_primary'])
        self.screen.blit(title_text, (sidebar_x, 30))
        
        # Next piece card
        next_card = pygame.Rect(sidebar_x, 80, 200, 120)
        self.draw_modern_card(self.screen, next_card, self.colors['bg_secondary'])
        
        next_text = self.fonts['medium'].render("NEXT", True, self.colors['text_secondary'])
        self.screen.blit(next_text, (sidebar_x + 15, 95))
        
        # Dibujar next piece
        shape = self.get_piece_shape(self.next_piece, 0)
        color = self.colors[self.next_piece]
        
        start_x = sidebar_x + 100 - (len(shape[0]) * 8)
        start_y = 130
        
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    x = start_x + col_i * 16
                    y = start_y + row_i * 16
                    
                    mini_rect = pygame.Rect(x, y, 14, 14)
                    pygame.draw.rect(self.screen, color, mini_rect, border_radius=3)
        
        # Stats card
        stats_card = pygame.Rect(sidebar_x, 220, 200, 200)
        self.draw_modern_card(self.screen, stats_card, self.colors['bg_secondary'])
        
        # Estadísticas
        stats_y = 240
        stats = [
            ("SCORE", f"{self.score:,}", self.colors['accent']),
            ("LINES", str(self.lines_cleared), self.colors['success']),
            ("LEVEL", str(self.level), self.colors['warning']),
            ("HIGH", f"{self.high_score:,}", self.colors['text_primary'])
        ]
        
        for i, (label, value, color) in enumerate(stats):
            label_text = self.fonts['tiny'].render(label, True, self.colors['text_secondary'])
            value_text = self.fonts['medium'].render(value, True, color)
            
            self.screen.blit(label_text, (sidebar_x + 15, stats_y + i * 40))
            self.screen.blit(value_text, (sidebar_x + 15, stats_y + i * 40 + 15))
        
        # Controls card
        controls_card = pygame.Rect(sidebar_x, 440, 200, 160)
        self.draw_modern_card(self.screen, controls_card, self.colors['bg_secondary'])
        
        controls_y = 460
        controls = [
            "← → Move",
            "↓ Soft drop", 
            "↑ Rotate",
            "Space Pause",
            f"T Theme ({'Dark' if self.dark_mode else 'Light'})",
            "Esc Exit"
        ]
        
        for i, control in enumerate(controls):
            text = self.fonts['tiny'].render(control, True, self.colors['text_secondary'])
            self.screen.blit(text, (sidebar_x + 15, controls_y + i * 18))
    
    def draw_overlay(self, title, subtitle="", action_text=""):
        """Overlay modal moderno"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Modal card
        card_width = 400
        card_height = 200
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_modern_card(self.screen, card_rect, self.colors['bg_secondary'], 
                             radius=16, shadow=True)
        
        # Título
        title_text = self.fonts['title'].render(title, True, self.colors['text_primary'])
        title_x = card_x + (card_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, card_y + 40))
        
        # Subtítulo
        if subtitle:
            subtitle_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            subtitle_x = card_x + (card_width - subtitle_text.get_width()) // 2
            self.screen.blit(subtitle_text, (subtitle_x, card_y + 85))
            
        # Texto de acción
        if action_text:
            # Efecto pulso
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * 0.1)
            action_color = tuple(int(c * pulse) for c in self.colors['accent'])
            
            action_font = self.fonts['large'] if not subtitle else self.fonts['medium']
            action_text_render = action_font.render(action_text, True, action_color)
            action_x = card_x + (card_width - action_text_render.get_width()) // 2
            action_y = card_y + (130 if not subtitle else 150)
            self.screen.blit(action_text_render, (action_x, action_y))

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
            self.draw_placed_pieces()
            self.draw_current_piece()
            self.draw_sidebar()
            
            # Overlays
            if self.paused and not self.game_over:
                self.draw_overlay("PAUSED", "Game is on hold", "Press SPACE to resume")
            elif self.game_over:
                if self.score == self.high_score and self.score > 0:
                    self.draw_overlay("GAME OVER", f"NEW HIGH SCORE: {self.score}!", "Press SPACE to restart")
                else:
                    self.draw_overlay("GAME OVER", f"Score: {self.score}", "Press SPACE to restart")

            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    game = TetrisModern()
    game.run()

if __name__ == "__main__":
    main()