import pygame

class BaseElement(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.color = color
        self.rect = self.image.get_rect()
        self.image.fill(self.color)
        self.eleName = 'BaseElement'
        self.x = 0
        self.y = 0
        self.relMove = (0, 0)
        self.class_string = f'{self.__class__.__name__}({self.color}, {self.rect.width}, {self.rect.height})'
        
    def change_color(self, c):
        self.color = c
        self.image.fill(c)
        
    def update(self, *args):
        """
        this method is called by the sprite group to update .
        the sprite behavior should be implemented per subclass type.
        """
        pass
    
    def move_relative(self, pos):
        if pos != self.relMove:
            self.relMove = pos
            self.rect.move_ip(pos)
    
    def __repr__(self):
        # string representation of the class
        
        return self.class_string
    
class Panel(BaseElement):
    """
    background panels are the root of all menu groups.\n
    all other elements are drawn and move relative to the panels screen position.
    """
    def __init__(self, color, width, height, x=0, y=0):
        super().__init__(color, width, height)
        self.eleName = 'Panel'
        self.rect.x, self.rect.y = x, y
        
        
    def update(self, *args):
        self.move_relative(args[0])
        # fill the panel with our background color
        self.image.fill(self.color)

    def point_collide(self, pos):
        return self.rect.collidepoint(pos)
    
    def __repr__(self):
        return f'base_Element.{self.eleName}({self.color}, {self.rect.width}, {self.rect.height}, {self.rect.x}, {self.rect.y})'
        
class Trim(Panel):
    """panel wrapper for a smaller panel"""
    def __init__(self, color, width, height, x=0, y=0):
        super().__init__(color, width, height, x, y)
        self.eleName = 'Trim'