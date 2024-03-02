# Started from PyGame template. from https://gist.github.com/MatthewJA/7544830
# 
# Import standard modules.
import sys
import time
import json
# Import non-standard modules.
import pygame
from pygame.locals import *
import pygame.font as font
from UI_elements_temp import *
# import UI_elements as UI
from GameObjects import Player, Enemy
from dev_tools import MousePositions as MP



class DebugMenu(Txt_confirm):
    def __init__(self,subject='-debug menu-', add_cursor=True, buttons=['direction: ','']):
        super().__init__(prompt_subject=subject, add_cursor_box=add_cursor, button_labels=buttons)
        # make debug rects bigger
        self.buttons[0]['rect'].width += 50
        self.buttons[1]['rect'].width = 225
        self.rect_text.width += 125
        self.prompt['rect'].width += 125
        self.button_offsets.append((80,80))
        self.add_buttons(['fps:'], [(80,80)])
    @property
    def xy_field(self) -> str:
        return self.text
    
    @xy_field.setter
    def xy_field(self, value):
        self.text = value
        
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
        return self.buttons[-1]['label']
    
    @fps_field.setter
    def fps_field(self, value):
        self.buttons[-1]['label'] = value
    
    def set_all(self, frame_counts, direction_field, fps_field, xy_field):
        self.frame_counts = frame_counts
        self.direction_field = direction_field
        self.fps_field = fps_field
        self.xy_field = xy_field

def update(dt, player: Player, mouse_positions: MP, collision_group: pygame.sprite.Group, **kwargs):
    """
    Update game. Called once per frame.
    dt is the amount of time passed since last frame.
    If you want to have constant apparent movement no matter your framerate,
    what you can do is something like

    x += v * dt

    and this will scale your velocity based on time. Extend as necessary."""
    show_debug = kwargs.get('show_debug', False)
    record_collision = kwargs.get('record_collision', False)
    enemies = kwargs.get('enemies', [])
    # Go through events that are passed to the script by the window.
    events = pygame.event.get()
    for event in events:
        # If the window is closed, quit the game.
        if event.type == QUIT:
            pygame.quit()  # Opposite of pygame.init
            sys.exit()  # Not including this line crashes the script on Windows. Possibly
            # on other operating systems too, but I don't know for sure.
        if not show_debug and record_collision:
            record_mouse_positions(event, mouse_positions, collision_group)
        
        # Handle other events as you wish.
        # response to keypress and held keys (movement) such that movement is smooth
        if event.type == pygame.KEYDOWN:
            player.k_up_e(event.key, True)
            
            
            if event.key == pygame.K_o:
                print('saving mouse positions: mouse_positions_m.json')
                with open('mouse_positions.json', 'w') as f:
                    json.dump(mouse_positions.positions, f)
                    
            elif event.key == pygame.K_1:
                show_debug = not show_debug
                
            elif event.key == pygame.K_2:
               record_collision = not record_collision
               print(f'record collision enabled: {record_collision}')
                
        elif event.type == pygame.KEYUP:
            player.k_up_e(event.key, False)
        # record mouse positions
        
    player.update(collision_group, debug=show_debug)
    # update the enemy
    
    return show_debug, record_collision ,events
        

def draw(screen, scene:pygame.Surface, player: Player, player_name: pygame.Surface, collision_group: pygame.sprite.Group):
    
    """
    Draw things to the window. Called once per frame.
    """
    # Blit the scene onto the screen.
    screen.blit(scene, (0, 0))
    # draw the debug text above the player
    txt = player_name
    # use player center to get x and y coordinates for the text
    txt_loc = (player.x+player.rect.width/3, player.y-player.rect.height/4)
    # draw the player
    player.blitme()
    # draw the player name
    screen.blit(txt, txt_loc)
    # draw the enemy
    
    
    # draw the collision test
    collision_group.draw(screen)
    

def record_mouse_positions(event, mouse_positions: MP, test_collision_group: pygame.sprite.Group ):
    
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_positions.is_dragging = True
    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_positions.is_dragging = False
        
    if event.type == pygame.MOUSEMOTION and mouse_positions.is_dragging:
        mouse_positions.positions.append(pygame.mouse.get_pos())
        # print(mouse_positions)
        # add new collision rects to the collision group
        test_collision_group.add(pygame.sprite.Sprite())
        test_collision_group.sprites()[-1].rect = pygame.Rect(pygame.mouse.get_pos(), (1, 1))
        test_collision_group.sprites()[-1].image = pygame.Surface((4,4))
        test_collision_group.sprites()[-1].image.fill((255, 0, 0))
        
        time.sleep(0.05)
    # handle normal mouse clicks
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        print(pygame.mouse.get_pos())
        # time.sleep(0.05)

def runPyGame(**kwargs):
    # create a global variable for show_collision
    show_debug = False
    record_collision = False
    # Initialise PyGame.
    pygame.init()
    # Set up the clock. This will tick every frame and thus maintain a relatively constant framerate. Hopefully.
    fps = 60.0
    fpsClock = pygame.time.Clock()
    # setup a default font for pygame
    myFont = font.SysFont('Comic Sans MS', 12)
    # Set up the window.
    width, height = 1920, 1080
    screen = pygame.display.set_mode((width, height))
    
    # make the player
    player = Player(screen)
    # setup test enemy
    enemy = Enemy(screen)
    # make enemy part of a sprite group, this will be its actual implementation, currently testing
    enemy_group = pygame.sprite.Group()
    enemy_group.add(enemy)
    start_menu = Txt_confirm(
        prompt_subject='-enter player name-',
        add_cursor_box=True)
    debug_menu = DebugMenu()
    
    menu_result = start_menu.main(screen)
    player_name = myFont.render(menu_result, False, (255, 255, 255))
    # test collision has an x and y coordinate for each segment of test_collision
    # make a sprite group for the test collision so we can use pygame's collision detection
    test_collision = json.load(open('mouse_positions_m.json'))
    m_record = MP(test_collision)
    test_collision_group = pygame.sprite.Group()
    for i in range(len(test_collision)):
        test_collision_group.add(pygame.sprite.Sprite())
        test_collision_group.sprites()[i].rect = pygame.Rect(test_collision[i], (1, 1))
        test_collision_group.sprites()[i].image = pygame.Surface((4,4))
        test_collision_group.sprites()[i].image.fill((255, 0, 0))

    # load the background image: cave_bg.png
    bg = pygame.image.load('cave_bg.png')
    # scale the background image to the screen size
    bg = pygame.transform.scale(bg, (width, height))
    # Main game loop.
    dt = 1/fps  # dt is the time since last frame.
    while True:  # Loop forever!
        # You can update/draw here, I've just moved the code for neatness.
        show_debug, record_collision, events = update(dt, 
               player,
               m_record,
               test_collision_group,
               show_debug=show_debug,
               record_collision=record_collision,
               enemies=enemy)
        draw(screen,
            bg,
            player,
            player_name,
            test_collision_group)
        
        dt = fpsClock.tick(fps)
        if show_debug:
            # set the debug menu fields
            debug_menu.set_all(f'{player}', 
                               str(player.active_keys),
                               f'fps: {int(fpsClock.get_fps())}', 
                               repr(player))
            # draw the debug menu
            debug_menu.main_no_loop(screen, events)
        pygame.display.flip()

if __name__ == "__main__":

    
    runPyGame()
    # If the script is run directly (i.e. not imported), run the game.
