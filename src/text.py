from variables import variables, BLACK, WHITE
from utils import convert_pos

if variables.display_game:
    import pygame
    pygame.init()  # Initiates pygame
    font = pygame.font.Font(None, 36)


def change_text_victory(str):    
    # Text on the screen that says what is the turn 
    text = font.render(str, True, BLACK)
    textRect = text.get_rect()
    textRect.center = (convert_pos((1.3, 8.3)))
    
    # Delete the past text
    if variables.text_victory is not None:
        pygame.draw.rect(variables.screen, WHITE, variables.text_victory[1])
    
    variables.set_text_victory(text, textRect)
    show_text_victory()


def show_text_victory():
    if not variables.display_game:
        return
    variables.screen.blit(variables.text_victory[0], variables.text_victory[1])