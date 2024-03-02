# Author: Cameron Kerley
# Date: 03/1/2024
# Description: this file contains the GameObjects used in the game such as the player and enemies and their animations
# this is my original code, but the chat feature of copilot was used to help provide examples on how to achieve certain tasks

import glob
import json
import random
import pygame


class Keyframe:
    def __init__(self, image, duration, flip: bool = False) -> None:
        """create a keyframe sequence for an animation\n


        Args:
            image (str): path to image file
            duration (int): number of frames to display the image
            flip (bool, optional): flip the image horizontally. Defaults to False.
        """
        self.flip = flip
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (100, 100))
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.duration = duration

    @property
    def key_sequence(self):
        return self.create_sequence(self.duration)

    def create_sequence(self, duration=3) -> list:
        return [self.image for i in range(duration)]

    def __repr__(self):
        return f'Keyframe({self.image}, {self.duration}, {self.flip})'

    # allow *Keyframe
    def __iter__(self):
        return self.key_sequence.__iter__()

    def __next__(self):
        return self.key_sequence.__next__()

    def __getitem__(self, key) -> pygame.Surface:
        return self.key_sequence[key]

    def __len__(self):
        return len(self.key_sequence)

    def __setitem__(self, key, value):
        self.key_sequence[key] = value

    def __delitem__(self, key):
        del self.key_sequence[key]


class Animation:
    def __init__(self, keyframes: list, flip=False) -> None:
        """create an animation from a list of keyframes\n
        keyframes are tuples of (image, duration, flip)\n
        image is the path to the image file\n
        duration is the number of frames to display the image\n
        flip is a boolean value to flip the image horizontally\n
        """
        self.setup_args = keyframes
        self.keyframes = [Keyframe(*keyframe, flip=flip) for keyframe in keyframes]
        self.current_frame = 0
        self.frame_count = 0
        self.image = self.keyframes[self.current_frame]
        # duration is len of all keyframes
        self.duration = len(self.animation_sequence)

    @property
    def animation_sequence(self):
        return self.create_sequence()

    def create_sequence(self):
        result = []
        for keyframe in self.keyframes:
            result.extend([*keyframe])
        return result

    def get_frame(self):
        frame = self.animation_sequence[self.frame_count]
        self.frame_count = (self.frame_count+1) % self.duration
        return frame

    def set_frame(self, frame: int):
        '''set the frame count to the given frame number relative to the duration of the animation\n
        frame > duration = frame%duration\n'''
        self.frame_count = frame % self.duration

    def __repr__(self):
        return f'Animation({self.setup_args})'

    # str(Animation) returns current frame number
    def __str__(self):
        return f'{self.frame_count}'

# class to represent bound_keys
class BoundKeys(dict):
    def __init__(self, keys: list) -> None:
        super().__init__()
        self.buttons = keys
        self.vals = [False]*len(keys)
        self.bound_keys = dict(zip(keys, self.vals))

    def __getitem__(self, button) -> bool:
        return self.bound_keys[button]

    def __setitem__(self, button, value) -> None:
        self.bound_keys[button] = value

    def __repr__(self) -> str:
        return f'BoundKeys({self.bound_keys})'

    def __str__(self) -> str:
        return f'{self.bound_keys}'
    
    def keys(self) -> list:
        return self.bound_keys.keys()
    
    def values(self) -> list:
        return self.bound_keys.values()
    
    def items(self) -> list:
        return self.bound_keys.items()
    
