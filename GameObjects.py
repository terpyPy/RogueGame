# Author: Cameron Kerley
# Date: 03/1/2024
# Description: this file contains the GameObjects used in the game such as the player and enemies and their animations
# this is my original code, but the chat feature of copilot was used to help provide examples on how to achieve certain tasks

import glob
import json
import math
import random
import time
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
        try:
            self.image = pygame.image.load(image)
            self.image = pygame.transform.scale(self.image, (100, 100))
            if flip:
                self.image = pygame.transform.flip(self.image, True, False)
        except FileNotFoundError:
            print(f"Unable to load image at {image}.")
            # set a default image that is a neon pink square
            self.image = pygame.Surface((100, 100))
            self.image.fill((255, 0, 255))
            # fill with 'error' text
            font = pygame.font.Font(None, 25)
            text = font.render('Error', True, (0, 0, 0))
            self.image.blit(text, (50, 50))
        except TypeError:
            # assume image is already a surface
            self.image = image
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
        self.keyframes = [Keyframe(*keyframe, flip=flip)
                          for keyframe in keyframes]
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


# class to represent bound_keys for the player
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
        self.wasd_keys = BoundKeys(
            [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])

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


class PlayerInterface(pygame.sprite.Sprite, WASD):
    def __init__(self):
        """initialize the player interface\n
        wrapper class for the player to inherit from\n"""
        pygame.sprite.Sprite.__init__(self)
        WASD.__init__(self)


class hit_box(pygame.sprite.Sprite):
    def __init__(self, cords: tuple, size: tuple):
        """create a hit box for collision detection\n

        Args:
            cords (tuple): tuple of x, y coordinates
            size (tuple): tuple of width, height
        """
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords
        self.colliding = False
        
    def isColliding(self, value):
        self.colliding = value    


class Player(PlayerInterface):
    def __init__(self, screen):
        # Call the parent inits to inherit from both classes
        super().__init__()
        # Add any additional initialization code here
        self.screen = screen
        self.screen_rect = screen.get_rect()

        # gather all the images in the current directory
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

        # setup the walking animations from the json files
        self.front_w_a = json.load(open('front_walk.json'))
        self.side_w_a = json.load(open('side_walk.json'))
        self.back_w_a = json.load(open('back_walk.json'))
        self.idle_w_a = json.load(open('idle_walk.json'))
        # append a bad path to the idle animation to test the error handling
        # self.idle_w_a.append(('bad_path.png', 10))
        self.front_walk = Animation(self.front_w_a)
        self.b_walk = Animation(self.back_w_a)
        self.right_walk = Animation(self.side_w_a)
        # other direction only requires flipping the image
        self.left_walk = Animation(self.side_w_a, flip=True)
        # idle animation is the same for all directions currently
        self.idle_walk = Animation(self.idle_w_a)
        self.idle_walk_r = Animation(self.idle_w_a, flip=True)
        self.current_idle = self.idle_walk
        # imaginary box for collision detection
        self.empty_sprite = hit_box((self.x, self.y), (50, 25))

        self.stable_ground = (0, 0)
        self.show_debug = False
        self.dot = self.get_dot()
        self.no_clip = False

    @property
    def colliding(self):
        return self.empty_sprite.colliding

    @colliding.setter
    def colliding(self, value):
        self.empty_sprite.colliding = value

    def get_dot(self):
        dot = pygame.sprite.Sprite()
        dot.image = pygame.Surface((4, 4))
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
        """Update the player's position based on wasd keypress."""
        #
        # check directions, if not moving the sum of the keys values will be 0
        if sum(self.wasd_keys.values()) == 0:
            self.idle()
        else:
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

    def idle(self):
        # when the player is not inputting any movement keys
        # set the player's image to the default image.
        self.image = self.current_idle.get_frame()

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
            self.current_idle = self.idle_walk

        elif self.moving_right:
            # flip the image to face right
            self.image = self.right_walk.get_frame()
            self.x += self.speed
            self.current_idle = self.idle_walk_r

    def player_collision(self, coli_group, x_mod: int = 0, y_mod: int = 0, r_depth: int = 0):
        if self.colliding and not self.no_clip:
            #
            # go back to the last stable ground
            self.x, self.y = self.stable_ground
            print(f'stable ground chosen at {self.stable_ground}')

        self.stable_ground = (self.x, self.y)

    def hit_box_update(self):
        '''update rect used for collision detection\n
        updates Player.h_rect, DOES NOT UPDATE 'Player.rect'\n'''
        self.empty_sprite.rect.x = self.x
        self.empty_sprite.rect.y = self.y
        self.empty_sprite.rect.width = self.rect.width*0.5
        self.empty_sprite.rect.height = self.rect.height*0.25
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


