# Author: Cameron Kerley
# Date: 03/1/2024

import os
import sys
import pygame
import inspect
import glob

import json

from .txt_confirm import Txt_confirm

class DebugMenu(Txt_confirm):
    def __init__(self, subject='-debug menu-', add_cursor=True, buttons=['direction: ', '']):
        """DebugMenu class is a subclass of Txt_confirm, it is a text box with additional buttons for debugging purposes.

        Args:
            subject (str, optional): The prompt subject of the debug menu. Defaults to '-debug menu-'.
            add_cursor (bool, optional): add | to the end of user in line. Defaults to True.
            buttons (list, optional): list of button labels. Defaults to ['direction: ', ''].
        """
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
        self.add_buttons([f'default-txt'], [(0, 120)], width=350, height=125)
        # make a surface for the error message
        m_rect = self.buttons[-1]['rect']
        self.err_surf = pygame.Surface((m_rect.width, m_rect.height))
        self.e_font = pygame.font.Font(None, 20)
        
        json_list = glob.glob('**/*.json', recursive=True, root_dir='\RogueGame')
        f_name = list(filter(lambda x: "debug_info" in x, json_list))[0]
        self.f_path = os.path.join(os.curdir, f_name)
        
        f = open(self.f_path, 'r')
        self.info = json.load(f)    
        f.close()
        self.d_hash = self.info['hash']
        
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
        
        # format of error message:
        #    found obj hash: {self.d_hash}\n{error_msg}
        #         ^                       ^      ^
        #         |--> set in game loop   |      | 
        #              new fields sep <---|      |
        #              final text added <--------|
        #
        return self.buttons[self.len_b_norm+1]
    
    @error_field.setter
    def error_field(self, value):
        self.buttons[self.len_b_norm+1]['label'] = value
        
    def active_box(self, event):
        super().active_box(event)
        # if not self.choice and self.destroy:
        #     self.destroy = False
        self.cancel['color'] = self.passive_color
             
    def set_all(self, **kwargs):
        """
        set all text properties of the debug menu

        i.e. menu.set_all(frame_counts=f'{object}', ...)
        """
        # find any properties in the kwargs that are private name space
        violations = self.scope_changes(kwargs)
        error_msg = ''
        if violations:
            # remove any private name space properties from the kwargs dict without checking if its none
            self.remove_inval_scope(kwargs, violations, inspect.currentframe())
            error_msg = 'error in scope changes'
        
        # set all the properties of the debug menu
        for key, value in kwargs.items():
            setattr(self, key, value)
        curr_txt = getattr(self, 'error_field')['label']
        curr_txt = f'{curr_txt}\n{error_msg}'
        lines_in_buff = curr_txt.split('\n')
        if len(lines_in_buff) > 5:
            lines_in_buff = lines_in_buff[-5:]
            curr_txt = '\n'.join(lines_in_buff) 
        setattr(self, 'error_field', curr_txt)
        
    def handle_hotkeys(self, event):
        return super().handle_hotkeys(event, event_handlers=[self.toggle_debug_text.__name__])    
        
    def toggle_debug_text(self, event):
        if event.key == pygame.K_RALT:
            self.exclude_flag = not self.exclude_flag
            if self.exclude_flag:
                self.exclude.append(self.error_field)
            else:
                self.exclude = []

    def main_file_attached(self, screen, debug=False, debug_target=None):
        """ 
        The main loop of the debug menu, it handles events and updates the screen.
        It is directly tied to debug_info.json. 
        will update the debug menu with the information in the file
        """
        while not self.destroy:
            events = pygame.event.get()
            try:
                f = open(self.f_path, 'r')
                self.info = json.load(f)    
                f.close()
                if self.info['hash'] != self.d_hash:
                    self.set_all(**self.info)
                    self.d_hash = self.info['hash']
                    
            except:
                self.error_field = 'no file found'
            
            
            if debug and debug_target:
                # add a debug action to the event queue
                events.append(debug_target.pop(0))


            for event in events:
                # handle case where user closes main window while input box is active,
                if event.type == pygame.QUIT:
                    # without this the program will hang because the input box shares a screen object with main window.
                    self.destroy = True
                self.handle_event(event)
            # fill the screen with black to clear the screen
            screen.fill(pygame.Color('black'), screen.get_rect())
            self.blitme(screen)
            pygame.display.flip()
            self.clock.tick(60)

        return self.exit_value()
    