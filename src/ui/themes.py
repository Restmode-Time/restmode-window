from src.utils.qt_compat import QColor

# Define the theme color palettes
THEMES = {
    'dark': {
        'background': QColor(18, 18, 18),
        'text': QColor(255, 255, 255),
        'accent': QColor(0, 150, 255),
        'gradient_start': QColor(25, 25, 35),
        'gradient_end': QColor(15, 15, 25)
    },
    'light': {
        'background': QColor(245, 245, 245),
        'text': QColor(30, 30, 30),
        'accent': QColor(0, 120, 215),
        'gradient_start': QColor(250, 250, 255),
        'gradient_end': QColor(240, 240, 250)
    },
    'blue': {
        'background': QColor(15, 25, 45),
        'text': QColor(255, 255, 255),
        'accent': QColor(0, 200, 255),
        'gradient_start': QColor(20, 35, 60),
        'gradient_end': QColor(10, 20, 40)
    },
    'green': {
        'background': QColor(20, 40, 20),
        'text': QColor(255, 255, 255),
        'accent': QColor(0, 255, 150),
        'gradient_start': QColor(25, 50, 25),
        'gradient_end': QColor(15, 30, 15)
    },
    'purple': {
        'background': QColor(40, 20, 50),
        'text': QColor(255, 255, 255),
        'accent': QColor(200, 100, 255),
        'gradient_start': QColor(50, 25, 65),
        'gradient_end': QColor(30, 15, 40)
    }
}

def get_themes():
    """Returns the dictionary of defined themes."""
    return THEMES 