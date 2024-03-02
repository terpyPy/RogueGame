# Author: Cameron Kerley
# Date: 03/1/2024
# PyGame template author: MatthewJA @ https://gist.github.com/MatthewJA/7544830
#
# This game is primarily an exercise in using PyGame, OOP and building a game from scratch, not from a book or tutorial.
# the code found here is primarily my own, starting from a very basic PyGame template show the event loop and basic game loop.
# code used from stackoverflow cannot be properly attributed as the same solutions are found in multiple places all claiming to be OP's own work,
# or AI generated, without the author explicitly stating otherwise. Unless you are the original author of that code, and capable of producing
# the license it originally published under, I cannot properly attribute it to you. If you are the original author, please contact me on github.
# I will be happy to attribute you as the original author of that code and provide a link to your original work.

# Import standard modules.
import sys
import time
import json
# Import non-standard modules.
import pygame
from pygame.locals import *
import pygame.font as font
# import UI_elements as UI
from UI_elements_temp import *
from GameObjects import Player, Enemy
from dev_tools import MousePositions as MP


class MyGame:
    def __init__(self):
        # create a global variable for show_collision
        self.show_debug = False
        self.record_collision = False
        # Initialise PyGame.
        pygame.init()
        # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
        self.fps = 60.0
        self.fpsClock = pygame.time.Clock()
        # setup a default font for pygame
        self.myFont = font.SysFont('Comic Sans MS', 12)
        # Set up the window.
        self.width, self.height = 1920, 1080
        self.screen = pygame.display.set_mode((self.width, self.height))

        # make the player
        self.player = Player(self.screen)
        # setup test enemies for the player to interact with
        # create a list of starting positions with hight and width as max bounds
        cords = list(zip(range(100, 1920, 100), range(100, 1080, 100)))

        enemies = [Enemy(self.screen, cords[i]) for i in range(len(cords))]

        # make enemy part of a sprite group, this will be its actual implementation, currently testing
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group.add(enemies)

        self.start_menu = Txt_confirm(
            prompt_subject='-enter player name-',
            add_cursor_box=True)
        self.debug_menu = DebugMenu()

        menu_result = self.start_menu.main(self.screen)
        self.player_name = self.myFont.render(
            menu_result, False, (255, 255, 255))
        # test collision has an x and y coordinate for each segment of test_collision
        # make a sprite group for the test collision so we can use pygame's collision detection
        self.test_collision = json.load(open('mouse_positions_m.json'))
        self.m_record = MP(self.test_collision)
        self.test_collision_group = pygame.sprite.Group()
        for i in range(len(self.test_collision)):
            self.test_collision_group.add(pygame.sprite.Sprite())
            self.test_collision_group.sprites()[i].rect = pygame.Rect(self.test_collision[i],
                                                                    (1, 1))
            self.test_collision_group.sprites()[i].image = pygame.Surface((4, 4))
            self.test_collision_group.sprites()[i].image.fill((255, 0, 0))

        # load the background image: cave_bg.png
        self.bg = pygame.image.load('cave_bg.png')
        # scale the background image to the screen size
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        # Main game loop.
        self.dt = 1/self.fps  # dt is the time since last frame.
        self.debug_group = pygame.sprite.Group()
        self.hit_box_group = pygame.sprite.Group()
        self.hit_box_group.add(
            [n.empty_sprite for n in self.enemy_group.sprites()])
        self.debug_m_targets = {
            True: self.debug_UI_handler, False: self.empty_event}
        self.debug_menu.exclude = []

    def debug_UI_handler(self, screen, events):

        self.debug_menu.set_all(frame_counts=f'{self.player}',
                                direction_field=str(self.player.active_keys),
                                fps_field=f'fps: {int(self.fpsClock.get_fps())}',
                                xy_field=repr(self.player)
                               )
        self.debug_menu.main_no_loop(screen, events)

    def empty_event(self, *args):
        pass

    def update(self, dt):
        """
        Update game. Called once per frame.
        dt is the amount of time passed since last frame.
        If you want to have constant apparent movement no matter your framerate,
        what you can do is something like

        x += v * dt

        and this will scale your velocity based on time. Extend as necessary."""
        # Go through events that are passed to the script by the window.
        events = pygame.event.get()
        for event in events:
            esc_con = (event.type == KEYDOWN and event.key == K_ESCAPE)
            # If the window is closed, quit the game.
            x_out_con = (event.type == QUIT)
            if x_out_con or esc_con:
                pygame.quit()  # Opposite of pygame.init
                sys.exit()
            # record mouse positions
            if not self.show_debug and self.record_collision:
                self.record_mouse_positions(event)

            # response to keypress and held keys (movement) such that movement is smooth
            if event.type == pygame.KEYDOWN:
                self.player.k_up_e(event.key, True)

                if event.key == pygame.K_o:
                    print('saving mouse positions: mouse_positions_m.json')
                    with open('mouse_positions.json', 'w') as f:
                        json.dump(self.m_record.positions, f)

                elif event.key == pygame.K_1:
                    self.show_debug = not self.show_debug
                    if self.show_debug:
                        self.add_debug_groups()
                    else:
                        self.debug_group.empty()

                elif event.key == pygame.K_2:
                    self.record_collision = not self.record_collision
                    print(f'record collision enabled: {self.record_collision}')

            elif event.type == pygame.KEYUP:
                self.player.k_up_e(event.key, False)
            # record mouse positions

        self.group_updates()
        return events

    def add_debug_groups(self):
        self.debug_group.add(self.hit_box_group.sprites())
        self.debug_group.add([n.agro_circle for n in self.enemy_group.sprites()])
        self.debug_group.add(self.player.empty_sprite)
        self.debug_group.add(self.player.dot)

    def group_updates(self):
        player_scene_collision = pygame.sprite.spritecollideany(
            self.player.empty_sprite, self.test_collision_group)
        self.player.colliding = player_scene_collision
        self.player.update(self.test_collision_group, debug=self.show_debug)

        # update the enemy
        enemy_scene_collision = pygame.sprite.groupcollide(
            self.hit_box_group, self.test_collision_group, False, False)
        for enemy in enemy_scene_collision:
            enemy.colliding = True

        p_events = self.player.rect.center
        self.enemy_group.update(p_events, debug=self.show_debug)

    def draw(self):
        """
        Draw things to the window. Called once per frame.
        """
        # Blit the scene onto the screen.
        self.screen.blit(self.bg, (0, 0))
        # draw the debug text above the player
        txt = self.player_name
        # use player center to get x and y coordinates for the text
        txt_loc = (self.player.x+self.player.rect.width/3,
                   self.player.y-self.player.rect.height/4)
        # draw the player name
        # draw the player
        self.player.blitme()
        self.debug_group.draw(self.screen)
        self.screen.blit(txt, txt_loc)
        # draw the enemy
        self.enemy_group.draw(self.screen)

        # draw the collision test
        self.test_collision_group.draw(self.screen)

    def record_mouse_positions(self, event):
        # self.m_record, self.test_collision_group
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.m_record.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.m_record.is_dragging = False

        if event.type == pygame.MOUSEMOTION and self.m_record.is_dragging:
            self.m_record.positions.append(pygame.mouse.get_pos())
            # print(mouse_positions)
            # add new collision rects to the collision group
            self.test_collision_group.add(pygame.sprite.Sprite())
            self.test_collision_group.sprites(
            )[-1].rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
            self.test_collision_group.sprites(
            )[-1].image = pygame.Surface((4, 4))
            self.test_collision_group.sprites()[-1].image.fill((255, 0, 0))

            time.sleep(0.05)
        # handle normal mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            print(pygame.mouse.get_pos())
            # time.sleep(0.05)

    def main(self):
        while True:
            events = self.update(self.dt)
            self.draw()
            self.fpsClock.tick(self.fps)
            self.dt = self.fpsClock.get_time()/1000
            self.debug_m_targets[self.show_debug](self.screen, events)
            pygame.display.update()


if __name__ == '__main__':
    # test the game
    game = MyGame()
    game.main()
