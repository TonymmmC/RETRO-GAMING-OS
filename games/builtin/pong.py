#!/usr/bin/env python3
"""
Pong Modern - VERSIÓN CORREGIDA
Modo AI y 2 jugadores garantizado que funciona
"""

import pygame
import random
import math
import sys

class PongModern:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración moderna
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pong Modern - Fixed")
        
        # Tema moderno
        self.colors = {
            'bg_primary': (26, 26, 26),
            'bg_secondary': (45, 45, 45),
            'text_primary': (255, 255, 255),
            'text_secondary': (160, 160, 160),
            'accent_player1': (0, 122, 255),      # Azul
            'accent_player2': (255, 149, 0),      # Naranja
            'ball': (52, 199, 89),                # Verde
            'grid_line': (61, 61, 61),
            'shadow': (0, 0, 0, 60)
        }
        
        # Fuentes
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 32),
            'small': pygame.font.Font(None, 22),
            'tiny': pygame.font.Font(None, 16)
        }
        
        # Estado del juego
        self.game_state = "menu"
        
        # CONFIGURACIÓN CRUCIAL - AI
        self.ai_enabled = True  # Por defecto AI activada
        self.ai_difficulty = 0.75
        
        self.reset_game()
        
        # Control
        self.clock = pygame.time.Clock()
        self.screen_shake = 0
        self.animation_time = 0
        
    def reset_game(self):
        """Reiniciar juego"""
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
        
        self.ball = {
            'x': self.width // 2,
            'y': self.height // 2,
            'size': 12,
            'speed_x': random.choice([-6, 6]),
            'speed_y': random.choice([-4, 4]),
            'max_speed': 15,
            'trail': []
        }
        
        self.winning_score = 5
        
    def play_sound(self, sound_type):
        """Sonidos modernos"""
        try:
            frequencies = {
                'paddle_hit': 800,
                'wall_hit': 600,
                'score': 1000,
                'menu': 400,
                'ai_toggle': 1200
            }
            
            freq = frequencies.get(sound_type, 800)
            duration = 80 if sound_type != 'score' else 200
            
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
                
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                        self.reset_game()
                        print(f"GAME STARTED - AI Mode: {'ON' if self.ai_enabled else 'OFF'}")
                    elif self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "game_over":
                        self.game_state = "menu"
                        self.reset_game()
                    self.play_sound('menu')
                
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.reset_game()
                    self.game_state = "playing"
                    self.play_sound('menu')
                
                # TOGGLE AI - CRUCIAL
                elif event.key == pygame.K_a:
                    self.ai_enabled = not self.ai_enabled
                    print(f"AI TOGGLED: {'ON' if self.ai_enabled else 'OFF'}")
                    self.play_sound('ai_toggle')
        
        return True
    
    def update_game(self):
        """Actualizar lógica del juego"""
        if self.game_state != "playing":
            return
        
        # CONTROLES JUGADOR 1 (SIEMPRE HUMANO)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.player1['y'] > 0:
            self.player1['y'] -= self.player1['speed']
        if keys[pygame.K_s] and self.player1['y'] < self.height - self.player1['height']:
            self.player1['y'] += self.player1['speed']
        
        # CONTROLES JUGADOR 2 - AQUÍ ESTÁ LA LÓGICA CRUCIAL
        if self.ai_enabled:
            # MODO IA ACTIVADA
            self.update_ai_player2()
        else:
            # MODO 2 JUGADORES - CONTROLES HUMANOS
            if keys[pygame.K_UP] and self.player2['y'] > 0:
                self.player2['y'] -= self.player2['speed']
            if keys[pygame.K_DOWN] and self.player2['y'] < self.height - self.player2['height']:
                self.player2['y'] += self.player2['speed']
        
        # Actualizar pelota
        self.update_ball()
        
        # Verificar victoria
        if self.player1['score'] >= self.winning_score or self.player2['score'] >= self.winning_score:
            self.game_state = "game_over"
            self.play_sound('score')
    
    def update_ai_player2(self):
        """IA para el jugador 2 - FUNCIÓN SEPARADA"""
        ball_center_y = self.ball['y'] + self.ball['size'] // 2
        paddle_center_y = self.player2['y'] + self.player2['height'] // 2
        
        diff = ball_center_y - paddle_center_y
        move_threshold = 15 * (1.0 - self.ai_difficulty)
        move_speed = self.player2['speed'] * self.ai_difficulty
        
        # Solo mover si la diferencia es significativa
        if abs(diff) > move_threshold:
            if diff > 0 and self.player2['y'] < self.height - self.player2['height']:
                self.player2['y'] += min(move_speed, abs(diff))
            elif diff < 0 and self.player2['y'] > 0:
                self.player2['y'] -= min(move_speed, abs(diff))
    
    def update_ball(self):
        """Actualizar pelota"""
        # Trail de la pelota
        self.ball['trail'].append((self.ball['x'], self.ball['y']))
        if len(self.ball['trail']) > 8:
            self.ball['trail'].pop(0)
        
        # Mover pelota
        self.ball['x'] += self.ball['speed_x']
        self.ball['y'] += self.ball['speed_y']
        
        # Colisión con paredes superiores/inferiores
        if self.ball['y'] <= 0 or self.ball['y'] >= self.height - self.ball['size']:
            self.ball['speed_y'] = -self.ball['speed_y']
            self.play_sound('wall_hit')
            self.screen_shake = 5
        
        # Colisión con paletas
        self.check_paddle_collisions()
        
        # Goles
        if self.ball['x'] < -self.ball['size']:
            self.player2['score'] += 1
            self.reset_ball()
            self.play_sound('score')
        elif self.ball['x'] > self.width:
            self.player1['score'] += 1
            self.reset_ball()
            self.play_sound('score')
    
    def check_paddle_collisions(self):
        """Verificar colisiones con paletas"""
        ball_rect = pygame.Rect(self.ball['x'], self.ball['y'], self.ball['size'], self.ball['size'])
        player1_rect = pygame.Rect(self.player1['x'], self.player1['y'], 
                                   self.player1['width'], self.player1['height'])
        player2_rect = pygame.Rect(self.player2['x'], self.player2['y'], 
                                   self.player2['width'], self.player2['height'])
        
        # Colisión con jugador 1
        if ball_rect.colliderect(player1_rect) and self.ball['speed_x'] < 0:
            self.handle_paddle_collision(self.player1)
        
        # Colisión con jugador 2
        elif ball_rect.colliderect(player2_rect) and self.ball['speed_x'] > 0:
            self.handle_paddle_collision(self.player2)
    
    def handle_paddle_collision(self, paddle):
        """Manejar colisión con paleta"""
        # Invertir dirección X
        self.ball['speed_x'] = -self.ball['speed_x']
        
        # Calcular ángulo de rebote
        ball_center_y = self.ball['y'] + self.ball['size'] // 2
        paddle_center_y = paddle['y'] + paddle['height'] // 2
        
        relative_intersect_y = (paddle_center_y - ball_center_y) / (paddle['height'] / 2)
        bounce_angle_factor = 0.75
        self.ball['speed_y'] = -relative_intersect_y * self.ball['max_speed'] * bounce_angle_factor
        
        # Aumentar velocidad gradualmente
        self.ball['speed_x'] *= 1.05
        
        # Limitar velocidad máxima
        current_speed = math.sqrt(self.ball['speed_x']**2 + self.ball['speed_y']**2)
        if current_speed > self.ball['max_speed']:
            scale_factor = self.ball['max_speed'] / current_speed
            self.ball['speed_x'] *= scale_factor
            self.ball['speed_y'] *= scale_factor
        
        self.play_sound('paddle_hit')
        self.screen_shake = 3
    
    def reset_ball(self):
        """Reiniciar pelota"""
        self.ball['x'] = self.width // 2
        self.ball['y'] = self.height // 2
        self.ball['speed_x'] = random.choice([-6, 6])
        self.ball['speed_y'] = random.uniform(-4, 4)
        while abs(self.ball['speed_y']) < 1.0:
            self.ball['speed_y'] = random.uniform(-4, 4)
        self.ball['trail'].clear()
    
    def draw_modern_card(self, surface, rect, color, radius=12, shadow=True):
        """Dibujar card moderna"""
        if shadow:
            shadow_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width, rect.height)
            shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, self.colors['shadow'], 
                           (0, 0, rect.width, rect.height), border_radius=radius)
            surface.blit(shadow_surface, shadow_rect.topleft)
        
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def draw_menu(self):
        """Dibujar menú moderno"""
        self.screen.fill(self.colors['bg_primary'])
        
        # Título
        title_text = self.fonts['title'].render("PONG", True, self.colors['text_primary'])
        title_x = (self.width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, 80))
        
        # Subtítulo
        subtitle = self.fonts['medium'].render("Modern Edition - Fixed", True, self.colors['accent_player1'])
        sub_x = (self.width - subtitle.get_width()) // 2
        self.screen.blit(subtitle, (sub_x, 140))
        
        # Card principal del menú
        card_width = 500
        card_height = 350
        card_x = (self.width - card_width) // 2
        card_y = self.height // 2 - card_height // 2 + 30
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_modern_card(self.screen, card_rect, self.colors['bg_secondary'])
        
        # Opciones del menú
        options_y = card_y + 40
        
        # INDICADOR CLARO DEL ESTADO DE AI
        ai_status = "ON" if self.ai_enabled else "OFF"
        ai_color = self.colors['accent_player1'] if self.ai_enabled else self.colors['accent_player2']
        
        options = [
            ("SPACE - Start Game", self.colors['accent_player1']),
            (f"A - AI Mode: {ai_status}", ai_color),
            ("ESC - Exit", self.colors['text_secondary'])
        ]
        
        for i, (option_text, color) in enumerate(options):
            text_render = self.fonts['medium'].render(option_text, True, color)
            text_x = card_x + (card_width - text_render.get_width()) // 2
            self.screen.blit(text_render, (text_x, options_y + i * 60))
        
        # Controles detallados
        controls_y = card_y + 220
        controls_title = self.fonts['small'].render("CONTROLS:", True, self.colors['text_primary'])
        controls_title_x = card_x + (card_width - controls_title.get_width()) // 2
        self.screen.blit(controls_title, (controls_title_x, controls_y))
        
        controls = [
            "Player 1 (Left): W / S",
            f"Player 2 (Right): {'AI Controlled' if self.ai_enabled else 'Flechas Arriba/Abajo'}",
            "",
            "Press A to toggle between AI and 2-Player mode"
        ]
        
        for i, control in enumerate(controls):
            if control == "":
                continue
            control_text = self.fonts['tiny'].render(control, True, self.colors['text_secondary'])
            control_x = card_x + (card_width - control_text.get_width()) // 2
            self.screen.blit(control_text, (control_x, controls_y + 25 + i * 18))
    
    def draw_game(self):
        """Dibujar juego"""
        # Screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        self.screen_shake = max(0, self.screen_shake - 1)
        
        self.screen.fill(self.colors['bg_primary'])
        
        # Línea central
        center_x = self.width // 2
        for y in range(0, self.height, 20):
            line_rect = pygame.Rect(center_x - 2 + shake_x, y + shake_y, 4, 10)
            pygame.draw.rect(self.screen, self.colors['grid_line'], line_rect, border_radius=2)
        
        # Paletas
        # Player 1
        p1_rect = pygame.Rect(self.player1['x'] + shake_x, self.player1['y'] + shake_y, 
                              self.player1['width'], self.player1['height'])
        pygame.draw.rect(self.screen, self.colors['accent_player1'], p1_rect, border_radius=8)
        
        # Player 2
        p2_rect = pygame.Rect(self.player2['x'] + shake_x, self.player2['y'] + shake_y, 
                              self.player2['width'], self.player2['height'])
        pygame.draw.rect(self.screen, self.colors['accent_player2'], p2_rect, border_radius=8)
        
        # Trail de la pelota
        for i, (trail_x, trail_y) in enumerate(self.ball['trail']):
            alpha = (i + 1) / len(self.ball['trail']) * 0.6
            size = int(self.ball['size'] * alpha)
            
            if size > 0:
                trail_surface = pygame.Surface((size, size), pygame.SRCALPHA)
                trail_color = (*self.colors['ball'], int(255 * alpha))
                pygame.draw.circle(trail_surface, trail_color, (size // 2, size // 2), size // 2)
                self.screen.blit(trail_surface, (trail_x + shake_x, trail_y + shake_y))
        
        # Pelota
        ball_x = int(self.ball['x'] + shake_x)
        ball_y = int(self.ball['y'] + shake_y)
        pygame.draw.circle(self.screen, self.colors['ball'], 
                         (ball_x + self.ball['size'] // 2, ball_y + self.ball['size'] // 2), 
                         self.ball['size'] // 2)
        
        # Puntuaciones
        score1_text = self.fonts['large'].render(str(self.player1['score']), True, self.colors['accent_player1'])
        score2_text = self.fonts['large'].render(str(self.player2['score']), True, self.colors['accent_player2'])
        
        self.screen.blit(score1_text, (self.width // 2 - 100 + shake_x, 50 + shake_y))
        self.screen.blit(score2_text, (self.width // 2 + 80 + shake_x, 50 + shake_y))
        
        # INDICADORES CLAROS DE MODO
        p1_label = "HUMAN (W/S)"
        p2_label = "AI" if self.ai_enabled else "HUMAN (Flechas)"
        
        label1 = self.fonts['tiny'].render(p1_label, True, self.colors['text_secondary'])
        label2 = self.fonts['tiny'].render(p2_label, True, self.colors['text_secondary'])
        
        self.screen.blit(label1, (self.player1['x'] + shake_x, 15 + shake_y))
        self.screen.blit(label2, (self.player2['x'] - 30 + shake_x, 15 + shake_y))
        
        # Controles en la parte inferior
        if self.ai_enabled:
            controls = "W/S: Player 1 • AI: Automatic • A: Toggle AI • Space: Pause • Esc: Menu"
        else:
            controls = "W/S: Player 1 • Flechas: Player 2 • A: Toggle AI • Space: Pause • Esc: Menu"
            
        controls_text = self.fonts['tiny'].render(controls, True, self.colors['text_secondary'])
        controls_x = (self.width - controls_text.get_width()) // 2
        self.screen.blit(controls_text, (controls_x + shake_x, self.height - 25 + shake_y))
    
    def draw_overlay(self, title, subtitle="", action_text=""):
        """Overlay modal moderno"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        card_width = 400
        card_height = 200
        card_x = (self.width - card_width) // 2
        card_y = (self.height - card_height) // 2
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        self.draw_modern_card(self.screen, card_rect, self.colors['bg_secondary'], 
                             radius=16, shadow=True)
        
        title_text = self.fonts['large'].render(title, True, self.colors['text_primary'])
        title_x = card_x + (card_width - title_text.get_width()) // 2
        self.screen.blit(title_text, (title_x, card_y + 40))
        
        if subtitle:
            subtitle_text = self.fonts['medium'].render(subtitle, True, self.colors['text_secondary'])
            subtitle_x = card_x + (card_width - subtitle_text.get_width()) // 2
            self.screen.blit(subtitle_text, (subtitle_x, card_y + 85))
            
        if action_text:
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * 0.1)
            action_color = tuple(int(c * pulse) for c in self.colors['accent_player1'])
            
            action_font = self.fonts['medium'] if not subtitle else self.fonts['small']
            action_text_render = action_font.render(action_text, True, action_color)
            action_x = card_x + (card_width - action_text_render.get_width()) // 2
            action_y = card_y + (130 if not subtitle else 150)
            self.screen.blit(action_text_render, (action_x, action_y))
    
    def run(self):
        """Loop principal"""
        running = True
        
        print("PONG MODERN - VERSION CORREGIDA")
        print("Controles:")
        print("   - A: Alternar IA ON/OFF")
        print("   - Jugador 1: W/S")
        print("   - Jugador 2: Flechas arriba/abajo (solo cuando IA OFF)")
        print("   - SPACE: Jugar/Pausar")
        print("   - ESC: Menu/Salir")
        
        while running:
            # Eventos
            running = self.handle_events()
            
            # Lógica
            self.update_game()
            
            # Render
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.draw_game()
            elif self.game_state == "paused":
                self.draw_game()
                self.draw_overlay("PAUSED", "Game is on hold", "PRESS SPACE TO RESUME")
            elif self.game_state == "game_over":
                self.draw_game()
                winner = "PLAYER 1" if self.player1['score'] >= self.winning_score else ("AI" if self.ai_enabled else "PLAYER 2")
                score_text = f"{self.player1['score']} - {self.player2['score']}"
                self.draw_overlay(f"{winner} WINS!", score_text, "SPACE: Menu • R: Restart")
            
            # Update
            self.animation_time += 1
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    game = PongModern()
    game.run()

if __name__ == "__main__":
    main()