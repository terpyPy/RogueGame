# Author: Cameron Kerley
# Date: 03/1/2024

import pygame
from pygame.sprite import Sprite

from .invalidColorElement import InvalidColorElement

class Colors(Sprite):
    
    def __init__(self):
        super().__init__()
        self.colors = {'panel': pygame.Color('darkgrey'),
                       'bg': pygame.Color('black'),
                       'font': pygame.Color('white'),
                       'active': pygame.Color('lightskyblue3'),
                       'passive': pygame.Color('chartreuse4')}

    @property
    def panel_color(self):
        return self.colors['panel']

    @property
    def bg_color(self):
        return self.colors['bg']

    @property
    def font_color(self):
        return self.colors['font']

    @property
    def active_color(self):
        return self.colors['active']

    @property
    def passive_color(self):
        return self.colors['passive']

    @panel_color.setter
    def panel_color(self, color: tuple):
        self.colors['panel'] = color

    @bg_color.setter
    def bg_color(self, color: tuple):
        self.colors['bg'] = color

    @font_color.setter
    def font_color(self, color: tuple):
        self.colors['font'] = color

    @active_color.setter
    def active_color(self, color: tuple):
        self.colors['active'] = color

    @passive_color.setter
    def passive_color(self, color: tuple):
        self.colors['passive'] = color

    def modify_color(self, element: str, color: tuple) -> None:
        
        if element not in self.colors.keys():
            raise InvalidColorElement(element)
        else: 
            self.colors[element] = color