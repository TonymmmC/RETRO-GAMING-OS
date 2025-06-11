"""
Game Launcher - Lanzador de juegos retro con interfaz grid
"""

import pygame
import os
import json
import subprocess
import time
from pathlib import Path

class GameLauncher:
    def __init__(self, screen, colors, fonts):
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
        
        # Estado del launcher
        self.selected_game = 0
        self.scroll_offset = 0
        self.games_per_row = 4
        self.games_per_page = 12
        
        # Lista de juegos
        self.games = []
        self.categories = ["ALL", "ARCADE", "RPG", "PUZZLE", "ACTION", "CLASSIC"]
        self.current_category = "ALL"
        
        # Variables de animación
        self.selection_animation = 0
        self.title_scroll = 0
        
        # Cargar base de datos de juegos
        self.load_game_database()
        self.scan_games_directory()
    
    def load_game_database(self):
        """Cargar base de datos de juegos"""
        db_path = Path("config/game_database.json")
        
        # Base de datos por defecto
        default_games = [
            {
                "title": "SNAKE RETRO",
                "filename": "snake.py",
                "category": "CLASSIC",
                "description": "Classic snake game with retro twist",
                "builtin": True,
                "playable": True
            },
            {
                "title": "RETRO PONG",
                "filename": "pong.py", 
                "category": "ARCADE",
                "description": "Two-player pong game",
                "builtin": True,
                "playable": True
            },
            {
                "title": "SPACE INVADERS",
                "filename": "invaders.py",
                "category": "ARCADE", 
                "description": "Defend Earth from alien invasion",
                "builtin": True,
                "playable": False
            },
            {
                "title": "BREAKOUT",
                "filename": "breakout.py",
                "category": "ARCADE",
                "description": "Break all the bricks",
                "builtin": True,
                "playable": False
            },
            {
                "title": "TETRIS CLONE",
                "filename": "tetris.py",
                "category": "PUZZLE",
                "description": "Falling blocks puzzle game",
                "builtin": True,
                "playable": False
            },
            {
                "title": "PAC-MAN MINI",
                "filename": "pacman.py",
                "category": "ARCADE",
                "description": "Maze chase game",
                "builtin": True,
                "playable": False
            }
        ]
        
        if db_path.exists():
            try:
                with open(db_path, 'r') as f:
                    self.games = json.load(f)
            except:
                self.games = default_games
        else:
            self.games = default_games
            self.save_game_database()
    
    def save_game_database(self):
        """Guardar base de datos de juegos"""
        db_path = Path("config/game_database.json")
        try:
            with open(db_path, 'w') as f:
                json.dump(self.games, f, indent=2)
        except Exception as e:
            print(f"Error saving game database: {e}")
    
    def scan_games_directory(self):
        """Escanear directorio de juegos para encontrar nuevos"""
        games_dir = Path("games")
        
        # Escanear juegos builtin
        builtin_dir = games_dir / "builtin"
        if builtin_dir.exists():
            for file in builtin_dir.glob("*.py"):
                # Verificar si ya existe en la base de datos
                if not any(g["filename"] == file.name for g in self.games):
                    self.games.append({
                        "title": file.stem.upper().replace("_", " "),
                        "filename": file.name,
                        "category": "CLASSIC",
                        "description": "Discovered game",
                        "builtin": True,
                        "playable": file.exists()
                    })
        
        # Escanear ROMs
        roms_dir = games_dir / "roms"
        if roms_dir.exists():
            for file in roms_dir.glob("*"):
                if file.suffix.lower() in [".nes", ".gb", ".gbc", ".sms", ".gg"]:
                    if not any(g["filename"] == file.name for g in self.games):
                        self.games.append({
                            "title": file.stem.upper(),
                            "filename": file.name,
                            "category": "RETRO",
                            "description": f"{file.suffix.upper()} ROM",
                            "builtin": False,
                            "playable": False  # Requiere emulador
                        })
    
    def get_filtered_games(self):
        """Obtener juegos filtrados por categoría"""
        if self.current_category == "ALL":
            return self.games
        return [g for g in self.games if g["category"] == self.current_category]
    
    def draw_header(self):
        """Dibujar cabecera del launcher"""
        # Título principal
        title = "GAME LAUNCHER"
        text = self.fonts["large"].render(title, True, self.colors["green_phosphor"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, 20))
        
        # Categorías
        cat_y = 60
        total_width = sum(self.fonts["medium"].size(cat)[0] + 40 for cat in self.categories)
        start_x = (self.screen.get_width() - total_width) // 2
        
        current_x = start_x
        for i, category in enumerate(self.categories):
            color = self.colors["green_phosphor"] if category == self.current_category else self.colors["gray"]
            text = self.fonts["medium"].render(category, True, color)
            
            # Highlight para categoría seleccionada
            if category == self.current_category:
                pygame.draw.rect(self.screen, self.colors["dark_green"], 
                               (current_x - 5, cat_y - 5, text.get_width() + 10, text.get_height() + 10))
            
            self.screen.blit(text, (current_x, cat_y))
            current_x += text.get_width() + 40
        
        # Línea separadora
        pygame.draw.line(self.screen, self.colors["green_phosphor"], 
                        (50, 100), (self.screen.get_width() - 50, 100), 2)
    
    def draw_game_grid(self):
        """Dibujar grid de juegos"""
        filtered_games = self.get_filtered_games()
        
        if not filtered_games:
            # No hay juegos
            text = self.fonts["medium"].render("NO GAMES FOUND", True, self.colors["gray"])
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, 300))
            return
        
        # Configuración del grid
        start_x = 80
        start_y = 120
        game_width = 150
        game_height = 100
        margin_x = 20
        margin_y = 20
        
        # Calcular índices visibles
        start_index = self.scroll_offset * self.games_per_row
        end_index = min(start_index + self.games_per_page, len(filtered_games))
        
        # Dibujar juegos
        for i in range(start_index, end_index):
            game = filtered_games[i]
            
            # Calcular posición en grid
            grid_index = i - start_index
            row = grid_index // self.games_per_row
            col = grid_index % self.games_per_row
            
            x = start_x + col * (game_width + margin_x)
            y = start_y + row * (game_height + margin_y)
            
            # Color del rectángulo según estado
            if i == self.selected_game:
                # Juego seleccionado - animación
                pulse = abs(pygame.math.Vector2(pygame.time.get_ticks() / 10).x % 20 - 10) / 10
                border_color = (
                    int(self.colors["green_phosphor"][0] * (0.7 + 0.3 * pulse)),
                    int(self.colors["green_phosphor"][1] * (0.7 + 0.3 * pulse)),
                    int(self.colors["green_phosphor"][2] * (0.7 + 0.3 * pulse))
                )
                bg_color = self.colors["dark_green"]
            elif game["playable"]:
                border_color = self.colors["green_phosphor"]
                bg_color = (0, 64, 0)
            else:
                border_color = self.colors["gray"]
                bg_color = (32, 32, 32)
            
            # Dibujar rectángulo del juego
            pygame.draw.rect(self.screen, bg_color, (x, y, game_width, game_height))
            pygame.draw.rect(self.screen, border_color, (x, y, game_width, game_height), 2)
            
            # Título del juego
            title = game["title"]
            if len(title) > 12:
                title = title[:12] + "..."
            
            text = self.fonts["small"].render(title, True, self.colors["white"])
            text_x = x + (game_width - text.get_width()) // 2
            self.screen.blit(text, (text_x, y + 10))
            
            # Categoría
            cat_text = self.fonts["small"].render(game["category"], True, self.colors["amber"])
            cat_x = x + (game_width - cat_text.get_width()) // 2
            self.screen.blit(cat_text, (cat_x, y + 30))
            
            # Estado
            if game["builtin"]:
                status = "BUILT-IN"
                status_color = self.colors["green_phosphor"]
            elif game["playable"]:
                status = "READY"
                status_color = self.colors["green_phosphor"]
            else:
                status = "N/A"
                status_color = self.colors["gray"]
            
            status_text = self.fonts["small"].render(status, True, status_color)
            status_x = x + (game_width - status_text.get_width()) // 2
            self.screen.blit(status_text, (status_x, y + 50))
        
        # Información del juego seleccionado
        if 0 <= self.selected_game < len(filtered_games):
            self.draw_game_info(filtered_games[self.selected_game])
    
    def draw_game_info(self, game):
        """Dibujar información del juego seleccionado"""
        info_y = 450
        
        # Fondo para información
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (50, info_y, self.screen.get_width() - 100, 120))
        pygame.draw.rect(self.screen, self.colors["green_phosphor"], (50, info_y, self.screen.get_width() - 100, 120), 1)
        
        # Título
        title_text = self.fonts["medium"].render(game["title"], True, self.colors["green_phosphor"])
        self.screen.blit(title_text, (60, info_y + 10))
        
        # Descripción
        desc_text = self.fonts["small"].render(game["description"], True, self.colors["white"])
        self.screen.blit(desc_text, (60, info_y + 40))
        
        # Controles
        if game["playable"]:
            controls = "PRESS ENTER TO PLAY • SPACE FOR OPTIONS"
            color = self.colors["amber"]
        else:
            controls = "GAME NOT AVAILABLE"
            color = self.colors["gray"]
        
        controls_text = self.fonts["small"].render(controls, True, color)
        self.screen.blit(controls_text, (60, info_y + 90))
    
    def draw_footer(self):
        """Dibujar pie de página con controles"""
        footer_y = self.screen.get_height() - 40
        
        controls = [
            "ARROWS: Navigate",
            "ENTER: Play",
            "TAB: Category", 
            "ESC: Back"
        ]
        
        control_text = " • ".join(controls)
        text = self.fonts["small"].render(control_text, True, self.colors["amber"])
        x = (self.screen.get_width() - text.get_width()) // 2
        self.screen.blit(text, (x, footer_y))
    
    def handle_input(self, event):
        """Manejar input del usuario"""
        filtered_games = self.get_filtered_games()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_LEFT:
                if self.selected_game > 0:
                    self.selected_game -= 1
                return "beep"
            
            elif event.key == pygame.K_RIGHT:
                if self.selected_game < len(filtered_games) - 1:
                    self.selected_game += 1
                return "beep"
            
            elif event.key == pygame.K_UP:
                if self.selected_game >= self.games_per_row:
                    self.selected_game -= self.games_per_row
                return "beep"
            
            elif event.key == pygame.K_DOWN:
                if self.selected_game + self.games_per_row < len(filtered_games):
                    self.selected_game += self.games_per_row
                return "beep"
            
            elif event.key == pygame.K_TAB:
                # Cambiar categoría
                current_index = self.categories.index(self.current_category)
                self.current_category = self.categories[(current_index + 1) % len(self.categories)]
                self.selected_game = 0
                return "beep"
            
            elif event.key == pygame.K_RETURN:
                if 0 <= self.selected_game < len(filtered_games):
                    game = filtered_games[self.selected_game]
                    if game["playable"]:
                        return ("launch_game", game)
                return "error"
        
        return None
    
    def launch_game(self, game):
        """Lanzar un juego específico"""
        if game["builtin"]:
            # Juego integrado
            game_path = Path("games/builtin") / game["filename"]
            if game_path.exists():
                try:
                    # Ejecutar juego en proceso separado
                    result = subprocess.run([
                        "python", str(game_path)
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"Game error: {result.stderr}")
                        return False
                    
                    return True
                except Exception as e:
                    print(f"Failed to launch game: {e}")
                    return False
        else:
            # ROM o juego externo
            print(f"External game launch not implemented: {game['filename']}")
            return False
    
    def draw(self):
        """Dibujar el launcher completo"""
        self.draw_header()
        self.draw_game_grid()
        self.draw_footer()
    
    def update(self):
        """Actualizar animaciones del launcher"""
        self.selection_animation = (self.selection_animation + 1) % 120
        self.title_scroll = (self.title_scroll + 1) % 1000