import pygame
from gameGUI import base_Element, text_element, input_element

# Initialize Pygame
pygame.init()

ui_group = pygame.sprite.Group()
menuBg = base_Element.Panel((120, 120, 120), *(225, 125))
x, y = menuBg.rect.center
w, h = 125, 50
# input_line = input_element.InputElement('New test', (0,0,255), None, 20, w,h, *(x-w//2, y//2))
# yes = text_element.TextElement('Yes', (0, 255, 0), None, 18, w//2, h//2, *input_line.rect.bottomleft)
# no = text_element.TextElement('No', (255, 0, 0), None, 18, w//2, h//2, *yes.rect.topright)
# ui_group.add(menuBg)
# ui_group.add(input_line)
# ui_group.add([yes, no])
txt_confirm = text_element.TextElement('confirm to exit', (0,0,255), None, 20, w,h, *(x-w//2, y//3))
x1,y1 = txt_confirm.rect.bottomleft
confirm = text_element.InteractiveTextElement('confirm', (120, 100, 100), None, 18, w//1.5, h//2, *(x-w/3, y1))
# make a dark gray background for the buttons to sit on
x2, y2 = menuBg.rect.midtop
trim = base_Element.Trim((50, 50, 50), *(225*0.75, 125*0.75), *(x2-225*0.375, y2+125*0.1))
ui_group.add(menuBg)
ui_group.add(trim)
ui_group.add(txt_confirm)
ui_group.add(confirm)

ui_rep = list(map(repr, ui_group))

            
