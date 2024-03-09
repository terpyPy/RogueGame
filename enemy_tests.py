import unittest
import os

import pygame

from GameObjects import Enemy

# enemy unit tests for the Enemy class

class TestEnemy(unittest.TestCase):
    def test_enemy(self):
        screen = pygame.display.set_mode((400, 400))
        cords = list(zip(range(100, 400, 100), range(100, 400, 100)))
        enemies = [Enemy(screen, cords[0])]
        self.assertEqual(len(enemies), 1, "Result does not match expected value")
        del enemies

    def test_enemy_group(self):
        screen = pygame.display.set_mode((400, 400))
        cords = list(zip(range(0, 400, 100), range(0, 400, 100)))
        enemies = [Enemy(screen, cords[i]) for i in range(len(cords))]
        enemy_group = pygame.sprite.Group()
        enemy_group.add(enemies)
        self.assertEqual(len(enemy_group.sprites()), 4, "Result does not match expected value")
        del enemies
        del enemy_group
        
if __name__ == '__main__':
# usage example:
    # python -m unittest enemy_tests.TestEnemy
    unittest.main()