# Lidar로 위치 인식

import pygame
import numpy as np
import ad_util

# pygame 초기화
pygame.init()

# 스크린 정의
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width * 2, screen_height + 200))

# 타이틀
pygame.display.set_caption("AUTO DRIVING")

# 자동차
car_image = pygame.image.load("car.png")
car_image = pygame.transform.scale(car_image, (50, 30))
car = ad_util.AD_Car(100,100,np.radians(90))
icp_car = ad_util.AD_Car(100,100,np.radians(90))
look_ahead_distance = 30

#Lidar
lidar_range = 500
angular_resolution = 1

target_speed = 0
target_steer = 0

# 목표점 설정
target_x = car.x
target_y = car.y

# 장애물
walls = [
    (5, 5, screen_width-5, 5, 5),
    (5, screen_height-5, screen_width-5, screen_height-5, 5),
    (5, 5, 5, screen_height-5, 5),
    (screen_width-5, 5, screen_width-5, screen_height-5, 5),
    (200, 5, 200, 300, 5),
    (5, 500, 500, 500, 5),
    (500, 200, 500, screen_height-5, 5)
]

# Grid map 만들기
GRID_INTERVAL = 8
GRID_W, GRID_H = screen_width // GRID_INTERVAL, screen_height // GRID_INTERVAL

global_map_set = set()


# path 설정
path =[]
path_index = 0

# 초기 T 구하기
c, s = np.cos(car.angle), np.sin(car.angle)
T = np.array([[c, -s, car.x], [s, c, car.y], [0, 0, 1]])

lidar_pos = (car.x, car.y, car.angle)
lidar_pnts = ad_util.lidar_scan(lidar_pos, walls, lidar_range, angular_resolution)
local_lidar_pnts = ad_util.lidar_scan_origin_lidar(lidar_pos, lidar_pnts)

down_pnts = ad_util.grid_downsample(local_lidar_pnts, cell_size=GRID_INTERVAL)
homo = np.hstack((down_pnts, np.ones((down_pnts.shape[0], 1))))

global_pts = (T @ homo.T).T[:, :2]

global_pts = ad_util.grid_downsample(global_pts, cell_size=GRID_INTERVAL)
global_map_set = ad_util.update_global_map(global_pts, global_map_set)

grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
for gx, gy in global_map_set:
    grid_y = int(gy // GRID_INTERVAL)
    grid_x = int(gx // GRID_INTERVAL)
    if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
        grid[grid_y, grid_x] = 1
ad_util.apply_margin_to_grid(grid,5)

# FPS 설정
FPS = 10
clock = pygame.time.Clock()


# icp로 맵 업데이트 하는 주기
map_update_count = 1
map_update = 50

# 게임 진행
running = True

while running:
    dt = clock.tick(FPS) / 1000.
    for event in pygame.event.get():
        # 종료
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x >= screen_width:  # 마우스가 오른쪽 맵에 있으면 무시
                    continue
                car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
                mouse_grid = (int(mouse_x // GRID_INTERVAL), int(mouse_y // GRID_INTERVAL))
                path = ad_util.ad_dijkstra(grid, car_grid, mouse_grid)
                real_path = [(x * GRID_INTERVAL + GRID_INTERVAL // 2, y * GRID_INTERVAL + GRID_INTERVAL // 2) for (x, y)
                             in path]
                real_path[-1] = (mouse_x, mouse_y)
                path_index = 0

    if path:
        lookahead_point, dist, next_path_index = car.set_look_ahead_point(real_path, path_index,look_ahead_distance,10)
        path_index = next_path_index

        if lookahead_point:
            target_speed = 10
            target_x = lookahead_point[0]
            target_y = lookahead_point[1]
            target_steer = car.cal_steer(lookahead_point[0], lookahead_point[1])
        else:
            target_x = car.x
            target_y = car.y
            target_speed = 0
            target_steer = 0
            path =[]
            path_index = 0
        car.set_speed(target_speed,dt)
        car.set_steering(target_steer,dt)
        car.update(dt)

        lidar_pos = (car.x, car.y, car.angle)
        lidar_pnts = ad_util.lidar_scan(lidar_pos, walls, lidar_range = 500, angular_resolution = 1)
        local_lidar_pnts = ad_util.lidar_scan_origin_lidar(lidar_pos, lidar_pnts)
        down_pnts = ad_util.grid_downsample(local_lidar_pnts, cell_size=GRID_INTERVAL)
        dst_pts = np.array(list(global_map_set))

        T, trans_scr, err = ad_util.icp_2d_rmse(down_pnts, dst_pts, T, max_iterations=20, distance_threshold=50.0,rmse_threshold=1e-2)
        _x, _y, _theta = ad_util.matrix_to_pose(T)

        icp_car.x = _x
        icp_car.y = _y
        icp_car.angle = _theta

        if map_update_count ==0:
            grid_indices = ad_util.grid_downsample(trans_scr, cell_size=GRID_INTERVAL)
            global_map_set = ad_util.update_global_map(grid_indices, global_map_set)
            grid = np.zeros((GRID_H, GRID_W), dtype=np.uint8)
            for gx, gy in global_map_set:
                grid_y = int(gy // GRID_INTERVAL)
                grid_x = int(gx // GRID_INTERVAL)
                if 0 <= grid_x < GRID_W and 0 <= grid_y < GRID_H:
                    grid[grid_y, grid_x] = 1
            ad_util.apply_margin_to_grid(grid, 5)
            car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
            mouse_grid = (int(mouse_x // GRID_INTERVAL), int(mouse_y // GRID_INTERVAL))
            path = ad_util.ad_dijkstra(grid, car_grid, mouse_grid)
            if path:
                real_path = [(x * GRID_INTERVAL + GRID_INTERVAL // 2, y * GRID_INTERVAL + GRID_INTERVAL // 2) for (x, y)
                             in path]
                real_path[-1] = (mouse_x, mouse_y)
                path_index = 0

    # 충돌 여부 확인
    is_collision = ad_util.check_collision((car.x, car.y), car.angle, 50, 30, walls)

    if is_collision:
        print("충돌")
        screen.fill(ad_util.red)
    else:
        screen.fill(ad_util.black)

    # 그리기
    pygame.draw.circle(screen, ad_util.white, (int(car.x), int(car.y)), 500)

    ad_util.draw_car(screen,car_image,car.x,car.y,car.angle,alpha=100)
    ad_util.draw_car(screen, car_image, icp_car.x, icp_car.y, icp_car.angle)

    ad_util.draw_lidar_pnts(screen,lidar_pnts)

    car_grid = (int(car.x // GRID_INTERVAL), int(car.y // GRID_INTERVAL))
    target_grid = (int(target_x // GRID_INTERVAL), int(target_y // GRID_INTERVAL))

    for gx, gy in global_map_set:
        grid_y = int(gy//GRID_INTERVAL)
        grid_x = int(gx // GRID_INTERVAL)
        if 0<= grid_x<GRID_W and 0<= grid_y<GRID_H:
            grid[grid_y,grid_x] = 1

    rect = pygame.Rect(screen_width, 0, screen_width, screen_height)
    pygame.draw.rect(screen, ad_util.black, rect)
    ad_util.draw_map(screen, screen_width, grid, GRID_INTERVAL,car_grid,target_grid,path)

    ad_util.draw_info(screen, screen_height, car, target_speed, target_steer, target_x, target_y)

    pygame.display.flip()
    map_update_count = (map_update_count + 1) % map_update
pygame.quit()