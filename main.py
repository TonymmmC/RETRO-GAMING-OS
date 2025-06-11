#!/usr/bin/env python3
"""
Retro Gaming OS - Boot Loader Principal (Versión Simplificada)
Sistema operativo retro gaming que arranca directo a interfaz nostálgica
"""

import pygame
import sys
import os
import time
import json
from pathlib import Path

# Inicializar Pygame
pygame.init()

class RetroGameOS:
    def __init__(self):
        # Configuración básica
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Retro Gaming OS v1.0")
        
        # Colores tema retro
        self.colors = {
            "green_phosphor": (0, 255, 0),
            "black": (0, 0, 0),
            "dark_green": (0, 128, 0),
            "gray": (128, 128, 128),
            "white": (255, 255, 255),
            "amber": (255, 191, 0)
        }
        
        # Fuentes
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 16)
        
        # Estados del sistema
        self.current_state = "boot"
        self.boot_progress = 0
        self.boot_start_time = time.time()
        
        # Clock para FPS
        self.clock = pygame.time.Clock()
        
        # Variables de animación
        self.cursor_blink = 0
        
        # Game launcher simple
        self.selected_option = 0
        self.games = self.scan_games()
        
    def scan_games(self):
        """Escanear juegos disponibles"""
        games = []
        builtin_dir = Path("games/builtin")
        
        if builtin_dir.exists():
            for file in builtin_dir.glob("*.py"):
                games.append({
                    "title": file.stem.upper(),
                    "filename": file.name,
                    "path": str(file)
                })
        
        return games
    
    def draw_boot_screen(self):
        """Dibujar pantalla de arranque simplificada"""
        self.screen.fill(self.colors["black"])
        
        # Logo simple
        title = "RETRO GAMING OS"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 200))
        
        # Mensaje de carga
        loading_text = "LOADING..."
        text = self.font_medium.render(loading_text, True, self.colors["green_phosphor"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 300))
        
        # Barra de progreso simple
        bar_width = 400
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = 350
        
        # Fondo
        pygame.draw.rect(self.screen, self.colors["dark_green"], 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Progreso
        fill_width = int((self.boot_progress / 100) * bar_width)
        pygame.draw.rect(self.screen, self.colors["green_phosphor"], 
                        (bar_x, bar_y, fill_width, bar_height))
        
        # Porcentaje
        percent_text = f"{int(self.boot_progress)}%"
        text = self.font_medium.render(percent_text, True, self.colors["green_phosphor"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 380))
    
    def draw_main_menu(self):
        """Dibujar menú principal"""
        self.screen.fill(self.colors["black"])
        
        # Título
        title = "RETRO GAMING OS - MAIN MENU"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        # Opciones del menú
        menu_options = [
            "1. GAME LAUNCHER",
            "2. SNAKE GAME", 
            "3. PONG GAME",
            "4. EXIT"
        ]
        
        start_y = 200
        for i, option in enumerate(menu_options):
            color = self.colors["amber"] if i == self.selected_option else self.colors["green_phosphor"]
            text = self.font_medium.render(option, True, color)
            self.screen.blit(text, (100, start_y + i * 40))
        
        # Información
        info_lines = [
            "PRESS NUMBER KEY TO SELECT",
            "OR USE ARROWS + ENTER",
            "ESC TO EXIT"
        ]
        
        info_y = 400
        for i, line in enumerate(info_lines):
            text = self.font_small.render(line, True, self.colors["gray"])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, info_y + i * 20))
    
    def draw_game_launcher(self):
        """Dibujar lanzador de juegos simple"""
        self.screen.fill(self.colors["black"])
        
        # Título
        title = "GAME LAUNCHER"
        text = self.font_large.render(title, True, self.colors["green_phosphor"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, 50))
        
        if not self.games:
            # No hay juegos
            text = self.font_medium.render("NO GAMES FOUND", True, self.colors["gray"])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, 200))
            
            text = self.font_small.render("Add .py files to games/builtin/", True, self.colors["gray"])
            x = (self.width - text.get_width()) // 2
            self.screen.blit(text, (x, 230))
        else:
            # Lista de juegos
            start_y = 150
            for i, game in enumerate(self.games):
                color = self.colors["amber"] if i == self.selected_option else self.colors["green_phosphor"]
                prefix = "► " if i == self.selected_option else "  "
                game_text = f"{prefix}{game['title']}"
                
                text = self.font_medium.render(game_text, True, color)
                self.screen.blit(text, (100, start_y + i * 30))
        
        # Controles
        controls = "ARROWS: Navigate • ENTER: Play • ESC: Back"
        text = self.font_small.render(controls, True, self.colors["amber"])
        x = (self.width - text.get_width()) // 2
        self.screen.blit(text, (x, self.height - 50))
    
    def update_boot(self):
        """Actualizar progreso de boot con timer"""
        elapsed = time.time() - self.boot_start_time
        
        # Boot completo en 3 segundos
        self.boot_progress = min(100, (elapsed / 3.0) * 100)
        
        if self.boot_progress >= 100:
            self.current_state = "main_menu"
    
    def launch_game(self, game_path):
        """Lanzar un juego"""
        try:
            import subprocess
            result = subprocess.run(["python", game_path], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Game error: {result.stderr}")
            
            return True
        except Exception as e:
            print(f"Failed to launch game: {e}")
            return False
    
    def handle_events(self):
        """Manejar eventos de input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "main_menu":
                        return False
                    else:
                        self.current_state = "main_menu"
                        self.selected_option = 0
                
                elif self.current_state == "main_menu":
                    if event.key == pygame.K_1:
                        self.current_state = "game_launcher"
                        self.selected_option = 0
                    elif event.key == pygame.K_2:
                        # Lanzar Snake directamente
                        snake_path = Path("games/builtin/snake.py")
                        if snake_path.exists():
                            self.launch_game(str(snake_path))
                    elif event.key == pygame.K_3:
                        # Lanzar Pong directamente
                        pong_path = Path("games/builtin/pong.py")
                        if pong_path.exists():
                            self.launch_game(str(pong_path))
                    elif event.key == pygame.K_4:
                        return False
                    
                    # Navegación con flechas
                    elif event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = min(3, self.selected_option + 1)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:
                            self.current_state = "game_launcher"
                            self.selected_option = 0
                        elif self.selected_option == 1:
                            snake_path = Path("games/builtin/snake.py")
                            if snake_path.exists():
                                self.launch_game(str(snake_path))
                        elif self.selected_option == 2:
                            pong_path = Path("games/builtin/pong.py")
                            if pong_path.exists():
                                self.launch_game(str(pong_path))
                        elif self.selected_option == 3:
                            return False
                
                elif self.current_state == "game_launcher":
                    if event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = min(len(self.games) - 1, self.selected_option + 1)
                    elif event.key == pygame.K_RETURN and self.games:
                        if 0 <= self.selected_option < len(self.games):
                            game = self.games[self.selected_option]
                            self.launch_game(game["path"])
        
        return True
    
    def run(self):
        """Loop principal del sistema"""
        running = True
        
        print("🎮 Sistema iniciado. Presiona ESC para salir.")
        
        while running:
            # Manejar eventos
            running = self.handle_events()
            
            # Actualizar estado
            if self.current_state == "boot":
                self.update_boot()
            
            # Dibujar según estado
            if self.current_state == "boot":
                self.draw_boot_screen()
            elif self.current_state == "main_menu":
                self.draw_main_menu()
            elif self.current_state == "game_launcher":
                self.draw_game_launcher()
            
            # Actualizar animaciones
            self.cursor_blink = (self.cursor_blink + 1) % 60
            
            # Actualizar pantalla
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    """Función principal"""
    print("🎮 Iniciando Retro Gaming OS (Versión Simplificada)...")
    
    # Crear directorios necesarios
    os.makedirs("games/builtin", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Iniciar sistema
    retro_os = RetroGameOS()
    retro_os.run()

if __name__ == "__main__":
    main()