import pygame
import time
import importlib
import json
import New_ele as ui_elements
def load_ui_elements():
    global ui_rep, ui_group
    # Assuming `ui_rep` and `ui_group` are defined in `New_ele.py`
    ui_rep = ui_elements.ui_rep
    ui_group = ui_elements.ui_group
    
def export_ui_elements(ui_rep, fname='ui_elements_editor.json'):
    with open(fname, 'w') as f:
        json.dump(ui_rep, f)


pygame.init()
screen = pygame.display.set_mode((800, 600))

load_ui_elements()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            exit()
        # Save the UI elements to a file if Ctrl+S is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
            print('saving ui elements {}'.format(ui_rep))
            export_ui_elements(ui_rep, 'text_confirm.json')
        # Reload the UI elements if Ctrl+R is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
            importlib.reload(ui_elements)
            print('reloading ui elements')
            load_ui_elements()
            screen.fill((0, 0, 0))
    
    ui_group.update((0, 0), 'New test')
    ui_group.draw(screen)
    pygame.display.flip()
    time.sleep(0.01)