from pygame.font import Font
# --- create the ui elements from scratch ---
# menuBg = base_Element.Panel((120, 120, 120), *(200, 100))
# x, y = menuBg.rect.midtop
# w, h = 125, 50
# input_line = input_element.InputElement(msg, (0,0,255), None, 20, w,h, *(x-w//2, y))
# yes = text_element.TextElement('Yes', (0, 255, 0), None, 18, w//2, h//2, *input_line.rect.bottomleft)
# no = text_element.TextElement('No', (255, 0, 0), None, 18, w//2, h//2, *yes.rect.topright)
# ui_group.add(menuBg)
# ui_group.add(input_line)
# ui_group.add([yes, no])
# --- end of create ui elements from scratch ---
try:
    # Try relative import 
    from .base_Element import BaseElement
except ImportError:
    # Fallback to absolute import for when the module is run directly
    from base_Element import BaseElement

class TextElement(BaseElement):
    def __init__(self, text, color, font, size, width, height, x=0, y=0, text_color=(0, 0, 0)):
        super().__init__(color, width, height)
        self.text = text
        self.text_color = text_color
        self.font = Font(font, size)
        self.eleName = 'TextElement'
        self.txtr = self.font.render(self.text, False, self.text_color)
        self.rect.x, self.rect.y = x, y
        self.active = False
        self.ftype = font
        self.s = size
        self.text_center = (self.rect.width//2 - self.txtr.get_width()//2, 
                            self.rect.height//2 - self.txtr.get_height()//2)
        
    def update(self, *args):
        new_rel = args[0]
        self.txtr = self.font.render(self.text, False, self.text_color)
        self._render_text(self.text_center)
        self.move_relative(new_rel)
        
    def _render_text(self, txt_loc, **kwargs):
        self.image.fill(self.color)
        self.image.blit(self.txtr, txt_loc)
        
    def change_txt_color(self, c):
        self.text_color = c
    
    def check_active(self, pos, inplace=False):
        if inplace:
            self.active = self.rect.collidepoint(pos)
            return self.active
        else:
            return self.rect.collidepoint(pos)        
    
    def __repr__(self):
        return f'text_element.{self.eleName}("{self.text}", {self.color}, {self.ftype}, {self.s}, {self.rect.width}, {self.rect.height}, {self.rect.x}, {self.rect.y}, {self.text_color})'
    
class InteractiveTextElement(TextElement):
    # just a wrapper class for the text element that responds to mouse events
    def __init__(self, text, color, font, size, width, height, x=0, y=0, text_color=(0, 0, 0)):
        super().__init__(text, color, font, size, width, height, x, y, text_color)
        self.eleName = 'InteractiveTextElement'