class WASD:
    def __init__(self) -> None:
        self.wasd_keys = BoundKeys([pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])
    
    def k_up_e(self, key, held):
        """key up event handler\n"""
        if key in self.wasd_keys.keys():
            self.wasd_keys[key] = held
    
    def __repr__(self) -> str:
        return f'WASD({self.wasd_keys})'
    
    def __str__(self) -> str:
        return f'{self.wasd_keys}'
      
    @property
    def active_keys(self) -> list:
        return [chr(key) for key, value in self.wasd_keys.items() if value]
    
    @property
    def moving_up(self) -> bool:
        return self.wasd_keys[pygame.K_w]
    
    @moving_up.setter
    def moving_up(self, value) -> None:
        self.wasd_keys[pygame.K_w] = value
        
    @property
    def moving_down(self) -> bool:
        return self.wasd_keys[pygame.K_s]
    
    @moving_down.setter
    def moving_down(self, value) -> None:
        self.wasd_keys[pygame.K_s] = value
        
    @property
    def moving_left(self):
        return self.wasd_keys[pygame.K_a]
    
    @moving_left.setter
    def moving_left(self, value) -> None:
        self.wasd_keys[pygame.K_a] = value
        
    @property
    def moving_right(self) -> bool:
        return self.wasd_keys[pygame.K_d]
    
    @moving_right.setter
    def moving_right(self, value) -> None:
        self.wasd_keys[pygame.K_d] = value

class Player(pygame.sprite.Sprite, WASD):
    def __init__(self, screen):
        # Call the parent inits to inherit from both classes
        pygame.sprite.Sprite.__init__(self)
        # set up WASD movement
        WASD.__init__(self)
        # Add any additional initialization code here
        self.screen = screen
        self.screen_rect = screen.get_rect()

        #gather all the images in the current directory
        im_list = glob.glob('**/*.png', recursive=True)
        player_paths = list(filter(lambda x: 'Player_ims' in x, im_list))
        # walk_imgs = list(filter(lambda x: 'walk' in x, local_imgs))
        def_img = list(filter(lambda x: 'rogue_default' in x, player_paths))[0]
        if def_img in im_list:
            self.image = pygame.image.load(def_img)
        else:
            self.image = pygame.Surface((100, 100))
            self.image.fill((0, 255, 0))

        # scale the image
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()

        # Start each new player at the center of the screen.
        self.rect.center = self.screen_rect.center

        # store x and y coordinates
        self.x = self.rect.x
        self.y = self.rect.y

        # set the speed of the player
        self.speed = 2.5

        self.face_l = self.image.copy()
        def_img = list(filter(lambda x: 'rogue_b' in x, player_paths))[0]
        self.face_u = pygame.image.load(def_img)
        self.face_u = pygame.transform.scale(self.face_u, (100, 100))
        self.face_r = pygame.transform.flip(self.face_l, True, False)

        # setup the walking animations from the json files
        self.front_w_a = json.load(open('front_walk.json'))
        self.side_w_a = json.load(open('side_walk.json'))
        self.back_w_a = json.load(open('back_walk.json'))

        
        self.front_walk = Animation(self.front_w_a)
        self.b_walk = Animation(self.back_w_a)
        self.right_walk = Animation(self.side_w_a)
        # other direction only requires flipping the image
        self.left_walk = Animation(self.side_w_a, flip=True)

        self.empty_sprite = hit_box((self.x, self.y), (50, 25))
        
        self.stable_ground = (0, 0)
        self.show_debug = False
        self.dot = self.get_dot()
        
    @property
    def colliding(self):
        return self.empty_sprite.colliding
    
    @colliding.setter
    def colliding(self, value):
        self.empty_sprite.colliding = value
        
    
    def get_dot(self):
        dot = pygame.sprite.Sprite()
        dot.image = pygame.Surface((4,4))
        dot.image.fill((0, 255, 0))
        dot.rect = pygame.Rect(self.rect.center, (4, 4))
        return dot

     
    def update(self, coli_group, debug=False):
        """Update the player's position based on wasd keypress."""
        self.show_debug = debug
        self.wasd_movement()
        #
        # check for player collision with the test_collision_group
        self.hit_box_update()
        self.player_collision(coli_group)

    def wasd_movement(self, debug=False):
        if debug:
            self.image = self.b_walk.get_frame()

        # check for key presses modifying up&down
        self.y_axis_movement()
        # same for left&right
        self.x_axis_movement()
        # update the player's rect: pushes x,y -> rect.x, rect.y
        self.pos_update()

    def pos_update(self):
        '''update the player's position based on changes to x and y.\n
        Player.x, Player.y -> Player.rect.x, Player.rect.y'''
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def y_axis_movement(self):
        if self.moving_up:
            # make it look like it's moving up
            self.image = self.b_walk.get_frame()
            self.y -= self.speed

        elif self.moving_down:
            # make sure its the normal image
            self.image = self.front_walk.get_frame()
            self.y += self.speed

    def x_axis_movement(self):
        if self.moving_left:
            # image faces left by default
            self.image = self.left_walk.get_frame()
            self.x -= self.speed

        elif self.moving_right:
            # flip the image to face right
            self.image = self.right_walk.get_frame()
            self.x += self.speed
        

    def player_collision(self, coli_group, x_mod: int = 0, y_mod: int = 0, r_depth: int = 0):
        
        if self.colliding:
            #
            # go back to the last stable ground
            self.x, self.y = self.stable_ground
            print(f'stable ground chosen at {self.stable_ground}')
            
        
        self.stable_ground = (self.x, self.y)
            

    def check_next_collision(self, p_hit, coli_group,  co_ef: tuple = (0, 0)):
        '''use negative values for subtracting from the hit box, 
        so we can simply add the co_ef to the player's rect regardless of direction\n
        usage: \n
            co_ef = [-x_mod, +y_mod, +w_mod, -h_mod],\n
            hit_box = [x+(-x_mod), y+(+y_mod), w+(+w_mod), h+(-h_mod)]'''
        x_mod, y_mod, = co_ef
        p_hit.rect.x, p_hit.rect.y = self.empty_sprite.rect.x+x_mod, self.empty_sprite.rect.y+y_mod

        return pygame.sprite.spritecollide(p_hit, coli_group, False)

    def hit_box_update(self):
        '''update rect used for collision detection\n
        updates Player.h_rect, DOES NOT UPDATE 'Player.rect'\n'''
        self.empty_sprite.rect.x = self.x
        self.empty_sprite.rect.y = self.y
        self.empty_sprite.rect.width = self.rect.width/2
        self.empty_sprite.rect.height = self.rect.height/4
        self.empty_sprite.rect.midbottom = self.rect.midbottom
        # Update rect object from self.x and self.y.
        self.dot.rect.center = self.rect.center
        
    def blitme(self):
        """Draw the player at its current location."""
        # self.rect = self.image.get_rect()
        self.screen.blit(self.image, (self.x, self.y))
        

    def save_animations(self):
        save_setup = zip([self.front_w_a, self.side_w_a, self.back_w_a],
                         ['front_walk', 'side_walk', 'back_walk'])
        for anim, name in save_setup:
            with open(f'{name}.json', 'w') as f:
                json.dump(anim, f)

    def __repr__(self):
        return f'P(x: {round(self.x)}, y: {round(self.y)})'

    # str(Player) returns all animation frame counts
    def __str__(self):
        return f'Frames(front:{self.front_walk} |back:{self.b_walk} |right:{self.right_walk} |left:{self.left_walk})'

