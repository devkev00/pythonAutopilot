# pygame 기본
import pygame
import numpy as np

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 게임 진행
running = True

while running:
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
pygame.quit()