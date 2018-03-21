from kivy.config import Config, ConfigParser


Config.set('kivy', 'keyboard_mode', '')
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')
Config.set('graphics', 'fullscreen', '0')
# Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '200')
Config.set('graphics', 'left', '550')
Config.set('graphics', 'show_cursor','0')
Config.write()
# Config.read()