# we want enemies that create a patrol route on init
# this generator should yield next such that when the last element is reached we reverse the list and continue to yield next.
# it should yield "left" "right" "up" "down" for the duration of the time given in the constructor
class Patrol:
    """
    A class representing a patrol that moves along a predefined route.

    Attributes:
    - time (int): The total number of times the patrol will move along the route.
    - route (list): The list of locations representing the patrol's route.
    - index (int): The current index of the patrol's position in the route.
    - direction (int): The direction of movement (-1 for reverse, 1 for forward).

    Methods:
    - __init__(time: int, route: list): Initializes the Patrol object with the given time and route.
    - __iter__(): Returns the iterator object for the Patrol.
    - __next__(): Returns the next location in the patrol's route.
    """

    def __init__(self, time: int, route: list):
        self.times = time
        self.T = time
        self.route = route
        self.index = 0
        self.direction = 1

    def __iter__(self):
        return self

    def __next__(self):
        # if the time is up, reset the time and determine the direction
        if self.times == 0:
            self.times = self.T
            # if the index is at the end of the route, reverse the direction
            if self.index == len(self.route)-1:
                self.direction = -1
            # if the index is at the beginning of the route, set the direction to forward
            if self.index == 0:
                self.direction = 1

            self.index += self.direction  # index current direction
        # decrement iteration count for current direction
        self.times -= 1
        return self.route[self.index]

# create a cord generator that produces a valid point the enemy can move to for n frames


class EnemyPath:
    def __init__(self, n_frames: int, screen_size: tuple, frame_count: int = 0):
        self.game_tics = n_frames
        self.screen_size = screen_size
        self.x = random.randint(0, self.screen_size[0])
        self.y = random.randint(0, self.screen_size[1])
        self.frame_count = frame_count

    def __iter__(self):
        return self

    def __next__(self):
        # every 60 frames = 1 game tic (60 fps target)
        # calculate current game tic from frame count
        game_tic = self.frame_count//self.game_tics
        if game_tic >= self.game_tics:
            self.x = random.randint(0, self.screen_size[0])
            self.y = random.randint(0, self.screen_size[1])
            self.frame_count = 0
        return (self.x, self.y)
    
