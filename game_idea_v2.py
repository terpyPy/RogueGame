# author: Cameron Kerley
# date: 03/7/2024
# version: 2.5
# description: a test bed for systems and mechanics like how enemies will interact with the player 
# and UI elements like the txt_confirm class. pygame has no menu system and most online examples
# dont use a class structure which is not ideal for actual game development. I have little experience
# with game development and UI design and have been really pleased with even this test bed.
# 
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
        cords = list(zip(range(100, 1920, 400), range(100, 1080, 400)))

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
        for dot in self.test_collision:
            self.test_collision_group.add(self.make_temp_sprite(
                (255, 0, 0), dot, (4, 4)))

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
        self.found_obj_info = '----'
        self.ids = map(lambda x: hash(x), self.enemy_group.sprites())
        self.e_lookup = dict(zip(list(self.ids), self.enemy_group.sprites()))

    def debug_UI_handler(self, screen, events):

        self.debug_menu.set_all(frame_counts=f'{self.player}',
                                direction_field=str(self.player.active_keys),
                                fps_field=f'fps: {int(self.fpsClock.get_fps())}',
                                xy_field=repr(self.player),
                                error_field=f'obj info: {self.found_obj_info}'
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
            click_in_debug_con = (event.type == MOUSEBUTTONDOWN and self.show_debug)
            if x_out_con or esc_con:
                pygame.quit()  # Opposite of pygame.init
                sys.exit()
            
            if click_in_debug_con:
                # get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                # make mouse position a sprite
                mouse_sprite = self.make_temp_sprite((255, 0, 0), mouse_pos)
                # check if the mouse is in enemy sprite, not the hit box
                obj_found = pygame.sprite.spritecollideany(mouse_sprite, self.enemy_group)
                # take the first enemy found always
                if obj_found:
                    print(f"(ID, '{hash(obj_found)}')")
                    self.found_obj_info += f"\n(ID, '{hash(obj_found)}'), (type, '{type(obj_found).__name__}')\nlocated at x,y{obj_found.rect.center}"
                
            
            # record mouse positions
            if not self.show_debug and self.record_collision:
                self.record_mouse_positions(event)
            
            # response to keypress and held keys (movement) such that movement is smooth
            if event.type == pygame.KEYDOWN:
                

                if event.key == pygame.K_o:
                    print('saving mouse positions: mouse_positions_m.json')
                    with open('mouse_positions.json', 'w') as f:
                        json.dump(self.m_record.positions, f)

                elif event.key == pygame.K_m:
                    self.show_debug = not self.show_debug
                    if self.show_debug:
                        self.add_debug_groups()
                    else:
                        self.debug_group.empty()

                elif event.key == pygame.K_r:
                    self.record_collision = not self.record_collision
                    print(f'record collision enabled: {self.record_collision}')
                    
                elif event.key == pygame.K_RETURN:
                    self.parse_debug_command(self.debug_menu.text)
                
                else:
                    self.player.k_up_e(event.key, True)

            elif event.type == pygame.KEYUP:
                self.player.k_up_e(event.key, False)
           
        return events

    def parse_debug_command(self, command):
        parts = command.split()

        if len(parts) == 0:
            return

        if parts[0] == "e_spawn":
            new_e = Enemy(self.screen, pygame.mouse.get_pos())
            self.enemy_group.add(new_e)
            self.hit_box_group.add(new_e.empty_sprite)
            self.e_lookup[hash(new_e)] = new_e
            
        elif parts[0] == "e_del":
            if len(parts) < 2:
                print("Error: 'e_del' command requires an enemy hash.")
                return
            hash_str = parts[1]
            target_e = self.e_lookup.get(int(hash_str))
            if target_e is None: print(f"Error: No enemy with hash '{hash_str}' found.")
            else:
                self.enemy_group.remove(target_e)
                self.hit_box_group.remove(target_e.empty_sprite)
                self.e_lookup.pop(int(hash_str))
                
        elif parts[0] == "p_nc":
            self.player.no_clip = not self.player.no_clip
            self.player.colliding = False
            self.found_obj_info += f'\nno clip: {self.player.no_clip}'

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
        # set the colliding attribute of the enemy to the collision result
        [enemy.isColliding(True) for enemy in enemy_scene_collision]
        # observe the player for enemy AI
        p_events = self.player.rect.center
        self.enemy_group.update([p_events], debug=self.show_debug)

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
        # NOTE: shows the line of enemy paths
        # if self.show_debug:
        #     [n.add_line(*n.path_line) for n in self.enemy_group.sprites()]
        # draw the collision test
        self.test_collision_group.draw(self.screen)
        
    def make_temp_sprite(self, color, pos=(0, 0), size=(4, 4)):
        temp_sprite = pygame.sprite.Sprite()
        temp_sprite.rect = pygame.Rect(pos, size)
        temp_sprite.image = pygame.Surface(size)
        temp_sprite.image.fill(color)
        return temp_sprite

    def record_mouse_positions(self, event):
        # self.m_record, self.test_collision_group
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.m_record.is_dragging = True
            print(pygame.mouse.get_pos())
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.m_record.is_dragging = False
            
        if self.m_record.is_dragging:
            self.m_record.positions.append(pygame.mouse.get_pos())
            # print(mouse_positions)
            # add new collision rects to the collision group
            dot = self.make_temp_sprite((255, 0, 0), pygame.mouse.get_pos())
            self.test_collision_group.add(dot)
            

    def main(self):
        self.screen.blit(self.bg, (0, 0))
        while True:
            events = self.update(self.dt)
            self.group_updates()
            self.draw()
            self.fpsClock.tick(self.fps)
            self.debug_m_targets[self.show_debug](self.screen, events)
            pygame.display.update(self.screen.get_rect())
            self.dt = self.fpsClock.get_time()/1000

if __name__ == '__main__':
    # test the game
    game = MyGame()
    game.main()