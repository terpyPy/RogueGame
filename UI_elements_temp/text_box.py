# Author: Cameron Kerley
# Date: 03/1/2024

from .input_txt import Input_txt

class Text_box(Input_txt):
    def __init__(self, active_color='lightskyblue3', passive_color='chartreuse4', prompt_subject='default_text') -> None:
        """ 
        a class for creating a text box with no input line. subclasses Input_txt class.
        """
        super().__init__(active_color, passive_color, prompt_subject, add_cursor_box=False,exit_types=[str])
        # reset rect_text at the top of the screen, all other rects are relative to this one

        self.rect_text = self.rect_text.move(0, -40)

    def handle_event(self, event):
        # run the inherited handle_event method
        super().handle_event(event)

    def blitme(self, screen):
        # run the inherited blitme method
        super().blitme(screen)

    def exit_value(self):
        return self.text