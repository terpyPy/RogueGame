# import cProfile
# command to profile the code with cProfile, use -O to optimize the code
# 'python -m cProfile -o tmp/tmp.prof ui_demo_v2.py'
# then snakeviz tmp/tmp.prof to view the profile
import logging
import json
import numpy as np
import pygame
from gameGUI import base_Element, text_element, input_element

# Set up logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())
log.info('Starting UI demo')
# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
ui_group = pygame.sprite.Group()
ui_group2 = pygame.sprite.Group()
ui_group3 = pygame.sprite.Group()
ui_group4 = pygame.sprite.Group()
ui_group5 = pygame.sprite.Group()


def load_ui_elements(ui_group, fname='ui_elements_t.json'):
    with open(fname, 'r') as f:
        ui_rep = json.load(f)
        # Generate elements from the stringified representations of the UI
        ui_group.add([eval(ele.encode('utf-8')) for ele in ui_rep])
    log.info(f'Loaded {len(ui_group)} elements from {fname}')

# Read the UI elements from a JSON file
load_ui_elements(ui_group)
load_ui_elements(ui_group2, 'ui_elements_4.json')
load_ui_elements(ui_group3, 'ui_elements_3.json')
load_ui_elements(ui_group4, 'text_confirm.json')
load_ui_elements(ui_group5, 'UI_text_prompt.json')

# List of button names that have interactive behavior
inter = ['InputElement', 'InteractiveTextElement']
# Lambda function to filter the interactive elements
def active_elements(x): return x.eleName in inter
# lambda function to update the active state and return the active state
def active_map(x, pos): return x.check_active(pos, inplace=True)
def filter_active(x): return x.active


def export_ui_elements(ui_rep, fname='ui_elements_t.json'):
    with open(fname, 'w') as f:
        json.dump(ui_rep, f)


class Menu:
    def __init__(self, background, input_element, group, kill_con=lambda t: t == None, name='menu'):
        self.background = background
        self.check = [False]
        if input_element:
            self.input_element = input_element
            self.msg = input_element.text
        else:
            self.msg = ''
            self.input_element = None
        self.rel = (0, 0)
        self.event_handlers = {
            pygame.MOUSEBUTTONDOWN: self._find_active_ele,
            pygame.KEYDOWN: self._update_message,
            # pygame.MOUSEMOTION: self._move_menu
        }
        self.ID = id(self)
        self.kill = False
        self.kill_con = kill_con
        self.name = name
        self.interactive = list(filter(active_elements, group))
        log.info(f'Created menu {self.name} with ID {self.ID}')

    def get_active(self):
        if self.input_element:
            return self.input_element.active
        else:
            return False

    def handle_event(self, event, group):
        if event.type in self.event_handlers:
            x = self.event_handlers[event.type](event, group)
            log.debug(
                f'Event handler {self.event_handlers[event.type].__name__} handled by {self.name} event pushed = {x}')
            return x

    def _find_active_ele(self, event, mygroup):
        self.check = list(map(active_map, self.interactive, [
                          event.pos] * len(self.interactive)))
        if any(self.check):
            ele_search = list(filter(filter_active, self.interactive))[0].text
            if self.kill_con(ele_search):
                self.kill = True
            return True
        else:
            return False

    def _update_message(self, event, mygroup):
        if event.key == pygame.K_BACKSPACE and self.input_element.active:
            self.msg = self.msg[:-1]
        elif event.key == pygame.K_RETURN and self.input_element.active:
            self.msg = ''
        elif self.input_element.active:
            self.msg = self.msg + event.unicode
        else:
            return False
        return True

    def _move_menu(self, event, mygroup):
        self.rel = event.rel

    def update(self, mygroup):
        mygroup.update(self.rel, self.msg)

    def draw(self, screen, mygroup):
        mygroup.draw(screen)


class GroupMenuInterface(dict):
    def __init__(self, menu: Menu, group: pygame.sprite.Group) -> None:
        """class interface for menus and their graphical representation.
        Makes all members accessible with properties or dict syntax

        Args:
            menu (Menu): the menus logical interface
            group (pygame.sprite.Group): the menu graphical interface
        """
        super().__init__()
        self.menu: Menu = menu
        self.group: pygame.sprite.Group = group
        self.update({'menu': self.menu, 'group': self.group})


class MenusGroup(dict):
    def __init__(self, menus: list[GroupMenuInterface]) -> None:
        """class to manage multiple menus with a common interface parent.

        Args:
            menus (list[GroupMenuInterface]): list of GroupMenuInterface objects
        """
        super().__init__()
        self.update({interface.menu.name: interface for interface in menus})
        self.interfaces = menus
        # make the menus accessible .menu_name
        for interface in self.interfaces:
            setattr(self, interface.menu.name, interface)

    def append(self, interface: GroupMenuInterface) -> None:
        """Add a menu to the group

        Args:
            interface (GroupMenuInterface): the menu interface to add
        """
        self.update({interface.menu.name: interface})
        self.interfaces.append(interface)
        setattr(self, interface.menu.name, interface)

    def bringToFront(self, key: str) -> None:
        """Bring a menu to the front of the group
        """
        interface = self.pop(key)
        # remove the menu from the list
        self.interfaces.remove(interface)
        # add the menu to the front of the list
        self.interfaces.insert(0, interface)
        # update the dict with the new order
        self.clear()
        self.update(
            {interface.menu.name: interface for interface in self.interfaces})


