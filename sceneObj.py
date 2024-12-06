# Author: Cameron Kerley
# Date: 06/22/2024
# Description: 
# subclass of the AniRig class that represents a collection of scene sprites making up the game background. 
# This class is responsible for:
#   * loading and managing the scene sprites.
#   * maintain rects used for collision detection.
#   * rescaling all components to the screen resolution. 
#   * drawing components in the correct order and location on screen.

import numpy as np
import pygame
from pygame.locals import *
from GameObjects import AniRig

class Background(AniRig):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # get the screen size, used to calculate the size of all other components
        self.screen_size = self.screen_rect.size
        # create an error sprite that is a neon pink square
        self.entityDict = {}
        self.initialize_error_sprite()
        # calculate the tile size given the screen size (initial size is 100x100).
        self.tile_size = self.screen_size[0] // 10, self.screen_size[1] // 10
        self.create_grid(*self.tile_size)
        self.scene_elements = pygame.sprite.Group()
        
    def initialize_error_sprite(self):
        self.errorSprite = pygame.Surface((100, 100))
        self.errorSprite.fill((255, 0, 255))
        # fill with 'error' text
        font = pygame.font.Font(None, 25)
        text = font.render('Error', True, (0, 0, 0))
        self.errorSprite.blit(text, (50, 50))
        
    def create_grid(self, tile_width, tile_height):
        screen_width, screen_height = self.screen_size
        num_columns = screen_width // tile_width
        num_rows = screen_height // tile_height
        self.grid = np.empty((num_rows, num_columns), dtype=object)
        # add all dark tiles to the grid
        self.grid.fill(self.dark_tile)
        flat_grid = self.grid.flatten()
        np.vectorize(self.add_tile)(flat_grid, range(len(flat_grid)))
        
    
    def add_tile(self, tile, index, tType='dark'):
        # scale the tile to the correct size
        image = pygame.transform.scale(tile.image, self.tile_size)
        # get new rect after scaling
        rect = image.get_rect()
        # convert the 1D index to row and column
        row, column = np.unravel_index(index, self.grid.shape)
        # convert the row and column to pixel coordinates
        rect.x = column * self.tile_size[0]
        rect.y = row * self.tile_size[1]
        # create a mask for the tile
        mask = pygame.mask.from_surface(image)
        # make the mask a property of the tile
        tile.mask = mask
        self.grid[row, column] = image.copy(), rect.copy(), tType
        # if the tType is not a key in the entityDict add it
        self.register_entity(tType, rect)

    def register_entity(self, tType, rect):
        if tType not in self.entityDict:
            self.entityDict[tType] = []
        # add the rect to the entityDict
        self.entityDict[tType].append(rect)
            
        
    def get_tile(self, row, column):
        return self.grid[row, column]
    
    def draw_element_at(self, element, row, column):
        img, rect = self.get_tile(row, column)[:2]
        x, y = rect.topleft
        y-=element.rect.height/2.2
        self.scene_elements.add(element)
        # set the element's rect to the correct location
        element.rect.topleft = (x, y)
        
        
    def draw_tile(self, tile):
        # draw the tile at the correct location
        img, rect = tile[:2]
        x, y = rect.x, rect.y
        self.image.blit(img, (x, y))
        
    def draw_scene(self):
        # flatten the grid and draw each tile
        flat_grid = self.grid.flatten()
        np.vectorize(self.draw_tile)(flat_grid)
        # draw all scene elements
        self.scene_elements.draw(self.image)
        return self.image
                
if __name__ == "__main__":
    import time
    from GameObjects import EnemyGroup, Player
    pygame.init()
    # set fullscreen to the 2nd monitor
    screen = pygame.display.set_mode((0,0),display=1)
    size = screen.get_rect().size
    screen.fill((0, 0, 0))
    pathDir = 'imgs\\scene\\'
    fNames = ['dark_tile.png', 'light_tile.png','house_t.png']
    imgPaths = [pathDir + f for f in fNames]
    background = Background(screen,imgPaths=imgPaths, surfSize=size, offSet=[[0, 0], [0, 0], [0, 0]])
    tileRange = [0, 1, 10, 11, 21,31,32,33,43] 
    np.vectorize(background.add_tile)(background.light_tile, tileRange, tType='light')
    background.draw_element_at(background.house_t, 0, 0)
    background.draw_scene()
    enemy = EnemyGroup(screen, 
                       cords=background.get_tile(0, 0)[1].center, 
                       size=3)

    player = Player(screen)
    # get rect for only the light tiles
    light_tile = background.entityDict['light']
    # make a group to check for tile collisions
    light_group = pygame.sprite.Group()
    for rect in light_tile:
        light_group.add(pygame.sprite.Sprite())
        light_group.sprites()[-1].rect = rect
    gamestate = pygame.sprite.Group()
    gamestate.add([player, enemy, enemy.ehb, enemy.e_agro])
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
        
        # check for collisions with the light tiles
        check = pygame.sprite.groupcollide(enemy.ehb, light_group, False, False)
        # if there is a collision, we ar in a valid tile and can move isColliding(False)
        # update group collision status
        enemy.ehb.valid_tile_update(check)
        gamestate.update(enemy_events=[player.rect.center], debug=True)
        
        # draw the background
        screen.blit(background.image, (0, 0))
        
        # draw the gamestate except the agro sprite
        gamestate.remove(enemy.e_agro)
        gamestate.draw(screen)
        gamestate.add(enemy.e_agro)
        
        # screen.blit(player.image, player.rect)
        # enemy.draw(screen)
        # # draw the collision sprites
        # enemy.ehb.draw(screen)
        pygame.display.update()
        clock.tick(60)
    pygame.display.flip()
    pygame.quit()