import panel as pn
import json
import os
from pathlib import Path

class ThemeManager:
    _instance = None
    _config_file = Path.home() / '.crp_theme_config.json'

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize theme manager with dark grey theme"""
        self.current_theme = 'dark'
        self._apply_theme()
        
    def _apply_theme(self):
        """Apply dark grey theme with good contrast"""
        # Set Panel's theme to dark
        pn.state.theme = 'dark'
        
        # Apply custom CSS for better contrast
        custom_css = """
        :root {
            --background-color: #2b2b2b;
            --text-color: #ffffff;
            --accent-color: #4a9eff;
        }
        
        body {
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }
        
        .panel-widget-box {
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
        }
        
        .panel-input {
            background-color: #3b3b3b !important;
            color: var(--text-color) !important;
        }
        
        .panel-button {
            background-color: var(--accent-color) !important;
            color: #ffffff !important;
        }
        
        .panel-button:hover {
            background-color: #5aaeff !important;
            color: #ffffff !important;
        }
        
        .panel-tabs {
            background-color: #3b3b3b !important;
        }
        
        .panel-tab {
            color: var(--text-color) !important;
        }
        
        .panel-tab.active {
            background-color: var(--accent-color) !important;
            color: #ffffff !important;
        }

        /* Additional styles to ensure text is white */
        .panel-widget-box * {
            color: #ffffff !important;
        }

        .panel-input input {
            color: #ffffff !important;
        }

        .panel-select select {
            color: #ffffff !important;
        }

        .panel-textarea textarea {
            color: #ffffff !important;
        }

        /* Header styles */
        .app-header {
            background-color: #1a1a1a;
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid var(--accent-color);
        }

        .app-header img {
            max-width: 300px;
            height: auto;
            margin-bottom: 10px;
        }
        """
        
        # Add the custom CSS to Panel
        pn.config.raw_css.append(custom_css)
        
        # Clear Panel's cache to refresh components
        if hasattr(pn.state, 'cache'):
            pn.state.cache.clear()

    def get_theme(self):
        """Get current theme"""
        return self.current_theme

    def create_logo(self, logo_url, width=200, height=None):
        """Create a logo widget from a URL
        
        Args:
            logo_url (str): URL of the logo image
            width (int): Width of the logo in pixels
            height (int, optional): Height of the logo in pixels. If None, maintains aspect ratio.
            
        Returns:
            panel.pane.HTML: A Panel HTML widget containing the logo
        """
        # Create HTML for the logo with proper sizing
        height_style = f"height: {height}px;" if height else "height: auto;"
        logo_html = f"""
        <div style="text-align: center; margin: 10px 0;">
            <img src="{logo_url}" 
                 style="width: {width}px; {height_style} max-width: 100%;" 
                 alt="Logo">
        </div>
        """
        return pn.pane.HTML(logo_html)

    def create_header(self):
        """Create a header with the logo"""
        header_html = """
        <div class="app-header">
            <img src="https://i.imgur.com/nuFPYE7.png" alt="Logo">
        </div>
        """
        return pn.pane.HTML(header_html)

# Create a singleton instance
theme_manager = ThemeManager() 