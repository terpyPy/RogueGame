# Author: Cameron Kerley
# Date: 03/1/2024

import pygame
import inspect
from .txt_confirm import Txt_confirm

class DebugMenu(Txt_confirm):
    def __init__(self, subject='-debug menu-', add_cursor=True, buttons=['direction: ', '']):
        super().__init__(prompt_subject=subject, add_cursor_box=add_cursor, button_labels=buttons)
        # make debug rects bigger
        self.buttons[0]['rect'].width += 50
        self.buttons[1]['rect'].width = 225
        self.rect_text.width += 125
        self.prompt['rect'].width += 125
        
        
        # add player xy_field button below the prompt
        self.button_offsets.append((0, 80))
        self.add_buttons(['xy:'], [(0, 80)], width=150, height=30)
        
        self.button_offsets.append((175, 80))
        self.add_buttons(['fps:'], [(175, 80)])
        # len of buttons before adding error buttons, used to index the error buttons 
        self.len_b_norm = len(self.buttons)-1
        
        self.button_offsets.append((0, 120))
        self.add_buttons([f'default-txt'], [(0, 120)], width=375, height=125)
        # make a surface for the error message
        m_rect = self.buttons[-1]['rect']
        self.err_surf = pygame.Surface((m_rect.width, m_rect.height))
        self.e_font = pygame.font.Font(None, 20)
        
    @property
    def xy_field(self) -> str:
        return self.buttons[2]

    @xy_field.setter
    def xy_field(self, value):
        self.buttons[2]['label'] = value

    @property
    def frame_counts(self) -> str:
        return self.prompt['label']

    @frame_counts.setter
    def frame_counts(self, value):
        self.prompt['label'] = value

    @property
    def direction_field(self) -> str:
        return self.buttons[1]['label']

    @direction_field.setter
    def direction_field(self, value):
        self.buttons[1]['label'] = value

    @property
    def fps_field(self) -> str:
        return self.buttons[3]['label']

    @fps_field.setter
    def fps_field(self, value):
        self.buttons[3]['label'] = value

    @property
    def error_field(self) -> dict:
        return self.buttons[self.len_b_norm+1]
    
    @error_field.setter
    def error_field(self, value):
        self.buttons[self.len_b_norm+1]['label'] = value
             
    def set_all(self, **kwargs):
        """
        set all text properties of the debug menu

        i.e. menu.set_all(frame_counts=f'{object}', ...)
        """
        # find any properties in the kwargs that are private name space
        violations = self.scope_changes(kwargs)

        if violations == []:
            self.error_field = 'no errors'
        else:
            # remove any private name space properties from the kwargs dict without checking if its none
            self.remove_inval_scope(kwargs, violations, inspect.currentframe())
        
        # set all the properties of the debug menu
        for key, value in kwargs.items():
            setattr(self, key, value)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.exclude_flag = not self.exclude_flag
            if self.exclude_flag:
                self.exclude.append(self.error_field)
            else:
                self.exclude = []
        super().handle_event(event)

