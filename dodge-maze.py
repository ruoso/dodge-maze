import json
import pygame
import thread
import time
import math

screen_x_size = 820;
screen_y_size = 820;

wall_thickness = 0.1
character_box_size = 0.15

def clear_screen(screen):
    pygame.draw.rect(screen, (100,100,100),
                     pygame.Rect(0,0,screen_x_size,screen_y_size))

def l2p( value ):
    return value * 100

def l2p_pos( value ):
    return 10 + l2p(value)

def draw_tile( color, screen, x, y ):
    pygame.draw.rect(screen, color,
                     pygame.Rect(l2p_pos(x), l2p_pos(y),
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
                         pygame.Rect(l2p_pos(x), l2p_pos(y),
                                     l2p(1), l2p(wall_thickness)))
    if (mask & 2):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p_pos(x+(1-wall_thickness)), l2p_pos(y),
                                     l2p(wall_thickness), l2p(1)))
    if (mask & 4):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p_pos(x), l2p_pos(y+(1-wall_thickness)),
                                     l2p(1), l2p(wall_thickness)))
    if (mask & 8):
        pygame.draw.rect(screen, color,
                         pygame.Rect(l2p_pos(x), l2p_pos(y),
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
                     pygame.Rect(l2p_pos(x-(character_box_size / 2)),
                                 l2p_pos(y-(character_box_size / 2)),
                                 l2p(character_box_size),
                                 l2p(character_box_size)))

def draw_enemy( screen, x, y ):
    color = ( 127, 127, 0 )
    pygame.draw.rect(screen, color,
                     pygame.Rect(l2p_pos(x-character_box_size/2),
                                 l2p_pos(y-character_box_size/2),
                                 l2p(character_box_size),
                                 l2p(character_box_size)))

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

def character_move( level_data, character, pressed, elapsed, velocity ):
    
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
        
        distance_y = math.sin(angle)
        distance_x = math.cos(angle)
        current_x = character[0]
        current_y = character[1]

        cur_left_x = current_x - character_box_size/2
        cur_left_rel_x = cur_left_x - int(cur_left_x)
        cur_top_y = current_y - character_box_size/2
        cur_top_rel_y = cur_top_y - int(cur_top_y)
        cur_right_x = current_x + character_box_size/2
        cur_right_rel_x = cur_right_x - int(cur_right_x)
        cur_bottom_y = current_y + character_box_size/2
        cur_bottom_rel_y = cur_bottom_y - int(cur_bottom_y)

        new_x = current_x + distance_x * distance
        new_y = current_y + distance_y * distance
        new_left_x = new_x - character_box_size/2
        new_left_rel_x = new_left_x - int(new_left_x)
        new_top_y = new_y - character_box_size/2
        new_top_rel_y = new_top_y - int(new_top_y)
        new_right_x = new_x + character_box_size/2
        new_right_rel_x = new_right_x - int(new_right_x)
        new_bottom_y = new_y + character_box_size/2
        new_bottom_rel_y = new_bottom_y - int(new_bottom_y)
        walls_in_tl_tile = level_data["walls"][int(new_top_y)][int(new_left_x)]
        walls_in_tr_tile = level_data["walls"][int(new_top_y)][int(new_right_x)]
        walls_in_bl_tile = level_data["walls"][int(new_bottom_y)][int(new_left_x)]
        walls_in_br_tile = level_data["walls"][int(new_bottom_y)][int(new_right_x)]

        if ((new_left_rel_x <= wall_thickness) and
            (walls_in_tl_tile & 8 or walls_in_bl_tile & 8)):
            new_x = current_x
            if ((cur_left_rel_x <= wall_thickness) and
                (walls_in_tl_tile & 8 or walls_in_bl_tile & 8)):
                new_y = current_y
                
        if ((new_left_rel_x >= 1 - wall_thickness) and
            (walls_in_tl_tile & 2 or walls_in_bl_tile & 2)):
            new_x = current_x
            if ((cur_left_rel_x >= wall_thickness) and
                (walls_in_tl_tile & 2 or walls_in_bl_tile & 2)):
                new_y = current_y

        if ((new_right_rel_x >= 1 - wall_thickness) and
            (walls_in_tr_tile & 2 or walls_in_br_tile & 2)):
            new_x = current_x
            if ((cur_right_rel_x >= 1 - wall_thickness) and
                (walls_in_tr_tile & 2 or walls_in_br_tile & 2)):
                new_y  = current_y
            
        if (((new_right_rel_x <= wall_thickness) and
             (walls_in_tr_tile & 8 or walls_in_br_tile & 8))):
            new_x = current_x
            if (((cur_right_rel_x <= wall_thickness) and
                 (walls_in_tr_tile & 8 or walls_in_br_tile & 8))):
                new_y = current_y

        if ((new_bottom_rel_y >= 1 - wall_thickness) and
            (walls_in_br_tile & 4 or walls_in_bl_tile & 4)):
            new_y = current_y
            if ((cur_bottom_rel_y >= 1 - wall_thickness) and
                (walls_in_br_tile & 4 or walls_in_bl_tile & 4)):
                new_x = current_x

        if ((new_bottom_rel_y <= wall_thickness) and
            (walls_in_br_tile & 1 or walls_in_bl_tile & 1)):
            new_y = current_y
            if ((cur_bottom_rel_y <= wall_thickness) and
                (walls_in_br_tile & 1 or walls_in_bl_tile & 1)):
                new_x = current_x

        if ((new_top_rel_y <= wall_thickness) and
            (walls_in_tl_tile & 1 or walls_in_tr_tile & 1)):
            new_y = current_y
            if ((cur_top_rel_y <= wall_thickness) and
                (walls_in_tl_tile & 1 or walls_in_tr_tile & 1)):
                new_x = current_x
            
        if ((new_top_rel_y >= 1 - wall_thickness) and
            (walls_in_tl_tile & 4 or walls_in_tr_tile & 4)):
            new_y = current_y
            if ((cur_top_rel_y >= 1 - wall_thickness) and
                (walls_in_tl_tile & 4 or walls_in_tr_tile & 4)):
                new_x = cuurent_x

        character[0] = new_x
        character[1] = new_y

def player_velocity( level_data ):
    character = level_data["player"]
    floor_type = level_data["floor"][int(character[1])][int(character[0])]
    if floor_type == "A":
        return 2.5
    elif floor_type == "B":
        return 1.5
    else:
        return 0

def enemy_velocity( level_data, character ):
    floor_type = level_data["floor"][int(character[1])][int(character[0])]
    if floor_type == "B":
        return 2.5
    elif floor_type == "A":
        return 1.8
    else:
        return 0

def can_see_point_from_point(level, viewer_x, viewer_y, target_x, target_y):
    # 1) what is the angle between the two points
    rel_to_viewer_x = target_x - viewer_x
    rel_to_viewer_y = target_y - viewer_y
    angle = math.atan2( rel_to_viewer_y, rel_to_viewer_x  )

    # 2) what is the current tile
    tile_x = int(viewer_x)
    tile_y = int(viewer_y)

    # 3) which tile the target is
    target_tile_x = int(target_x)
    target_tile_y = int(target_y)

    if (tile_x == target_tile_x and
        tile_y == target_tile_y):
        # we are on the same tile, it can definitely see it
        return True
    else:
        # 4) our position inside that tile
        rel_to_tile_x = viewer_x - tile_x
        rel_to_tile_y = viewer_y - tile_y
        
        # 5) find the exit point in this tile
        viewer_to_l_x = 0 - rel_to_tile_x
        viewer_to_r_x = 1 - rel_to_tile_x
        viewer_to_t_y = 0 - rel_to_tile_y
        viewer_to_b_y = 1 - rel_to_tile_y

        # Find the angle to the corners
        tl_angle = math.atan2(viewer_to_t_y, viewer_to_l_x )
        bl_angle = math.atan2(viewer_to_b_y, viewer_to_l_x )
        tr_angle = math.atan2(viewer_to_t_y, viewer_to_r_x )
        br_angle = math.atan2(viewer_to_b_y, viewer_to_r_x )
       
        this_wall_mask = level["walls"][tile_y][tile_x]
               
        if (angle <= tl_angle or angle >= bl_angle):
            # looking left
            if (this_wall_mask & 8):
                return False
            else:
                next_wall_mask = level["walls"][tile_y][tile_x - 1]
                if (next_wall_mask & 2):
                    return False
                else:
                    adjusted_y = math.tan(angle) * viewer_to_l_x
                    if can_see_point_from_point( level,
                                                 tile_x - 0.001,
                                                 viewer_y + adjusted_y,
                                                 target_x, target_y ):
                        return "left"
                    else:
                        return False

        elif (angle < bl_angle and angle >= br_angle):
            # looking down
            if (this_wall_mask & 4):
                return False
            else:
                next_wall_mask = level["walls"][tile_y + 1][tile_x]
                if (next_wall_mask & 1):
                    return False
                else:
                    adjusted_x = 1/(math.tan(angle)) * viewer_to_b_y
                    if can_see_point_from_point( level,
                                                 viewer_x + adjusted_x,
                                                 tile_y + 1.001,
                                                 target_x, target_y ):
                        return "down"
                    else:
                        return False

        elif (angle < br_angle and angle >= tr_angle):
            # looking to the right
            if (this_wall_mask & 2):
                return False
            else:
                next_wall_mask = level["walls"][tile_y][tile_x + 1]
                if (next_wall_mask & 8):
                    return False
                else:
                    adjusted_y = math.tan(angle) * viewer_to_r_x
                    if can_see_point_from_point( level,
                                                 tile_x + 1.001,
                                                 viewer_y + adjusted_y,
                                                 target_x, target_y ):
                        return "right"
                    else:
                        return False

        elif (angle < tr_angle or angle >= tl_angle):
            # looking up
            if (this_wall_mask & 1):
                return False
            else:
                next_wall_mask = level["walls"][tile_y - 1][tile_x]
                if (next_wall_mask & 4):
                    return False
                else:
                    adjusted_x = (1/math.tan(angle)) * viewer_to_t_y
                    if can_see_point_from_point( level,
                                                 viewer_x + adjusted_x,
                                                 tile_y - 0.0001,
                                                 target_x, target_y ):
                        return "up"
                    else:
                        return False

        else:
            # ?
            print "huh, really?"
            return False

def enemy_behavior( elapsed, level_data, player_x, player_y, enemy ):
    enemy_x = enemy[0]
    enemy_y = enemy[1]
    direction = can_see_point_from_point(level_data,
                                         enemy_x, enemy_y,
                                         player_x, player_y)
    if direction:
        enemy_pressed = {
            pygame.K_w: 0,
            pygame.K_a: 0,
            pygame.K_s: 0,
            pygame.K_d: 0
        }

        if (direction == True):
            if (player_x < enemy_x):
                enemy_pressed[pygame.K_a] = 1
            elif (player_x > enemy_x):
                enemy_pressed[pygame.K_d] = 1
                    
            if (player_y < enemy_y):
                enemy_pressed[pygame.K_w] = 1
            elif (player_y > enemy_y):
                enemy_pressed[pygame.K_s] = 1
        else:
            rel_x = enemy_x - int(enemy_x)
            rel_y = enemy_y - int(enemy_y)
            if (direction == "up"):
                enemy_pressed[pygame.K_w] = 1
                if (rel_x < 0.6):
                    enemy_pressed[pygame.K_d] = 1
                elif (rel_x > 0.4):
                    enemy_pressed[pygame.K_a] = 1
                        
            elif (direction == "down"):
                enemy_pressed[pygame.K_s] = 1
                if (rel_x < 0.4):
                    enemy_pressed[pygame.K_d] = 1
                elif (rel_x > 0.6):
                    enemy_pressed[pygame.K_a] = 1

            elif (direction == "left"):
                enemy_pressed[pygame.K_a] = 1
                if (rel_y < 0.4):
                    enemy_pressed[pygame.K_s] = 1
                elif (rel_y > 0.6):
                    enemy_pressed[pygame.K_w] = 1

            elif (direction == "right"):
                enemy_pressed[pygame.K_d] = 1
                if (rel_y < 0.4):
                    enemy_pressed[pygame.K_s] = 1
                elif (rel_y > 0.6):
                    enemy_pressed[pygame.K_w] = 1

        character_move(level_data,
                       enemy,
                       enemy_pressed,
                       elapsed,
                       enemy_velocity(level_data, enemy))

def process_rules( level_data, elapsed ):
    pressed = pygame.key.get_pressed()
    character_move(level_data,
                   level_data["player"],
                   pressed,
                   elapsed,
                   player_velocity(level_data))
    player_x = level_data["player"][0]
    player_y = level_data["player"][1]
    for enemy in level_data["enemies"]:
        enemy_behavior(elapsed, level_data, player_x, player_y, enemy)

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
