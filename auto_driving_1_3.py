# 도형 회전하기
# FPS 설정

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

# 사각형 정의
ad_rect = pygame.Surface((100, 300), pygame.SRCALPHA)
pygame.draw.rect(ad_rect, green, (0, 0, 100, 300))
rotated_rect = pygame.transform.rotate(ad_rect, 50)
new_rect = rotated_rect.get_rect(center=(500, 500))

# 게임 진행
running = True

# FPS 설정
FPS = 30
clock = pygame.time.Clock()

i = 0
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
    screen.fill(black)
    rotated_rect = pygame.transform.rotate(ad_rect, i)
    new_rect = rotated_rect.get_rect(center=(500, 500))
    screen.blit(rotated_rect, new_rect)
    pygame.display.flip()
    i = (i+1) % 360
pygame.quit()