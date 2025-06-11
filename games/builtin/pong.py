#!/usr/bin/env python3
"""
Pong Modern - Clásico juego de pong con diseño minimalista y moderno
Para usar dentro del Gaming OS, con alternancia de temas (claro/oscuro)
"""

import pygame
import random
import math
import sys

class PongModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración de pantalla
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong Modern")
        
        # Sistema de temas
        self.dark_mode = False
        self.themes = {
            'light': {
                'bg': (248, 249, 250),       # Gris muy claro
                'card_bg': (255, 255, 255),  # Blanco para tarjetas/elementos UI
                'grid_line': (233, 236, 239),# Gris claro para línea central
                'border': (206, 212, 218),   # Gris medio para bordes
                'text_primary': (33, 37, 41),# Casi negro para texto principal
                'text_secondary': (108, 117, 125), # Gris para texto secundario
                'accent_player1': (0, 123, 255), # Azul de acento (para P1)
                'accent_player2': (255, 87, 34), # Naranja de acento (para P2)
                'ball': (255, 193, 7),       # Amarillo/Ámbar para la pelota
                'overlay': (255, 255, 255, 200), # Overlay claro
                'shadow_light': (0, 0, 0, 20), # Sombra sutil
                'shadow_dark': (0, 0, 0, 40),  # Sombra más intensa
                'scanline_color': (0, 0, 0, 30) # Para el efecto de scanlines
            },
            'dark': {
                'bg': (18, 18, 18),          # Negro suave
                'card_bg': (33, 37, 41),     # Gris oscuro para tarjetas/elementos UI
                'grid_line': (52, 58, 64),   # Gris medio para línea central
                'border': (73, 80, 87),      # Gris claro para bordes
                'text_primary': (248, 249, 250), # Blanco para texto principal
                'text_secondary': (173, 181, 189), # Gris claro para texto secundario
                'accent_player1': (13, 202, 240), # Cyan (para P1)
                'accent_player2': (255, 127, 80), # Coral/Naranja (para P2)
                'ball': (255, 212, 59),      # Amarillo más brillante para la pelota
                'overlay': (33, 37, 41, 220), # Overlay oscuro
                'shadow_light': (0, 0, 0, 40), # Sombra sutil
                'shadow_dark': (0, 0, 0, 60),  # Sombra más intensa
                'scanline_color': (0, 0, 0, 40) # Para el efecto de scanlines
            }
        }
        
        # Colores actuales (empezar en modo claro)
        self.colors = self.themes['light'].copy()
        
        # Fuentes modernas
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 16)
        }
        
        # Estado del juego
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.reset_game()
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Efectos visuales
        self.screen_shake = 0
        
    def reset_game(self):
        """Reiniciar estado del juego"""
        # Paletas
        paddle_width = 15
        paddle_height = 80
        
        self.player1 = {
            'x': 50,
            'y': self.height // 2 - paddle_height // 2,
            'width': paddle_width,
            'height': paddle_height,
            'speed': 8,
            'score': 0
        }
        
        self.player2 = {
            'x': self.width - 50 - paddle_width,
            'y': self.height // 2 - paddle_height // 2,
            'width': paddle_width,
            'height': paddle_height,
            'speed': 8,
            'score': 0
        }
        
        # Pelota
        self.ball = {
            'x': self.width // 2,
            'y': self.height // 2,
            'size': 12,
            'speed_x': random.choice([-6, 6]),
            'speed_y': random.choice([-4, 4]),
            'max_speed': 15 # Increased max speed slightly for more dynamic play
        }
        
        # Configuración del juego
        self.winning_score = 5
        self.ai_enabled = True # AI enabled by default
        self.ai_difficulty = 0.8  # 0.0 a 1.0 (0.8 is a good starting point)
        
        # Efectos
        self.last_hit = None # To highlight the paddle that hit the ball
        self.ball_trail = [] # For ball trail effect
        
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
            pass # Fail silently if there's no audio or an error
    
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

    def toggle_theme(self):
        """Alternar entre modo claro y oscuro"""
        self.dark_mode = not self.dark_mode
        theme_name = 'dark' if self.dark_mode else 'light'
        self.colors = self.themes[theme_name].copy()
        self.play_beep(800, 80)
        
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
                    self.play_beep(600, 50)
                
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                        self.reset_game()
                    elif self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "game_over":
                        self.game_state = "menu" # Go back to menu from game over
                        self.reset_game() # Reset game state for next play
                    self.play_beep(600, 100)
                
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.reset_game()
                    self.game_state = "playing"
                    self.play_beep(800, 100)
                
                elif event.key == pygame.K_a:
                    self.ai_enabled = not self.ai_enabled
                    self.play_beep(1000, 50)

                elif event.key == pygame.K_t: # Toggle theme
                    self.toggle_theme()
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_state != "playing":
            return
        
        # Controles del jugador 1
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.player1['y'] > 0:
            self.player1['y'] -= self.player1['speed']
        if keys[pygame.K_s] and self.player1['y'] < self.height - self.player1['height']:
            self.player1['y'] += self.player1['speed']
        
        # Controles del jugador 2 (humano o AI)
        if self.ai_enabled:
            self.update_ai()
        else:
            if keys[pygame.K_UP] and self.player2['y'] > 0:
                self.player2['y'] -= self.player2['speed']
            if keys[pygame.K_DOWN] and self.player2['y'] < self.height - self.player2['height']:
                self.player2['y'] += self.player2['speed']
        
        # Actualizar pelota
        self.update_ball()
        
        # Verificar condición de victoria
        if self.player1['score'] >= self.winning_score or self.player2['score'] >= self.winning_score:
            self.game_state = "game_over"
            self.play_beep(400, 1000) # Longer beep for game over
    
    def update_ai(self):
        """Actualizar AI del jugador 2"""
        ball_center_y = self.ball['y'] + self.ball['size'] // 2
        paddle_center_y = self.player2['y'] + self.player2['height'] // 2
        
        # Calculate difference
        diff = ball_center_y - paddle_center_y
        
        # AI with adjustable difficulty
        # Lower move_threshold means AI is more precise and reacts to smaller differences
        move_threshold = 10 * (1.0 - self.ai_difficulty) 
        # move_speed determines how fast AI reacts, scaled by difficulty
        move_speed = self.player2['speed'] * self.ai_difficulty 
        
        if abs(diff) > move_threshold:
            if diff > 0 and self.player2['y'] < self.height - self.player2['height']:
                # Move down, limited by actual paddle speed and remaining difference
                self.player2['y'] += min(move_speed, diff)
            elif diff < 0 and self.player2['y'] > 0:
                # Move up, limited by actual paddle speed and remaining difference
                self.player2['y'] += max(-move_speed, diff)
    
    def update_ball(self):
        """Actualizar posición y colisiones de la pelota"""
        # Add current ball position to trail
        self.ball_trail.append((self.ball['x'], self.ball['y']))
        # Keep trail length managed
        if len(self.ball_trail) > 10: # Slightly longer trail for visual effect
            self.ball_trail.pop(0)
        
        # Mover pelota
        self.ball['x'] += self.ball['speed_x']
        self.ball['y'] += self.ball['speed_y']
        
        # Colisión con paredes superior e inferior
        if self.ball['y'] <= 0 or self.ball['y'] >= self.height - self.ball['size']:
            self.ball['speed_y'] = -self.ball['speed_y']
            self.play_beep(600, 60) # Shorter beep for wall collision
            self.screen_shake = 5
        
        # Colisión con paletas
        ball_rect = pygame.Rect(self.ball['x'], self.ball['y'], self.ball['size'], self.ball['size'])
        player1_rect = pygame.Rect(self.player1['x'], self.player1['y'], 
                                   self.player1['width'], self.player1['height'])
        player2_rect = pygame.Rect(self.player2['x'], self.player2['y'], 
                                   self.player2['width'], self.player2['height'])
        
        # Colisión con jugador 1
        if ball_rect.colliderect(player1_rect) and self.ball['speed_x'] < 0:
            self.handle_paddle_collision(self.player1, ball_rect)
            self.last_hit = "player1"
        
        # Colisión con jugador 2
        elif ball_rect.colliderect(player2_rect) and self.ball['speed_x'] > 0:
            self.handle_paddle_collision(self.player2, ball_rect)
            self.last_hit = "player2"
        
        # Gol
        if self.ball['x'] < -self.ball['size']:
            self.player2['score'] += 1
            self.reset_ball()
            self.play_beep(300, 300) # Goal sound
        elif self.ball['x'] > self.width:
            self.player1['score'] += 1
            self.reset_ball()
            self.play_beep(300, 300) # Goal sound
    
    def handle_paddle_collision(self, paddle, ball_rect):
        """Manejar colisión con paleta, ajustar rebote y velocidad"""
        # Invertir dirección X
        self.ball['speed_x'] = -self.ball['speed_x']
        
        # Calculate hit position relative to paddle center (-1 to 1)
        ball_center_y = ball_rect.centery
        paddle_center_y = paddle['y'] + paddle['height'] // 2
        
        # Normalize the hit position: -0.5 for top, 0 for middle, 0.5 for bottom
        relative_intersect_y = (paddle_center_y - ball_center_y) / (paddle['height'] / 2)
        
        # Adjust vertical speed based on where the ball hit the paddle
        # More extreme hits (closer to top/bottom edge) result in higher vertical speed
        bounce_angle_factor = 0.75 # Adjust to control max vertical bounce
        self.ball['speed_y'] = -relative_intersect_y * self.ball['max_speed'] * bounce_angle_factor
        
        # Increase horizontal speed gradually
        speed_multiplier = 1.05
        self.ball['speed_x'] *= speed_multiplier
        
        # Limit total speed to max_speed
        current_speed = math.sqrt(self.ball['speed_x']**2 + self.ball['speed_y']**2)
        if current_speed > self.ball['max_speed']:
            scale_factor = self.ball['max_speed'] / current_speed
            self.ball['speed_x'] *= scale_factor
            self.ball['speed_y'] *= scale_factor
        
        self.play_beep(800, 80) # Paddle hit sound
        self.screen_shake = 3
    
    def reset_ball(self):
        """Reiniciar pelota al centro con dirección aleatoria"""
        self.ball['x'] = self.width // 2
        self.ball['y'] = self.height // 2
        # Random initial direction, ensuring not perfectly horizontal
        self.ball['speed_x'] = random.choice([-6, 6])
        self.ball['speed_y'] = random.uniform(-4, 4) # Small random vertical component
        while abs(self.ball['speed_y']) < 1.0: # Ensure some vertical movement
            self.ball['speed_y'] = random.uniform(-4, 4)
        self.ball_trail.clear()
    
    def draw_menu(self):
        """Dibujar menú principal con estilo moderno"""
        self.screen.fill(self.colors['bg'])
        
        # Title
        title_text = self.fonts['title'].render("PONG MODERN", True, self.colors['accent_player1'])
        title_x = (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 100))
        
        # Menu card
        card_width = 500
        card_height = 300
        card_x = (self.width - card_width) // 2
        card_y = self.height // 2 - card_height // 2 + 50
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_shadow_rect(self.screen, card_rect, radius=12, shadow_offset=8, alpha=self.colors['shadow_dark'][3])
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], card_rect, 12)
        pygame.draw.rect(self.screen, self.colors['border'], card_rect, 1, border_radius=12)
        
        # Options
        options_y_start = card_y + 40
        options_x_offset = card_x + 50
        
        options = [
            ("SPACE - START GAME", self.colors['accent_player1']),
            (f"A - TOGGLE AI (Current: {'ON' if self.ai_enabled else 'OFF'})", self.colors['text_primary']),
            ("ESC - EXIT", self.colors['text_secondary'])
        ]
        
        for i, (option_text, color) in enumerate(options):
            text_render = self.fonts['medium'].render(option_text, True, color)
            # Center horizontally within the card
            text_x = card_x + (card_width - text_render.get_width()) // 2
            self.screen.blit(text_render, (text_x, options_y_start + i * 60))
        
        # Controls at bottom of card
        controls_label = self.fonts['small'].render("CONTROLS:", True, self.colors['text_secondary'])
        controls_label_x = card_x + (card_width - controls_label.get_width()) // 2
        self.screen.blit(controls_label, (controls_label_x, card_y + 180))

        controls_p1 = self.fonts['small'].render("PLAYER 1: W / S", True, self.colors['text_primary'])
        controls_p2 = self.fonts['small'].render("PLAYER 2: UP / DOWN (if AI off)", True, self.colors['text_primary'])

        controls_p1_x = card_x + (card_width - controls_p1.get_width()) // 2
        controls_p2_x = card_x + (card_width - controls_p2.get_width()) // 2

        self.screen.blit(controls_p1, (controls_p1_x, card_y + 210))
        self.screen.blit(controls_p2, (controls_p2_x, card_y + 235))

    def draw_game(self):
        """Dibujar juego en progreso con estilo moderno"""
        # Aplicar screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        self.screen_shake = max(0, self.screen_shake - 1)
        
        self.screen.fill(self.colors['bg'])
        
        # Línea central punteada
        dash_length = 10
        gap_length = 10
        for y in range(0, self.height, dash_length + gap_length):
            dash_rect = pygame.Rect(self.width // 2 - 2 + shake_x, y + shake_y, 4, dash_length)
            self.draw_rounded_rect(self.screen, self.colors['grid_line'], dash_rect, 2)
        
        # Paletas
        # Player 1
        p1_color = self.colors['accent_player1']
        p1_rect = pygame.Rect(self.player1['x'] + shake_x, self.player1['y'] + shake_y, 
                              self.player1['width'], self.player1['height'])
        self.draw_shadow_rect(self.screen, p1_rect, radius=8, shadow_offset=2, alpha=self.colors['shadow_light'][3])
        self.draw_rounded_rect(self.screen, p1_color, p1_rect, 8)
        # Highlight for player 1 paddle
        p1_highlight_rect = pygame.Rect(p1_rect.x + 1, p1_rect.y + 1, p1_rect.width - 2, p1_rect.height // 5)
        p1_highlight_color = tuple(min(255, c + 30) for c in p1_color)
        self.draw_rounded_rect(self.screen, p1_highlight_color, p1_highlight_rect, 6)
        
        # Player 2
        p2_color = self.colors['accent_player2']
        p2_rect = pygame.Rect(self.player2['x'] + shake_x, self.player2['y'] + shake_y, 
                              self.player2['width'], self.player2['height'])
        self.draw_shadow_rect(self.screen, p2_rect, radius=8, shadow_offset=2, alpha=self.colors['shadow_light'][3])
        self.draw_rounded_rect(self.screen, p2_color, p2_rect, 8)
        # Highlight for player 2 paddle
        p2_highlight_rect = pygame.Rect(p2_rect.x + 1, p2_rect.y + 1, p2_rect.width - 2, p2_rect.height // 5)
        p2_highlight_color = tuple(min(255, c + 30) for c in p2_color)
        self.draw_rounded_rect(self.screen, p2_highlight_color, p2_highlight_rect, 6)
        
        # Ball Trail
        for i, (trail_x, trail_y) in enumerate(self.ball_trail):
            alpha_multiplier = (i + 1) / len(self.ball_trail) # Fade from transparent to opaque
            alpha = int(255 * alpha_multiplier * 0.4) # Max alpha 40%
            size_scaled = int(self.ball['size'] * alpha_multiplier * 0.8) # Smaller, fading size
            
            if size_scaled > 0:
                trail_surface = pygame.Surface((size_scaled, size_scaled), pygame.SRCALPHA)
                trail_color = self.colors['ball']
                
                # Apply alpha to trail color
                trail_color_with_alpha = (trail_color[0], trail_color[1], trail_color[2], alpha)
                
                pygame.draw.circle(trail_surface, trail_color_with_alpha, 
                                   (size_scaled // 2, size_scaled // 2), size_scaled // 2, 0)
                self.screen.blit(trail_surface, (trail_x + shake_x + (self.ball['size'] - size_scaled) // 2, 
                                                 trail_y + shake_y + (self.ball['size'] - size_scaled) // 2))
        
        # Pelota
        ball_rect = pygame.Rect(self.ball['x'] + shake_x, self.ball['y'] + shake_y, 
                                self.ball['size'], self.ball['size'])
        self.draw_shadow_rect(self.screen, ball_rect, radius=self.ball['size'] // 2, shadow_offset=2, alpha=self.colors['shadow_light'][3])
        pygame.draw.circle(self.screen, self.colors['ball'], ball_rect.center, self.ball['size'] // 2)
        # Highlight for ball
        ball_highlight_rect = pygame.Rect(ball_rect.x + 1, ball_rect.y + 1, ball_rect.width - 2, ball_rect.height // 3)
        ball_highlight_color = tuple(min(255, c + 40) for c in self.colors['ball'])
        pygame.draw.circle(self.screen, ball_highlight_color, (ball_highlight_rect.x + ball_highlight_rect.width // 2, ball_highlight_rect.y + ball_highlight_rect.height // 2), ball_highlight_rect.width // 2 * 0.8)

        # Puntuación
        score1_text = str(self.player1['score'])
        score2_text = str(self.player2['score'])
        
        text1 = self.fonts['large'].render(score1_text, True, self.colors['accent_player1'])
        text2 = self.fonts['large'].render(score2_text, True, self.colors['accent_player2'])
        
        # Position scores closer to the center, higher up
        self.screen.blit(text1, (self.width // 2 - 100 - text1.get_width() // 2 + shake_x, 50 + shake_y))
        self.screen.blit(text2, (self.width // 2 + 100 - text2.get_width() // 2 + shake_x, 50 + shake_y))
        
        # Indicadores de jugador
        p1_label = "HUMAN"
        p2_label = "COMPUTER" if self.ai_enabled else "HUMAN"
        
        text1 = self.fonts['small'].render(p1_label, True, self.colors['text_secondary'])
        text2 = self.fonts['small'].render(p2_label, True, self.colors['text_secondary'])
        
        self.screen.blit(text1, (self.player1['x'] - 10 + shake_x, 20 + shake_y))
        self.screen.blit(text2, (self.player2['x'] + self.player2['width'] - text2.get_width() + 10 + shake_x, 20 + shake_y))
        
        # Controles en la parte inferior
        controls_main = f"W/S: P1 Move • {'AI Active' if self.ai_enabled else '↑/↓: P2 Move'}"
        controls_misc = "SPACE: Pause • T: Theme • ESC: Menu"
        
        text_main = self.fonts['small'].render(controls_main, True, self.colors['text_secondary'])
        text_misc = self.fonts['small'].render(controls_misc, True, self.colors['text_secondary'])

        x_main = (self.width - text_main.get_width()) // 2
        x_misc = (self.width - text_misc.get_width()) // 2

        self.screen.blit(text_main, (x_main + shake_x, self.height - 50 + shake_y))
        self.screen.blit(text_misc, (x_misc + shake_x, self.height - 25 + shake_y))
    
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
        self.draw_shadow_rect(self.screen, card_rect, radius=12, shadow_offset=8, alpha=self.colors['shadow_dark'][3])
        self.draw_rounded_rect(self.screen, self.colors['card_bg'], card_rect, 12)
        pygame.draw.rect(self.screen, self.colors['border'], card_rect, 1, border_radius=12)
        
        # Título
        title_text = self.fonts['large'].render(title, True, self.colors['text_primary'])
        title_x = card_x + (card_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, card_y + 40))
        
        # Subtítulo (si existe)
        if subtitle:
            subtitle_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            subtitle_x = card_x + (card_width - subtitle_text.get_width()) // 2
            self.screen.blit(subtitle_text, (subtitle_x, card_y + 85))
            
        # Texto de acción (si existe)
        if action_text:
            action_font = self.fonts['medium'] if not subtitle else self.fonts['small']
            action_text_render = action_font.render(action_text, True, self.colors['accent_player1'])
            action_x = card_x + (card_width - action_text_render.get_width()) // 2
            action_y = card_y + (130 if not subtitle else 150)
            self.screen.blit(action_text_render, (action_x, action_y))
    
    def draw_pause(self):
        """Dibujar pantalla de pausa con overlay moderno"""
        self.draw_game() # Draw game in background
        self.draw_overlay("PAUSED", "Game is on hold", "PRESS SPACE TO RESUME")
    
    def draw_game_over(self):
        """Dibujar pantalla de game over con overlay moderno"""
        # Determine winner
        if self.player1['score'] >= self.winning_score:
            winner_text = "HUMAN WINS!"
            winner_color = self.colors['accent_player1']
        else:
            winner_text = "COMPUTER WINS!" if self.ai_enabled else "HUMAN 2 WINS!"
            winner_color = self.colors['accent_player2']
        
        final_score_text = f"FINAL SCORE: {self.player1['score']} - {self.player2['score']}"
        action_text = "SPACE - MAIN MENU / R - PLAY AGAIN"

        self.draw_overlay(winner_text, final_score_text, action_text)
    
    def draw_scanlines(self):
        """Dibujar efecto de líneas de escaneo sutiles y que combinen con el tema"""
        scanline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Use a slightly darker version of the background color with transparency
        scanline_color = self.colors['scanline_color']
        
        for y in range(0, self.height, 3): # Draw every 3 pixels
            pygame.draw.line(scanline_surface, scanline_color, (0, y), (self.width, y))
        self.screen.blit(scanline_surface, (0, 0))
    
    def run(self):
        """Loop principal del juego"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar juego
            self.update_game()
            
            # Dibujar según estado
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.draw_game()
            elif self.game_state == "paused":
                self.draw_pause()
            elif self.game_state == "game_over":
                self.draw_game_over()
            
            # Efectos visuales que siempre se dibujan en la parte superior
            self.draw_scanlines()
            
            pygame.display.flip()
            self.clock.tick(60) # Maintain 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    game = PongModern()
    game.run()

if __name__ == "__main__":
    main()