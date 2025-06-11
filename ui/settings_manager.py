#!/usr/bin/env python3
"""
Settings Manager - Sistema de configuración moderna para Gaming Modern OS
VERSIÓN CORREGIDA - Arregla el error TypeError en draw_modern_card
"""

import pygame
import json
import sys
import math
from pathlib import Path

class SettingsManager:
    def __init__(self, screen, colors, fonts, config, save_callback=None):
        self.screen = screen
        self.colors = colors
        self.fonts = fonts
        self.config = config.copy()
        self.original_config = config.copy()
        self.save_callback = save_callback
        
        # Mapeo de fuentes para compatibilidad
        self.font_map = {
            'title': fonts.get('heading_xl', fonts.get('heading_lg', pygame.font.Font(None, 36))),
            'large': fonts.get('heading_lg', pygame.font.Font(None, 32)),
            'medium': fonts.get('body_lg', pygame.font.Font(None, 22)),
            'small': fonts.get('body_md', pygame.font.Font(None, 18)),
            'tiny': fonts.get('body_sm', pygame.font.Font(None, 16)),
            'caption': fonts.get('caption', pygame.font.Font(None, 14))
        }
        
        # Estado de la interfaz
        self.current_category = 0
        self.current_setting = 0
        self.animation_time = 0
        self.show_save_confirmation = False
        self.save_confirmation_timer = 0
        
        # Categorías y configuraciones
        self.categories = [
            {
                "name": "Display",
                "icon": "🖥️",
                "settings": [
                    {
                        "key": "resolution",
                        "name": "Resolution",
                        "type": "list",
                        "options": [[800, 600], [1024, 768], [1280, 720], [1920, 1080]],
                        "display_options": ["800x600", "1024x768", "1280x720", "1920x1080"],
                        "description": "Screen resolution"
                    },
                    {
                        "key": "fullscreen",
                        "name": "Fullscreen",
                        "type": "boolean",
                        "description": "Run in fullscreen mode"
                    },
                    {
                        "key": "theme",
                        "name": "Theme",
                        "type": "list",
                        "options": ["dark", "light", "auto"],
                        "display_options": ["Dark", "Light", "Auto"],
                        "description": "Interface color theme"
                    }
                ]
            },
            {
                "name": "Audio",
                "icon": "🔊",
                "settings": [
                    {
                        "key": "sound_enabled",
                        "name": "Sound Effects",
                        "type": "boolean",
                        "description": "Enable UI sound effects"
                    },
                    {
                        "key": "master_volume",
                        "name": "Master Volume",
                        "type": "slider",
                        "min": 0,
                        "max": 100,
                        "default": 80,
                        "description": "Overall audio volume"
                    },
                    {
                        "key": "music_volume",
                        "name": "Music Volume",
                        "type": "slider",
                        "min": 0,
                        "max": 100,
                        "default": 60,
                        "description": "Background music volume"
                    }
                ]
            },
            {
                "name": "Performance",
                "icon": "⚡",
                "settings": [
                    {
                        "key": "performance_mode",
                        "name": "Performance Mode",
                        "type": "list",
                        "options": ["low", "balanced", "high", "ultra"],
                        "display_options": ["Low", "Balanced", "High", "Ultra"],
                        "description": "Graphics performance level"
                    },
                    {
                        "key": "fps_limit",
                        "name": "FPS Limit",
                        "type": "list",
                        "options": [30, 60, 120, 144, 0],
                        "display_options": ["30 FPS", "60 FPS", "120 FPS", "144 FPS", "Unlimited"],
                        "description": "Maximum frames per second"
                    },
                    {
                        "key": "auto_scan_games",
                        "name": "Auto Scan Games",
                        "type": "boolean",
                        "description": "Automatically detect new games"
                    }
                ]
            },
            {
                "name": "System",
                "icon": "⚙️",
                "settings": [
                    {
                        "key": "boot_animation",
                        "name": "Boot Animation",
                        "type": "boolean",
                        "description": "Show startup animation"
                    },
                    {
                        "key": "minimize_to_tray",
                        "name": "Minimize to Tray",
                        "type": "boolean",
                        "description": "Minimize to system tray"
                    },
                    {
                        "key": "auto_save_settings",
                        "name": "Auto Save Settings",
                        "type": "boolean",
                        "default": True,
                        "description": "Automatically save configuration changes"
                    },
                    {
                        "key": "check_updates",
                        "name": "Check for Updates",
                        "type": "boolean",
                        "default": True,
                        "description": "Check for system updates on startup"
                    }
                ]
            }
        ]
        
        self.ensure_default_values()
    
    def ensure_default_values(self):
        """Asegurar que todas las configuraciones tengan valores por defecto"""
        defaults = {
            "master_volume": 80,
            "music_volume": 60,
            "fps_limit": 60,
            "auto_save_settings": True,
            "check_updates": True
        }
        
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
    
    def play_sound(self, sound_type="click"):
        """Reproducir sonidos de interfaz"""
        if not self.config.get("sound_enabled", True):
            return
            
        try:
            frequencies = {
                "click": 1000,
                "select": 1200,
                "toggle": 800,
                "save": 1500,
                "error": 400,
                "navigate": 600
            }
            
            frequency = frequencies.get(sound_type, 800)
            duration = 60
            
            sample_rate = 22050
            frames = int(duration * sample_rate / 1000)
            arr = []
            
            for i in range(frames):
                t = float(i) / sample_rate
                envelope = math.exp(-t * 8)
                wave = math.sin(2 * math.pi * frequency * t) * envelope * 0.08
                arr.append([int(32767 * wave)] * 2)
            
            sound = pygame.sndarray.make_sound(pygame.array.array('h', arr))
            sound.play()
        except:
            pass
    
    def draw_modern_card(self, surface, rect, color=None, elevation=1, selected=False):
        """Dibuja una card moderna con sombra - FUNCIÓN CORREGIDA"""
        # Si no se proporciona color, usar color por defecto
        if color is None:
            card_color = self.colors["bg_surface"] if selected else self.colors["bg_secondary"]
        else:
            card_color = color
        
        # Sombra
        shadow_offset = elevation * 3
        shadow_rect = pygame.Rect(rect.x + shadow_offset, rect.y + shadow_offset, 
                                 rect.width, rect.height)
        shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        shadow_alpha = 80 if selected else 40
        pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                        (0, 0, rect.width, rect.height), border_radius=12)
        surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Card principal
        pygame.draw.rect(surface, card_color, rect, border_radius=12)
        
        # Borde de selección
        if selected:
            pygame.draw.rect(surface, self.colors["accent"], rect, width=2, border_radius=12)
    
    def draw_slider(self, surface, x, y, width, height, value, min_val, max_val, selected=False):
        """Dibuja un slider moderno"""
        # Track del slider
        track_rect = pygame.Rect(x, y + height // 2 - 2, width, 4)
        pygame.draw.rect(surface, self.colors["bg_surface"], track_rect, border_radius=2)
        
        # Progreso
        progress = (value - min_val) / (max_val - min_val)
        progress_width = int(width * progress)
        if progress_width > 0:
            progress_rect = pygame.Rect(x, y + height // 2 - 2, progress_width, 4)
            pygame.draw.rect(surface, self.colors["accent"], progress_rect, border_radius=2)
        
        # Handle del slider
        handle_x = x + progress_width - 8
        handle_y = y + height // 2 - 8
        handle_rect = pygame.Rect(handle_x, handle_y, 16, 16)
        
        handle_color = self.colors["accent"] if selected else self.colors["text_primary"]
        pygame.draw.circle(surface, handle_color, handle_rect.center, 8)
        
        # Borde del handle
        pygame.draw.circle(surface, self.colors["text_primary"], handle_rect.center, 8, 2)
        
        return handle_rect
    
    def draw_toggle(self, surface, x, y, width, height, value, selected=False):
        """Dibuja un toggle switch moderno"""
        # Background del toggle
        bg_color = self.colors["accent"] if value else self.colors["bg_surface"]
        toggle_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, toggle_rect, border_radius=height // 2)
        
        # Handle del toggle
        handle_size = height - 4
        handle_x = x + (width - handle_size - 2) if value else x + 2
        handle_y = y + 2
        handle_rect = pygame.Rect(handle_x, handle_y, handle_size, handle_size)
        
        handle_color = self.colors["text_primary"]
        pygame.draw.ellipse(surface, handle_color, handle_rect)
        
        # Borde si está seleccionado
        if selected:
            pygame.draw.rect(surface, self.colors["text_primary"], toggle_rect, width=2, border_radius=height // 2)
        
        return toggle_rect
    
    def draw_dropdown(self, surface, x, y, width, height, options, selected_index, selected=False):
        """Dibuja un dropdown moderno"""
        # Background
        bg_color = self.colors["bg_surface"] if selected else self.colors["bg_secondary"]
        dropdown_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, dropdown_rect, border_radius=8)
        
        # Borde
        border_color = self.colors["accent"] if selected else self.colors["text_secondary"]
        pygame.draw.rect(surface, border_color, dropdown_rect, width=2, border_radius=8)
        
        # Texto seleccionado
        if 0 <= selected_index < len(options):
            text = str(options[selected_index])
            text_surface = self.font_map["small"].render(text, True, self.colors["text_primary"])
            text_x = x + 12
            text_y = y + (height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        
        # Flecha
        arrow_x = x + width - 20
        arrow_y = y + height // 2
        arrow_points = [
            (arrow_x, arrow_y - 4),
            (arrow_x + 8, arrow_y + 4),
            (arrow_x - 8, arrow_y + 4)
        ]
        pygame.draw.polygon(surface, self.colors["text_secondary"], arrow_points)
        
        return dropdown_rect
    
    def draw_categories_sidebar(self):
        """Dibuja la barra lateral con categorías"""
        sidebar_width = 200
        sidebar_rect = pygame.Rect(0, 0, sidebar_width, self.screen.get_height())
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], sidebar_rect)
        
        # Título de la sidebar
        title_text = self.font_map["medium"].render("Settings", True, self.colors["text_primary"])
        self.screen.blit(title_text, (20, 25))
        
        # Categorías
        start_y = 80
        category_height = 50
        
        for i, category in enumerate(self.categories):
            is_selected = i == self.current_category
            
            # Card de categoría
            cat_y = start_y + i * (category_height + 10)
            cat_rect = pygame.Rect(15, cat_y, sidebar_width - 30, category_height)
            
            if is_selected:
                pygame.draw.rect(self.screen, self.colors["accent"], cat_rect, border_radius=8)
                text_color = self.colors["text_primary"]
                icon_color = self.colors["text_primary"]
            else:
                pygame.draw.rect(self.screen, self.colors["bg_surface"], cat_rect, border_radius=8)
                text_color = self.colors["text_secondary"]
                icon_color = self.colors["text_secondary"]
            
            # Ícono
            icon_text = self.font_map["medium"].render(category["icon"], True, icon_color)
            self.screen.blit(icon_text, (cat_rect.x + 15, cat_rect.y + 12))
            
            # Nombre
            name_text = self.font_map["small"].render(category["name"], True, text_color)
            self.screen.blit(name_text, (cat_rect.x + 50, cat_rect.y + 15))
    
    def draw_settings_panel(self):
        """Dibuja el panel principal de configuraciones - FUNCIÓN CORREGIDA"""
        panel_x = 220
        panel_width = self.screen.get_width() - panel_x - 20
        
        # Header del panel
        header_rect = pygame.Rect(panel_x, 20, panel_width, 60)
        # CORRECCIÓN: Pasar solo el rectángulo y usar color por defecto
        self.draw_modern_card(self.screen, header_rect)
        
        # Título de la categoría actual
        category = self.categories[self.current_category]
        cat_title = f"{category['icon']} {category['name']}"
        title_text = self.font_map["large"].render(cat_title, True, self.colors["text_primary"])
        self.screen.blit(title_text, (header_rect.x + 20, header_rect.y + 15))
        
        # Configuraciones
        settings_start_y = 100
        setting_height = 80
        settings = category["settings"]
        
        for i, setting in enumerate(settings):
            is_selected = i == self.current_setting
            
            # Card de configuración
            setting_y = settings_start_y + i * (setting_height + 15)
            setting_rect = pygame.Rect(panel_x, setting_y, panel_width, setting_height)
            
            # CORRECCIÓN: Usar la función corregida
            self.draw_modern_card(self.screen, setting_rect, 
                                 elevation=2 if is_selected else 1, selected=is_selected)
            
            # Contenido de la configuración
            content_x = setting_rect.x + 20
            content_y = setting_rect.y + 15
            
            # Nombre y descripción
            name_text = self.font_map["small"].render(setting["name"], True, self.colors["text_primary"])
            self.screen.blit(name_text, (content_x, content_y))
            
            desc_text = self.font_map["tiny"].render(setting["description"], True, self.colors["text_secondary"])
            self.screen.blit(desc_text, (content_x, content_y + 20))
            
            # Control según el tipo
            control_x = setting_rect.x + setting_rect.width - 250
            control_y = content_y + 5
            
            current_value = self.config.get(setting["key"])
            
            if setting["type"] == "boolean":
                self.draw_toggle(self.screen, control_x, control_y, 50, 25, 
                               current_value, is_selected)
            
            elif setting["type"] == "list":
                options = setting.get("display_options", setting["options"])
                try:
                    if setting["key"] == "resolution":
                        current_index = setting["options"].index(current_value)
                    else:
                        current_index = setting["options"].index(current_value)
                except (ValueError, TypeError):
                    current_index = 0
                
                self.draw_dropdown(self.screen, control_x, control_y, 200, 30, 
                                 options, current_index, is_selected)
            
            elif setting["type"] == "slider":
                min_val = setting.get("min", 0)
                max_val = setting.get("max", 100)
                if current_value is None:
                    current_value = setting.get("default", min_val)
                    self.config[setting["key"]] = current_value
                
                self.draw_slider(self.screen, control_x, control_y, 180, 30, 
                               current_value, min_val, max_val, is_selected)
                
                # Mostrar valor
                value_text = f"{current_value}%"
                value_surface = self.font_map["tiny"].render(value_text, True, self.colors["text_secondary"])
                self.screen.blit(value_surface, (control_x + 190, control_y + 8))
    
    def draw_footer(self):
        """Dibuja el footer con controles"""
        footer_height = 60
        footer_rect = pygame.Rect(0, self.screen.get_height() - footer_height, 
                                 self.screen.get_width(), footer_height)
        pygame.draw.rect(self.screen, self.colors["bg_secondary"], footer_rect)
        
        # Controles
        controls = [
            "Tab Change Category",
            "↑↓ Navigate",
            "←→ Adjust", 
            "Enter Toggle",
            "S Save",
            "R Reset",
            "Esc Back"
        ]
        
        control_x = 30
        for control in controls:
            parts = control.split(' ', 1)
            if len(parts) == 2:
                key_part, action_part = parts
                
                # Tecla
                key_text = self.font_map["tiny"].render(key_part, True, self.colors["accent"])
                self.screen.blit(key_text, (control_x, footer_rect.y + 15))
                
                # Acción
                action_text = self.font_map["tiny"].render(action_part, True, self.colors["text_secondary"])
                self.screen.blit(action_text, (control_x + key_text.get_width() + 5, footer_rect.y + 15))
                
                control_x += key_text.get_width() + action_text.get_width() + 25
        
        # Indicador de cambios
        if self.has_unsaved_changes():
            changes_text = "● Unsaved changes"
            changes_surface = self.font_map["tiny"].render(changes_text, True, self.colors["warning"])
            changes_x = self.screen.get_width() - changes_surface.get_width() - 20
            self.screen.blit(changes_surface, (changes_x, footer_rect.y + 25))
        
        # Confirmación de guardado
        if self.show_save_confirmation:
            save_text = "✓ Settings saved!"
            save_surface = self.font_map["tiny"].render(save_text, True, self.colors["success"])
            save_x = self.screen.get_width() - save_surface.get_width() - 20
            self.screen.blit(save_surface, (save_x, footer_rect.y + 10))
    
    def has_unsaved_changes(self):
        """Verificar si hay cambios sin guardar"""
        return self.config != self.original_config
    
    def save_settings(self):
        """Guardar configuraciones"""
        try:
            config_path = Path("config/settings.json")
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            self.original_config = self.config.copy()
            self.show_save_confirmation = True
            self.save_confirmation_timer = 180
            
            if self.save_callback:
                self.save_callback(self.config)
            
            self.play_sound("save")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.play_sound("error")
            return False
    
    def reset_to_defaults(self):
        """Resetear a valores por defecto"""
        defaults = {
            "theme": "dark",
            "resolution": [1100, 700],
            "fullscreen": False,
            "sound_enabled": True,
            "boot_animation": True,
            "performance_mode": "balanced",
            "auto_scan_games": True,
            "minimize_to_tray": False,
            "auto_save_settings": True,
            "check_updates": True,
            "master_volume": 80,
            "music_volume": 60,
            "fps_limit": 60
        }
        
        self.config.update(defaults)
        self.play_sound("toggle")
    
    def handle_input(self, event):
        """Manejar input del usuario"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_TAB:
                self.current_category = (self.current_category + 1) % len(self.categories)
                self.current_setting = 0
                self.play_sound("navigate")
                return "navigate"
            
            elif event.key == pygame.K_UP:
                settings_count = len(self.categories[self.current_category]["settings"])
                if settings_count > 0:
                    self.current_setting = (self.current_setting - 1) % settings_count
                    self.play_sound("navigate")
                return "navigate"
            
            elif event.key == pygame.K_DOWN:
                settings_count = len(self.categories[self.current_category]["settings"])
                if settings_count > 0:
                    self.current_setting = (self.current_setting + 1) % settings_count
                    self.play_sound("navigate")
                return "navigate"
            
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                return self.adjust_current_setting(event.key == pygame.K_RIGHT)
            
            elif event.key == pygame.K_RETURN:
                return self.toggle_current_setting()
            
            elif event.key == pygame.K_s:
                success = self.save_settings()
                return "save" if success else "error"
            
            elif event.key == pygame.K_r:
                self.reset_to_defaults()
                return "reset"
        
        return None
    
    def adjust_current_setting(self, increase=True):
        """Ajustar la configuración actual"""
        category = self.categories[self.current_category]
        if self.current_setting >= len(category["settings"]):
            return None
            
        setting = category["settings"][self.current_setting]
        key = setting["key"]
        current_value = self.config.get(key)
        
        if setting["type"] == "boolean":
            self.config[key] = not current_value
            self.play_sound("toggle")
            return "toggle"
        
        elif setting["type"] == "list":
            options = setting["options"]
            try:
                if key == "resolution":
                    current_index = options.index(current_value)
                else:
                    current_index = options.index(current_value)
            except (ValueError, TypeError):
                current_index = 0
            
            if increase:
                new_index = (current_index + 1) % len(options)
            else:
                new_index = (current_index - 1) % len(options)
            
            self.config[key] = options[new_index]
            self.play_sound("select")
            return "select"
        
        elif setting["type"] == "slider":
            min_val = setting.get("min", 0)
            max_val = setting.get("max", 100)
            step = 5
            
            if current_value is None:
                current_value = setting.get("default", min_val)
            
            if increase:
                new_value = min(max_val, current_value + step)
            else:
                new_value = max(min_val, current_value - step)
            
            self.config[key] = new_value
            self.play_sound("select")
            return "select"
        
        return None
    
    def toggle_current_setting(self):
        """Alternar la configuración actual"""
        category = self.categories[self.current_category]
        if self.current_setting >= len(category["settings"]):
            return None
            
        setting = category["settings"][self.current_setting]
        
        if setting["type"] == "boolean":
            key = setting["key"]
            self.config[key] = not self.config.get(key, False)
            self.play_sound("toggle")
            return "toggle"
        
        return None
    
    def update(self):
        """Actualizar animaciones y timers"""
        self.animation_time += 1
        
        if self.show_save_confirmation:
            self.save_confirmation_timer -= 1
            if self.save_confirmation_timer <= 0:
                self.show_save_confirmation = False
    
    def draw(self):
        """Dibujar la interfaz completa"""
        self.screen.fill(self.colors["bg_primary"])
        self.draw_categories_sidebar()
        self.draw_settings_panel()
        self.draw_footer()
    
    def get_config(self):
        """Obtener configuración actual"""
        return self.config.copy()