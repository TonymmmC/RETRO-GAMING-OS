#!/usr/bin/env python3
"""
Tetris Modern - Juego de bloques con diseño minimalista y moderno
Controles WASD optimizados
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
        
        # Configuración de pantalla
        self.cell_size = 32
        self.grid_width = 10
        self.grid_height = 20
        self.game_width = self.grid_width * self.cell_size + 40  # Padding
        self.sidebar_width = 280
        self.width = self.game_width + self.sidebar_width
        self.height = self.grid_height * self.cell_size + 120
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Tetris Modern")
        
        # Sistema de temas
        self.dark_mode = False
        self.themes = {
            'light': {
                'bg': (248, 249, 250),       # Gris muy claro
                'card_bg': (255, 255, 255),  # Blanco para tarjetas
                'grid': (233, 236, 239),     # Gris claro para líneas
                'border': (206, 212, 218),   # Gris medio para bordes
                'text_primary': (33, 37, 41),# Casi negro para texto principal
                'text_secondary': (108, 117, 125), # Gris para texto secundario
                'accent': (0, 123, 255),     # Azul de acento
                'success': (40, 167, 69),    # Verde éxito
                'warning': (255, 193, 7),    # Amarillo advertencia
                'shadow': (0, 0, 0, 20),     # Sombra sutil
                'overlay': (255, 255, 255, 200), # Overlay claro
                # Colores de tetrominos - paleta moderna y suave
                'I': (52, 144, 220),    # Azul moderno
                'O': (255, 206, 84),    # Amarillo dorado suave
                'T': (156, 39, 176),    # Púrpura moderno
                'S': (76, 175, 80),     # Verde material
                'Z': (244, 67, 54),     # Rojo material
                'J': (63, 81, 181),     # Indigo
                'L': (255, 152, 0)      # Naranja material
            },
            'dark': {
                'bg': (18, 18, 18),          # Negro suave
                'card_bg': (33, 37, 41),     # Gris oscuro para tarjetas
                'grid': (52, 58, 64),        # Gris medio para líneas
                'border': (73, 80, 87),      # Gris claro para bordes
                'text_primary': (248, 249, 250), # Blanco para texto principal
                'text_secondary': (173, 181, 189), # Gris claro para texto secundario
                'accent': (13, 202, 240),    # Cyan más vibrante
                'success': (32, 201, 151),   # Verde más vibrante
                'warning': (255, 212, 59),   # Amarillo más vibrante
                'shadow': (0, 0, 0, 40),     # Sombra más intensa
                'overlay': (33, 37, 41, 220), # Overlay oscuro
                # Colores de tetrominos - versiones más vibrantes para contraste
                'I': (79, 172, 254),    # Azul más brillante
                'O': (255, 230, 109),   # Amarillo más brillante
                'T': (186, 85, 211),    # Púrpura más brillante
                'S': (102, 187, 106),   # Verde más brillante
                'Z': (239, 83, 80),     # Rojo más brillante
                'J': (92, 107, 192),    # Indigo más brillante
                'L': (255, 167, 38)     # Naranja más brillante
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
        
        # Definir formas de tetrominos
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
        
        # Clock
        self.clock = pygame.time.Clock()
        self.fall_time = 0
        self.fall_speed = 500
        
        # Control de teclas repetidas
        self.key_repeat_timer = {}
        self.key_repeat_delay = 150
        self.key_repeat_interval = 50
        
        # Animaciones
        self.animation_time = 0
        
        # Estado del juego - Inicializar DESPUÉS de definir tetrominos
        self.reset_game()
        
    def get_new_piece(self):
        """Obtener nueva pieza aleatoria"""
        return random.choice(list(self.tetrominos.keys()))
        
    def get_piece_shape(self, piece, rotation):
        """Obtener forma de la pieza con rotación"""
        shapes = self.tetrominos[piece]
        return shapes[rotation % len(shapes)]
        
    def reset_game(self):
        """Reiniciar estado del juego"""
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
        
    def load_high_score(self):
        """Cargar puntuación máxima"""
        try:
            with open("games/builtin/tetris_highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
        
    def save_high_score(self):
        """Guardar puntuación máxima"""
        try:
            with open("games/builtin/tetris_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
        
    def toggle_theme(self):
        """Alternar entre modo claro y oscuro"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_beep(800, 80)
    
    def play_beep(self, frequency=800, duration=100):
        """Reproducir sonido beep suave"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            for i in range(frames):
                wave = 2048 * (frequency * 2 * 3.14159 * i / sample_rate) % (2 * 3.14159)
                arr.append([int(16383 * 0.05 * (wave - 3.14159) / 3.14159)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass
    
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
        
        # Verificar game over - solo cuando la nueva pieza no puede colocarse
        if not self.is_valid_position(self.current_piece, self.piece_x, self.piece_y, self.piece_rotation):
            self.game_over = True
            self.play_beep(300, 800)
            
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
    
    def clear_lines(self, lines):
        """Limpiar líneas completas"""
        self.line_clear_animation = lines
        
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
            self.play_beep(800, 200)  # Tetris!
        else:
            self.play_beep(600, 100)
    
    def handle_continuous_input(self):
        """Manejar input continuo"""
        if self.game_over or self.paused:
            return
            
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        
        if keys[pygame.K_a]:
            if (pygame.K_a not in self.key_repeat_timer or 
                current_time - self.key_repeat_timer[pygame.K_a] > self.key_repeat_interval):
                
                if self.is_valid_position(self.current_piece, self.piece_x - 1, 
                                         self.piece_y, self.piece_rotation):
                    self.piece_x -= 1
                    self.play_beep(500, 30)
                    self.key_repeat_timer[pygame.K_a] = current_time
        else:
            self.key_repeat_timer.pop(pygame.K_a, None)
            
        if keys[pygame.K_d]:
            if (pygame.K_d not in self.key_repeat_timer or 
                current_time - self.key_repeat_timer[pygame.K_d] > self.key_repeat_interval):
                
                if self.is_valid_position(self.current_piece, self.piece_x + 1, 
                                         self.piece_y, self.piece_rotation):
                    self.piece_x += 1
                    self.play_beep(500, 30)
                    self.key_repeat_timer[pygame.K_d] = current_time
        else:
            self.key_repeat_timer.pop(pygame.K_d, None)
            
        if keys[pygame.K_s]:
            if (pygame.K_s not in self.key_repeat_timer or 
                current_time - self.key_repeat_timer[pygame.K_s] > 80):
                
                if self.is_valid_position(self.current_piece, self.piece_x, 
                                         self.piece_y + 1, self.piece_rotation):
                    self.piece_y += 1
                    self.score += 1
                    self.play_beep(400, 20)
                    self.key_repeat_timer[pygame.K_s] = current_time
        else:
            self.key_repeat_timer.pop(pygame.K_s, None)
    
    def handle_events(self):
        """Manejar eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.K_ESCAPE:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.paused = not self.paused
                    self.play_beep(600, 100)
                
                elif event.key == pygame.K_t:
                    # Toggle tema con T
                    self.toggle_theme()
                
                elif not self.game_over and not self.paused:
                    if event.key == pygame.K_w or event.key == pygame.K_e:
                        new_rotation = (self.piece_rotation + 1) % len(self.tetrominos[self.current_piece])
                        if self.is_valid_position(self.current_piece, self.piece_x, 
                                                  self.piece_y, new_rotation):
                            self.piece_rotation = new_rotation
                            self.play_beep(700, 60)
                    
                    elif event.key == pygame.K_q:
                        new_rotation = (self.piece_rotation - 1) % len(self.tetrominos[self.current_piece])
                        if self.is_valid_position(self.current_piece, self.piece_x, 
                                                  self.piece_y, new_rotation):
                            self.piece_rotation = new_rotation
                            self.play_beep(700, 60)
                    
                    elif event.key == pygame.K_RETURN:
                        while self.is_valid_position(self.current_piece, self.piece_x, 
                                                     self.piece_y + 1, self.piece_rotation):
                            self.piece_y += 1
                            self.score += 2
                        self.play_beep(300, 80)
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_over or self.paused:
            return
        
        self.handle_continuous_input()
        
        current_time = pygame.time.get_ticks()
        if current_time - self.fall_time > self.fall_speed:
            if self.is_valid_position(self.current_piece, self.piece_x, 
                                       self.piece_y + 1, self.piece_rotation):
                self.piece_y += 1
            else:
                self.place_piece()
            
            self.fall_time = current_time
        
        if self.line_clear_animation:
            self.line_clear_animation = []
        
        self.animation_time += 1
    
    def draw_rounded_rect(self, surface, color, rect, radius=8):
        """Dibujar rectángulo con bordes redondeados"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_shadow_rect(self, surface, rect, radius=8, shadow_offset=2):
        """Dibujar rectángulo con sombra sutil"""
        shadow_rect = rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 20), (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
    
    def draw_game_area(self):
        """Dibujar área de juego moderna"""
        # Fondo general
        self.screen.fill(self.colors['bg'])
        
        # Área del juego con sombra
        game_rect = pygame.Rect(20, 20, self.grid_width * self.cell_size, 
                               self.grid_height * self.cell_size)
        
        # Sombra
        self.draw_shadow_rect(self.screen, game_rect)
        
        # Fondo del área de juego
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], game_rect)
        
        # Borde sutil
        pygame.draw.rect(self.screen, self.colors['border'], game_rect, 1, border_radius=8)
        
        return game_rect
    
    def draw_placed_pieces(self, game_rect):
        """Dibujar piezas colocadas con estilo moderno"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] is not None:
                    color = self.colors[self.grid[y][x]]
                    
                    # Posición con padding
                    cell_x = game_rect.x + x * self.cell_size + 2
                    cell_y = game_rect.y + y * self.cell_size + 2
                    cell_size = self.cell_size - 4
                    
                    cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                    
                    # Sombra sutil
                    self.draw_shadow_rect(self.screen, cell_rect, radius=6, shadow_offset=1)
                    
                    # Celda principal
                    self.draw_rounded_rect(self.screen, color, cell_rect, 6)
                    
                    # Highlight superior para efecto 3D sutil
                    highlight_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size // 3)
                    highlight_color = tuple(min(255, c + 30) for c in color)
                    self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 6)
    
    def draw_current_piece(self, game_rect):
        """Dibujar pieza actual con ghost"""
        if self.game_over:
            return
            
        shape = self.get_piece_shape(self.current_piece, self.piece_rotation)
        color = self.colors[self.current_piece]
        
        # Ghost piece (sombra)
        ghost_y = self.piece_y
        while self.is_valid_position(self.current_piece, self.piece_x, 
                                   ghost_y + 1, self.piece_rotation):
            ghost_y += 1
        
        # Dibujar ghost
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    x = self.piece_x + col_i
                    y = ghost_y + row_i
                    
                    if 0 <= x < self.grid_width and y >= 0:
                        cell_x = game_rect.x + x * self.cell_size + 2
                        cell_y = game_rect.y + y * self.cell_size + 2
                        cell_size = self.cell_size - 4
                        
                        cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                        ghost_color = (*color, 60)  # Transparencia
                        
                        ghost_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                        pygame.draw.rect(ghost_surface, ghost_color, (0, 0, cell_size, cell_size), 
                                         border_radius=6)
                        pygame.draw.rect(ghost_surface, (*color, 120), (0, 0, cell_size, cell_size), 
                                         2, border_radius=6)
                        self.screen.blit(ghost_surface, (cell_x, cell_y))
        
        # Pieza actual
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
                        
                        # Sombra
                        self.draw_shadow_rect(self.screen, cell_rect, radius=6, shadow_offset=1)
                        
                        # Celda principal
                        self.draw_rounded_rect(self.screen, color, cell_rect, 6)
                        
                        # Highlight
                        highlight_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size // 3)
                        highlight_color = tuple(min(255, c + 40) for c in color)
                        self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 6)
    
    def draw_sidebar(self):
        """Dibujar barra lateral moderna"""
        sidebar_x = self.game_width + 20
        
        # Título
        title_text = self.fonts['title'].render("TETRIS", True, self.colors['text_primary'])
        self.screen.blit(title_text, (sidebar_x, 30))
        
        # Subtítulo
        subtitle_text = self.fonts['small'].render("MODERN", True, self.colors['text_secondary'])
        self.screen.blit(subtitle_text, (sidebar_x, 70))
        
        # Next piece card
        next_card = pygame.Rect(sidebar_x, 100, 200, 120)
        self.draw_shadow_rect(self.screen, next_card)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], next_card)
        pygame.draw.rect(self.screen, self.colors['border'], next_card, 1, border_radius=8)
        
        # Next piece título
        next_text = self.fonts['medium'].render("NEXT", True, self.colors['text_secondary'])
        self.screen.blit(next_text, (sidebar_x + 15, 115))
        
        # Dibujar next piece
        shape = self.get_piece_shape(self.next_piece, 0)
        color = self.colors[self.next_piece]
        
        piece_width = len(shape[0])
        piece_height = len(shape)
        start_x = sidebar_x + 100 - (piece_width * 8)
        start_y = 150
        
        for row_i, row in enumerate(shape):
            for col_i, cell in enumerate(row):
                if cell == '#':
                    x = start_x + col_i * 16
                    y = start_y + row_i * 16
                    
                    mini_rect = pygame.Rect(x, y, 14, 14)
                    self.draw_rounded_rect(self.screen, color, mini_rect, 3)
        
        # Stats card
        stats_card = pygame.Rect(sidebar_x, 240, 200, 200)
        self.draw_shadow_rect(self.screen, stats_card)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], stats_card)
        pygame.draw.rect(self.screen, self.colors['border'], stats_card, 1, border_radius=8)
        
        # Stats
        stats_y = 260
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
        controls_card = pygame.Rect(sidebar_x, 460, 200, 160)
        self.draw_shadow_rect(self.screen, controls_card)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], controls_card)
        pygame.draw.rect(self.screen, self.colors['border'], controls_card, 1, border_radius=8)
        
        controls_y = 480
        controls = [
            "A/D  Move",
            "S  Soft drop",
            "W/E  Rotate",
            "Enter  Hard drop",
            "Space  Pause",
            f"T  Theme ({('Dark' if self.dark_mode else 'Light')})"
        ]
        
        for i, control in enumerate(controls):
            text = self.fonts['tiny'].render(control, True, self.colors['text_secondary'])
            self.screen.blit(text, (sidebar_x + 15, controls_y + i * 18))
    
    def draw_overlay(self, title, subtitle="", action_text=""):
        """Dibujar overlay moderno"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        self.screen.blit(overlay, (0, 0))
        
        # Card principal
        card_width = 400
        card_height = 200
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_shadow_rect(self.screen, card_rect, shadow_offset=8)
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
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            
            game_rect = self.draw_game_area()
            self.draw_placed_pieces(game_rect)
            self.draw_current_piece(game_rect)
            self.draw_sidebar()
            
            if self.paused and not self.game_over:
                self.draw_overlay("PAUSED", "Game is on hold", "Press SPACE to resume")
            elif self.game_over:
                self.draw_overlay("GAME OVER", f"Score: {self.score}", "Press SPACE to restart")

            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisModern()
    game.run()