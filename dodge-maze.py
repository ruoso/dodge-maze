import json
import pygame
import thread
import time
import math

screen_x_size = 830;
screen_y_size = 830;

wall_thickness = 0.1
character_box_size = 0.04

def clear_screen(screen):
    pygame.draw.rect(screen, (100,100,100),
                     pygame.Rect(0,0,screen_x_size,screen_y_size))

def l2p( value ):
    return 10 + (value * 100)

def draw_tile( color, screen, x, y ):
    pygame.draw.rect(screen, color,
                     pygame.Rect(l2p(x), l2p(y),
                                 l2p(1), l2p(1)))

def draw_floor( level, screen ):
    floor = level["floor"]
    level_y_size = len(floor)
    level_x_size = len(floor[0])
    for x in range(0, level_x_size):
        for y in range(0, level_y_size):
            floor_type = floor[y][x]
            if floor_type == "A":
                draw_tile( (100, 255, 100), screen, x, y )
            elif floor_type == "B":
                draw_tile( (255, 100, 100), screen, x, y )
            elif floor_type == "P":
                draw_tile( (0, 0, 0), screen, x, y )
            elif floor_type == "G":
                draw_tile( (0, 255, 0), screen, x, y )
            else:
                draw_tile( (0, 0, 0), screen, x, y )

def draw_wall_in_tile( screen, x, y, mask ):
    color = ( 255, 255, 255 )
    if (mask & 1):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p(x), l2p(y),
                                     l2p(1), l2p(wall_thickness)))
    if (mask & 2):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p(x+(1-wall_thickness)), l2p(y),
                                     l2p(wall_thickness), l2p(1)))
    if (mask & 4):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p(x), l2p(y+(1-wall_thickness)),
                                     l2p(1), l2p(wall_thickness)))
    if (mask & 8):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p(x), l2p(y),
                                     l2p(wall_thickness), l2p(1)))

def draw_walls( level, screen ):
    walls = level["walls"]
    level_y_size = len(walls)
    level_x_size = len(walls[0])
    for x in range(0, level_x_size):
        for y in range(0, level_y_size):
            wall_mask = walls[y][x]
            draw_wall_in_tile( screen, x, y, wall_mask )

def draw_player( level, screen ):
    color = ( 0, 0, 255 )
    x = level["player"][0]
    y = level["player"][1]
    pygame.draw.rect(screen, color,
                     pygame.Rect(l2p(x-(character_box_size / 2)),
                                 l2p(y-(character_box_size / 2)),
                                 l2p(character_box_size),
                                 l2p(character_box_size)))

def draw_enemy( screen, x, y ):
    color = ( 127, 127, 0 )
    pygame.draw.rect(screen, color,
                     pygame.Rect(l2p(x-0.02),
                                 l2p(y-0.02),
                                 l2p(0.04), l2p(0.04)))

def draw_enemies( level, screen ):
    enemies = level["enemies"]
    for enemy in enemies:
        draw_enemy( screen, enemy[0], enemy[1] )

def draw_everything( level_data, screen ):        
    clear_screen( screen )
    draw_floor( level_data, screen )
    draw_walls( level_data, screen )
    draw_player( level_data, screen )
    draw_enemies( level_data, screen )
    pygame.display.flip()

def player_move( level_data, pressed, elapsed ):
    player = level_data["player"]
    floor_type = level_data["floor"][int(player[1])][int(player[0])]

    if floor_type == "A":
        velocity = 2.5
    elif floor_type == "B":
        velocity = 1.5
    elif floor_type == "0":
        velocity = 0
    
    distance = velocity * elapsed
    vertical = 0
    horizontal = 0

    if (pressed[pygame.K_w] != 0):
        vertical -= 1
    if (pressed[pygame.K_s] != 0):
        vertical += 1
        
    if (pressed[pygame.K_a] != 0):
        horizontal -= 1
    if (pressed[pygame.K_d] != 0):
        horizontal += 1

    if (horizontal or vertical):
        angle = math.atan2(vertical, horizontal )
        
        current_x = player[0]
        distance_x = math.cos(angle)
        current_y = player[1]
        distance_y = math.sin(angle)
        new_x = current_x + distance_x * distance
        new_y = current_y + distance_y * distance

        # is ( new_x, new_y ) going to bump into a wall?
        relative_x = new_x - int(current_x)
        relative_y = new_y - int(current_y)
        walls_in_this_tile = level_data["walls"][int(player[1])][int(player[0])]
        walls_in_new_tile = level_data["walls"][int(new_y)][int(new_x)]
        print "{0}\n".format((int(current_x), int(current_y)))
        wall_collision_distance = (wall_thickness*2 + character_box_size/2)
        if (relative_x <= wall_collision_distance):
            if (walls_in_this_tile & 8):
                new_x = current_x
        if (relative_x >= 1 - wall_collision_distance):
            if (walls_in_this_tile & 2):
                new_x = current_x
        if (relative_y <= wall_collision_distance):
            if (walls_in_this_tile & 1):
                new_y = current_y
        if (relative_y >= 1 - wall_collision_distance):
            if (walls_in_this_tile & 4):
                new_y = current_y

        player[0] = new_x
        player[1] = new_y

def process_rules( level_data, elapsed ):
    pressed = pygame.key.get_pressed()
    player_move(level_data, pressed, elapsed)

def main( screen ):
    with open("levels/level1.json") as level_file:
        level_data = json.load(level_file)

    framerate = 30
    frame_duration = 1/30

    done = False
    tick = time.time()
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        tock = time.time()
        elapsed = tock - tick
        draw_everything( level_data, screen )
        process_rules( level_data, elapsed )
        tick = tock
        if (elapsed < frame_duration):
            sleep(frame_duration - elapsed)
    
pygame.init()
screen = pygame.display.set_mode((screen_x_size, screen_y_size))
main(screen)
