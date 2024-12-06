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
import numpy as np
import json
# Import non-standard modules.
import pygame
from pygame.locals import *
import pygame.font as font
# import UI_elements as UI
from UI_elements_temp import *
from GameObjects import Player, Enemy, EnemyGroup, txtSprite
# import gameGUI.Base_Element as BE
from gameGUI import base_Element as BE
from sceneObj import Background
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
        self.screen = pygame.display.set_mode((0,0),display=1)
        self.width, self.height = self.screen.get_rect().size
        self.screen_rect = self.screen.get_rect()
        # scene setup
        pathDir = 'imgs\\scene\\'
        fNames = ['dark_tile.png', 'light_tile.png','house_t.png']
        imgPaths = [pathDir + f for f in fNames]
        self.background = Background(self.screen,imgPaths=imgPaths,
                                surfSize=self.screen.get_rect().size,
                                offSet=[[0, 0], [0, 0], [0, 0]])
        tileRange = [0, 1, 10, 11, 21,31,32,33,43,53,54,64,65,66,67,68] 
        np.vectorize(self.background.add_tile)(self.background.light_tile, tileRange, tType='light')
        self.background.draw_element_at(self.background.house_t, 0, 0)
        self.background.draw_scene()
        
        # get rect for only the light tiles
        light_tile = self.background.entityDict['light']
        # make a group to check for tile collisions
        self.light_group = pygame.sprite.Group()
        for rect in light_tile:
            self.light_group.add(pygame.sprite.Sprite())
            self.light_group.sprites()[-1].rect = rect
        # make the player
        self.player = Player(self.screen)
        # setup test enemies for the player to interact with
        self.enemy_group = EnemyGroup(self.screen, 
                                      self.background.get_tile(0, 0)[1].center,
                                      50)
        
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
        # 
        self.dt = 1/self.fps  # dt is the time since last frame.
        self.debug_group = pygame.sprite.Group()
        
        # gamestate is the group that will be drawn to the screen and updated
        self.gamestate = pygame.sprite.Group()
        self.gamestate.add([self.player, 
                            self.enemy_group,
                            self.enemy_group.ehb,
                            self.enemy_group.e_agro])
        # ---------------------------------------------------------------------- #
        self.debug_m_targets = {
            True: self.debug_UI_handler, False: self.empty_event}
        self.debug_menu.exclude = []
        self.found_obj_info = '----'
        self.ids = map(lambda x: hash(x), self.enemy_group.sprites())
        self.e_lookup = dict(zip(list(self.ids), self.enemy_group.sprites()))
        
        # make a text sprite for fps
        self.fps_txt = txtSprite((0, 0), 'fps: 0', self.myFont, (255, 255, 255))
        # add the fps text to the main gamestate
        self.gamestate.add(self.fps_txt)
        
    def debug_UI_handler(self, screen, events):
        # NOTE: shows the line of enemy paths
        # [n.drawPathing(*n.path_line) for n in self.enemy_group.sprites()]
        
        self.debug_menu.set_all(frame_counts=f'{self.player}',
                                direction_field=str(self.player.active_keys),
                                fps_field=f'fps: {int(self.fpsClock.get_fps())}',
                                xy_field=repr(self.player),
                                error_field=f'obj info: {self.found_obj_info}'
                               )
        self.debug_menu.main_no_loop(screen, events)
        self.debug_menu.blitme(self.screen)
        

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
                self.player.k_up_e(event.key, True)
                self.match_kdEvent(event)
            if event.type == pygame.KEYUP:
                self.player.k_up_e(event.key, False)
           
        return events

    def match_kdEvent(self, event):
        key = event.key
        match key:
            case pygame.K_o:
                print('saving mouse positions: mouse_positions_m.json')
                with open('mouse_positions.json', 'w') as f:
                    json.dump(self.m_record.positions, f)
            case pygame.K_m:
                self.show_debug = not self.show_debug
                if self.show_debug:
                    self.add_debug_groups()
                else:
                    self.debug_group.empty()
                    self.screen.blit(self.background.image, (0, 0))
            case pygame.K_r:
                self.record_collision = not self.record_collision
                print(f'record collision enabled: {self.record_collision}')
            case pygame.K_RETURN:
                # self.parse_debug_command(self.debug_menu.text)
                pass
            case _:
                pass

    def parse_debug_command(self, command):
        parts = command.split()
        if len(parts) == 0:
            return
        
        cmd = parts[0]
        
        match cmd:
            case "e_spawn":
                try:
                    n = int(parts[1])
                except ValueError:
                    n = 0
                    print("Error: 'e_spawn' command requires an integer argument. Defaulting to 0.")
                for _ in range(n): 
                    self.spawn_enemy()
                    
            case "e_del":
                if len(parts) < 2:
                    print("Error: 'e_del' command requires an enemy hash.")
                    return
                hash_str = parts[1]
                target_e = self.e_lookup.get(int(hash_str))
                if target_e is None: print(f"Error: No enemy with hash '{hash_str}' found.")
                else:
                    self.enemy_group.remove(target_e)
                    self.enemy_group.ehb.remove(target_e.collisionSprite)
                    self.e_lookup.pop(int(hash_str))
                
            case "p_nc":
                self.player.no_clip = not self.player.no_clip
                self.player.colliding = False
                self.found_obj_info += f'\nno clip: {self.player.no_clip}'
                
            case "count_e":
                print(f'enemy count: {len(self.enemy_group)}')
                self.found_obj_info += f'\nenemy count: {len(self.enemy_group)}'
            
            case _:
                print(f"Error: '{cmd}' is not a valid command.")

    def spawn_enemy(self):
        new_e = self.enemy_group.spawnEnemy(pygame.mouse.get_pos())
        self.e_lookup[hash(new_e)] = new_e
        # add the new enemy to the hit box group
        self.enemy_group.ehb.add(new_e.collisionSprite)
        self.enemy_group.e_agro.add(new_e.agro_circle)
        self.gamestate.add(self.enemy_group)
        

    def add_debug_groups(self):
        self.debug_group.add(self.enemy_group.e_agro.sprites())
        # self.debug_group.add(self.enemy_group.ehb.sprites())
        # self.debug_group.add(self.player.collisionSprite)
        self.debug_group.add(self.player.dot)
        # [n.drawPathing(*n.path_line) for n in self.enemy_group.sprites()]
        
    def group_updates(self):
        # check enemy pos vs scene valid tiles
        check = pygame.sprite.groupcollide(
            self.enemy_group.ehb, self.light_group, False, False)
        # update group collision status
        # # if there is a collision, we ar in a valid tile and can move isColliding(False)
        self.player.collisionSprite.update()
        self.enemy_group.ehb.valid_tile_update(check)
        # observe the player for enemy AI
        self.gamestate.update(enemy_events=[self.player.rect.center], 
                              debug=False,
                              text=f'fps: {int(self.fpsClock.get_fps())}')

    def draw(self):
        """
        Draw things to the window. Called once per frame.
        """
        self.gamestate.remove([self.enemy_group.ehb, self.enemy_group.e_agro])
        self.debug_group.clear(self.screen, self.background.image)
        self.test_collision_group.clear(self.screen, self.background.image)       
        self.gamestate.clear(self.screen, self.background.image)
        # draw gamestate
        self.debug_group.draw(self.screen)
        if self.show_debug:
            
            [n.drawPathing(*n.path_line) for n in self.enemy_group.sprites()]
        self.test_collision_group.draw(self.screen)
        self.gamestate.draw(self.screen)
        
        # add back gamestate groups
        self.gamestate.add([self.enemy_group.ehb, self.enemy_group.e_agro])
        # update the display using rects in pygame.display.update
        
        
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
        self.screen.blit(self.background.image, (0, 0))
        pygame.display.update()
        while True:
            events = self.update(self.dt)
            self.group_updates()
            if self.show_debug:
                # clear the background
                self.screen.blit(self.background.image, (0, 0))
            self.draw()
            # self.debug_m_targets[self.show_debug](self.screen, events)
            self.dt = self.fpsClock.get_time()/1000
            self.fpsClock.tick(self.fps)
            pygame.display.update() 

if __name__ == '__main__':
    # test the game
    game = MyGame()
    game.main()