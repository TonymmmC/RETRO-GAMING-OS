#!/usr/bin/env python3
"""
Game Launcher Modern - Lanzador de juegos con diseño moderno y limpio
"""

import pygame
import os
import json
import subprocess
import sys
import math
from pathlib import Path

class GameLauncher:
    def __init__(self, screen, colors, fonts):
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
        
        # Mapeo de fuentes para compatibilidad
        self.font_map = {
            'title': fonts.get('heading_xl', fonts.get('heading_lg', pygame.font.Font(None, 36))),
            'large': fonts.get('heading_lg', pygame.font.Font(None, 32)),
            'medium': fonts.get('body_lg', pygame.font.Font(None, 22)),
            'small': fonts.get('body_md', pygame.font.Font(None, 18)),
            'tiny': fonts.get('body_sm', pygame.font.Font(None, 16)),
            'caption': fonts.get('caption', pygame.font.Font(None, 14))
        }
        
        # Estado del launcher
        self.selected_game = 0
        self.scroll_offset = 0
        self.games_per_row = 3
        self.games_per_page = 9
        
        # Animaciones
        self.animation_time = 0
        self.card_hover_scale = {}
        
        # Cargar juegos
        self.games = []
        self.categories = ["ALL", "ARCADE", "PUZZLE", "ACTION", "CLASSIC"]
        self.current_category = "ALL"
        
        self.load_game_database()
        self.scan_games_directory()
    
    def load_game_database(self):
        """Cargar base de datos de juegos"""
        db_path = Path("config/game_database.json")
        
        default_games = [
            {
                "title": "Snake Modern",
                "filename": "snake.py",
                "category": "CLASSIC",
                "description": "Classic snake with modern design",
                "builtin": True,
                "playable": True,
                "rating": 4.5,
                "icon": "🐍"
            },
            {
                "title": "Tetris Modern",
                "filename": "tetris.py", 
                "category": "PUZZLE",
                "description": "Block puzzle with sleek interface",
                "builtin": True,
                "playable": True,
                "rating": 4.8,
                "icon": "🧩"
            },
            {
                "title": "Pong Modern",
                "filename": "pong.py", 
                "category": "ARCADE",
                "description": "Two-player classic reimagined",
                "builtin": True,
                "playable": True,
                "rating": 4.2,
                "icon": "🏓"
            },
            {
                "title": "Breakout Modern",
                "filename": "breakout.py",
                "category": "ARCADE", 
                "description": "Break bricks with modern physics",
                "builtin": True,
                "playable": True,
                "rating": 4.6,
                "icon": "🧱"
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
        """Escanear directorio de juegos"""
        games_dir = Path("games/builtin")
        if not games_dir.exists():
            return
            
        for file in games_dir.glob("*.py"):
            # Verificar si el juego ya existe en la base de datos
            if not any(g["filename"] == file.name for g in self.games):
                # Agregar juego recién descubierto
                self.games.append({
                    "title": file.stem.replace("_", " ").title(),
                    "filename": file.name,
                    "category": "CLASSIC",
                    "description": "Discovered game",
                    "builtin": True,
                    "playable": file.exists(),
                    "rating": 3.0,
                    "icon": "🎮"
                })
        
        # Verificar playable status
        for game in self.games:
            if game["builtin"]:
                game_path = games_dir / game["filename"]
                game["playable"] = game_path.exists()
    
    def get_filtered_games(self):
        """Obtener juegos filtrados por categoría"""
        if self.current_category == "ALL":
            return [g for g in self.games if g["playable"]]
        return [g for g in self.games if g["category"] == self.current_category and g["playable"]]
    
    def draw_modern_card(self, surface, rect, elevation=1, selected=False):
        """Dibuja una card moderna con sombra y efectos"""
        # Sombra
        shadow_offset = elevation * 3
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, 
                                 rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_alpha = 80 if selected else 40
        pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                        (0, 0, rect.width, rect.height), border_radius=16)
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Card base
        card_color = self.colors["bg_surface"] if selected else self.colors["bg_secondary"]
        pygame.draw.rect(surface, card_color, rect, border_radius=16)
        
        # Borde de selección
        if selected:
            pygame.draw.rect(surface, self.colors["accent"], rect, width=2, border_radius=16)
    
    def draw_rating_stars(self, surface, x, y, rating):
        """Dibuja estrellas de rating"""
        star_size = 12
        star_spacing = 14
        
        for i in range(5):
            star_x = x + i * star_spacing
            if i < int(rating):
                # Estrella llena
                star_color = self.colors["warning"]
            elif i < rating:
                # Media estrella
                star_color = self.colors["text_secondary"]
            else:
                # Estrella vacía
                star_color = self.colors["text_secondary"]
            
            star_text = self.fonts["caption"].render("★", True, star_color)
            surface.blit(star_text, (star_x, y))
    
    def draw(self):
        """Dibujar el launcher completo"""
        # Header moderno
        header_rect = pygame.Rect(0, 0, self.screen.get_width(), 70)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], header_rect)
        
        # Título
        title = self.fonts["heading_lg"].render("Game Library", True, self.colors["text_primary"])
        self.screen.blit(title, (30, 20))
        
        # Filtros de categoría como pills modernas
        filter_x = 350
        for i, category in enumerate(self.categories):
            is_active = category == self.current_category
            
            # Pill background
            pill_width = 70
            pill_height = 30
            pill_rect = pygame.Rect(filter_x + i * 80, 20, pill_width, pill_height)
            
            if is_active:
                pygame.draw.rect(self.screen, self.colors["accent"], pill_rect, border_radius=15)
                text_color = self.colors["text_primary"]
            else:
                pygame.draw.rect(self.screen, self.colors["bg_surface"], pill_rect, border_radius=15)
                text_color = self.colors["text_secondary"]
            
            cat_text = self.fonts["caption"].render(category, True, text_color)
            text_x = pill_rect.x + (pill_width - cat_text.get_width()) // 2
            text_y = pill_rect.y + (pill_height - cat_text.get_height()) // 2
            self.screen.blit(cat_text, (text_x, text_y))
        
        # Obtener juegos filtrados
        filtered_games = self.get_filtered_games()
        
        if not filtered_games:
            # No hay juegos
            no_games_text = self.fonts["body_lg"].render("No games found", True, self.colors["text_secondary"])
            text_x = (self.screen.get_width() - no_games_text.get_width()) // 2
            self.screen.blit(no_games_text, (text_x, 300))
            
            help_text = self.fonts["body_md"].render("Make sure game files are in games/builtin/", True, self.colors["text_secondary"])
            help_x = (self.screen.get_width() - help_text.get_width()) // 2
            self.screen.blit(help_text, (help_x, 330))
            return
        
        # Grid optimizado - Layout 3xN con scroll
        grid_start_x = 50
        grid_start_y = 100
        card_width = 280   # Más ancho para aprovechar mejor el espacio
        card_height = 240  
        margin_x = 40      # Margen generoso entre cards
        margin_y = 30      
        
        # Configurar para exactamente 3 por fila
        self.games_per_row = 3  
        max_visible_rows = 2  # Mostrar 2 filas = 6 juegos máximo visibles
        max_visible_games = self.games_per_row * max_visible_rows
        
        # Calcular el ancho total y verificar que cabe
        total_grid_width = (card_width * 3) + (margin_x * 2)
        available_width = self.screen.get_width() - (grid_start_x * 2)  # Margen en ambos lados
        
        if total_grid_width > available_width:
            # Ajustar si no cabe
            card_width = (available_width - (margin_x * 2)) // 3
        
        # Scroll logic
        total_games = len(filtered_games)
        if total_games > max_visible_games:
            # Mostrar indicador de que hay más juegos
            has_more_games = True
            # Ajustar scroll offset si es necesario
            max_scroll = max(0, total_games - max_visible_games)
            self.scroll_offset = min(self.scroll_offset, max_scroll)
        else:
            has_more_games = False
            self.scroll_offset = 0
        
        games_to_show = min(total_games - self.scroll_offset, max_visible_games)
        
        for i in range(games_to_show):
            game_index = i + self.scroll_offset
            if game_index >= len(filtered_games):
                break
                
            game = filtered_games[game_index]
            is_selected = i == self.selected_game
            
            # Posición de la card
            row = i // self.games_per_row
            col = i % self.games_per_row
            
            card_x = grid_start_x + col * (card_width + margin_x)
            card_y = grid_start_y + row * (card_height + margin_y)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # Efecto hover más sutil
            if is_selected:
                # Sombra más pronunciada para selección
                shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
                shadow_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surface, (0, 0, 0, 100), 
                               (0, 0, card_width, card_height), border_radius=12)
                self.screen.blit(shadow_surface, shadow_rect.topleft)
                
                # Card con borde de acento
                pygame.draw.rect(self.screen, self.colors["bg_surface"], card_rect, border_radius=12)
                pygame.draw.rect(self.screen, self.colors["accent"], card_rect, width=2, border_radius=12)
            else:
                # Sombra sutil
                shadow_rect = pygame.Rect(card_x + 3, card_y + 3, card_width, card_height)
                shadow_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surface, (0, 0, 0, 40), 
                               (0, 0, card_width, card_height), border_radius=12)
                self.screen.blit(shadow_surface, shadow_rect.topleft)
                
                pygame.draw.rect(self.screen, self.colors["bg_secondary"], card_rect, border_radius=12)
            
            # Contenido de la card más compacto
            content_padding = 15
            
            # Icono del juego más pequeño
            icon_size = 36  # Reducido
            icon_text = self.fonts["heading_md"].render(game.get("icon", "🎮"), True, self.colors["text_primary"])
            icon_x = card_rect.x + (card_rect.width - icon_text.get_width()) // 2
            self.screen.blit(icon_text, (icon_x, card_rect.y + content_padding))
            
            # Título del juego
            title_text = self.fonts["body_lg"].render(game["title"], True, self.colors["text_primary"])
            # Truncar título si es muy largo
            max_title_width = card_width - content_padding * 2
            if title_text.get_width() > max_title_width:
                # Truncar y agregar "..."
                truncated_title = game["title"]
                while self.fonts["body_lg"].size(truncated_title + "...")[0] > max_title_width and len(truncated_title) > 3:
                    truncated_title = truncated_title[:-1]
                title_text = self.fonts["body_lg"].render(truncated_title + "...", True, self.colors["text_primary"])
            
            title_x = card_rect.x + (card_rect.width - title_text.get_width()) // 2
            self.screen.blit(title_text, (title_x, card_rect.y + content_padding + 50))
            
            # Descripción más corta
            desc_lines = self.wrap_text(game["description"], card_width - content_padding * 2, self.fonts["body_sm"])
            desc_y = card_rect.y + content_padding + 80
            
            for line in desc_lines[:2]:  # Máximo 2 líneas
                line_text = self.fonts["body_sm"].render(line, True, self.colors["text_secondary"])
                line_x = card_rect.x + content_padding
                self.screen.blit(line_text, (line_x, desc_y))
                desc_y += 14
            
            # Rating más compacto
            rating = game.get("rating", 0)
            if rating > 0:
                self.draw_rating_stars(self.screen, card_rect.x + content_padding, 
                                     card_rect.y + card_rect.height - 60, rating)
            
            # Categoría y estado
            category_text = self.fonts["caption"].render(game["category"], True, self.colors["accent"])
            cat_x = card_rect.x + content_padding
            cat_y = card_rect.y + card_rect.height - 35
            self.screen.blit(category_text, (cat_x, cat_y))
            
            # Indicador de estado playable
            if game["playable"]:
                status_color = self.colors["success"]
                status_text = "●"
            else:
                status_color = self.colors["danger"]
                status_text = "●"
                
            status_render = self.fonts["caption"].render(status_text, True, status_color)
            status_x = card_rect.right - content_padding - status_render.get_width()
            self.screen.blit(status_render, (status_x, cat_y))
            
            # Overlay de no disponible más sutil
            if not game["playable"]:
                overlay = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 80))
                self.screen.blit(overlay, card_rect.topleft)
                
                na_text = self.fonts["caption"].render("Not Available", True, self.colors["danger"])
                na_x = card_rect.x + (card_rect.width - na_text.get_width()) // 2
                na_y = card_rect.y + (card_rect.height - na_text.get_height()) // 2
                self.screen.blit(na_text, (na_x, na_y))
        
        # Footer más limpio y compacto
        self.draw_footer()
    
    def draw_rating_stars(self, surface, x, y, rating):
        """Dibuja estrellas de rating más pequeñas"""
        star_size = 8  # Reducido
        star_spacing = 10  # Reducido
        
        for i in range(5):
            star_x = x + i * star_spacing
            if i < int(rating):
                star_color = self.colors["warning"]
            elif i < rating:
                star_color = self.colors["text_secondary"]
            else:
                star_color = self.colors["text_secondary"]
            
            star_text = self.fonts["caption"].render("★", True, star_color)
            surface.blit(star_text, (star_x, y))
    
    def draw_footer(self):
        """Dibuja footer más limpio"""
        footer_rect = pygame.Rect(0, self.screen.get_height() - 50, 
                                 self.screen.get_width(), 50)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], footer_rect)
        
        # Controles actualizados con scroll
        controls_text = "↑↓←→ Navigate  •  PgUp/PgDn Scroll  •  Enter Play  •  Tab Category  •  Esc Back"
        control_render = self.fonts["body_sm"].render(controls_text, True, self.colors["text_secondary"])
        
        control_x = (self.screen.get_width() - control_render.get_width()) // 2
        self.screen.blit(control_render, (control_x, footer_rect.y + 18))
    
    def wrap_text(self, text, max_width, font):
        """Envuelve texto para que quepa en el ancho especificado"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_footer(self):
        """Dibuja footer con controles"""
        footer_rect = pygame.Rect(0, self.screen.get_height() - 60, 
                                 self.screen.get_width(), 60)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], footer_rect)
        
        controls = [
            "↑↓←→ Navigate",
            "Enter Play",
            "Tab Category", 
            "Esc Back"
        ]
        
        control_x = 50
        for i, control in enumerate(controls):
            # Separar tecla de acción
            parts = control.split(' ', 1)
            if len(parts) == 2:
                key_part, action_part = parts
                
                # Dibujar tecla
                key_text = self.fonts["body_sm"].render(key_part, True, self.colors["accent"])
                self.screen.blit(key_text, (control_x, footer_rect.y + 15))
                
                # Dibujar acción
                action_text = self.fonts["body_sm"].render(action_part, True, self.colors["text_secondary"])
                self.screen.blit(action_text, (control_x + key_text.get_width() + 5, footer_rect.y + 15))
                
                control_x += key_text.get_width() + action_text.get_width() + 40
            else:
                control_text = self.fonts["body_sm"].render(control, True, self.colors["text_secondary"])
                self.screen.blit(control_text, (control_x, footer_rect.y + 15))
                control_x += control_text.get_width() + 40
    
    def handle_input(self, event):
        """Manejar input del usuario con scroll"""
        filtered_games = self.get_filtered_games()
        total_games = len(filtered_games)
        max_visible_games = 6  # 3x2
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
                
            elif event.key == pygame.K_TAB:
                # Cambiar categoría
                current_index = self.categories.index(self.current_category)
                self.current_category = self.categories[(current_index + 1) % len(self.categories)]
                self.selected_game = 0
                self.scroll_offset = 0
                return "beep"
                
            elif event.key == pygame.K_UP:
                if self.selected_game >= self.games_per_row:
                    # Mover una fila arriba
                    self.selected_game -= self.games_per_row
                else:
                    # Estamos en la primera fila, scroll hacia arriba si hay contenido
                    if self.scroll_offset > 0:
                        self.scroll_offset = max(0, self.scroll_offset - self.games_per_row)
                        # Mantener la misma columna
                        remaining_games = min(total_games - self.scroll_offset, max_visible_games)
                        if remaining_games > 0:
                            last_row_start = ((remaining_games - 1) // self.games_per_row) * self.games_per_row
                            self.selected_game = min(last_row_start + (self.selected_game % self.games_per_row), remaining_games - 1)
                return "beep"
                
            elif event.key == pygame.K_DOWN:
                visible_games = min(total_games - self.scroll_offset, max_visible_games)
                if self.selected_game + self.games_per_row < visible_games:
                    # Mover una fila abajo
                    self.selected_game += self.games_per_row
                else:
                    # Estamos en la última fila, scroll hacia abajo si hay más contenido
                    if self.scroll_offset + max_visible_games < total_games:
                        self.scroll_offset = min(total_games - max_visible_games, self.scroll_offset + self.games_per_row)
                        # Ir a la primera fila, misma columna
                        self.selected_game = self.selected_game % self.games_per_row
                return "beep"
                
            elif event.key == pygame.K_LEFT:
                if self.selected_game > 0:
                    self.selected_game -= 1
                else:
                    # Wrap around al final de la página actual
                    visible_games = min(total_games - self.scroll_offset, max_visible_games)
                    self.selected_game = visible_games - 1
                return "beep"
                
            elif event.key == pygame.K_RIGHT:
                visible_games = min(total_games - self.scroll_offset, max_visible_games)
                if self.selected_game < visible_games - 1:
                    self.selected_game += 1
                else:
                    # Wrap around al principio
                    self.selected_game = 0
                return "beep"
                
            elif event.key == pygame.K_PAGEUP:
                # Scroll una página completa hacia arriba
                if self.scroll_offset > 0:
                    self.scroll_offset = max(0, self.scroll_offset - max_visible_games)
                    self.selected_game = 0
                return "beep"
                
            elif event.key == pygame.K_PAGEDOWN:
                # Scroll una página completa hacia abajo
                if self.scroll_offset + max_visible_games < total_games:
                    self.scroll_offset = min(total_games - max_visible_games, self.scroll_offset + max_visible_games)
                    self.selected_game = 0
                return "beep"
                
            elif event.key == pygame.K_RETURN:
                if total_games > 0:
                    game_index = self.selected_game + self.scroll_offset
                    if 0 <= game_index < len(filtered_games):
                        game = filtered_games[game_index]
                        if game["playable"]:
                            success = self.launch_game(game)
                            if success:
                                return ("launch_game", game)
                            else:
                                return "error"
                return "error"
        
        return None
    
    def launch_game(self, game):
        """Lanzar un juego específico"""
        if game["builtin"]:
            game_path = Path("games/builtin") / game["filename"]
            if game_path.exists():
                try:
                    print(f"Launching game: {game['title']}")
                    result = subprocess.run([sys.executable, str(game_path)], 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"Game '{game['title']}' executed successfully.")
                    else:
                        print(f"Game error (code {result.returncode}):")
                        print("STDOUT:", result.stdout)
                        print("STDERR:", result.stderr)
                    
                    return result.returncode == 0
                except Exception as e:
                    print(f"Failed to launch game: {e}")
                    return False
        return False
    
    def update(self):
        """Actualizar animaciones"""
        self.animation_time += 1