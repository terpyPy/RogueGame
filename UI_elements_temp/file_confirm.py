
import os

import pygame

from .txt_confirm import Txt_confirm

class File_Confirm(Txt_confirm):
    # lets create a file_confirm prompt that inherits from txt_confirm, overriding the exit_value method
    # new exit_value method will handle path validation and return a valid path or exit the program with an error message
    def __init__(self, active_color='lightskyblue3', passive_color='chartreuse4', prompt_subject='default_text'):
        """ 
        a class for creating a confirm/cancel prompt with an input box above and a text above that.

        inherits from txt_confirm class. 
        """
        super().__init__(active_color, passive_color,
                         prompt_subject, add_cursor_box=True)

    def exit_value(self) -> str:
        # determine if the the string is absolute or relative path
        if os.path.isabs(self.text):
            # if absolute path, check if the path exists
            if os.path.exists(self.text):
                return str(self.text)
            else:
                print(f'Error: {self.text} is not a valid path.')
                pygame.quit()
        else:
            # if relative path, check if the path exists
            if os.path.exists(os.path.join(os.getcwd(), self.text)):
                return str(os.path.join(os.getcwd(), self.text))
            else:
                print(f'Error: {self.text} is not a valid path.')
                pygame.quit()