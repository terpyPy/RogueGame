# Author: Cameron Kerley
# Date: 03/1/2024

import time

import pygame

from .scopedMenu import ScopedMenu

class Input_txt(ScopedMenu):
    def __init__(self, active_color='lightskyblue3', passive_color='chartreuse4', prompt_subject='default_text', add_cursor_box=False, exit_types=[int, str, bool]):
        # -------------------
        # |    child:'txt'  |---> static text in an box with no listener
        # -------------------
        # ___________________
        # |    parent:input | ---> user input,
        # -------------------      has event handling & main loop,
        #                          returns text,
        """ 
        a class for creating an input box with a prompt above it optionally.
        when window is destroyed: 
            the input box returns the text entered by the user when input box is active.
            
        Args:
            active_color (str, optional): _description_. Defaults to 'lightskyblue3'.
            passive_color (str, optional): _description_. Defaults to 'chartreuse4'.
            prompt_subject (str, optional): _description_. Defaults to 'default_text'.
            text_above (bool, optional): _description_. Defaults to False:
            when text_above is True:
                If text_above is True, the element will display a prompt above the input box.
                This allows subclasses an easy means to create a prompt/input box pair.
                useful for creating confirm/cancel, yes/no, binary choice, or file input menus.

        Returns:
            input_txt: a UI element that handles text entered by the user checking valid type. 
        """
        # initialize the parent hierarchy
        super().__init__(exit_types=exit_types)
        # basic properties of the input box
        self.active_color = pygame.Color(active_color)
        self.passive_color = pygame.Color(passive_color)
        self.color = self.passive_color
        self.active = False
        self.text = ''
        # pygame properties of the input box
        self.rect_text = pygame.Rect(10, 50, 200, 30)
        self.font = pygame.font.Font(None, 22)
        self.clock = pygame.time.Clock()
        # flags that modify the input box default behavior:
        self.destroy = False
        self.text_above = add_cursor_box
        self.starting_elements = []
        self.prompt_font = pygame.font.Font(None, 22)
        self.cumulative_f_time = 0
        # attach the text above the input box as a prompt
        if add_cursor_box:
            self.prompt = {'rect': self.rect_text.move(0, -40),
                           'color': self.passive_color,
                           'label': prompt_subject}
        else:
            self.text = prompt_subject
            # initialize the prompt in case it is called, but not used, must have a rect will not be drawn
            self.prompt = {'rect': self.rect_text.move(0, -40),
                           # make this super visible so it is obvious if rendered
                           'color': pygame.Color('red'),
                           'label': '***-ERROR_TXT-***'}
        self.private_name_space = ['active_color',
                                   'passive_color',
                                   'color',
                                   'active',
                                   'destroy',
                                   'text_above']
        self.parent_panel = {'rect': self.rect_text,
                        'color': self.color, 'label': self.text}
        self.starting_elements.append(self.parent_panel)
        self.cursor_f = lambda x: x # default cursor function, returns the text unmodified
        match self.text_above:
            case True:
                self.starting_elements.append(self.prompt)
                self.cursor_f = self.add_cursor
            case False:
                pass
            case _:
                raise ValueError('text_above must be a boolean')

        
        self.c_time = time.time()
        self.f_count = 0
        self.buttons = []
        
        
    def modify_color(self, element: str, color: tuple) -> None:
        super().modify_color(element, color)
        # modify the color of the buttons in self.buttons
        list(map(lambda x: x.update({'color': self.passive_color}), self.buttons))
        # for button in self.buttons:
        #     button['color'] = self.passive_color

    def handle_hotkeys(self, event, event_handlers=[]):
        """
        Handles hotkey events. should be called after checking if key is pressed.\n
        Generalized to except hotkey definitions from subclasses.\n
        simply add the method name to event_handlers list.\n
        if a menu does not have the specified hotkey attribute, an error message is displayed.\n

        Args:
            event (pygame.event.Event): The event object representing the hotkey event.
            event_handlers (list, optional): A list of method names that represent hotkey events. Defaults to [].
        """
        self.keyboard_input(event)
        # add hotkey quit to the event handlers, this behavior is intrinsic to all menus.
        event_handlers.extend([self.handle_quit_event.__name__])
        # handle hotkeys for menu, 
        # 
        for handler in event_handlers:
            if hasattr(self, handler):
                getattr(self, handler)(event)
            else:
                print(f'handler {handler} not found in {self.__class__.__name__}')
        

    def handle_quit_event(self, event):
        shift_quit = (
            event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_SHIFT)
        
        if shift_quit or event.type == pygame.QUIT:
            self.destroy = True

    def handle_event(self, event):
        '''
        handles input events for the input box.
        subclasses should append to this method when adding additional behavior.
        '''
        if event.type == pygame.MOUSEBUTTONDOWN:
            # check if the input box is clicked
            self.active_box(event)

        elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
            self.drag_rect_text(event)
            
        elif event.type == pygame.KEYDOWN:
            # handle hotkeys for menu,
            self.handle_hotkeys(event)

        self.pos_update([(0, -40)], [self.prompt])

    def active_box(self, event):
        '''
        checks if the input box is clicked, if so, set active to True.
        subclasses should append to this method when adding additional behavior.
        '''
        if self.rect_text.collidepoint(event.pos) and self.text_above:
            self.active = True
            self.color = self.active_color
        else:
            self.active = False
            self.color = self.passive_color

    def keyboard_input(self, event):
        '''
        keyboard input for the input box. requires active box and text above modifiers to be True.
        subclasses should NEVER override or append to this method, especially if that subclass does not read keyboard input as text.
        '''
        if self.active and self.text_above:
            # handle backspace and return key events regardless of active state
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif (event.key == pygame.K_RETURN) and (self.text.strip() != ""):
                self.destroy = True
                self.active = False
                
            else:
                self.text += event.unicode

    def drag_rect_text(self, event):
        drag_group = []
        drag_group.append(self.prompt['rect'])
        drag_group.append(self.rect_text)
        for rect in drag_group:
            if rect.collidepoint(event.pos):
                self.rect_text.x, self.rect_text.y = event.pos
                self.rect_text.x -= self.rect_text.width / 2
                self.rect_text.y -= self.rect_text.height / 2
                break

    def pos_update(self, offsets, buttons=[]):
        """
        Update the position of the buttons relative to the text box.

        This method updates the position of the buttons based on the position of the text box.
        It uses the x_y_offsets tuple to calculate the new position for each button.

        Parameters:
        - offsets: a tuple of tuples containing the x and y offsets for each button
        - buttons: a list of dictionaries containing the button properties

        Returns:
        - None
        """
        x_y_offsets = offsets
        # update your position relative to the text box
        r_x, r_y = self.rect_text.x, self.rect_text.y
        list(map(lambda x,y: self.move_group(x['rect'], y, origin_x=r_x, origin_y=r_y), buttons, x_y_offsets))

    def move_group(self, button, x_y_offsets, origin_x=0, origin_y=0) -> None:
        x_off, y_off = x_y_offsets
        button.x = origin_x + x_off
        button.y = origin_y + y_off

    def blitme(self, screen):
        '''
        blit the input box to the screen.
        subclasses should only append to this method when adding additional behavior.
        '''
        
        display_text = self.text
        display_text = self.cursor_f(display_text)
        self.parent_panel['label'] = display_text
        self.parent_panel['rect'] = self.rect_text
        self.parent_panel['color'] = self.color
        self.draw_panels(screen, panels=self.starting_elements)
        self.draw_all_elements(screen, self.starting_elements)


    def draw_panels(self, screen, panels=[]):
        '''
        draws a panel around each element in the panels list. \n
        subclasses should overload & append to this method with \n
        super().draw_panels() when adding additional behavior.\n
        '''
        # reference to the bottom right corner of the input box
        br = self.rect_text.bottomright[0]
        bl = self.rect_text.bottomleft[0]
        list(map(lambda x: self.blit_panel(screen, br, bl, x), panels))
        

    def blit_panel(self, screen, br, bl, toDraw):
        region = self.calc_panles(br, bl, toDraw)
            # fill the box with grey
        screen.fill(self.panel_color, region)
            

    def calc_panles(self, br, bl,toDraw):
        pad_r = abs(toDraw['rect'].x-br)
        pad_l = abs(toDraw['rect'].bottomleft[0]-bl)
        region = pygame.Rect(
                            (toDraw['rect'].x-pad_l)-5,
                            toDraw['rect'].y - 5,
                            (pad_r+pad_l)+10,
                            toDraw['rect'].height+10
                            )
                            
        return region

    def draw_all_elements(self, screen, panels):
        """draws all elements in the panels list to the screen. \n
        subclasses should NEVER override or append to this method, \n

        Args:
            screen (Surface): any pygame surface object.
            panels (dict): a list of dictionaries containing the properties of the elements to draw.
        """
        
        list(map(lambda x: self.draw_element(screen, x), panels))
        # for toDraw in panels:
        #     self.draw_element(screen, toDraw)

    def draw_element(self, screen, toDraw):
        '''
        steps:
        1) pygame.draw.rect draw a rectangle with the color of the button\n
        2) render the text to a surface with the font\n
        3) blit the text surface to the screen at the position of the button. pad to center text\n
        this method is called by draw_panels() to draw the buttons and text boxes.
        subclasses should NEVER override or append to this method, 
        only reuse with super().draw_element() when adding additional behavior to draw_panels().
        ''' 
        temp_surface = pygame.Surface((toDraw['rect'].width, toDraw['rect'].height))
        temp_surface.fill(self.bg_color)
        self.blit_text(temp_surface, toDraw['label'], (5, 5), self.font, self.font_color)
        screen.blit(temp_surface, (toDraw['rect'].x, toDraw['rect'].y))
        pygame.draw.rect(screen, toDraw['color'], toDraw['rect'], 2)

    def add_cursor(self, txt):
        """ 
        adds a cursor to the end of the text in the input box.
            the cursor is a vertical bar that blinks on and off.
            subclasses should NEVER access this method, it is for internal use only.

        Args:
            txt (str): the text to add the cursor to.

        Returns:
            str: the text with the cursor added.
        """
        # set a 2 second blink rate for the cursor
        self.f_count = int(time.time() - self.c_time)
        
        if "|" not in self.text and self.f_count > 1:
            txt += "|"
            self.c_time = time.time()

        if "|" in self.text and  self.f_count > 4:
            txt.replace("|", "")
            self.c_time = time.time()
            

        return txt

    def exit_value(self) -> int | str | bool | None:
        """
        returns the text entered by the user as an expected type.
        subclasses should append to this method when adding additional behavior.
        """
        # run is isinstance loop and add to a list we will match by true
        
        for peram in self.exit_types:
            try:
                return peram(self.text)
            except ValueError:
                self.text = ''
            print(
                f'Error recived {self.text}.\n Input must be integer not _{type(self.text)}_')
        
        # exit()

    def main(self, screen, debug=False, debug_target=None):
        """ 
            a main loop for the input box.
            if debug is True, the input box will run in debug mode.
            debug_target is a list of pygame events that will be passed to the input box's event handler.
            this allows the user to simulate user input for automated testing.
            if debug is False, the input box will run in normal mode.
            normal mode requires user input to run the main loop.
            the input box will exit when the user clicks the okay button or closes the window.
        Args:
            screen (pygame.display): the main window.
            debug (bool, optional): run in debug mode. Defaults to False.
            debug_target (list, optional): a list of pygame events. Defaults to None.

        Returns:
            int: the text entered by the user as an integer.
        """
        while not self.destroy:
            events = pygame.event.get()
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
            self.clock.tick(30)

        return self.exit_value()
    
    def main_testing(self, screen):
        """ 
            a main loop for the input box.
            if debug is True, the input box will run in debug mode.
            debug_target is a list of pygame events that will be passed to the input box's event handler.
            this allows the user to simulate user input for automated testing.
            if debug is False, the input box will run in normal mode.
            normal mode requires user input to run the main loop.
            the input box will exit when the user clicks the okay button or closes the window.
        Args:
            screen (pygame.display): the main window.
            debug (bool, optional): run in debug mode. Defaults to False.
            debug_target (list, optional): a list of pygame events. Defaults to None.

        Returns:
            int: the text entered by the user as an integer.
        """
        line_correct = False
        end = False
        # read file of text to type
        with open('samps.txt', 'r') as f:
            text = f.read()
        # turn text into list of lines
        text = text.split('\n')
        while not end:
            events = pygame.event.get()
            for event in events:
                # handle case where user closes main window while input box is active,
                if event.type == pygame.QUIT:
                    # without this the program will hang because the input box shares a screen object with main window.
                    end = True
                self.handle_event(event)
                # we will use destroy flag to determine when to check user input 
                if self.destroy:
                    excepted, user_in = self.text.split('\n')
                    line_correct =  excepted == user_in
                    self.prompt['label'] = f'correct: {line_correct}'
                    self.destroy =  False
                    self.active = True
                if line_correct:
                    # clear the text buffer
                    self.text = ''
                    self.prompt['label'] = 'type this text'
                    line_correct = False
                    # set new text to type
                    self.text = text.pop(0) + '\n'
                    
                if not text:
                    end = True
                    
            # fill the screen with black to clear the screen
            screen.fill(pygame.Color('black'), screen.get_rect())
            self.blitme(screen)
            pygame.display.flip()
            self.clock.tick(30)

        return self.exit_value()

    def main_no_loop(self, screen, events):
        self.destroy = False
        for event in events:
            # handle case where user closes main window while input box is active,
            if event.type == pygame.QUIT:
                # without this the program will hang because the input box shares a screen object with main window.
                self.destroy = True
            self.handle_event(event)
        # self.blitme(screen)
        if self.destroy:
            print('destroyed')
            return self.exit_value()