import numpy as np
import pygame

pygame.init()

white = (255, 255, 255)
red= (255, 0, 0)
blue = (0, 0, 255)
gray = (180, 180, 180)
green = (0, 255, 0)
black = (0, 0, 0)

screen_width = 800 # pixel 단위
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

ad_rect = pygame.Surface((100, 300), pygame.SRCALPHA)
pygame.draw.rect(ad_rect, green, (0, 0, 100, 300))
rotated_rect = pygame.transform.rotate(ad_rect, 50)
new_rect = rotated_rect.get_rect(center=(500, 500))

pygame.display.set_caption('Auto_Driving')
car_image = pygame.image.load('car.png')
car_image = pygame.transform.scale(car_image, (50, 30))
car_x = 400
car_y = 400
car_angle = 0 # 차 머리 초기 각도
car_rect = car_image.get_rect(center=(car_x, car_y)) # 차 위치 설정
car_speed = 300 # 초당 이동 가능한 픽셀 수
FPS = 60
clock = pygame.time.Clock()

running = True
i = 0

while running:
    dt = clock.tick(FPS) / 1000
    clock.tick(FPS)
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - car_x
    dy = mouse_y - car_y

    dist = np.sqrt(dx ** 2 + dy ** 2)
    car_angle = np.atan2(dy, dx) # arctan dy / dx

    if dist > 0:
        v_x = dx / dist # 단위 벡터
        v_y = dy / dist
        move_distance = car_speed * dt
        if move_distance > dist:
            car_x = mouse_x
            car_y = mouse_y
        else:
            car_x = car_x + v_x * move_distance
            car_y = car_y + v_y * move_distance
    screen.fill(black)

    rotated_car_image = pygame.transform.rotate(car_image, -np.degrees(car_angle))
    # 회전은 반시계가 + 방향이지만 좌표계는 시계방향이 + 방향임
    new_car_rect = rotated_car_image.get_rect(center=(car_x, car_y))
    screen.blit(rotated_car_image, new_car_rect)

    pygame.display.flip()

    i = (i + 1) % 360

pygame.quit()


