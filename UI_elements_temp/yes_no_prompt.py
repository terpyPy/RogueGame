import pygame

from .input_txt import Input_txt

class Yes_no_prompt(Input_txt):
    def __init__(self, active_color='lightskyblue3', passive_color='chartreuse4', prompt_subject='default_text', add_cursor_box=False):
        """ 
        a class for creating a yes/no prompt with a text box above it optionally. 

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
        self.button_offsets = ((0, 40), (100, 40), (50, 80))
        y, n, o = self.button_offsets
        y1, y2 = y
        n1, n2 = n
        o1, o2 = o
        button_positions = [(10+y1, self.rect_text.y + y2),
                            (10+n1, self.rect_text.y + n2),
                            (10+o1, self.rect_text.y + o2)]
        button_labels = ["Yes", "No", "Okay"]
        #
        # create the buttons placing them in a list of dictionaries, each dict contains the button's properties
        for i in range(len(button_positions)):
            button_rect = pygame.Rect(button_positions[i][0],
                                      button_positions[i][1],
                                      75, 30)
            self.buttons.append({'rect': button_rect,
                                 'color': self.passive_color,
                                 'label': button_labels[i]})
        # unpack the buttons, this menu has 3 fixed buttons so we can unpack them for ease of reading
        self.yes, self.no, self.okay = self.buttons[:3]

    def handle_event(self, event):
        # run the inherited handle_event method
        super().handle_event(event)
        # menu specific event handling after inherited event handling for ease of reading
        self.pos_update(self.button_offsets, self.buttons)

    def active_box(self, event):
        # run the inherited active_box method
        super().active_box(event)
        # we are appending to the inherited method with dependent behavior
        if self.yes['rect'].collidepoint(event.pos):
            self.choice = True
            # change the color of the button that was clicked
            self.yes['color'] = self.active_color
            self.no['color'] = self.passive_color
        elif self.no['rect'].collidepoint(event.pos):
            self.choice = False
            # change the color of the button that was clicked
            self.no['color'] = self.active_color
            self.yes['color'] = self.passive_color
        elif self.okay['rect'].collidepoint(event.pos) and self.choice != None:
            # if the user has made a choice and clicks the okay button, destroy the prompt
            self.destroy = True
            self.okay['color'] = self.active_color

    def blitme(self, screen):
        # run the inherited blitme method
        super().blitme(screen)
        self.draw_panels(screen, panels=[self.yes, self.okay, self.no])
        self.draw_all_elements(screen, [self.yes, self.okay, self.no])

    def draw_panels(self, screen, panels=[]):
        '''
        uses the inherited draw_panels method to draw additional panels
        '''
        super().draw_panels(screen, panels)
        # draws a button without adding a panel to its background
        

    def exit_value(self) -> bool:
        try:
            return bool(self.choice)
        except ValueError:
            print(
                f'Error recived {self.choice}.\n Input must be boolean not _{type(self.choice)}_')
            pygame.quit()