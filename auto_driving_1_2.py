# 색칠하기
# 도형 그리기

import pygame
import numpy as np

# pygame 초기화
pygame.init()

# 색상 정의
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
gray = (180, 180, 180)
green = (0, 255, 0)
black = (0,0,0)

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
    screen.fill(black)

    pygame.draw.circle(screen, red, (int(100), int(100)), 10)
    pygame.draw.circle(screen, red, (int(200), int(200)), 30,2)

    pygame.draw.rect(screen, red, (300,200,100,100))
    pygame.draw.rect(screen, white, (300, 300, 100, 100),1)

    pygame.draw.line(screen, blue, (500,500), (700,700), 2)

    pygame.display.flip()
pygame.quit()