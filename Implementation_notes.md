# Map Grids

Floor and walls are represented as a grid of the entire level, e.g.:

Follows a sample level

## Floor

 * 0 - nothing
 * A - You are faster than the enemy
 * B - Enemy is faster than you
 * P - Pit
 * G - Goal

|0|B|0|0|0|B|B|B|
|0|B|0|0|0|B|0|B|
|B|B|B|B|A|A|P|B|
|B|A|0|A|B|0|0|B|
|B|A|A|A|B|0|0|G|
|B|0|0|0|0|0|0|0|
|B|0|0|0|0|0|0|0|
|0|0|0|0|0|0|0|0|

## Walls

 * 1 - Top
 * 2 - Right
 * 4 - Bottom
 * 8 - Left

|0|B|0|0|0|9|5|3|
|0|A|0|0|0|A|0|A|
|9|0|5|1|1|4|5|2|
|A|A|0|A|A|0|0|A|
|A|C|5|6|E|0|0|E|
|A|0|0|0|0|0|0|0|
|E|0|0|0|0|0|0|0|
|0|0|0|0|0|0|0|0|

## Dynamic Elements

 * Player: [ 0.5, 6.5 ]
 * Enemies:
   [
    [ 1.5, 0.5 ],
    [ 4.5, 4.5 ],
   ]
  * Goal: [ 7.5, 4.5 ]
  