class hit_box(pygame.sprite.Sprite):
    def __init__(self, cords: tuple, size: tuple):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords
        self.colliding = False

# enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, cords: tuple = (0, 0)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = pygame.image.load('imgs\\enemy\\enemy.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.clean_image = self.image.copy()
        self.rect = self.image.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom
            
        self.rect.x, self.rect.y = self.rect.x-100, self.rect.y-100
        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = 2
        self.empty_sprite = hit_box(cords, (50, 25))
        
        self.agro_range = random.randint(150, 200)
        # make a circle to represent the agro range
        self.agro_circle = pygame.sprite.Sprite()
        self.agro_circle.image = pygame.Surface((self.agro_range*2, self.agro_range*2), pygame.SRCALPHA)
        # draw the circle is transparent white
        self.agro_circle.rect = pygame.draw.circle(self.agro_circle.image, 
                                                   (255, 255, 255, 100),
                                                   (self.agro_range, self.agro_range),
                                                   self.agro_range)
        self.agro_circle.rect.center = self.rect.center
        
        self.show_debug = False
        self.frame_count = 0
        self.frame_seed = random.randint(10, 49)
        self.rand_mod = random.randint(50,70)
        self.stable_ground = (0, 0)
        self.line = pygame.sprite.Sprite()
        self.line.image = pygame.Surface((self.agro_range*2, self.agro_range*2), pygame.SRCALPHA)
        self.line.image.fill((0, 0, 0, 0))
        self.line.rect = self.agro_circle.rect
        self.flush_match = dict(zip((False, True), (lambda: None, self.flush_agro)))
        self.line_match = dict(zip((False, True), (lambda x, y: None, self.add_line)))
    # alias for self.empty_sprite.colliding
    @property
    def colliding(self):
        return self.empty_sprite.colliding
    
    @colliding.setter
    def colliding(self, value):
        self.empty_sprite.colliding = value
    
    def update(self, enemy_events, debug=False, colliding=False):
        self.show_debug = debug
        self.flush_match[self.show_debug]()
        self.enemy_movement(enemy_events)
        self.colliding = colliding
        
        self.pos_update()
        self.hit_box_update()
        # ground is likely to be stable
        

    def dist_from_agro(self, p_x, p_y):
        '''return the distance from the player\n
        distance = sqrt((x2-x1)^2 + (y2-y1)^2)'''
        x, y = self.agro_circle.rect.center
        return ((p_x - x)**2 + (p_y - y)**2)**0.5
        
    def enemy_movement(self, enemy_events):
        # move the enemy towards the player if the player is within 200 pixels
        p_x, p_y = enemy_events
        
        if not self.colliding:
            dist = self.dist_from_agro(p_x, p_y)
            if abs(dist) <= self.agro_range:
                # draw a line from the enemy to the player on agro circle
                self.line_match[self.show_debug](*enemy_events)
                if p_x > self.x:
                    self.x += self.speed
                elif p_x < self.x:
                    self.x -= self.speed
                if p_y > self.y:
                    self.y += self.speed
                elif p_y < self.y:
                    self.y -= self.speed
                    
            elif self.frame_count%self.rand_mod > self.frame_seed: 
                    m1 = random.randint(-3, 3)
                    m2 = random.randint(-3, 3)
                    self.x += m1
                    self.y += m2
        else:
            # don't move if colliding
            self.x -= self.speed
            self.y -= self.speed
            
        self.frame_count += 1

    def add_line(self, p_x, p_y):
        e_x, e_y = self.rect.center
                # convert our position to the agro circle's coordinate system
        e_x_mod = e_x - self.agro_circle.rect.x
        e_y_mod = e_y - self.agro_circle.rect.y
                # convert the player's position to the agro circle's coordinate system
        p_x_mod = p_x - self.agro_circle.rect.x
        p_y_mod = p_y - self.agro_circle.rect.y
                # flush previous lines
                
        pygame.draw.line(self.agro_circle.image, (0, 255, 0), (e_x_mod, e_y_mod), (p_x_mod, p_y_mod), 2)

    def flush_agro(self):
        self.agro_circle.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.agro_circle.image, 
                            (255, 255, 255, 100),
                            (self.agro_range, self.agro_range),
                            self.agro_range)
        
    def pos_update(self):
        '''update the player's position based on changes to x and y.\n
        Player.x, Player.y -> Player.rect.x, Player.rect.y'''
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        # update the agro circle
        self.agro_circle.rect.center = self.rect.center
        
    def hit_box_update(self):
        '''update rect used for collision detection\n
        updates Player.h_rect, DOES NOT UPDATE 'Enemy.rect'\n'''
        self.empty_sprite.rect = self.empty_sprite.rect
        self.empty_sprite.rect.x = self.x + self.rect.width/4
        self.empty_sprite.rect.y = self.y + self.rect.height*0.7
        

        # Update rect object from self.x and self.y.
    
    # override the draw method
    def blitme(self):
        """Draw the player at its current location."""
        # self.rect = self.image.get_rect()
        self.screen.blit(self.image, (self.x, self.y))
        # show the collision rect if debug is on
       
    
        

if "__main__" == __name__:
    import glob
    im_list = glob.glob('**/*.png', recursive=True)
    print('\n'.join(im_list))
    pygame.init()
    pygame.quit()
