

try:
    # Try relative import 
    from .text_element import TextElement
except ImportError:
    # Fallback to absolute import for when the module is run directly
    from text_element import TextElement
    
class InputElement(TextElement):
    def __init__(self, text, color, font, size, width, height, x=0, y=0, text_color=(0, 0, 0)):
        super().__init__(text, color, font, size, width, height, x, y, text_color)
        self.eleName = 'InputElement'
        self.blink = 0
        self.leftCenter = (0, 
                           self.rect.height//2 - self.txtr.get_height()//2)
        
    def update(self, *args):
        tin = args[1] 
        new_rel = args[0]
        self.blink_cursor_text(tin)
        self._render_text(self.leftCenter)
        self.move_relative(new_rel)

    def blink_cursor_text(self, txt_in):
        # when active add a blinking cursor to the text
        txt_in +=  '|' if self.active and self.blink < 30 else ''
        # mod 60 to make the cursor blink every 30 frames over a 60 frame period
        self.blink = (self.blink + 1) % 60
        self.text = txt_in
        self.txtr = self.font.render(self.text, False, self.text_color)
        
    def __repr__(self):
        if "|" in self.text:
            self.text = self.text[:-1]
        return f'input_element.{self.eleName}("{self.text}", {self.color}, {self.ftype}, {self.s}, {self.rect.width}, {self.rect.height}, {self.rect.x}, {self.rect.y}, {self.text_color})'
    
