from variables import variables, BLACK, WHITE
from utils import convert_pos

if variables.display_game:
    import pygame

    pygame.init()
    font = pygame.font.Font(None, 36)
    confidence_font = pygame.font.Font(None, 24)


def change_text_victory(str):
    text = font.render(str, True, BLACK)
    textRect = text.get_rect()
    textRect.center = convert_pos((1.3, 8.3))

    if variables.text_victory is not None:
        pygame.draw.rect(variables.screen, WHITE, variables.text_victory[1])

    variables.set_text_victory(text, textRect)
    show_text_victory()


def show_text_victory():
    if not variables.display_game:
        return
    variables.screen.blit(variables.text_victory[0], variables.text_victory[1])


def draw_confidence_text():
    if not variables.display_game:
        return
    if variables.confidence_text_rect is not None:
        pygame.draw.rect(variables.screen, WHITE, variables.confidence_text_rect)
        variables.confidence_text_rect = None
    if variables.confidence_message is None:
        return
    text = confidence_font.render(variables.confidence_message, True, BLACK)
    rect = text.get_rect()
    rect.center = convert_pos((3.75, 8.7))
    variables.screen.blit(text, rect)
    variables.confidence_text_rect = rect
