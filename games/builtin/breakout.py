#!/usr/bin/env python3
"""
Breakout Modern - Clásico juego de romper ladrillos con diseño moderno
Controles: A/D para mover, W para disparar/lanzar, Espacio para pausa
"""

import pygame
import random
import math
import sys

class BreakoutModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración de pantalla
        self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Breakout Modern")
        
        # Sistema de temas
        self.dark_mode = False
        self.themes = {
            'light': {
                'bg': (248, 249, 250),
                'card_bg': (255, 255, 255),
                'grid': (233, 236, 239),
                'border': (206, 212, 218),
                'text_primary': (33, 37, 41),
                'text_secondary': (108, 117, 125),
                'accent': (0, 123, 255),
                'success': (40, 167, 69),
                'warning': (255, 193, 7),
                'danger': (220, 53, 69),
                'shadow': (0, 0, 0, 20),
                'overlay': (255, 255, 255, 200),
                'paddle': (0, 123, 255),
                'ball': (33, 37, 41),
                'wall': (206, 212, 218),
                # Colores de ladrillos modernos
                'brick_colors': [
                    (220, 53, 69),    # Rojo material
                    (255, 152, 0),    # Naranja material
                    (255, 193, 7),    # Amarillo material
                    (40, 167, 69),    # Verde material
                    (23, 162, 184),   # Cyan material
                    (0, 123, 255),    # Azul material
                ]
            },
            'dark': {
                'bg': (18, 18, 18),
                'card_bg': (33, 37, 41),
                'grid': (52, 58, 64),
                'border': (73, 80, 87),
                'text_primary': (248, 249, 250),
                'text_secondary': (173, 181, 189),
                'accent': (13, 202, 240),
                'success': (32, 201, 151),
                'warning': (255, 212, 59),
                'danger': (255, 99, 132),
                'shadow': (0, 0, 0, 40),
                'overlay': (33, 37, 41, 220),
                'paddle': (13, 202, 240),
                'ball': (248, 249, 250),
                'wall': (73, 80, 87),
                # Colores de ladrillos más vibrantes para modo oscuro
                'brick_colors': [
                    (255, 99, 132),   # Rojo más brillante
                    (255, 167, 38),   # Naranja más brillante
                    (255, 212, 59),   # Amarillo más brillante
                    (32, 201, 151),   # Verde más brillante
                    (58, 191, 248),   # Cyan más brillante
                    (79, 172, 254),   # Azul más brillante
                ]
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
        self.game_state = "menu"  # menu, playing, paused, game_over, level_complete
        self.reset_game()
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Efectos
        self.particles = []
        self.screen_shake = 0
        self.powerups = []
        self.animation_time = 0
        
        # Control de teclas repetidas
        self.key_repeat_timer = {}
        self.key_repeat_delay = 100
        self.key_repeat_interval = 50
        
    def reset_game(self):
        """Reiniciar estado del juego"""
        # Paleta
        self.paddle = {
            'x': self.width // 2 - 75,
            'y': self.height - 80,
            'width': 150,
            'height': 20,
            'speed': 10,
            'sticky': False,
            'size_modifier': 1.0
        }
        
        # Pelota
        self.balls = [{
            'x': self.width // 2,
            'y': self.height - 110,
            'radius': 10,
            'speed_x': 0,
            'speed_y': 0,
            'stuck_to_paddle': True,
            'trail': []
        }]
        
        # Ladrillos
        self.bricks = []
        self.create_bricks()
        
        # Puntuación y estado
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = self.load_high_score()
        
        # Power-ups activos
        self.active_powerups = {
            'multi_ball': 0,
            'big_paddle': 0,
            'sticky_paddle': 0,
            'laser': 0
        }
        
        # Efectos
        self.brick_break_combo = 0
        self.last_brick_break = 0
        
    def load_high_score(self):
        """Cargar puntuación máxima"""
        try:
            with open("games/builtin/breakout_highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        """Guardar puntuación máxima"""
        try:
            with open("games/builtin/breakout_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def toggle_theme(self):
        """Alternar entre modo claro y oscuro"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_sound('menu')
    
    def create_bricks(self):
        """Crear ladrillos con diseño moderno"""
        self.bricks = []
        brick_width = 85
        brick_height = 30
        margin = 8
        rows = 6
        cols = 9
        
        # Calcular posición inicial centrada
        total_width = cols * brick_width + (cols - 1) * margin
        start_x = (self.width - total_width) // 2
        start_y = 120
        
        points_per_row = [50, 40, 30, 20, 15, 10]
        
        for row in range(rows):
            for col in range(cols):
                brick = {
                    'x': start_x + col * (brick_width + margin),
                    'y': start_y + row * (brick_height + margin),
                    'width': brick_width,
                    'height': brick_height,
                    'color': self.colors['brick_colors'][row],
                    'points': points_per_row[row],
                    'hits_required': 1 if row >= 3 else 2,  # Filas superiores más resistentes
                    'current_hits': 0,
                    'powerup': random.choice([None, None, None, None, 'multi_ball', 'big_paddle', 'sticky']) if random.random() < 0.12 else None,
                    'animation_offset': random.uniform(0, 360)  # Para animaciones
                }
                self.bricks.append(brick)
    
    def play_sound(self, sound_type):
        """Reproducir sonidos modernos del juego"""
        frequencies = {
            'paddle_hit': 400,
            'brick_break': 600,
            'wall_hit': 300,
            'powerup': 800,
            'life_lost': 150,
            'level_complete': 1000,
            'menu': 500
        }
        
        try:
            frequency = frequencies.get(sound_type, 500)
            duration = 80 if sound_type != 'life_lost' else 300
            
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
    
    def handle_continuous_input(self):
        """Manejar input continuo para movimiento suave"""
        if self.game_state != "playing":
            return
            
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        
        # Movimiento izquierda con A
        if keys[pygame.K_a]:
            if (pygame.K_a not in self.key_repeat_timer or 
                current_time - self.key_repeat_timer[pygame.K_a] > 16):  # ~60fps
                
                if self.paddle['x'] > 0:
                    self.paddle['x'] -= self.paddle['speed']
                    self.paddle['x'] = max(0, self.paddle['x'])
                    self.key_repeat_timer[pygame.K_a] = current_time
        else:
            self.key_repeat_timer.pop(pygame.K_a, None)
            
        # Movimiento derecha con D
        if keys[pygame.K_d]:
            if (pygame.K_d not in self.key_repeat_timer or 
                current_time - self.key_repeat_timer[pygame.K_d] > 16):
                
                if self.paddle['x'] < self.width - self.paddle['width']:
                    self.paddle['x'] += self.paddle['speed']
                    self.paddle['x'] = min(self.width - self.paddle['width'], self.paddle['x'])
                    self.key_repeat_timer[pygame.K_d] = current_time
        else:
            self.key_repeat_timer.pop(pygame.K_d, None)
    
    def handle_events(self):
        """Manejar eventos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "menu":
                        return False
                    else:
                        self.game_state = "menu"
                        self.play_sound('menu')
                
                elif event.key == pygame.K_t:
                    # Toggle tema
                    self.toggle_theme()
                
                elif event.key == pygame.K_r and self.game_state in ["game_over", "level_complete"]:
                    # Reiniciar juego
                    self.reset_game()
                    self.game_state = "playing"
                    self.play_sound('menu')
                
                elif event.key == pygame.K_RETURN and self.game_state == "menu":
                    # Comenzar juego
                    self.game_state = "playing"
                    self.reset_game()
                    self.play_sound('menu')
                
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                        self.play_sound('menu')
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                        self.play_sound('menu')
                    elif self.game_state in ["game_over", "level_complete"]:
                        self.game_state = "menu"
                        self.play_sound('menu')
                
                elif event.key == pygame.K_w and self.game_state == "playing":
                    # Lanzar pelota o disparo
                    launched = False
                    for ball in self.balls:
                        if ball['stuck_to_paddle']:
                            ball['stuck_to_paddle'] = False
                            # Ángulo aleatorio hacia arriba
                            angle = random.uniform(-math.pi/4, math.pi/4)
                            speed = 8
                            ball['speed_x'] = speed * math.sin(angle)
                            ball['speed_y'] = -speed * math.cos(angle)
                            launched = True
                    
                    if launched:
                        self.play_sound('paddle_hit')
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_state != "playing":
            return
        
        # Input continuo
        self.handle_continuous_input()
        
        # Actualizar pelotas
        self.update_balls()
        
        # Actualizar power-ups
        self.update_powerups()
        
        # Actualizar efectos
        self.update_effects()
        
        # Verificar condiciones del juego
        self.check_game_conditions()
        
        # Actualizar tiempo de animación
        self.animation_time += 1
    
    def update_balls(self):
        """Actualizar movimiento de pelotas"""
        for ball in self.balls[:]:
            if ball['stuck_to_paddle']:
                # Pelota pegada a la paleta
                ball['x'] = self.paddle['x'] + self.paddle['width'] // 2
                ball['y'] = self.paddle['y'] - ball['radius'] - 5
            else:
                # Actualizar trail
                ball['trail'].append((ball['x'], ball['y']))
                if len(ball['trail']) > 12:
                    ball['trail'].pop(0)
                
                # Mover pelota
                ball['x'] += ball['speed_x']
                ball['y'] += ball['speed_y']
                
                # Colisión con paredes laterales
                if ball['x'] - ball['radius'] <= 0 or ball['x'] + ball['radius'] >= self.width:
                    ball['speed_x'] = -ball['speed_x']
                    ball['x'] = max(ball['radius'], min(self.width - ball['radius'], ball['x']))
                    self.play_sound('wall_hit')
                    self.screen_shake = 3
                
                # Colisión con pared superior
                if ball['y'] - ball['radius'] <= 0:
                    ball['speed_y'] = -ball['speed_y']
                    ball['y'] = ball['radius']
                    self.play_sound('wall_hit')
                    self.screen_shake = 3
                
                # Colisión con paleta
                if self.check_paddle_collision(ball):
                    self.handle_paddle_collision(ball)
                
                # Colisión con ladrillos
                self.check_brick_collisions(ball)
                
                # Pelota perdida
                if ball['y'] > self.height:
                    self.balls.remove(ball)
    
    def check_paddle_collision(self, ball):
        """Verificar colisión con paleta"""
        return (ball['y'] + ball['radius'] >= self.paddle['y'] and
                ball['y'] - ball['radius'] <= self.paddle['y'] + self.paddle['height'] and
                ball['x'] >= self.paddle['x'] - ball['radius'] and
                ball['x'] <= self.paddle['x'] + self.paddle['width'] + ball['radius'])
    
    def handle_paddle_collision(self, ball):
        """Manejar colisión con paleta con física mejorada"""
        # Calcular punto de impacto en la paleta (0.0 = izquierda, 1.0 = derecha)
        hit_point = (ball['x'] - self.paddle['x']) / self.paddle['width']
        hit_point = max(0.0, min(1.0, hit_point))
        
        # Calcular ángulo de rebote basado en punto de impacto
        angle = (hit_point - 0.5) * math.pi * 0.7  # Máximo 63 grados hacia los lados
        
        speed = math.sqrt(ball['speed_x']**2 + ball['speed_y']**2)
        speed = min(speed * 1.02, 12)  # Incrementar ligeramente la velocidad, con límite
        
        ball['speed_x'] = speed * math.sin(angle)
        ball['speed_y'] = -abs(speed * math.cos(angle))  # Siempre hacia arriba
        
        # Asegurar que la pelota no se quede atrapada
        ball['y'] = self.paddle['y'] - ball['radius'] - 1
        
        # Efecto sticky paddle
        if self.paddle['sticky'] and not ball['stuck_to_paddle']:
            ball['stuck_to_paddle'] = True
            ball['speed_x'] = 0
            ball['speed_y'] = 0
        
        self.play_sound('paddle_hit')
        self.screen_shake = 4
    
    def check_brick_collisions(self, ball):
        """Verificar colisiones con ladrillos"""
        ball_rect = pygame.Rect(ball['x'] - ball['radius'], ball['y'] - ball['radius'],
                               ball['radius'] * 2, ball['radius'] * 2)
        
        for brick in self.bricks[:]:
            brick_rect = pygame.Rect(brick['x'], brick['y'], brick['width'], brick['height'])
            
            if ball_rect.colliderect(brick_rect):
                # Determinar lado de colisión más preciso
                ball_center_x = ball['x']
                ball_center_y = ball['y']
                brick_center_x = brick['x'] + brick['width'] // 2
                brick_center_y = brick['y'] + brick['height'] // 2
                
                # Calcular diferencias
                dx = ball_center_x - brick_center_x
                dy = ball_center_y - brick_center_y
                
                # Determinar si rebota horizontal o verticalmente
                if abs(dx / brick['width']) > abs(dy / brick['height']):
                    ball['speed_x'] = -ball['speed_x']
                else:
                    ball['speed_y'] = -ball['speed_y']
                
                # Dañar ladrillo
                brick['current_hits'] += 1
                
                if brick['current_hits'] >= brick['hits_required']:
                    # Destruir ladrillo
                    self.score += brick['points']
                    
                    # Sistema de combo
                    current_time = pygame.time.get_ticks()
                    if current_time - self.last_brick_break < 1500:  # 1.5 segundos
                        self.brick_break_combo += 1
                        combo_bonus = brick['points'] * (self.brick_break_combo // 3 + 1)
                        self.score += combo_bonus
                    else:
                        self.brick_break_combo = 0
                    self.last_brick_break = current_time
                    
                    # Crear power-up si el ladrillo lo tiene
                    if brick['powerup']:
                        self.create_powerup(brick['x'] + brick['width']//2, 
                                          brick['y'] + brick['height']//2, 
                                          brick['powerup'])
                    
                    # Efectos visuales
                    self.create_brick_particles(brick)
                    
                    # Remover ladrillo
                    self.bricks.remove(brick)
                    
                    self.play_sound('brick_break')
                    self.screen_shake = 6
                else:
                    # Ladrillo dañado pero no destruido - cambiar color
                    original_color = brick['color']
                    brick['color'] = tuple(max(50, c - 80) for c in original_color)
                    self.play_sound('wall_hit')
                    self.screen_shake = 3
                
                break  # Solo una colisión por frame
    
    def create_powerup(self, x, y, powerup_type):
        """Crear power-up"""
        powerup = {
            'x': x,
            'y': y,
            'type': powerup_type,
            'speed': 3,
            'animation': 0,
            'pulse': 0
        }
        self.powerups.append(powerup)
    
    def update_powerups(self):
        """Actualizar power-ups"""
        # Mover power-ups cayendo
        for powerup in self.powerups[:]:
            powerup['y'] += powerup['speed']
            powerup['animation'] = (powerup['animation'] + 1) % 60
            powerup['pulse'] = (powerup['pulse'] + 1) % 40
            
            # Verificar colisión con paleta
            if (powerup['y'] + 15 >= self.paddle['y'] and
                powerup['x'] >= self.paddle['x'] - 15 and
                powerup['x'] <= self.paddle['x'] + self.paddle['width'] + 15):
                
                self.activate_powerup(powerup['type'])
                self.powerups.remove(powerup)
                continue
            
            # Remover si sale de pantalla
            if powerup['y'] > self.height:
                self.powerups.remove(powerup)
        
        # Reducir duración de power-ups activos
        for powerup_type in self.active_powerups:
            if self.active_powerups[powerup_type] > 0:
                self.active_powerups[powerup_type] -= 1
                
                # Desactivar cuando expire
                if self.active_powerups[powerup_type] == 0:
                    self.deactivate_powerup(powerup_type)
    
    def activate_powerup(self, powerup_type):
        """Activar power-up"""
        self.play_sound('powerup')
        
        if powerup_type == 'multi_ball':
            # Duplicar pelotas
            new_balls = []
            for ball in self.balls:
                if not ball['stuck_to_paddle']:
                    for i in range(2):
                        new_ball = ball.copy()
                        new_ball['trail'] = []
                        angle = random.uniform(-math.pi/3, math.pi/3)
                        speed = math.sqrt(ball['speed_x']**2 + ball['speed_y']**2)
                        new_ball['speed_x'] = speed * math.sin(angle)
                        new_ball['speed_y'] = speed * math.cos(angle) * (-1 if ball['speed_y'] < 0 else 1)
                        new_balls.append(new_ball)
            self.balls.extend(new_balls)
            
        elif powerup_type == 'big_paddle':
            self.paddle['width'] = int(150 * 1.6)
            self.active_powerups['big_paddle'] = 900  # 15 segundos
            
        elif powerup_type == 'sticky':
            self.paddle['sticky'] = True
            self.active_powerups['sticky_paddle'] = 900
    
    def deactivate_powerup(self, powerup_type):
        """Desactivar power-up"""
        if powerup_type == 'big_paddle':
            self.paddle['width'] = 150
        elif powerup_type == 'sticky_paddle':
            self.paddle['sticky'] = False
    
    def create_brick_particles(self, brick):
        """Crear partículas al romper ladrillo"""
        for _ in range(12):
            particle = {
                'x': brick['x'] + brick['width'] // 2,
                'y': brick['y'] + brick['height'] // 2,
                'dx': random.uniform(-6, 6),
                'dy': random.uniform(-6, 6),
                'life': 40,
                'max_life': 40,
                'color': brick['color'],
                'size': random.uniform(2, 5)
            }
            self.particles.append(particle)
    
    def update_effects(self):
        """Actualizar efectos visuales"""
        # Actualizar partículas
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += 0.3  # Gravedad
            particle['life'] -= 1
            particle['size'] *= 0.98  # Reducir tamaño
            
            if particle['life'] <= 0 or particle['size'] < 0.5:
                self.particles.remove(particle)
        
        # Reducir screen shake
        self.screen_shake = max(0, self.screen_shake - 1)
    
    def check_game_conditions(self):
        """Verificar condiciones del juego"""
        # Sin pelotas = vida perdida
        if not self.balls:
            self.lives -= 1
            self.play_sound('life_lost')
            
            if self.lives <= 0:
                self.game_state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
            else:
                # Resetear pelota
                self.balls = [{
                    'x': self.width // 2,
                    'y': self.height - 110,
                    'radius': 10,
                    'speed_x': 0,
                    'speed_y': 0,
                    'stuck_to_paddle': True,
                    'trail': []
                }]
        
        # Sin ladrillos = nivel completado
        if not self.bricks:
            self.level += 1
            self.score += 2000  # Bonus por nivel
            self.play_sound('level_complete')
            self.game_state = "level_complete"
    
    def draw_rounded_rect(self, surface, color, rect, radius=8):
        """Dibujar rectángulo con bordes redondeados"""
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_shadow_rect(self, surface, rect, radius=8, shadow_offset=3):
        """Dibujar rectángulo con sombra sutil"""
        shadow_rect = rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, self.colors['shadow'], (0, 0, rect.width, rect.height), border_radius=radius)
        surface.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
    
    def draw_background(self):
        """Dibujar fondo moderno"""
        self.screen.fill(self.colors['bg'])
        
        # Grid sutil
        for x in range(0, self.width, 50):
            pygame.draw.line(self.screen, self.colors['grid'], (x, 0), (x, self.height), 1)
        for y in range(0, self.height, 50):
            pygame.draw.line(self.screen, self.colors['grid'], (0, y), (self.width, y), 1)
    
    def draw_paddle(self):
        """Dibujar paleta moderna"""
        # Aplicar screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        x = self.paddle['x'] + shake_x
        y = self.paddle['y'] + shake_y
        
        paddle_rect = pygame.Rect(x, y, self.paddle['width'], self.paddle['height'])
        
        # Sombra
        self.draw_shadow_rect(self.screen, paddle_rect, radius=10, shadow_offset=2)
        
        # Color según power-ups activos
        color = self.colors['paddle']
        if self.active_powerups['big_paddle'] > 0:
            color = self.colors['warning']
        elif self.active_powerups['sticky_paddle'] > 0:
            color = self.colors['danger']
        
        # Dibujar paleta
        self.draw_rounded_rect(self.screen, color, paddle_rect, 10)
        
        # Borde
        pygame.draw.rect(self.screen, self.colors['border'], paddle_rect, 2, border_radius=10)
        
        # Highlight superior
        highlight_rect = pygame.Rect(x, y, self.paddle['width'], self.paddle['height'] // 3)
        highlight_color = tuple(min(255, c + 30) for c in color)
        self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 10)
    
    def draw_balls(self):
        """Dibujar pelotas modernas"""
        for ball in self.balls:
            # Dibujar trail moderno
            for i, (tx, ty) in enumerate(ball['trail']):
                if i > 0:
                    alpha = (i / len(ball['trail'])) * 0.6
                    size = int(ball['radius'] * alpha)
                    if size > 0:
                        trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                        color_with_alpha = (*self.colors['ball'], int(255 * alpha))
                        pygame.draw.circle(trail_surface, color_with_alpha, (size, size), size)
                        self.screen.blit(trail_surface, (tx - size, ty - size))
            
            # Sombra de la pelota
            shadow_x = int(ball['x'] + 2)
            shadow_y = int(ball['y'] + 2)
            shadow_surface = pygame.Surface((ball['radius'] * 2, ball['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, self.colors['shadow'], (ball['radius'], ball['radius']), ball['radius'])
            self.screen.blit(shadow_surface, (shadow_x - ball['radius'], shadow_y - ball['radius']))
            
            # Dibujar pelota principal
            pygame.draw.circle(self.screen, self.colors['ball'], 
                             (int(ball['x']), int(ball['y'])), ball['radius'])
            
            # Borde
            pygame.draw.circle(self.screen, self.colors['border'], 
                             (int(ball['x']), int(ball['y'])), ball['radius'], 2)
            
            # Highlight para efecto 3D
            highlight_x = int(ball['x'] - ball['radius'] // 3)
            highlight_y = int(ball['y'] - ball['radius'] // 3)
            pygame.draw.circle(self.screen, self.colors['text_primary'], 
                             (highlight_x, highlight_y), max(1, ball['radius'] // 4))
    
    def draw_bricks(self):
        """Dibujar ladrillos modernos"""
        for brick in self.bricks:
            # Animación sutil de respiración
            pulse = math.sin((self.animation_time + brick['animation_offset']) * 0.05) * 0.02 + 1
            
            # Calcular posición con animación
            brick_rect = pygame.Rect(
                brick['x'], 
                brick['y'], 
                int(brick['width'] * pulse), 
                int(brick['height'] * pulse)
            )
            
            # Sombra
            self.draw_shadow_rect(self.screen, brick_rect, radius=8, shadow_offset=2)
            
            # Color base
            color = brick['color']
            
            # Dibujar ladrillo principal
            self.draw_rounded_rect(self.screen, color, brick_rect, 8)
            
            # Borde
            pygame.draw.rect(self.screen, self.colors['border'], brick_rect, 1, border_radius=8)
            
            # Highlight superior para efecto 3D
            highlight_rect = pygame.Rect(brick_rect.x, brick_rect.y, brick_rect.width, brick_rect.height // 3)
            highlight_color = tuple(min(255, c + 40) for c in color)
            self.draw_rounded_rect(self.screen, highlight_color, highlight_rect, 8)
            
            # Indicador de power-up
            if brick['powerup']:
                center_x = brick_rect.centerx
                center_y = brick_rect.centery
                
                # Animación de pulso para power-ups
                powerup_pulse = math.sin(self.animation_time * 0.2) * 0.3 + 0.7
                powerup_size = int(6 * powerup_pulse)
                
                pygame.draw.circle(self.screen, self.colors['accent'], (center_x, center_y), powerup_size + 2)
                pygame.draw.circle(self.screen, self.colors['text_primary'], (center_x, center_y), powerup_size)
            
            # Indicador de daño (cracks)
            if brick['current_hits'] > 0:
                crack_surface = pygame.Surface((brick_rect.width, brick_rect.height), pygame.SRCALPHA)
                crack_color = (*self.colors['text_secondary'], 120)
                
                # Líneas de crack
                pygame.draw.line(crack_surface, crack_color,
                               (brick_rect.width * 0.2, brick_rect.height * 0.3),
                               (brick_rect.width * 0.8, brick_rect.height * 0.7), 2)
                pygame.draw.line(crack_surface, crack_color,
                               (brick_rect.width * 0.3, brick_rect.height * 0.7),
                               (brick_rect.width * 0.7, brick_rect.height * 0.3), 2)
                
                self.screen.blit(crack_surface, (brick_rect.x, brick_rect.y))
    
    def draw_powerups(self):
        """Dibujar power-ups cayendo modernos"""
        for powerup in self.powerups:
            # Colores según tipo
            colors = {
                'multi_ball': self.colors['danger'],
                'big_paddle': self.colors['success'],
                'sticky': self.colors['warning']
            }
            color = colors.get(powerup['type'], self.colors['accent'])
            
            # Animación de rotación y pulso
            rotation = powerup['animation'] * 6
            pulse = math.sin(powerup['pulse'] * 0.3) * 0.2 + 0.8
            size = int(12 * pulse)
            
            # Sombra
            shadow_rect = pygame.Rect(powerup['x'] - size + 2, powerup['y'] - size + 2, size * 2, size * 2)
            shadow_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, self.colors['shadow'], (size, size), size)
            self.screen.blit(shadow_surface, (shadow_rect.x, shadow_rect.y))
            
            # Power-up principal
            pygame.draw.circle(self.screen, color, (int(powerup['x']), int(powerup['y'])), size)
            pygame.draw.circle(self.screen, self.colors['text_primary'], (int(powerup['x']), int(powerup['y'])), size, 2)
            
            # Ícono/letra en el centro
            icon_text = {
                'multi_ball': 'M',
                'big_paddle': 'B',
                'sticky': 'S'
            }
            icon = icon_text.get(powerup['type'], '?')
            
            text_surface = self.fonts['small'].render(icon, True, self.colors['text_primary'])
            text_rect = text_surface.get_rect(center=(powerup['x'], powerup['y']))
            self.screen.blit(text_surface, text_rect)
    
    def draw_particles(self):
        """Dibujar partículas modernas"""
        for particle in self.particles:
            alpha = particle['life'] / particle['max_life']
            size = max(0.5, particle['size'] * alpha)
            
            if size > 0.5:
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                color_with_alpha = (*particle['color'], int(255 * alpha))
                pygame.draw.circle(particle_surface, color_with_alpha, (size, size), size)
                self.screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
    
    def draw_hud(self):
        """Dibujar HUD moderno"""
        # Card principal para estadísticas
        hud_card = pygame.Rect(20, 20, 350, 80)
        self.draw_shadow_rect(self.screen, hud_card)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], hud_card)
        pygame.draw.rect(self.screen, self.colors['border'], hud_card, 1, border_radius=8)
        
        # Estadísticas principales
        stats = [
            ("SCORE", f"{self.score:,}", self.colors['accent']),
            ("HIGH", f"{self.high_score:,}", self.colors['success']),
            ("LEVEL", str(self.level), self.colors['warning']),
            ("LIVES", str(self.lives), self.colors['danger'])
        ]
        
        for i, (label, value, color) in enumerate(stats):
            x = 35 + i * 80
            
            # Label
            label_text = self.fonts['tiny'].render(label, True, self.colors['text_secondary'])
            self.screen.blit(label_text, (x, 30))
            
            # Valor
            value_text = self.fonts['medium'].render(value, True, color)
            self.screen.blit(value_text, (x, 45))
        
        # Power-ups activos
        if any(self.active_powerups[key] > 0 for key in self.active_powerups):
            powerup_card = pygame.Rect(20, 120, 200, 60)
            self.draw_shadow_rect(self.screen, powerup_card)
            self.draw_rounded_rect(self.screen, self.colors['card_bg'], powerup_card)
            pygame.draw.rect(self.screen, self.colors['border'], powerup_card, 1, border_radius=8)
            
            title_text = self.fonts['tiny'].render("ACTIVE POWERS", True, self.colors['text_secondary'])
            self.screen.blit(title_text, (30, 130))
            
            powerup_y = 145
            if self.active_powerups['big_paddle'] > 0:
                time_left = self.active_powerups['big_paddle'] // 60
                text = self.fonts['tiny'].render(f"Big Paddle ({time_left}s)", True, self.colors['success'])
                self.screen.blit(text, (30, powerup_y))
                powerup_y += 12
            
            if self.active_powerups['sticky_paddle'] > 0:
                time_left = self.active_powerups['sticky_paddle'] // 60
                text = self.fonts['tiny'].render(f"Sticky ({time_left}s)", True, self.colors['warning'])
                self.screen.blit(text, (30, powerup_y))
        
        # Combo
        if self.brick_break_combo > 2:
            combo_text = f"COMBO x{self.brick_break_combo}!"
            text = self.fonts['large'].render(combo_text, True, self.colors['accent'])
            x = (self.width - text.get_width()) // 2
            
            # Efecto de pulso
            pulse = math.sin(self.animation_time * 0.3) * 0.1 + 0.9
            text = pygame.transform.scale(text, (int(text.get_width() * pulse), int(text.get_height() * pulse)))
            self.screen.blit(text, (x, 200))
    
    def draw_menu(self):
        """Dibujar menú principal moderno"""
        self.draw_background()
        
        # Card principal del menú
        menu_card = pygame.Rect(self.width // 2 - 300, 150, 600, 400)
        self.draw_shadow_rect(self.screen, menu_card, shadow_offset=8)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], menu_card, 16)
        pygame.draw.rect(self.screen, self.colors['border'], menu_card, 2, border_radius=16)
        
        # Título
        title_text = self.fonts['title'].render("BREAKOUT", True, self.colors['text_primary'])
        title_x = menu_card.centerx - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, 180))
        
        # Subtítulo
        subtitle_text = self.fonts['medium'].render("MODERN EDITION", True, self.colors['accent'])
        subtitle_x = menu_card.centerx - subtitle_text.get_width() // 2
        self.screen.blit(subtitle_text, (subtitle_x, 220))
        
        # Descripción del juego
        description = "Break all the bricks to advance levels!"
        desc_text = self.fonts['small'].render(description, True, self.colors['text_secondary'])
        desc_x = menu_card.centerx - desc_text.get_width() // 2
        self.screen.blit(desc_text, (desc_x, 260))
        
        # Controles
        controls_y = 300
        controls = [
            "CONTROLS:",
            "A/D - Move paddle",
            "W - Launch ball",
            "Space - Pause game",
            "T - Toggle theme",
            "",
            "POWER-UPS:",
            "M - Multi Ball  •  B - Big Paddle  •  S - Sticky"
        ]
        
        for i, control in enumerate(controls):
            if control == "CONTROLS:" or control == "POWER-UPS:":
                color = self.colors['text_primary']
                font = self.fonts['small']
            elif control == "":
                continue
            else:
                color = self.colors['text_secondary']
                font = self.fonts['tiny']
            
            text = font.render(control, True, color)
            text_x = menu_card.centerx - text.get_width() // 2
            self.screen.blit(text, (text_x, controls_y + i * 18))
        
        # Botón de inicio (simulado)
        start_y = 480
        start_text = self.fonts['medium'].render("PRESS ENTER TO START", True, self.colors['accent'])
        start_x = menu_card.centerx - start_text.get_width() // 2
        
        # Efecto de pulso para el texto de inicio
        pulse = math.sin(self.animation_time * 0.1) * 0.1 + 0.9
        scaled_text = pygame.transform.scale(start_text, (int(start_text.get_width() * pulse), int(start_text.get_height() * pulse)))
        self.screen.blit(scaled_text, (start_x, start_y))
        
        # Tema actual
        theme_text = f"Current theme: {('Dark' if self.dark_mode else 'Light')}"
        theme_surface = self.fonts['tiny'].render(theme_text, True, self.colors['text_secondary'])
        self.screen.blit(theme_surface, (20, self.height - 30))
    
    def draw_overlay(self, title, subtitle="", action_text="", overlay_type="info"):
        """Dibujar overlay moderno"""
        # Overlay de fondo
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.colors['overlay'])
        self.screen.blit(overlay, (0, 0))
        
        # Card principal
        card_width = 500
        card_height = 250
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_shadow_rect(self.screen, card_rect, shadow_offset=10)
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], card_rect, 16)
        pygame.draw.rect(self.screen, self.colors['border'], card_rect, 2, border_radius=16)
        
        # Color del título según tipo
        title_colors = {
            'info': self.colors['text_primary'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'danger': self.colors['danger']
        }
        title_color = title_colors.get(overlay_type, self.colors['text_primary'])
        
        # Título
        title_text = self.fonts['title'].render(title, True, title_color)
        title_x = card_x + (card_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, card_y + 50))
        
        # Subtítulo
        if subtitle:
            subtitle_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            subtitle_x = card_x + (card_width - subtitle_text.get_width()) // 2
            self.screen.blit(subtitle_text, (subtitle_x, card_y + 100))
        
        # Texto de acción
        if action_text:
            action_font = self.fonts['medium']
            action_text_render = action_font.render(action_text, True, self.colors['accent'])
            action_x = card_x + (card_width - action_text_render.get_width()) // 2
            action_y = card_y + (160 if subtitle else 140)
            
            # Efecto de pulso
            pulse = math.sin(self.animation_time * 0.15) * 0.05 + 0.95
            scaled_action = pygame.transform.scale(action_text_render, 
                                                 (int(action_text_render.get_width() * pulse), 
                                                  int(action_text_render.get_height() * pulse)))
            self.screen.blit(scaled_action, (action_x, action_y))
    
    def run(self):
        """Loop principal del juego"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar juego
            if self.game_state == "level_complete":
                # Auto-continuar después de mostrar nivel completado
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w] or keys[pygame.K_RETURN]:
                    self.create_bricks()  # Crear nuevos ladrillos
                    self.game_state = "playing"
                    # Resetear pelota para el nuevo nivel
                    self.balls = [{
                        'x': self.width // 2,
                        'y': self.height - 110,
                        'radius': 10,
                        'speed_x': 0,
                        'speed_y': 0,
                        'stuck_to_paddle': True,
                        'trail': []
                    }]
            else:
                self.update_game()
            
            # Dibujar según estado
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state in ["playing", "paused"]:
                self.draw_background()
                self.draw_bricks()
                self.draw_paddle()
                self.draw_balls()
                self.draw_powerups()
                self.draw_particles()
                self.draw_hud()
                
                if self.game_state == "paused":
                    self.draw_overlay("PAUSED", "Game is on hold", "Press SPACE to resume", "info")
            elif self.game_state == "game_over":
                self.draw_background()
                self.draw_bricks()
                self.draw_paddle()
                self.draw_balls()
                self.draw_powerups()
                self.draw_particles()
                self.draw_hud()
                
                high_score_text = f"Final Score: {self.score:,}"
                if self.score == self.high_score and self.score > 0:
                    self.draw_overlay("GAME OVER", "NEW HIGH SCORE!", "Press SPACE to continue", "success")
                else:
                    self.draw_overlay("GAME OVER", high_score_text, "Press SPACE to continue", "danger")
            elif self.game_state == "level_complete":
                self.draw_background()
                self.draw_hud()
                level_text = f"Level {self.level - 1} Complete!"
                score_text = f"Score: {self.score:,} (+2000 bonus)"
                self.draw_overlay("LEVEL COMPLETE", level_text, "Press W to continue", "success")
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    game = BreakoutModern()
    game.run()

if __name__ == "__main__":
    main()