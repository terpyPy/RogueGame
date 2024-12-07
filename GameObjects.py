# Author: Cameron Kerley
# Date: 03/1/2024
# Description: this file contains the GameObjects used in the game such as the player and enemies and their animations
# this is my original code, but the chat feature of copilot was used to help provide examples on how to achieve certain tasks
import pathlib
import glob
import numpy as np
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
            self.image = image.copy()
            
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

class txtSprite(pygame.sprite.Sprite):
    def __init__(self, cords: tuple, text: str, font: pygame.font.Font, color: tuple = (0, 0, 0)) -> None:
        """create a text sprite\n

        Args:
            cords (tuple): x, y coordinates
            text (str): text to display
            font (pygame.font.Font): font object
            color (tuple, optional): font color. Defaults to (0, 0, 0).
        """
        super().__init__()
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect()
        self.rect.topleft = cords
        self.font = font
        self.color = color

    def update(self, text='',*args, **kwargs):  
        """update the text displayed by the sprite\n"""
        self.image = self.font.render(text, False, self.color)

class hit_box(pygame.sprite.Sprite):
    def __init__(self, cords: tuple, size: tuple, parentRect: pygame.Rect = None):
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
        self.parentRect = parentRect
        # mask for pixel perfect collision detection
        self.mask = pygame.mask.from_surface(self.image)
        
    def isColliding(self, value):
        self.colliding = value    

    def update(self, *args, **kwargs):
        self.rect.center = self.parentRect.center
        adjustY = self.parentRect.midbottom[1] - self.rect.height
        self.rect.y = adjustY
        
class hb_group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
    
    def valid_tile_update(self, sub_group):
        # for e in self.sprites():
        #     if e in sub_group:
        #         e.colliding = False
        #     else:
        #         e.colliding = True
            # Extract the colliding status into a NumPy array
        colliding_status = np.array([e in sub_group for e in self.sprites()])

        # Perform the vectorized operation to update the colliding status
        colliding_status = ~colliding_status

        # Update the original sprite objects with the new colliding status
        for e, status in zip(self.sprites(), colliding_status):
            e.colliding = status
            
    def __repr__(self):
        return f'hit_box_group({self.sprites()})'
    
class agro_group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        
    def __repr__(self):
        return f'agro_group({self.sprites()})'
    
    def __str__(self):
        return f'{self.sprites()}'
        
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
        ani_folder = pathlib.WindowsPath('ani_configs')
        # setup the walking animations from the json files
        f = open(ani_folder / 'front_walk.json')
        self.front_w_a = json.load(f)
        f.close()
        f = open(ani_folder / 'side_walk.json')
        self.side_w_a = json.load(f)
        f.close()
        f = open(ani_folder / 'back_walk.json')
        self.back_w_a = json.load(f)
        f.close()
        f = open(ani_folder / 'idle_walk.json')
        self.idle_w_a = json.load(f)
        f.close()
        
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
        self.collisionSprite = hit_box((self.x, self.y), (50, 25), self.rect)

        self.stable_ground = (0, 0)
        self.show_debug = False
        self.dot = self.get_dot()
        self.no_clip = False

    @property
    def colliding(self):
        return self.collisionSprite.colliding

    @colliding.setter
    def colliding(self, value):
        self.collisionSprite.colliding = value

    def get_dot(self):
        dot = pygame.sprite.Sprite()
        dot.image = pygame.Surface((4, 4))
        dot.image.fill((0, 255, 0))
        dot.rect = pygame.Rect(self.rect.center, (4, 4))
        return dot

    def update(self, debug=False, *args, **kwargs):
        """Update the player's position based on wasd keypress."""
        self.show_debug = debug
        #
        # check for player collision with the test_collision_group
        self.player_collision()
        self.wasd_movement()
        self.pos_update()
        self.hit_box_update()
        
    def wasd_movement(self, debug=False):
        """Update the player's position based on wasd keypress."""
        #
        # check directions, 'not any' is the same as 'all are False'
        if not any(self.wasd_keys.values()):
            self.idle()
        else:
            # check for key presses modifying up&down
            self.y_axis_movement()
            # same for left&right
            self.x_axis_movement()
            # update the player's rect: pushes x,y -> rect.x, rect.y
            

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

    def player_collision(self):
        if not self.no_clip:
            # check for collision with the test_collision_group
            if not self.colliding:
                #
                # go back to the last stable ground
                self.stable_ground = self.x, self.y
            else:    
                print(f'stable ground chosen at {self.stable_ground}')
                self.x, self.y = self.stable_ground
                self.colliding = False

    def hit_box_update(self):
        '''update rect used for collision detection\n
        updates Player.h_rect, DOES NOT UPDATE 'Player.rect'\n'''
        
        self.collisionSprite.parentRect = self.rect
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
             
