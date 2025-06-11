#!/usr/bin/env python3
"""
Snake Retro - Juego de la serpiente con estilo retro
Para usar dentro del Gaming OS
"""

import pygame
import random
import sys
import time

class SnakeGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuración de pantalla
        self.cell_size = 20
        self.grid_width = 30
        self.grid_height = 20
        self.width = self.grid_width * self.cell_size
        self.height = self.grid_height * self.cell_size + 100  # Extra para UI
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Retro")
        
        # Colores retro
        self.colors = {
            'bg': (0, 0, 0),
            'snake': (0, 255, 0),
            'food': (255, 255, 0),
            'wall': (0, 128, 0),
            'text': (0, 255, 0),
            'score': (255, 191, 0)
        }
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Estado del juego
        self.reset_game()
        
        # Clock para controlar FPS
        self.clock = pygame.time.Clock()
        self.game_speed = 8  # Velocidad inicial
        
    def reset_game(self):
        """Reiniciar estado del juego"""
        # Serpiente inicial (centro de la pantalla)
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        
        # Dirección inicial
        self.direction = (1, 0)  # Derecha
        self.next_direction = (1, 0)
        
        # Comida
        self.food = self.generate_food()
        
        # Puntuación
        self.score = 0
        self.high_score = self.load_high_score()
        
        # Estado
        self.game_over = False
        self.paused = False
        
        # Efectos
        self.food_blink = 0
        self.snake_segments_animation = []
        for i in range(len(self.snake)):
            self.snake_segments_animation.append(0)
    
    def load_high_score(self):
        """Cargar puntuación máxima"""
        try:
            with open("games/builtin/snake_highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        """Guardar puntuación máxima"""
        try:
            with open("games/builtin/snake_highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def generate_food(self):
        """Generar nueva comida en posición aleatoria"""
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def play_beep(self, frequency=800, duration=100):
        """Reproducir sonido beep"""
        try:
            # Generar tono simple
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            for i in range(frames):
                wave = 4096 * (frequency * 2 * 3.14159 * i / sample_rate) % (2 * 3.14159)
                arr.append([int(32767 * 0.1 * (wave - 3.14159) / 3.14159)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass  # Fallar silenciosamente si no hay audio
    
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
                
                elif not self.game_over and not self.paused:
                    # Controles de dirección
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.next_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.next_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.next_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.next_direction = (1, 0)
        
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
            self.play_beep(200, 500)
            return
        
        # Verificar colisión consigo misma
        if new_head in self.snake:
            self.game_over = True
            self.play_beep(200, 500)
            return
        
        # Agregar nueva cabeza
        self.snake.insert(0, new_head)
        
        # Verificar si comió
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.play_beep(1000, 100)
            
            # Aumentar velocidad gradualmente
            if self.score % 50 == 0 and self.game_speed < 15:
                self.game_speed += 1
            
            # Actualizar high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        else:
            # Quitar cola si no comió
            self.snake.pop()
        
        # Actualizar animaciones
        self.food_blink = (self.food_blink + 1) % 30
        for i in range(len(self.snake_segments_animation)):
            self.snake_segments_animation[i] = (self.snake_segments_animation[i] + 1) % 60
    
    def draw_grid(self):
        """Dibujar grid de fondo"""
        for x in range(0, self.width, self.cell_size * 2):
            pygame.draw.line(self.screen, (0, 32, 0), (x, 0), (x, self.grid_height * self.cell_size))
        for y in range(0, self.grid_height * self.cell_size, self.cell_size * 2):
            pygame.draw.line(self.screen, (0, 32, 0), (0, y), (self.width, y))
    
    def draw_snake(self):
        """Dibujar serpiente con efectos"""
        for i, (x, y) in enumerate(self.snake):
            # Color de segmento
            if i == 0:  # Cabeza
                color = self.colors['snake']
                # Agregar brillo a la cabeza
                brightness = 1.2
                color = (min(255, int(color[0] * brightness)), 
                        min(255, int(color[1] * brightness)), 
                        min(255, int(color[2] * brightness)))
            else:  # Cuerpo
                # Degradado en el cuerpo
                fade = 1.0 - (i * 0.1)
                fade = max(0.3, fade)
                color = (int(self.colors['snake'][0] * fade),
                        int(self.colors['snake'][1] * fade),
                        int(self.colors['snake'][2] * fade))
            
            # Dibujar segmento
            rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                             self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, color, rect)
            
            # Borde para definición
            pygame.draw.rect(self.screen, (0, 64, 0), rect, 1)
    
    def draw_food(self):
        """Dibujar comida con efecto parpadeante"""
        x, y = self.food
        
        # Efecto de parpadeo
        if self.food_blink < 15:
            color = self.colors['food']
        else:
            color = (255, 255, 128)  # Más claro
        
        # Dibujar comida como círculo
        center_x = x * self.cell_size + self.cell_size // 2
        center_y = y * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 2
        
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (128, 128, 0), (center_x, center_y), radius, 2)
    
    def draw_ui(self):
        """Dibujar interfaz de usuario"""
        ui_y = self.grid_height * self.cell_size
        
        # Fondo de UI
        pygame.draw.rect(self.screen, (0, 0, 0), (0, ui_y, self.width, 100))
        pygame.draw.line(self.screen, self.colors['wall'], (0, ui_y), (self.width, ui_y), 2)
        
        # Puntuación
        score_text = f"SCORE: {self.score:04d}"
        text = self.font_medium.render(score_text, True, self.colors['score'])
        self.screen.blit(text, (10, ui_y + 10))
        
        # High Score
        high_score_text = f"HIGH: {self.high_score:04d}"
        text = self.font_medium.render(high_score_text, True, self.colors['score'])
        self.screen.blit(text, (10, ui_y + 35))
        
        # Velocidad
        speed_text = f"SPEED: {self.game_speed}"
        text = self.font_small.render(speed_text, True, self.colors['text'])
        self.screen.blit(text, (10, ui_y + 60))
        
        # Longitud
        length_text = f"LENGTH: {len(self.snake)}"
        text = self.font_small.render(length_text, True, self.colors['text'])
        self.screen.blit(text, (120, ui_y + 60))
        
        # Controles
        controls = "ARROWS: Move • SPACE: Pause • ESC: Exit"
        text = self.font_small.render(controls, True, self.colors['text'])
        text_x = self.width - text.get_width() - 10
        self.screen.blit(text, (text_x, ui_y + 75))
    
    def draw_game_over(self):
        """Dibujar pantalla de game over"""
        # Overlay semi-transparente
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto principal
        game_over_text = "GAME OVER"
        text = self.font_large.render(game_over_text, True, self.colors['snake'])
        x = (self.width - text.get_width()) // 2
        y = self.height // 2 - 60
        self.screen.blit(text, (x, y))
        
        # Puntuación final
        final_score = f"FINAL SCORE: {self.score}"
        text = self.font_medium.render(final_score, True, self.colors['score'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, y + 40))
        
        # Nuevo récord
        if self.score == self.high_score and self.score > 0:
            record_text = "NEW HIGH SCORE!"
            text = self.font_medium.render(record_text, True, self.colors['food'])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, y + 70))
        
        # Instrucciones
        restart_text = "PRESS SPACE TO PLAY AGAIN"
        text = self.font_small.render(restart_text, True, self.colors['text'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, y + 100))
    
    def draw_pause(self):
        """Dibujar pantalla de pausa"""
        # Overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(64)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        pause_text = "PAUSED"
        text = self.font_large.render(pause_text, True, self.colors['snake'])
        x = (self.width - text.get_width()) // 2
        y = self.height // 2 - 20
        self.screen.blit(text, (x, y))
        
        resume_text = "PRESS SPACE TO RESUME"
        text = self.font_small.render(resume_text, True, self.colors['text'])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, y + 40))
    
    def run(self):
        """Loop principal del juego"""
        running = True
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar juego
            self.update_game()
            
            # Dibujar todo
            self.screen.fill(self.colors['bg'])
            self.draw_grid()
            self.draw_snake()
            self.draw_food()
            self.draw_ui()
            
            if self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_pause()
            
            pygame.display.flip()
            self.clock.tick(self.game_speed)
        
        pygame.quit()

def main():
    """Función principal"""
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()