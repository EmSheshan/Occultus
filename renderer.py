import sys
import pyautogui
import pygame
from pygame.locals import *


class Renderer:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font('assets/Mono a Mano.ttf', 36)
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = pyautogui.size()
        self.primary_text_rect = pygame.Rect(20, self.SCREEN_HEIGHT - 20, self.SCREEN_WIDTH - 40, 0)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def render_background(self):
        self.screen.fill((20, 20, 40))

    def render_primary_text(self, text, confirm=True):
        self.render_background()
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(bottomleft=(20, self.SCREEN_HEIGHT - 20))
        self.screen.blit(text_surface, text_rect)
        waiting = confirm
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE or event.key == K_RETURN:
                        waiting = False

    def render_health_bars(self, characters, enemies, press_turn_count):
        for i, character in enumerate(characters):
            text_surface = self.font.render(f"{character.name} HP: [{character.hp}/{character.max_hp}]", True,
                                            (255, 255, 255))
            self.screen.blit(text_surface, (20, 20 + i * 40))

        for i, enemy in enumerate(enemies):
            text_surface = self.font.render(f"{enemy.name} HP: [{enemy.hp}/{enemy.max_hp}]", True, (255, 255, 255))
            self.screen.blit(text_surface, (self.SCREEN_WIDTH - 320, 20 + i * 40))

        text_surface = self.font.render(f"Press turns = {press_turn_count}", True, (255, 255, 255))
        self.screen.blit(text_surface, (-320 + self.SCREEN_WIDTH // 2, 20))

        pygame.display.flip()