class AniRig(pygame.sprite.Group):
    def __init__(self, screen, offSet=[[1,1]], imgPaths: list = [], surfSize: tuple = (100, 100), cords: tuple = (0, 0)):
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
        offSetcopy = self.offSet.copy()
        for img in imgPaths:
            try:
                image = pygame.image.load(img)
                img_name = img.name.split('.')[0]
                images[img_name] = image, offSetcopy.pop(0)
            except pygame.error as e:
                print(f"Failed to load image {img}: {e}")
        return images

    def create_sprites(self):
        """
        Create sprites from the loaded images and add them to the group.
        """
        
        for attr, img_w_offset in self.images.items():
            img, offset = img_w_offset
            sprite = pygame.sprite.Sprite()
            sprite.image = img.copy()
            sprite.rect = img.get_rect(topleft=offset)
            sprite.clean_image = img.copy()
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
            original_image = self.images[component_name][0]
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
            original_image = self.images[component_name][0]
            
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
        32,
        32,39
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
            
    def flip_component_vertically(self, component_name):
        """
        Flip a target component sprite vertically.
        Args:
            component_name (str): The name of the component sprite to flip.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            sprite.image = pygame.transform.flip(sprite.image, False, True)
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
            
    def flip_component_horizontally(self, component_name):
        """
        Flip a target component sprite horizontally.
        Args:
            component_name (str): The name of the component sprite to flip.
        """
        if hasattr(self, component_name):
            sprite = getattr(self, component_name)
            sprite.image = pygame.transform.flip(sprite.image, True, False)
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
            sprite.rect = sprite.image.get_rect(topleft=self.images[component_name][1])
        else:
            print(f"Component '{component_name}' does not exist in the rig.")
    
    def __repr__(self):
        return f'AniRig({self.images})'        

class NpcVision(pygame.sprite.Sprite):
    def __init__(self, parentRect: tuple, radius: int, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        self.transparentColor = (255, 255, 255, 15)
        self.size = (radius, radius)
        self.rect = pygame.draw.circle(self.image, self.transparentColor, self.size, radius)
        self.radius = radius
        self.parentRect = parentRect
        self.rect.center = parentRect.center
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image,
                           self.transparentColor,
                           self.size,
                           self.radius)
    
    def refresh(self):
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, self.transparentColor, self.size, self.radius)
        
    def update(self, *args, **kwargs):
        self.rect.center = self.parentRect.center
        
# enemy base class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen, animation, img, cords: tuple = (0, 0)):
        super().__init__()
        self.flipped = 'right'
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.rect = img.get_rect()
        if cords != (0, 0):
            self.rect.x, self.rect.y = cords
        else:
            self.rect.midbottom = self.screen_rect.midbottom

        self.rect.x, self.rect.y = self.rect.x-100, self.rect.y-100
        self.x = self.rect.x
        self.y = self.rect.y
        self.speed = 2.3
        self.collisionSprite = hit_box(cords, (50, 25), self.rect)
        
        # draw the full rig
        self.clean_image = img.copy()
        self.tempImage = img.copy()
        
        # generate a random int that determines radius of agro circle
        self.agro_range = random.randint(150, 200)
        # make a circle to represent the agro range
        self.agro_circle = NpcVision(self.rect, self.agro_range, self.screen)

        self.show_debug = False
        self.frame_count = 0
        self.frame_seed = random.choice(range(0, 60, 10))
        self.rand_mod = random.choice(range(60, 120, 10))
            
        self.UID = hash(time.time())
        # pathing sequence for the enemy to follow using a generator to yield the next point
        self.e_pathing = EnemyPath(
            random.randint(20, 40),
            self.screen_rect.size)
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
        
        self.collider_pos = (0, 0)
        self.path_line = (0, 0, 0, 0, self.screen)
        # ----------------------------
        # walking animation for the enemy, mimics json file format of keyframe type animations.
        # each function in the list is a keyframe rendered in the order given.
        # allows us to use either animation type interchangeably.
        rig_ani_test = animation
        
        self.walking_ani = Animation(rig_ani_test)
        self.walking_ani.set_frame(0)
        # self.walking_ani.get_frame()
        self.idle_sprite = self.clean_image.copy()
        self.idle_sprite_l = pygame.transform.flip(self.clean_image.copy(), True, False)
        self.updateMe = False
        self.saveCount = 0
        self.update([(self.x+2, self.y+2)])
        
    @property
    def colliding(self):
        return self.collisionSprite.colliding

    @colliding.setter
    def colliding(self, value):
        self.collisionSprite.colliding = value
        
    @property
    def image(self):
        return self.tempImage
    
    def update(self, enemy_events=[], debug=False, *args, **kwargs):
        self.show_debug = debug
        
        
        self.enemyMovement(enemy_events)
        
        self.handleAnimationState()
        
        self.posUpdate()

    def handleAnimationState(self):
        match self.updateMe:
            case True:
                image = self.walking_ani.get_frame()
            case False:
                # get the current frame of the animation
                image = self.idle_sprite
        
        match self.flipped:
            case 'left':
                self.tempImage = pygame.transform.flip(image, True, False)
            case 'right':
                self.tempImage = image.copy()
            case 'idle':
                self.tempImage = self.idle_sprite
        
        
        # reset the update flag for the next frame
        self.updateMe = False

    def dist_from_me(self, p_x, p_y):
        '''return the distance from the player\n
        distance = sqrt((x2-x1)^2 + (y2-y1)^2)'''
        x, y = self.agro_circle.rect.center
        return math.sqrt((p_x - x)**2 + (p_y - y)**2)

    def enemyMovement(self, enemy_events):
        # move the enemy towards the player if the player is within range
        has_target = 0
        on_screen = True if self.screen_rect.contains(self.rect) else False
        
        if not self.colliding and on_screen:
            self.stable_ground = (self.x, self.y)
            my_roaming_window = self.e_pathing.frame_count % self.rand_mod > self.frame_seed
            has_target = self.checkAggroStatus(*enemy_events)
            
            # flag the enemy to update sprite
            if my_roaming_window and has_target == 0:
                # move the enemy towards the next position in the pathing sequence
                head_towards = next(self.e_pathing)
                e_x, e_y = self.rect.center
                dist = self.dist_from_me(*head_towards)
                
                if abs(dist) >= 2:
                    s1, s2 = self.getScaledSpeed(
                        dist, e_x, e_y, *head_towards)
                    self.adjustRefPos(s1, s2)
                    self.toggleFlippedFlag(s1,s2)
                    # draw a dot at the target position
                    self.path_line = (*head_towards, e_x, e_y, self.screen)
                
                    
        else:
            self.x, self.y = self.stable_ground
            self.e_pathing.frame_count += 1000000
            # self.colliding = False
        self.e_pathing.frame_count += 1

    def adjustRefPos(self, s1, s2):
        self.x += s1
        self.y += s2
        self.updateMe = True

    def toggleFlippedFlag(self, s1, s2):
        if s1 > 0:
            self.flipped = 'right'
        elif s1 < 0:
            self.flipped = 'left'
        else:
            self.flipped = 'idle'
  
    def checkAggroStatus(self, enemy):

        p_x, p_y = enemy
        dist = self.dist_from_me(p_x, p_y)
        abs_dist = abs(dist)
        min_dist = 50
        inRange = abs_dist <= self.agro_range
        notReachedTarget = not abs_dist <= min_dist
        
        match inRange, notReachedTarget:
            case True, True:
                self.trackTarget(p_x, p_y, dist)
                return 1
            case True, False:
                return 2
            case False, _:
                return 0

    def trackTarget(self, p_x, p_y, dist):
        s_x, s_y = self.agro_circle.rect.x, self.agro_circle.rect.y
        e_x, e_y = self.rect.center
        scaled_pos = self.calculateDistanceVector(p_x, p_y, s_x, s_y, e_x, e_y)
            # set info to draw line from the enemy to the player on agro circle
        self.path_line = (p_x, p_y, e_x, e_y, self.screen)
            # we want this bound within the screen
            # scaled_pos contains our coordinates and targets relative to the agro circle
            # we just want to move the enemy towards the player relative coordinates as its the end point
        e_x, e_y, t_x, t_y = scaled_pos
            # move the enemy towards the player relative coordinates and speed
        s1, s2 = self.getScaledSpeed(dist, e_x, e_y, t_x, t_y)
            # push the reference position to our new speed adjusted position
        self.adjustRefPos(s1, s2) # also sets the update flag because we are moving
        self.toggleFlippedFlag(s1,s2)
        
    def getScaledSpeed(self, dist, e_x, e_y, t_x, t_y):
        def f_of_x(x1, x2): return (x1 - x2) / dist * self.speed
        def f_of_xy(x, y): return (f_of_x(*x), f_of_x(*y))
        s1, s2 = f_of_xy((t_x, e_x), (t_y, e_y))
        return s1, s2

    def drawPathing(self, e_x_mod, e_y_mod, t_x_mod, t_y_mod, surf_name=''):
        # draw a line from the enemy to our target position
        target_surf = surf_name
        pygame.draw.line(target_surf, (0, 255, 0),
                            (e_x_mod, e_y_mod), (t_x_mod, t_y_mod), 2)

    def calculateDistanceVector(self, t_x, t_y, surf_x, surf_y, e_x, e_y):
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

    def clearAgro(self):
        self.agro_circle.refresh()

    def posUpdate(self):
        '''update the player's position based on changes to x and y.\n
        Player.x, Player.y -> Player.rect.x, Player.rect.y'''
        self.rect = self.tempImage.get_rect()
        # Update rect object from self.x and self.y.
        self.rect.x = self.x
        self.rect.y = self.y
        # update the agro circle
        self.agro_circle.parentRect = self.rect
        # update the collision sprite
        self.collisionSprite.parentRect = self.rect
        
        
class EnemyGroup(pygame.sprite.Group):
    def __init__(self, screen, cords: tuple = (0, 0), size: int = 10):
        super().__init__()
        self.screen = screen
        self.screen_rect = screen.get_rect()
        pathDir = pathlib.WindowsPath('imgs\enemy')
        
        fNames = ['head.png', 'body.png', 'leg_l.png', 'leg_r.png', 'arm_l.png', 'arm_r.png',
                  'e_shield.png',
                  'scaled_dagger.png',
                  'e_helm.png']
        imgPaths = [pathDir / f for f in fNames]
        self.rig = AniRig(screen, imgPaths=imgPaths, cords=cords, 
                          offSet=[[1,1],
                                  [1,1],
                                  [47,84],
                                  [37,84],
                                  [1,1],
                                  [1,1],
                                  [1,1],
                                  [1,1],
                                  [1,1]])
        self.im = self.rig.draw_rig().copy()
        self.rig_ani_test = [
                        [self.legLeftMovement(-10), 2],
                        [self.legLeftMovement(-10), 2],
                        [self.moveArmsWithEquip(-10), 2],
                        [self.moveArmsWithEquip(-10), 1],
                        [self.legRightMovement(10), 2],
                        [self.legRightMovement(10), 2],
                        [self.moveArmsWithEquip(-10), 1],
                        [self.legLeftMovement(-10), 2],
                        [self.legLeftMovement(-10), 2],
                        [self.legLeftReset(), 2],
                        [self.legRightMovement(10), 2], 
                        [self.resetArmsWithEquip(), 1],
                        [self.moveArmsWithEquip(10), 1],
                        [self.legRightMovement(10), 2],
                        [self.legRightReset(), 2],
                        [self.moveArmsWithEquip(10), 1],
                        [self.moveArmsWithEquip(10), 2],
                        ]
        self.enemies = [Enemy(screen, self.rig_ani_test.copy(), self.im, cords) for _ in range(size)]
        self.add(self.enemies)
        self.show_debug = False
        # get all the hit boxes for the enemies
        self.ehb = hb_group()
        self.ehb.add([enemy.collisionSprite for enemy in self.enemies])
        self.e_agro = agro_group()
        self.e_agro.add([enemy.agro_circle for enemy in self.enemies])
        
        
    def spawnEnemy(self, cords: tuple = (0, 0)):
        self.enemies.append(Enemy(self.screen, self.rig_ani_test, self.im, cords))
        self.add(self.enemies[-1])
        self.ehb.add(self.enemies[-1].collisionSprite)
        self.e_agro.add(self.enemies[-1].agro_circle)
        return self.enemies[-1]

    def toggleDebug(self):
        self.show_debug = not self.show_debug
        return self.show_debug
    
    def moveArmsWithEquip(self, mod=-20):
        x, y = self.rig.arm_r.rect.center
        dx, dy = self.rig.scaled_dagger.rect.center
        self.rig.pivot_component('arm_r', (x,y), mod)
        self.rig.pivot_component('scaled_dagger', (dx,dy), mod)
        alx,aly = self.rig.arm_l.rect.center
        sx, sy = self.rig.e_shield.rect.center
        self.rig.pivot_component('arm_l', (alx,aly), mod)
        self.rig.pivot_component('e_shield', (sx,sy), mod)
        self.rig.draw_rig()
        return self.rig.image.copy()
    
    def resetArmsWithEquip(self):
        self.rig.reset_component('scaled_dagger')
        self.rig.reset_component('arm_r')
        self.rig.reset_component('arm_l')
        self.rig.reset_component('e_shield')
        self.rig.draw_rig()
        return self.rig.image.copy()
    
    def legRightMovement(self, mod):
        x, y = self.rig.leg_r.rect.topright
        self.rig.move_component('leg_r', (2.5, 0))
        self.rig.pivot_component('leg_r', (x,y), mod)
        self.rig.rotate_component('leg_r', mod*2)
        # redraw the body
        self.rig.draw_rig()
        return self.rig.image.copy()
        
    def legLeftMovement(self,mod):
        x, y = self.rig.leg_l.rect.topleft
        self.rig.move_component('leg_l', (-2.6,0))
        self.rig.pivot_component('leg_l', (x,y), mod)
        self.rig.rotate_component('leg_l', mod*2)
        # redraw the body
        self.rig.draw_rig()
        return self.rig.image.copy()
        
    def legRightReset(self):
        self.rig.reset_component('leg_r')
        self.rig.draw_rig()
        return self.rig.image.copy()
        
    def legLeftReset(self):
        self.rig.reset_component('leg_l')
        self.rig.draw_rig()
        return self.rig.image.copy()
    
    def __repr__(self):
        return f'EnemyGroup({self.enemies})'

    def __str__(self):
        return f'Enemies({len(self.enemies)})'
        
if "__main__" == __name__:
    import glob
    im_list = glob.glob('**/*.png', recursive=True)
    print('\n'.join(im_list))
    # put an enemy on a blank screen
    screen = pygame.display.set_mode((1920,1080))
    enemy = EnemyGroup(screen, cords=(100, 100), size=1)
    agro_group = pygame.sprite.Group()
    agro_group.add(enemy.enemies[0].agro_circle)
    player = Player(screen)
    clock = pygame.time.Clock()
    # basic game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                player.k_up_e(event.key, True)
            if event.type == pygame.KEYUP:
                player.k_up_e(event.key, False)
        screen.fill((0, 0, 0))
        player.update()
        enemy.update([player.rect.center], True)
        agro_group.update()
        screen.blit(player.image, player.rect)
        enemy.draw(screen)
        pygame.display.update()
        clock.tick(60)
    pygame.init()
    pygame.quit()