class base_weapon(pygame.sprite.Sprite):
    def __init__(self, screen, cords: tuple = (0, 0)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = pygame.image.load('imgs\\enemy\\scaled_dagger.png')
        # self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom

class base_helmet(pygame.sprite.Sprite):
    def __init__(self, screen, cords: tuple = (0, 0)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = pygame.image.load('imgs\\enemy\\e_helm.png')
        # self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom
            
class base_shield(pygame.sprite.Sprite):
    def __init__(self, screen, cords: tuple = (0, 0)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.image = pygame.image.load('imgs\\enemy\\e_shield.png')
        # self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom

class equip_group(pygame.sprite.Group):
    def __init__(self, screen, xy: tuple = (1,1)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.weapon = base_weapon(screen, cords=xy)
        self.helmet = base_helmet(screen, cords=xy)
        self.shield = base_shield(screen, cords=xy)
        self.add(self.weapon, self.helmet, self.shield)
        
    def blit_to_target(self, target):
        for item in self:
            target.blit(item.image, item.rect)
            
import pygame

class AniRig(pygame.sprite.Group):
    def __init__(self, screen, offSet: tuple = (1, 1), imgPaths: list = [], surfSize: tuple = (100, 100), cords: tuple = (0, 0)):
        """
        Create a sprite rig for animations, made up of multiple component sprites like head, body, legs, etc.
        Args:
            screen (pygame.Surface): The screen surface to blit the GameObject on.
            offSet (tuple, optional): The offset position of the GameObject's images. Defaults to (1, 1).
            imgPaths (list, optional): The list of image file paths for the GameObject's images. Defaults to an empty list.
            surfSize (tuple, optional): The size of the surface for the GameObject. Defaults to (100, 100).
            cords (tuple, optional): The initial coordinates of the GameObject. Defaults to (0, 0).
        """
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.offSet = offSet
        self.surfSize = surfSize
        self.cords = cords

        self.images = self.load_images(imgPaths)
        self.create_sprites()
        self.image = pygame.Surface(surfSize, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=cords)

    def load_images(self, imgPaths):
        """
        Load images from file paths and return a dictionary of image names and surfaces.
        Args:
            imgPaths (list): List of image file paths.
        Returns:
            dict: Dictionary with image names as keys and surfaces as values.
        """
        images = {}
        for img in imgPaths:
            try:
                image = pygame.image.load(img)
                img_name = img.split('\\')[-1].split('.')[0]
                images[img_name] = image
            except pygame.error as e:
                print(f"Failed to load image {img}: {e}")
        return images

    def create_sprites(self):
        """
        Create sprites from the loaded images and add them to the group.
        """
        for attr, image in self.images.items():
            sprite = pygame.sprite.Sprite()
            sprite.image = image
            sprite.clean_image = image.copy()
            sprite.rect = image.get_rect(topleft=self.offSet)
            setattr(self, attr, sprite)
            self.add(sprite)

    def draw_rig(self):
        """
        Blit the component sprites onto the rig's surface.
        Returns:
            pygame.Surface: The surface with all component sprites blitted.
        """
        self.image.fill((0, 0, 0, 0))  # Clear the surface by filling it with transparency
        for sprite in self.sprites():
            self.image.blit(sprite.image, sprite.rect.topleft)
        return self.image

    def rotate_component(self, component_name, angle):
        """
        Rotate a target component sprite by the given angle.
        Args:
            component_name (str): The name of the component sprite to rotate.
            angle (float): The angle to rotate the sprite by.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            original_image = self.images[component_name]
            rotated_image = pygame.transform.rotate(original_image, angle)
            sprite.image = rotated_image
            sprite.rect = rotated_image.get_rect(center=sprite.rect.center)
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
        
    def pivot_component(self, component_name, pivot_point, angle):
        """
        Rotate a target component sprite around a pivot point.
        Args:
            component_name (str): The name of the component sprite to rotate.
            pivot_point (tuple): The pivot point (x, y) around which to rotate the sprite.
            angle (float): The angle to rotate the sprite by.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            original_image = self.images[component_name]
            
            # Calculate the offset from the pivot point to the sprite's center
            pivot_x, pivot_y = pivot_point
            sprite_center_x, sprite_center_y = sprite.rect.center
            offset_x = sprite_center_x - pivot_x
            offset_y = sprite_center_y - pivot_y

            # Calculate the rotated offset
            angle_rad = math.radians(angle)
            rotated_offset_x = offset_x * math.cos(angle_rad) - offset_y * math.sin(angle_rad)
            rotated_offset_y = offset_x * math.sin(angle_rad) + offset_y * math.cos(angle_rad)

            # Update the sprite's position
            new_center_x = pivot_x + rotated_offset_x
            new_center_y = pivot_y + rotated_offset_y
            sprite.rect.center = (new_center_x, new_center_y)

            # Rotate the sprite image
            rotated_image = pygame.transform.rotate(original_image, angle)
            sprite.image = rotated_image
            sprite.rect = rotated_image.get_rect(center=sprite.rect.center)
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
            
    def move_component(self, component_name, offset):
        """
        Move a target component sprite by the given offset.
        Args:
            component_name (str): The name of the component sprite to move.
            offset (tuple): The offset (x, y) by which to move the sprite.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            sprite.rect.x += offset[0]
            sprite.rect.y += offset[1]
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
            
    def reset_component(self, component_name):
        """
        Reset a target component sprite to its original image and position.
        Args:
            component_name (str): The name of the component sprite to reset.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            sprite.image = sprite.clean_image
            sprite.rect = sprite.image.get_rect(topleft=self.offSet)
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
    
    def __repr__(self):
        return f'AniRig({self.images})'        
    
# enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, cords: tuple = (0, 0)):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        pathDir = 'imgs\\enemy\\'
        fNames = ['head.png', 'body.png', 'leg_l.png', 'leg_r.png', 'arm_l.png', 'arm_r.png']
        imgPaths = [pathDir + f for f in fNames]
        self.rig = AniRig(screen, imgPaths=imgPaths, cords=cords)
        
        self.clean_image = self.rig.image.copy()
        self.rect = self.rig.image.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom

        self.rect.x, self.rect.y = self.rect.x-100, self.rect.y-100
        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = 2.5
        self.empty_sprite = hit_box(cords, (50, 25))
        
        # give the enemy a weapon using the enemy's rect surface coordinates not the screen coordinates
        self.enemy_equipment = equip_group(screen)
        # add the equipment to animation rig, simplifies blitting complex character rigs
        self.rig.add(self.enemy_equipment)
        # draw the full rig
        self.rig.draw(self.screen)
        # generate a random int that determines radius of agro circle
        self.agro_range = random.randint(150, 200)
        # make a circle to represent the agro range
        self.agro_circle = pygame.sprite.Sprite()
        self.agro_circle.image = pygame.Surface(
            (self.agro_range*2, self.agro_range*2), pygame.SRCALPHA)
        # make the circle transparent white for debug purposes
        self.agro_circle.rect = pygame.draw.circle(self.agro_circle.image,
                                                   (255, 255, 255, 100),
                                                   (self.agro_range,
                                                    self.agro_range),
                                                   self.agro_range)
        self.agro_circle.rect.center = self.rect.center

        self.show_debug = False
        self.frame_count = 0
        self.frame_seed = random.randint(30, 55)
        self.rand_mod = random.randint(50, 70)
        self.UID = hash(time.time())
        # pathing sequence for the enemy to follow using a generator to yield the next point
        self.e_pathing = EnemyPath(
            random.randint(10, 15), self.screen_rect.size)
        # store the last stable ground position as a fallback for collision detection
        self.stable_ground = (0, 0)
        # ----------------------------
        # this is all debug garbage for agro circle and pathing line, will be removed later.
        # controls how debug groups interact with flags set during runtime from dev console.
        self.line = pygame.sprite.Sprite()
        self.line.image = pygame.Surface(
            (self.agro_range*2, self.agro_range*2), pygame.SRCALPHA)
        self.line.image.fill((0, 0, 0, 0))
        self.line.rect = self.agro_circle.rect
        self.flush_match = dict(
            zip((False, True), (lambda: None, self.flush_agro)))
        self.line_match = dict(
            zip((False, True), (lambda *x: None, self.add_line)))
        self.collider_pos = (0, 0)
        self.path_line = (0, 0, 0, 0, self.screen)
        # ----------------------------
        # walking animation for the enemy, mimics json file format of keyframe type animations.
        # each function in the list is a keyframe rendered in the order given.
        # allows us to use either animation type interchangeably.
        rig_ani_test = [[self.leg_r_forward(),1], 
                        [self.leg_l_back(),1], 
                        [self.leg_r_back(),1], 
                        [self.leg_l_forward(),1]]
        
        self.walking_ani = Animation(rig_ani_test)
        self.image = self.walking_ani.get_frame()
        self.updateMe = False
        self.saveCount = 0
        self.update([(self.x+2, self.y+2)])

    @property
    def colliding(self):
        return self.empty_sprite.colliding

    @colliding.setter
    def colliding(self, value):
        self.empty_sprite.colliding = value

    def leg_r_forward(self):
        self.rig.draw_rig()
        self.rig.move_component('leg_r', (5, 0))
        self.rig.pivot_component('leg_r', self.rig.leg_r.rect.midtop, 20)
        return self.rig.image.copy()
        
    def leg_l_back(self):
        self.rig.draw_rig()
        self.rig.move_component('leg_l', (-6, 0))
        self.rig.pivot_component('leg_l', self.rig.leg_l.rect.midtop, -20)
        return self.rig.image.copy()
        
    def leg_r_back(self):
        self.rig.draw_rig()
        self.rig.reset_component('leg_r')
        return self.rig.image.copy()
        
    def leg_l_forward(self):
        self.rig.draw_rig()
        self.rig.reset_component('leg_l')
        return self.rig.image.copy()
        
    def update(self, enemy_events, debug=False):
        self.show_debug = debug
        self.flush_match[self.show_debug]()
        self.enemy_movement(enemy_events)
        
        if self.updateMe:
            self.image = self.walking_ani.get_frame()
        
        self.pos_update()
        self.hit_box_update()
        # ground is likely to be stable

    def dist_from_agro(self, p_x, p_y):
        '''return the distance from the player\n
        distance = sqrt((x2-x1)^2 + (y2-y1)^2)'''
        x, y = self.agro_circle.rect.center
        return math.sqrt((p_x - x)**2 + (p_y - y)**2)

    def enemy_movement(self, enemy_events):
        # move the enemy towards the player if the player is within 200 pixels
        has_target = False
        my_roaming_window = self.frame_count % self.rand_mod > self.frame_seed
        on_screen = self.screen_rect.collidepoint(self.agro_circle.rect.center)
        
        if not self.colliding and on_screen:
            self.stable_ground = (self.x, self.y)
            
                
            
            has_target = self.check_agro(*enemy_events)

            if my_roaming_window and not has_target:
                # walk animation
                # self.walking_ani[self.walk_f_pointer]()
                self.updateMe = True
                # move the enemy towards the next position in the pathing sequence
                head_towards = next(self.e_pathing)
                # scene_x, scene_y = self.screen_rect.size
                e_x, e_y = self.rect.center
                # scaled_pos = self.calc_line(*head_towards, 0, 0, e_x, e_y)
                # self.line_match[self.show_debug](*scaled_pos)
                dist = math.sqrt(
                    (e_x - head_towards[0])**2 + (e_y - head_towards[1])**2)
                if dist > 1:
                    s1, s2 = self.get_scaled_speed(
                        dist, e_x, e_y, *head_towards)
                    self.x += s1
                    self.y += s2
                    # draw a dot at the target position
                    self.path_line = (*head_towards, e_x, e_y, self.screen)
                self.e_pathing.frame_count += 1
            
            elif not has_target and not my_roaming_window:
                self.updateMe = False

        else:
            self.x, self.y = self.stable_ground
            self.e_pathing.frame_count += 1000000
            self.colliding = False
        self.frame_count += 1

    def check_agro(self, enemy):

        p_x, p_y = enemy
        dist = self.dist_from_agro(p_x, p_y)
        abs_dist = abs(dist)
        if abs_dist <= self.agro_range and abs_dist > 20:
            # draw a line from the enemy to the player on agro circle
            s_x, s_y = self.agro_circle.rect.x, self.agro_circle.rect.y
            e_x, e_y = self.rect.center
            scaled_pos = self.calc_line(p_x, p_y, s_x, s_y, e_x, e_y)
            self.line_match[self.show_debug](
                *scaled_pos, self.agro_circle.image)
            # we want this bound within the screen
            # scaled_pos contains our coordinates and targets relative to the agro circle
            # we just want to move the enemy towards the player relative coordinates as its the end point
            e_x, e_y, t_x, t_y = scaled_pos
            # move the enemy towards the player relative coordinates and speed
            s1, s2 = self.get_scaled_speed(dist, e_x, e_y, t_x, t_y)
            # print(s1, s2)
            self.x += s1
            self.y += s2
            # self.walking_ani[self.walk_f_pointer]()
            self.updateMe = True
            return True

    def get_scaled_speed(self, dist, e_x, e_y, t_x, t_y):
        def f_of_x(x1, x2): return (x1 - x2) / dist * self.speed
        def f_of_xy(x, y): return (f_of_x(*x), f_of_x(*y))
        s1, s2 = f_of_xy((t_x, e_x), (t_y, e_y))
        return s1, s2

    def add_line(self, e_x_mod, e_y_mod, t_x_mod, t_y_mod, surf_name=''):
        # convert our position to the agro circle's coordinate system
        target_surf = surf_name
        pygame.draw.line(target_surf, (0, 255, 0),
                         (e_x_mod, e_y_mod), (t_x_mod, t_y_mod), 2)

    def calc_line(self, t_x, t_y, surf_x, surf_y, e_x, e_y):
        """scale the position to the surface's coordinate system\n
        surf_x, surf_y are the x and y coordinates of the surface\n
        x, y are the x and y coordinates of the target\n
        returns x_mod, y_mod"""
        # x1 - x2 for x_mod, y1 - y2 for y_mod
        def func(x1, x2): return x1 - x2
        def func_xy(x, y): return (func(*x), func(*y))
        def convert_all(x, y): return func_xy((x, surf_x), (y, surf_y))
        # convert the target's position to the agro circle's coordinate system
        return convert_all(e_x, e_y) + convert_all(t_x, t_y)

    def flush_agro(self):
        self.agro_circle.image.fill((0, 0, 0, 0))
        pygame.draw.circle(self.agro_circle.image,
                           (255, 255, 255, 100),
                           (self.agro_range, self.agro_range),
                           self.agro_range)

    def pos_update(self):
        '''update the player's position based on changes to x and y.\n
        Player.x, Player.y -> Player.rect.x, Player.rect.y'''
        self.rect = self.rig.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        # update the agro circle
        self.agro_circle.rect.center = self.rect.center

    def hit_box_update(self):
        '''update rect used for collision detection\n
        updates Player.h_rect, DOES NOT UPDATE 'Enemy.rect'\n'''
        self.empty_sprite.rect = self.empty_sprite.rect
        self.empty_sprite.rect.x = self.x + self.rect.width*0.25
        self.empty_sprite.rect.y = self.y + self.rect.height*0.7

        # Update rect object from self.x and self.y.
        
if "__main__" == __name__:
    import glob
    im_list = glob.glob('**/*.png', recursive=True)
    print('\n'.join(im_list))
    pygame.init()
    pygame.quit()