def retrieve_ui_panel(ui, name='Panel'):
    return list(filter(lambda x: x.eleName == name, ui))[0]


if __name__ == '__main__':
    # Create multiple menus
    # menu example with input element and kill condition set to 'Yes' button
    menuBg1 = retrieve_ui_panel(ui_group)
    inpt1 = retrieve_ui_panel(ui_group, 'InputElement')
    menu1 = Menu(menuBg1,
                 inpt1,
                 ui_group,
                 name='menu_1',
                 kill_con=lambda t: t == 'Yes'
                 )
    # same as above but with 'No' button
    menuBg2 = retrieve_ui_panel(ui_group2)
    inpt2 = retrieve_ui_panel(ui_group2, 'InputElement')
    menu2 = Menu(menuBg2,
                 inpt2,
                 ui_group2,
                 name='menu_2',
                 kill_con=lambda t: t == 'No'
                 )
    # yes/no menu example with no input element and kill condition set 'Yes' or 'No'
    menuBg3 = retrieve_ui_panel(ui_group3)
    menu3 = Menu(menuBg3,
                 None,
                 ui_group3,
                 name='menu_3',
                 kill_con=lambda t: t == 'Yes' or t == 'No'
                 )
    menu3.event_handlers.pop(pygame.KEYDOWN)
    # text prompt menu example with no input element and kill condition set to 'confirm'
    menuBg4 = retrieve_ui_panel(ui_group4)
    menu4 = Menu(menuBg4,
                 None,
                 ui_group4,
                 name='menu_4',
                 kill_con=lambda t: t == 'confirm')
    menu4.event_handlers.pop(pygame.KEYDOWN)
    # text prompt menu example with no input element and no kill condition
    menuBg5 = retrieve_ui_panel(ui_group5)
    menu5 = Menu(menuBg5,
                    None,
                    ui_group5,
                    name='menu_5')
    menu5.event_handlers.pop(pygame.KEYDOWN)
    # build the menus collection and couple Menu objects with their graphical representation
    menus = MenusGroup(
        [GroupMenuInterface(menu1, ui_group),
         GroupMenuInterface(menu2, ui_group2),
         GroupMenuInterface(menu3, ui_group3),
         GroupMenuInterface(menu4, ui_group4),
         GroupMenuInterface(menu5, ui_group5)]
    )

    def handler(event, ui): return ui["menu"].handle_event(event, ui["group"])
    def updater(ui): return ui["menu"].update(ui["group"])
    def drawer(ui): return ui["menu"].draw(screen, ui["group"])
    clock = pygame.time.Clock()
    running = True
    current_menu = None

    while running:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if hasattr(event, 'buttons'):
                et, ef, eb = event.type, [pygame.MOUSEMOTION], 1 in event.buttons
            else:
                et, ef, eb = event.type, [pygame.MOUSEMOTION], False
            lClickD = et in ef and eb
            if lClickD:
                active_menus = MenusGroup(
                    [menu for menu in menus.values() if menu.menu.background.rect.collidepoint(event.pos)])

            else:
                active_menus = MenusGroup([])

            x = list(map(lambda x: x.menu.ID, active_menus.interfaces))
            if active_menus.interfaces and current_menu:
                # current_menu = active_menus.interfaces[0]
                # menus.bringToFront(current_menu.menu.name)
                if current_menu.menu.ID in x:
                    current_menu.menu._move_menu(event, current_menu.group)
                    boarderToDraw = (screen, (255, 0, 0),
                                     current_menu.menu.background.rect, 1)

            elif active_menus.interfaces and not current_menu and lClickD:
                # find menu rect closest to the click event
                x1 = [i.menu.background.rect.x for i in active_menus.interfaces]
                y1 = [i.menu.background.rect.y for i in active_menus.interfaces]
                x2, y2 = event.pos
                xvec = (np.array(x1) - x2) ** 2
                yvec = (np.array(y1) - y2) ** 2
                dist_vec = np.sqrt(xvec + yvec)
                closest = active_menus.interfaces[np.argmin(dist_vec)]
                current_menu = closest
                boarderToDraw = (screen, (255, 0, 0),
                                 current_menu.menu.background.rect, 1)
                menus.bringToFront(current_menu.menu.name)
                log.debug(f'Current menu is {current_menu.menu.name}')
            else:
                current_menu = None
                boarderToDraw = None
                for menu in menus.interfaces:
                    # event handling
                    if handler(event, menu):
                        menus.bringToFront(menu.menu.name)
                        break

        # remove the menu if the kill condition is met
        menus_c = list(filter(lambda x: not x["menu"].kill, menus.values()))
        if len(menus_c) != len(menus.interfaces):
            menus = MenusGroup(menus_c)
            current_menu = None

        list(map(updater, menus_c))

        list(map(drawer, menus_c[::-1]))
        if boarderToDraw:
            pygame.draw.rect(*boarderToDraw)
        pygame.display.flip()
        clock.tick(60)

    ui_rep = list(map(repr, ui_group))
    export_ui_elements(ui_rep)
    ui_rep = list(map(repr, ui_group3))
    export_ui_elements(ui_rep, 'ui_elements_3.json')
    pygame.quit()
