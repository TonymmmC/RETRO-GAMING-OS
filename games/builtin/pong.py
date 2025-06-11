#!/usr/bin/env python3
"""
Retro Pong - Clásico juego de pong con estilo retro
Para usar dentro del Gaming OS
"""

import pygame
import random
import math
import sys

class PongGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración de pantalla
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Retro Pong")
        
        # Colores retro
        self.colors = {
            'bg': (0, 0, 0),
            'white': (255, 255, 255),
            'green': (0, 255, 0),
            'amber': (255, 191, 0),
            'red': (255, 0, 0),
            'gray': (128, 128, 128),
            'dark_green': (0, 128, 0)
        }
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Estado del juego
        self.game_state = "menu"  # menu, playing, paused, game_over
        self.reset_game()
        
        # Clock
        self.clock = pygame.time.Clock()
        
        # Efectos visuales
        self.trail_positions = []
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
            'max_speed': 12
        }
        
        # Configuración del juego
        self.winning_score = 5
        self.ai_enabled = True
        self.ai_difficulty = 0.8  # 0.0 a 1.0
        
        # Efectos
        self.last_hit = None
        self.ball_trail = []
        
    def play_beep(self, frequency=800, duration=100):
        """Reproducir sonido beep"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            for i in range(frames):
                wave = 4096 * (frequency * 2 * 3.14159 * i / sample_rate) % (2 * 3.14159)
                arr.append([int(32767 * 0.1 * (wave - 3.14159) / 3.14159)] * 2)
            
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
                
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "playing"
                        self.reset_game()
                    elif self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "game_over":
                        self.game_state = "menu"
                    
                    self.play_beep(600, 100)
                
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.reset_game()
                    self.game_state = "playing"
                    self.play_beep(800, 100)
                
                elif event.key == pygame.K_a:
                    self.ai_enabled = not self.ai_enabled
                    self.play_beep(1000, 50)
        
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
            self.play_beep(400, 1000)
    
    def update_ai(self):
        """Actualizar AI del jugador 2"""
        ball_center_y = self.ball['y']
        paddle_center_y = self.player2['y'] + self.player2['height'] // 2
        
        # Calcular diferencia
        diff = ball_center_y - paddle_center_y
        
        # AI con dificultad ajustable
        move_threshold = 20 * (1 - self.ai_difficulty)
        move_speed = self.player2['speed'] * self.ai_difficulty
        
        if abs(diff) > move_threshold:
            if diff > 0 and self.player2['y'] < self.height - self.player2['height']:
                self.player2['y'] += min(move_speed, diff)
            elif diff < 0 and self.player2['y'] > 0:
                self.player2['y'] += max(-move_speed, diff)
    
    def update_ball(self):
        """Actualizar posición y colisiones de la pelota"""
        # Guardar posición para trail
        self.ball_trail.append((self.ball['x'], self.ball['y']))
        if len(self.ball_trail) > 8:
            self.ball_trail.pop(0)
        
        # Mover pelota
        self.ball['x'] += self.ball['speed_x']
        self.ball['y'] += self.ball['speed_y']
        
        # Colisión con paredes superior e inferior
        if self.ball['y'] <= 0 or self.ball['y'] >= self.height - self.ball['size']:
            self.ball['speed_y'] = -self.ball['speed_y']
            self.play_beep(600, 100)
            self.screen_shake = 5
        
        # Colisión con paletas
        ball_rect = pygame.Rect(self.ball['x'], self.ball['y'], self.ball['size'], self.ball['size'])
        player1_rect = pygame.Rect(self.player1['x'], self.player1['y'], 
                                  self.player1['width'], self.player1['height'])
        player2_rect = pygame.Rect(self.player2['x'], self.player2['y'], 
                                  self.player2['width'], self.player2['height'])
        
        # Colisión con jugador 1
        if ball_rect.colliderect(player1_rect) and self.ball['speed_x'] < 0:
            self.handle_paddle_collision(self.player1)
            self.last_hit = "player1"
        
        # Colisión con jugador 2
        elif ball_rect.colliderect(player2_rect) and self.ball['speed_x'] > 0:
            self.handle_paddle_collision(self.player2)
            self.last_hit = "player2"
        
        # Gol
        if self.ball['x'] < -self.ball['size']:
            self.player2['score'] += 1
            self.reset_ball()
            self.play_beep(300, 300)
        elif self.ball['x'] > self.width:
            self.player1['score'] += 1
            self.reset_ball()
            self.play_beep(300, 300)
    
    def handle_paddle_collision(self, paddle):
        """Manejar colisión con paleta"""
        # Invertir dirección X
        self.ball['speed_x'] = -self.ball['speed_x']
        
        # Calcular ángulo basado en dónde golpeó la paleta
        ball_center = self.ball['y'] + self.ball['size'] // 2
        paddle_center = paddle['y'] + paddle['height'] // 2
        hit_pos = (ball_center - paddle_center) / (paddle['height'] // 2)
        
        # Modificar velocidad Y basada en el ángulo
        self.ball['speed_y'] = hit_pos * 6
        
        # Aumentar velocidad gradualmente
        speed_multiplier = 1.05
        self.ball['speed_x'] *= speed_multiplier
        self.ball['speed_y'] *= speed_multiplier
        
        # Limitar velocidad máxima
        if abs(self.ball['speed_x']) > self.ball['max_speed']:
            self.ball['speed_x'] = self.ball['max_speed'] * (1 if self.ball['speed_x'] > 0 else -1)
        if abs(self.ball['speed_y']) > self.ball['max_speed']:
            self.ball['speed_y'] = self.ball['max_speed'] * (1 if self.ball['speed_y'] > 0 else -1)
        
        self.play_beep(800, 100)
        self.screen_shake = 3
    
    def reset_ball(self):
        """Reiniciar pelota al centro"""
        self.ball['x'] = self.width // 2
        self.ball['y'] = self.height // 2
        self.ball['speed_x'] = random.choice([-6, 6])
        self.ball['speed_y'] = random.choice([-4, 4])
        self.ball_trail.clear()
    
    def draw_menu(self):
        """Dibujar menú principal"""
        self.screen.fill(self.colors['bg'])
        
        # Título
        title = "RETRO PONG"
        text = self.font_large.render(title, True, self.colors['green'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 150))
        
        # Opciones
        options = [
            "SPACE - START GAME",
            "A - TOGGLE AI (Current: " + ("ON" if self.ai_enabled else "OFF") + ")",
            "ESC - EXIT"
        ]
        
        for i, option in enumerate(options):
            color = self.colors['amber'] if i == 0 else self.colors['white']
            text = self.font_medium.render(option, True, color)
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, 300 + i * 50))
        
        # Controles
        controls = [
            "PLAYER 1: W/S",
            "PLAYER 2: UP/DOWN (if AI off)"
        ]
        
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, self.colors['gray'])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, 450 + i * 25))
    
    def draw_game(self):
        """Dibujar juego en progreso"""
        # Aplicar screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        self.screen_shake = max(0, self.screen_shake - 1)
        
        self.screen.fill(self.colors['bg'])
        
        # Línea central punteada
        for y in range(0, self.height, 20):
            pygame.draw.rect(self.screen, self.colors['gray'], 
                           (self.width // 2 - 2 + shake_x, y + shake_y, 4, 10))
        
        # Paletas
        # Jugador 1
        color1 = self.colors['green'] if self.last_hit == "player1" else self.colors['white']
        pygame.draw.rect(self.screen, color1, 
                        (self.player1['x'] + shake_x, self.player1['y'] + shake_y, 
                         self.player1['width'], self.player1['height']))
        
        # Jugador 2
        color2 = self.colors['green'] if self.last_hit == "player2" else self.colors['white']
        pygame.draw.rect(self.screen, color2, 
                        (self.player2['x'] + shake_x, self.player2['y'] + shake_y, 
                         self.player2['width'], self.player2['height']))
        
        # Trail de la pelota
        for i, (trail_x, trail_y) in enumerate(self.ball_trail):
            alpha = i / len(self.ball_trail)
            size = int(self.ball['size'] * alpha)
            if size > 0:
                trail_surface = pygame.Surface((size, size))
                trail_surface.set_alpha(int(255 * alpha))
                trail_surface.fill(self.colors['amber'])
                self.screen.blit(trail_surface, (trail_x + shake_x, trail_y + shake_y))
        
        # Pelota
        pygame.draw.rect(self.screen, self.colors['white'], 
                        (self.ball['x'] + shake_x, self.ball['y'] + shake_y, 
                         self.ball['size'], self.ball['size']))
        
        # Puntuación
        score1_text = str(self.player1['score'])
        score2_text = str(self.player2['score'])
        
        text1 = self.font_large.render(score1_text, True, self.colors['green'])
        text2 = self.font_large.render(score2_text, True, self.colors['green'])
        
        self.screen.blit(text1, (self.width // 4 - text1.get_width() // 2 + shake_x, 50 + shake_y))
        self.screen.blit(text2, (3 * self.width // 4 - text2.get_width() // 2 + shake_x, 50 + shake_y))
        
        # Indicadores de jugador
        p1_label = "PLAYER 1" if not self.ai_enabled else "HUMAN"
        p2_label = "PLAYER 2" if not self.ai_enabled else "COMPUTER"
        
        text1 = self.font_small.render(p1_label, True, self.colors['amber'])
        text2 = self.font_small.render(p2_label, True, self.colors['amber'])
        
        self.screen.blit(text1, (50 + shake_x, 20 + shake_y))
        self.screen.blit(text2, (self.width - 150 + shake_x, 20 + shake_y))
        
        # Controles en la parte inferior
        controls = "W/S: P1 Move • " + ("AI Active" if self.ai_enabled else "↑/↓: P2 Move") + " • SPACE: Pause • ESC: Menu"
        text = self.font_small.render(controls, True, self.colors['gray'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x + shake_x, self.height - 30 + shake_y))
    
    def draw_pause(self):
        """Dibujar pantalla de pausa"""
        self.draw_game()  # Dibujar juego de fondo
        
        # Overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(self.colors['bg'])
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        pause_text = "PAUSED"
        text = self.font_large.render(pause_text, True, self.colors['green'])
        x = (self.width - text.get_width()) // 2
        y = self.height // 2 - 50
        self.screen.blit(text, (x, y))
        
        resume_text = "PRESS SPACE TO RESUME"
        text = self.font_medium.render(resume_text, True, self.colors['white'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, y + 60))
    
    def draw_game_over(self):
        """Dibujar pantalla de game over"""
        self.screen.fill(self.colors['bg'])
        
        # Determinar ganador
        if self.player1['score'] >= self.winning_score:
            winner = "PLAYER 1 WINS!" if not self.ai_enabled else "HUMAN WINS!"
            winner_color = self.colors['green']
        else:
            winner = "PLAYER 2 WINS!" if not self.ai_enabled else "COMPUTER WINS!"
            winner_color = self.colors['red']
        
        # Texto de victoria
        text = self.font_large.render(winner, True, winner_color)
        x = (self.width - text.get_width()) // 2
        y = self.height // 2 - 100
        self.screen.blit(text, (x, y))
        
        # Puntuación final
        final_score = f"FINAL SCORE: {self.player1['score']} - {self.player2['score']}"
        text = self.font_medium.render(final_score, True, self.colors['white'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, y + 80))
        
        # Opciones
        options = [
            "R - PLAY AGAIN",
            "SPACE - MAIN MENU",
            "ESC - EXIT"
        ]
        
        for i, option in enumerate(options):
            text = self.font_medium.render(option, True, self.colors['amber'])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, y + 150 + i * 40))
    
    def draw_scanlines(self):
        """Dibujar efecto de líneas de escaneo"""
        for y in range(0, self.height, 3):
            pygame.draw.line(self.screen, (0, 0, 0, 30), (0, y), (self.width, y))
    
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
            
            # Efectos retro
            self.draw_scanlines()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    """Función principal"""
    game = PongGame()
    game.run()

if __name__ == "__main__":
    main()