import os

import pygame

from .colors import Colors

class ScopedMenu(Colors):
    def __init__(self):
        super().__init__()
        self.private_name_space = ['active_color',
                                   'passive_color',
                                   'color',
                                   'active',
                                   'destroy',
                                   'text_above',
                                   'cumulative_f_time',
                                   'access_violation_c']
        self.exclude_flag = False
        
        self.access_violation_c = 0
        
    def scope_changes(self, kwargs):
        return [key for key in kwargs.keys() if key in self.private_name_space]

    def remove_inval_scope(self, kwargs, violations, frame):
        for key in violations:
            attempted_change = kwargs.pop(key)
            self.access_violation_c += 1
            # get the call stack
            e_msg = self.scope_violation_msg(key, attempted_change, frame)
            # update game debug menu with the error message
            self.error_field = e_msg

    def scope_violation_msg(self, key, attempted_change, frame):
        '''
        -----------------------------------------------------------------------------------------------
        |==================================:-_Object_"DebugMenu"_-:===================================|
        | Scope-violation-:game_idea_v2.debug_UI_handler(active=None) in line 74                      |
        |                                     Violation_Count-:26                                     |
        -----------------------------------------------------------------------------------------------
        '''
        # inspect the call stack to get needed info for the violation message
        called = frame.f_back.f_code.co_name
        file = frame.f_back.f_code.co_filename
        line = frame.f_back.f_lineno
        # get just the name of the file not the path
        from_file = os.path.basename(file)
        # string representation of the function call that caused the violation
        func_str = f'{from_file.strip(".py")}.{called}({key}={attempted_change})'
        # string representation of the line number violation occurred
        on_line = f'in line {line}'

        # error_name string for the target object
        error_name = f':- Object "{self.__class__.__name__}" -:'

        # make a string for the violation message in form:
        #       'file.function(attribute=value) in line number'
        #
        vio_str = f'Scope violation-: {func_str} {on_line}'
        box_len = len(vio_str)+2, # only used for formatting the message with print
        vio_str_f = f'{vio_str}'

        # make a string for the violation count in form:
        vio_count = f'Violation Count-:{self.access_violation_c}'

        # make a message for the violation which is formatted to fit in a box with width box_len & hight of len(msg)
        msg = [
            f'|{error_name}|',  # =^{box_len}}, #target object
            f'|{vio_str_f}|',  # ^{box_len}}, file.function(attribute=value) in line number
            f'|{vio_count}|'  # ^{box_len}}, times called on stack
        ]

        # msg = [
        #         f'|{error_name:=^{box_len[0]}}|',
        #         f'|{vio_str_f: ^{box_len[0]}}|',
        #         f'|{vio_count: ^{box_len[0]}}|'
        #     ]
        return '\n'.join(msg)
            

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        
        return surface