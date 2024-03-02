# Author: Cameron Kerley
# Date: 03/1/2024

import pygame

from .input_txt import Input_txt

class Txt_confirm(Input_txt):
    def __init__(self, active_color='lightskyblue3', passive_color='chartreuse4', prompt_subject='default_text', add_cursor_box=True, button_labels=["Confirm", "Cancel"]):
        """ 
        a class for creating a confirm/cancel prompt with an input box above and a text above that.

        inherits from Input_txt class. add_cursor_box not used, but kept for future use like file name input with confirmation.

        active button is user's choice, passive button is not. confirm with okay button.    
        """
        super().__init__(active_color, passive_color,
                         prompt_subject, add_cursor_box=add_cursor_box)
        # reset rect_text at the top of the screen, all other rects are relative to this one
        if not add_cursor_box:
            self.rect_text = self.rect_text.move(0, -40)
        # choice represents yes=True, no=False, None=not chosen, prevents user from clicking okay before making a choice
        self.choice = None
        # create the buttons for the prompt
        self.buttons = []
        # set the positions of the buttons relative to the rect_text inherited from Input_txt
        self.button_offsets = [(0, 40), (100, 40)]
        confirm, cancel = self.button_offsets
        y1, y2 = confirm
        n1, n2 = cancel
        button_positions = [(10+y1, self.rect_text.y + y2),
                            (10+n1, self.rect_text.y + n2),]

        #
        # create the buttons placing them in a list of dictionaries, each dict contains the button's properties
        self.add_buttons(button_labels, button_positions)
        # unpack the buttons, this menu has 2 fixed buttons so we can unpack them for ease of reading
        self.confirm, self.cancel = self.buttons[:2]
        self.exclude = []
        self.len_b_norm = len(self.buttons)

    def add_buttons(self, button_labels, button_positions, width=75, height=30):
        for i in range(len(button_positions)):
            button_rect = pygame.Rect(button_positions[i][0],
                                      button_positions[i][1],
                                      width, height)
            self.buttons.append({'rect': button_rect,
                                 'color': self.passive_color,
                                 'label': button_labels[i]})

    def handle_event(self, event):
        # run the inherited handle_event method
        super().handle_event(event)
        # menu specific event handling after inherited event handling for ease of reading
        self.pos_update(self.button_offsets, self.buttons)

    def active_box(self, event):
        # run the inherited active_box method
        super().active_box(event)
        # we are appending to the inherited method with dependent behavior
        if self.confirm['rect'].collidepoint(event.pos) and self.text != '':
            self.choice = True
            # change the color of the button that was clicked
            self.confirm['color'] = self.active_color
            self.cancel['color'] = self.passive_color
            self.destroy = True
        elif self.cancel['rect'].collidepoint(event.pos):
            self.choice = False
            # change the color of the button that was clicked
            self.cancel['color'] = self.active_color
            self.confirm['color'] = self.passive_color
            self.destroy = True
            self.text = ''

    def blitme(self, screen, exclude=[]):
        # run the inherited blitme method
        super().blitme(screen)
        if len(self.buttons) > 2:
            # buttons past the first 2 are user defined so we just need 3 an on from buttons
            extra_buttons = self.buttons[2:]
            extra_buttons.insert(0, self.confirm)
            extra_buttons.insert(1, self.cancel)
            # remove any buttons that areq in the exclude list
            if not exclude:
                exclude = self.exclude
            
            extra_buttons = [button for button in extra_buttons if button not in exclude]
            self.draw_panels(screen, panels=extra_buttons)
            self.draw_all_elements(screen, extra_buttons)
        else:
            self.draw_panels(screen, panels=[self.confirm, self.cancel])
            self.draw_all_elements(screen, [self.confirm, self.cancel])

    def exit_value(self) -> str:
        try:
            return str(self.text)
        except ValueError:
            print(
                f'Error recived {self.choice}.\n Input must be str not _{type(self.choice)}_')
            pygame.quit()