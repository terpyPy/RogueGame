# Author: Cameron Kerley
# Date: 03/1/2024
# Description: This file contains the test cases for the workFlow_example.py file in the workFlow package,
# refactored by copilot for unittest workflow using my original tests script.
import unittest
import os

import pygame

# from UI_elements import Input_txt, Yes_no_prompt, Text_box, Txt_confirm, File_Confirm, DebugMenu
from UI_elements_temp import *
pygame.init()

def user_typing_sim(txt):
    for char in txt:
        yield pygame.event.Event(pygame.KEYDOWN, {'key': ord(char), 'unicode': char})

class TestInputTxt(unittest.TestCase):
    def test_user_input(self):
        screen = pygame.display.set_mode((400, 400))
        box = Input_txt(prompt_subject=f'debug {Input_txt.__name__}', add_cursor_box=True, exit_types=[int])

        # simulate user input on input box
        txt = '1234567890'
        gen = user_typing_sim(txt)
        debug_action = [next(gen) for _ in range(len(txt))]
        debug_action.append(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))

        # set active to True for automated testing
        box.active = True
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertIsInstance(r, int, "Result is not an integer")
        self.assertEqual(r, int(txt), "Result does not match expected value")

        del box

class TestYesNoPrompt(unittest.TestCase):
    def test_yes_no_choice(self):
        screen = pygame.display.set_mode((400, 400))
        box = Yes_no_prompt(prompt_subject='use check point?', add_cursor_box=False)

        # test color change
        changes = [('panel', pygame.Color('cyan3')),
                   ('bg', pygame.Color('gray')),
                   ('font', pygame.Color('black')),
                   ('active', pygame.Color('darkslateblue')),
                   ('passive', pygame.Color('deeppink3'))]
        for prop, color in changes:
            box.modify_color(prop, color)

        # simulate user input on yes/no prompt
        debug_action =  [pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                           {'button': 1, 'pos': (box.yes['rect'].x, box.yes['rect'].y)}),
                         pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                            {'button': 1, 'pos': (box.okay['rect'].x, box.okay['rect'].y)})]
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertIsInstance(r, bool, "Result is not a boolean")

        del box

class TestTextBox(unittest.TestCase):
    def test_text_box(self):
        screen = pygame.display.set_mode((400, 400))
        txt = f'debug {Text_box.__name__}'
        box = Text_box(prompt_subject=txt)        

        # pygame.QUIT event to exit text box
        debug_action = [pygame.event.Event(pygame.QUIT)]

        # set active to True for automated testing
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertEqual(r, txt, "Result does not match expected value")

        del box
    
class TestTxtConfirm(unittest.TestCase):
    def test_txt_confirm(self):
        screen = pygame.display.set_mode((400, 400))
        box = Txt_confirm(prompt_subject='debug txt_confirm',
                          active_color=pygame.Color('red'),
                          passive_color=pygame.Color('blue'))

        # test color change
        changes = [('panel', pygame.Color('cyan2')),
                   ('bg', pygame.Color('darkgray')),
                   ('font', pygame.Color('black'))
                   ]

        for prop, color in changes:
            box.modify_color(prop, color)

        # simulate user input expected by debug_target
        txt = 'hello world'
        gen = user_typing_sim(txt)
        debug_action = [next(gen) for _ in range(len(txt))]
        debug_action.append(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))

        # set active to True for automated testing
        box.active = True
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertEqual(r, txt, "Result does not match expected value")

        del box

class TestDebugMenu(unittest.TestCase):
    def test_debug_menu(self):
        screen = pygame.display.set_mode((400, 400))
        box = DebugMenu(subject='Test debug_menu')

        # simulate user input expected by debug_target
        txt = 'User Name input'
        gen = user_typing_sim(txt)
        debug_action = [next(gen) for _ in range(len(txt))]
        debug_action.append(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
        box.set_all(frame_counts='0', direction_field='None', fps_field='0', xy_field='(0, 0)')
        # set active to True for automated testing
        box.active = True
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertEqual(r, txt, "Result does not match expected value")

        del box
    
    def test_debug_menu_fa(self):
        screen = pygame.display.set_mode((400, 400))
        box = DebugMenu(subject='Test debug_menu')

        # simulate user input expected by debug_target
        txt = 'User Name input'
        gen = user_typing_sim(txt)
        debug_action = [next(gen) for _ in range(len(txt))]
        debug_action.append(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
        box.set_all(frame_counts='0', direction_field='None', fps_field='0', xy_field='(0, 0)')
        # set active to True for automated testing
        box.active = True
        r = box.main_file_attached(screen, debug=True, debug_target=debug_action) 

        # Use an assertion to check the result
        self.assertEqual(r, txt, "Result does not match expected value")

        del box  

    

class TestFileConfirm(unittest.TestCase):
    def test_file_confirm(self):
        screen = pygame.display.set_mode((400, 400))
        box = File_Confirm(prompt_subject='debug file_confirm')

        # simulate user input expected by debug_target
        txt = 'test_workFlow_example.py'
        gen = user_typing_sim(txt)
        debug_action = [next(gen) for _ in range(len(txt))]
        debug_action.append(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
        # set active to True for automated testing
        box.active = True
        r = box.main(screen, debug=True, debug_target=debug_action)

        # Use an assertion to check the result
        self.assertTrue(os.path.exists(r), "Resulting path does not exist")

        del box


if __name__ == '__main__':
    # usage example:
    # python -m unittest test_workFlow_example.TestFileConfirm
    unittest.main()