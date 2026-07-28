#!/usr/bin/env python3
#
#############################################################################
# Asciiquarium - An aquarium animation in ASCII art
#
# This program displays an aquarium/sea animation using ASCII art.
# It requires the curses module (built-in). Asciiquarium will
# only run on platforms with a curses library, so Windows is not supported.
#
# The current version of this program is available at:
#
# http://robobunny.com/projects/asciiquarium
#
#############################################################################
# Author:
#   Kirk Baucom <kbaucom@schizoid.com>
#
# Python port:
#   Literal 1:1 port from Perl for the reLang hackathon
#
# Contributors:
#   Joan Stark: http://www.geocities.com/SoHo/7373/
#     most of the ASCII art
#
#   Claudio Matsuoka <cmatsuoka@gmail.com>
#     improved marine biodiversity (backported from the Asciiquarium Live
#     Wallaper for Android)
#     https://market.android.com/details?id=org.helllabs.android.asciiquarium
#
# License:
#
# Copyright (C) 2003 Kirk Baucom (kbaucom@schizoid.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#############################################################################

import curses
import argparse
import signal
import sys
import time
import random


version = "1.1"
new_fish = 1
new_monster = 1


depth = {
    'guiText': 0,
    'gui': 1,
    'shark': 2,
    'fish_start': 3,
    'fish_end': 20,
    'seaweed': 21,
    'castle': 22,
    'water_line3': 2,
    'water_gap3': 3,
    'water_line2': 4,
    'water_gap2': 5,
    'water_line1': 6,
    'water_gap1': 7,
    'water_line0': 8,
    'water_gap0': 9,
}


class Entity:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type', '')
        raw_shape = kwargs.get('shape', '')
        self.auto_trans = kwargs.get('auto_trans', 0)
        self.color = kwargs.get('color', '')
        self.default_color = kwargs.get('default_color', 'WHITE')
        self._callback = kwargs.get('callback', None)
        self._callback_args = list(kwargs.get('callback_args', []))
        self.die_time = kwargs.get('die_time', None)
        self.death_cb = kwargs.get('death_cb', None)
        self.die_offscreen = kwargs.get('die_offscreen', 0)
        self._coll_handler = kwargs.get('coll_handler', None)
        self.transparent = kwargs.get('transparent', None)
        self.die_frame = kwargs.get('die_frame', None)
        self.depth = kwargs.get('depth', None)
        self.physical = kwargs.get('physical', 0)
        position = kwargs.get('position', [0, 0, 0])
        self.x = position[0]
        self.y = position[1]
        self.z = position[2] if len(position) > 2 else 0
        self.frame = 0
        self.frame_count = 0
        self.killed = False
        self.anim = None
        if isinstance(raw_shape, str):
            self.frames = [raw_shape]
        else:
            self.frames = list(raw_shape)
        if self.frames:
            lines = self.frames[0].split('\n')
            self.HEIGHT = len(lines)
            self.WIDTH = max((len(l) for l in lines), default=0)
        else:
            self.HEIGHT = 0
            self.WIDTH = 0

    def position(self):
        return [self.x, self.y, self.z]

    def size(self):
        return [self.WIDTH, self.HEIGHT]

    @property
    def height(self):
        return self.HEIGHT

    def callback_args(self):
        return self._callback_args

    def kill(self):
        self.killed = True

    def collisions(self):
        if self.anim is None:
            return []
        result = []
        for e in self.anim.entities:
            if e is not self and e.physical:
                if (self.x < e.x + e.WIDTH and
                        self.x + self.WIDTH > e.x and
                        self.y < e.y + e.HEIGHT and
                        self.y + self.HEIGHT > e.y):
                    result.append(e)
        return result

    def move_entity(self, anim):
        speed = self._callback_args
        if len(speed) > 0:
            self.x += speed[0]
        if len(speed) > 1:
            self.y += speed[1]
        if self.die_offscreen:
            if (self.x + self.WIDTH < 0 or
                    self.x > anim.width() or
                    self.y + self.HEIGHT < 0 or
                    self.y > anim.height()):
                return 1
        return 0


class Animation:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._color_enabled = 0
        self.entities = []
        self._init_colors()
        self._update_size()

    def _init_colors(self):
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    def _update_size(self):
        self.height_val, self.width_val = self.stdscr.getmaxyx()

    def width(self):
        return self.width_val

    def height(self):
        return self.height_val

    def color(self, flag):
        self._color_enabled = flag

    def new_entity(self, **kwargs):
        entity = Entity(**kwargs)
        self.add_entity(entity)
        return entity

    def add_entity(self, entity):
        entity.anim = self
        self.entities.append(entity)

    def del_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def remove_all_entities(self):
        self.entities = []

    def get_entities_of_type(self, type_name):
        return [e for e in self.entities if e.type == type_name]

    def update_term_size(self):
        self._update_size()

    def _color_to_attr(self, c):
        pair_map = {
            'r': 1, 'R': 1,
            'g': 2, 'G': 2,
            'y': 3, 'Y': 3,
            'b': 4, 'B': 4,
            'm': 5, 'M': 5,
            'c': 6, 'C': 6,
            'W': 7,
        }
        pair = pair_map.get(c, 0)
        if pair:
            attr = curses.color_pair(pair)
            if c.isupper():
                attr |= curses.A_BOLD
            return attr
        return 0

    def _draw_entity(self, entity):
        frame_str = entity.frames[entity.frame % len(entity.frames)]
        lines = frame_str.split('\n')
        if entity.color:
            if isinstance(entity.color, str):
                masks = [entity.color]
            else:
                masks = list(entity.color)
            if masks:
                mask_idx = entity.frame % len(masks)
                mask_lines = masks[mask_idx].split('\n')
            else:
                mask_lines = None
        else:
            mask_lines = None
        for i, line in enumerate(lines):
            y = entity.y + i
            if y < 0 or y >= self.height_val:
                continue
            ml = mask_lines[i] if mask_lines is not None and i < len(mask_lines) else None
            for j, ch in enumerate(line):
                x = entity.x + j
                if x < 0 or x >= self.width_val:
                    continue
                if entity.transparent is not None and ch == entity.transparent:
                    continue
                if entity.auto_trans and ch == ' ':
                    continue
                attr = 0
                if ml is not None and j < len(ml) and ml[j] != ' ':
                    attr = self._color_to_attr(ml[j])
                if attr:
                    try:
                        self.stdscr.addch(y, x, ch, attr)
                    except Exception:
                        pass
                else:
                    try:
                        self.stdscr.addch(y, x, ch)
                    except Exception:
                        pass

    def animate(self):
        dead = []
        for entity in self.entities:
            if entity.killed:
                dead.append(entity)
                continue
            if entity.die_time is not None and time.time() >= entity.die_time:
                dead.append(entity)
                continue
            if entity.die_frame is not None and entity.frame_count >= entity.die_frame:
                dead.append(entity)
                continue
            if entity._callback:
                result = entity._callback(entity, self)
                if result:
                    dead.append(entity)
                    continue
            else:
                if entity._callback_args and len(entity._callback_args) > 0:
                    entity.x += entity._callback_args[0]
                if entity._callback_args and len(entity._callback_args) > 1:
                    entity.y += entity._callback_args[1]
                if entity.die_offscreen:
                    if (entity.x + entity.WIDTH < 0 or
                            entity.x > self.width_val or
                            entity.y + entity.HEIGHT < 0 or
                            entity.y > self.height_val):
                        dead.append(entity)
                        continue
            if entity._coll_handler:
                entity._coll_handler(entity, self)
            if len(entity.frames) > 1:
                entity.frame = (entity.frame + 1) % len(entity.frames)
            entity.frame_count += 1
        for d in dead:
            if d.death_cb:
                d.death_cb(d, self)
            self.del_entity(d)
        self.redraw_screen()

    def redraw_screen(self):
        self.stdscr.erase()
        sorted_entities = sorted(self.entities, key=lambda e: e.depth if e.depth is not None else e.z)
        for entity in sorted_entities:
            self._draw_entity(entity)
        self.stdscr.refresh()


def add_environment(anim):
    water_line_segment = [
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',
        '^^^^ ^^^  ^^^   ^^^    ^^^^      ',
        '^^^^      ^^^^     ^^^    ^^     ',
        '^^      ^^^^      ^^^    ^^^^^^  '
    ]
    segment_size = len(water_line_segment[0])
    segment_repeat = int(anim.width() / segment_size) + 1
    for i in range(len(water_line_segment)):
        water_line_segment[i] = water_line_segment[i] * segment_repeat
    for i in range(len(water_line_segment)):
        anim.new_entity(
            name='water_seg_{}'.format(i),
            type='waterline',
            shape=water_line_segment[i],
            position=[0, i + 5, depth['water_line' + str(i)]],
            default_color='cyan',
            depth=22,
            physical=1,
        )


def add_castle(anim):
    castle_image = """
               T~~
               |
              /^\\
             /   \\
 _   _   _  /     \\  _   _   _
[ ]_[ ]_[ ]/ _   _ \\[ ]_[ ]_[ ]
|_=__-_ =_|_[ ]_[ ]_|_=-___-__|
 | _- =  | =_ = _    |= _=   |
 |= -[]  |- = _ =    |_-=_[] |
 | =_    |= - ___    | =_ =  |
 |=  []- |-  /| |\\   |=_ =[] |
 |- =_   | =| | | |  |- = -  |
 |_______|__|_|_|_|__|_______|
"""
    castle_mask = """
                RR

              yyy
             y   y
            y     y
           y       y



              yyy
             yy yy
            y y y y
            yyyyyyy
"""
    anim.new_entity(
        name='castle',
        shape=castle_image,
        color=castle_mask,
        position=[anim.width() - 32, anim.height() - 13, depth['castle']],
        default_color='BLACK',
    )


def add_all_seaweed(anim):
    seaweed_count = int(anim.width() / 15)
    for _ in range(seaweed_count):
        add_seaweed(None, anim)


def add_seaweed(old_seaweed, anim):
    seaweed_image = ['', '']
    height = int(random.random() * 4) + 3
    for i in range(1, height + 1):
        left_side = i % 2
        right_side = not left_side
        seaweed_image[left_side] += '(\n'
        seaweed_image[right_side] += ' )\n'
    x = int(random.random() * (anim.width() - 2)) + 1
    y = anim.height() - height
    anim_speed = random.random() * 0.05 + 0.25
    anim.new_entity(
        name='seaweed' + str(random.random()),
        shape=seaweed_image,
        position=[x, y, depth['seaweed']],
        callback_args=[0, 0, 0, anim_speed],
        die_time=time.time() + int(random.random() * 4 * 60) + (8 * 60),
        death_cb=add_seaweed,
        default_color='green',
    )


def add_bubble(fish, anim):
    cb_args = fish.callback_args()
    fish_size = fish.size()
    fish_pos = fish.position()
    bubble_pos = list(fish_pos)
    if cb_args[0] > 0:
        bubble_pos[0] += fish_size[0]
    bubble_pos[1] += int(fish_size[1] / 2)
    bubble_pos[2] -= 1
    anim.new_entity(
        shape=['.', 'o', 'O', 'O', 'O'],
        type='bubble',
        position=bubble_pos,
        callback_args=[0, -1, 0, 0.1],
        die_offscreen=1,
        physical=1,
        coll_handler=bubble_collision,
        default_color='CYAN',
    )


def bubble_collision(bubble, anim):
    collisions = bubble.collisions()
    for col_obj in collisions:
        if col_obj.type == 'waterline':
            bubble.kill()
            break


def add_all_fish(anim):
    screen_size = (anim.height() - 9) * anim.width()
    fish_count = int(screen_size / 350)
    for _ in range(fish_count):
        add_fish(None, anim)


def add_fish(*parm):
    if new_fish:
        if int(random.random() * 12) > 8:
            add_new_fish(*parm)
        else:
            add_old_fish(*parm)
    else:
        add_old_fish(*parm)


def add_new_fish(old_fish, anim):
    fish_image = [

"""
   \\
  / \\
>=_('>
  \\_/
   /
""",
"""
   1
  1 1
 663745
  111
   3
""",
"""
  /
 / \\
<')_=<
 \\_/
  \\
""",
"""
  2
  111
 547366
  111
   3
""",
"""
     ,
     \\}\\\\
\\\\  .'  `\\
\\}\\\}<   ( 6>
/  `,  .'
     \\}/
     '
""",
"""
     2
     22
6  11  11
661   7 45
6  11  11
     33
     3
""",
"""
    ,
   /\\{
 /'  `.  /
<6 )   >\\{\\{
 `.  ,'  \\
   \\\\{
    `
""",
"""
    2
   22
 11  11  6
54 7   166
 11  11  6
   33
    3
""",
"""
            \\\\'`.
             )  \\
(`.??????_.-`' ' '`-.
 \\ `.??.`        (o) \\_
  >  ><     (((       (
 / .`??`._      /_|  /'
(.`???????`-. _  _.-`
            /__/'

""",
"""
            1111
             1  1
111      11111 1 1111
 1 11  11        141 11
  1  11     777       5
 1 11  111      333  11
111       111 1  1111
            11111

""",
"""
       .'`/
      /  (
  .-'` ` `'-._??????.')
_/ (o)        '.??.' /
)       )))     ><  <
`\\  |_\\      _.'??'. \\
  '-._  _ .-'???????'.)
      `\\__\\
""",
"""
       1111
      1  1
  1111 1 11111      111
11 141        11  11 1
5       777     11  1
11  333      111  11 1
  1111  1 111       111
      11111
""",
"""
       ,--,_
__    _\\.---'-.
\\ '.-"     // o\\
/_.'-._    \\\\  /
       `"--(/`"
""",
"""
       22222
66    121111211
6 6111     77 41
6661111    77  1
       11113311
""",
"""
    _,--,
 .-'---./_    __
/o \\\\     "-.' /
\\  //    _.-'._\\
 `"\\)--`
""",
"""
    22222
 112111121    66
14 77     1116 6
1  77    1111666
 11331111
""",
    ]
    add_fish_entity(anim, *fish_image)


def add_old_fish(old_fish, anim):
    fish_image = [

"""
       \\
     ...\\..,
\\  /'       \\
 >=     (  ' >
/  \\      / /
    `"'"'/''
""",
"""
       2
     1112111
6  11       1
 66     7  4 5
6  1      3 1
    11111311
""",
"""
      /
  ,../...
 /       '\\  /
< '  )     =<
 \\ \\      /  \\
  `'\\'"'"'
""",
"""
      2
  1112111
 1       11  6
5 4  7     66
 1 3      1  6
  11311111
""",
"""
    \\
\\ /--\\
>=  (o>
/ \\__/
    /
""",
"""
    2
6 1111
66  745
6 1111
    3
""",
"""
  /
 /--\\ /
<o)  =<
 \\__/ \\
  \\
""",
"""
  2
 1111 6
547  66
 1111 6
  3
""",
"""
       \\:.
\\;,   ,;\\\\\\,
  \\\\\\\\;;:::::::o
  ///;;::::::::<
 /;` ``/////``
""",
"""
       222
666   1122211
  6661111111114
  66611111111115
 666 113333311
""",
"""
      .:/
   ,,///;,   ,;/
 o:::::::;;///
>::::::::;;\\\\\\
  ''\\\\\\\\\\\\'' ';\\
""",
"""
      222
   1122211   666
 4111111111666
51111111111666
  113333311 666
""",
"""
  __
><_'>
   '
""",
"""
  11
61145
   3
""",
"""
 __
<'_><
 `
""",
"""
 11
54116
 3
""",
"""
   ..\\,
>='   ('>
  '''/''
""",
"""
   1121
661   745
  111311
""",
"""
  ,/..
<')   `=<
 ``\\```
""",
"""
  1211
547   166
 113111
""",
"""
   \\
  / \\
>=_('>
  \\_/
   /
""",
"""
   2
  1 1
661745
  111
   3
""",
"""
  /
 / \\
<')_=<
 \\_/
  \\
""",
"""
  2
 1 1
547166
 111
  3
""",
"""
  ,\\
>=('>
  '/
""",
"""
  12
66745
  13
""",
"""
 /,
<')=<
 \\`
""",
"""
 21
54766
 31
""",
"""
  __
\\/ o\\
/\\__/
""",
"""
  11
61 41
61111
""",
"""
 __
/o \\/
\\__/\\
""",
"""
 11
14 16
11116
""",
    ]
    add_fish_entity(anim, *fish_image)


def add_fish_entity(anim, *fish_image):
    fish_image = list(fish_image)
    colors = ['c', 'C', 'r', 'R', 'y', 'Y', 'b', 'B', 'g', 'G', 'm', 'M']
    fish_num = int(random.random() * ((len(fish_image) - 1) / 2))
    fish_index = fish_num * 2
    speed = random.random() * 2 + 0.25
    f_depth = int(random.random() * (depth['fish_end'] - depth['fish_start'])) + depth['fish_start']
    color_mask = fish_image[fish_index + 1]
    color_mask = color_mask.replace('4', 'W')
    color_mask = rand_color(color_mask)
    if fish_num % 2:
        speed *= -1
    fish_object = Entity(
        type='fish',
        shape=fish_image[fish_index],
        auto_trans=1,
        color=color_mask,
        position=[0, 0, f_depth],
        callback=fish_callback,
        callback_args=[speed, 0, 0],
        die_offscreen=1,
        death_cb=add_fish,
        physical=1,
        coll_handler=fish_collision,
    )
    max_height = 9
    min_height = anim.height() - fish_object.HEIGHT
    fish_object.y = int(random.random() * (min_height - max_height)) + max_height
    if fish_num % 2:
        fish_object.x = anim.width() - 2
    else:
        fish_object.x = 1 - fish_object.WIDTH
    anim.add_entity(fish_object)


def fish_callback(fish, anim):
    if int(random.random() * 100) > 97:
        add_bubble(fish, anim)
    return fish.move_entity(anim)


def fish_collision(fish, anim):
    collisions = fish.collisions()
    for col_obj in collisions:
        if col_obj.type == 'teeth' and fish.height <= 5:
            add_splat(anim, *col_obj.position())
            fish.kill()
            break


def add_splat(anim, x, y, z):
    splat_image = [
"""

   .
  ***
   '

""",
"""

 ",*;`
 "*,**
 *"'~'

""",
"""
  , ,
 " ","'
 *" *'"
  " ; .

""",
"""
* ' , ' `
' ` * . '
 ' `' ",'
* ' " * .
" * ', '
""",
    ]
    anim.new_entity(
        shape=splat_image,
        position=[x - 4, y - 2, z - 2],
        default_color='RED',
        callback_args=[0, 0, 0, 0.25],
        transparent=' ',
        die_frame=15,
    )


def add_shark(old_ent, anim):
    shark_image = [
"""
                              __
                             ( `\\
  ,??????????????????????????)   `\\
;' `.????????????????????????(     `\\__
 ;   `.?????????????__..---''          `~~~~-._
  `.   `.____...--''                       (b  `--._
    >                     _.-'      .((      ._     )
  .`.-`--...__         .-'     -.___.....-(|/|/|/|/'
 ;.'?????????`. ...----`.___.',,,_______......---'
 '???????????'-'
""",
"""
                     __
                    /' )
                  /'   (??????????????????????????,
              __/'     )????????????????????????.' `;
      _.-~~~~'          ``---..__?????????????.'   ;
 _.--'  b)                       ``--...____.'   .'
(     _.      )).      `-._                     <
 `\\|\\|\\|\\|)-.....___.-     `-.         __...--'-.'.
   `---......_______,,,`.___.'----... .'?????????`.;
                                      `-`???????????`
""",
    ]
    shark_mask = [
"""




                                           cR

                                          cWWWWWWWW



""",
"""




        Rc

  WWWWWWWWc



""",
    ]
    dir = int(random.random() * 2)
    x = -53
    y = int(random.random() * (anim.height() - (10 + 9))) + 9
    teeth_x = -9
    teeth_y = y + 7
    speed = 2
    if dir:
        speed *= -1
        x = anim.width() - 2
        teeth_x = x + 9
    anim.new_entity(
        type='teeth',
        shape='*',
        position=[teeth_x, teeth_y, depth['shark'] + 1],
        depth=depth['fish_end'] - depth['fish_start'],
        callback_args=[speed, 0, 0],
        physical=1,
    )
    anim.new_entity(
        type='shark',
        color=shark_mask[dir],
        shape=shark_image[dir],
        auto_trans=1,
        position=[x, y, depth['shark']],
        default_color='WHITE',
        callback_args=[speed, 0, 0],
        die_offscreen=1,
        death_cb=shark_death,
    )


def shark_death(shark, anim):
    teeth = anim.get_entities_of_type('teeth')
    for obj in list(teeth):
        anim.del_entity(obj)
    random_object(shark, anim)


def add_ship(old_ent, anim):
    ship_image = [
"""
     |    |    |
    )_)  )_)  )_)
   )___))___))___)\\
  )____)____)_____)\\\\
_____|____|____|____\\\\\\__
\\                   /
""",
"""
         |    |    |
        (_(  (_(  (_(
      /(___((___((___(
    //(_____(____(____(
___///____|____|____|_____
    \\                   /
""",
    ]
    ship_mask = [
"""
     y    y    y

                  w
                   ww
yyyyyyyyyyyyyyyyyyyywwwyy
y                   y
""",
"""
         y    y    y

      w
    ww
yywwwyyyyyyyyyyyyyyyyyyyy
    y                   y
""",
    ]
    dir = int(random.random() * 2)
    x = -24
    speed = 1
    if dir:
        speed *= -1
        x = anim.width() - 2
    anim.new_entity(
        color=ship_mask[dir],
        shape=ship_image[dir],
        auto_trans=1,
        position=[x, 0, depth['water_gap1']],
        default_color='WHITE',
        callback_args=[speed, 0, 0],
        die_offscreen=1,
        death_cb=random_object,
    )


def add_whale(old_ent, anim):
    whale_image = [
"""
        .-----:
      .'       `.
,????/       (o) \\
\\`._/          ,__)
""",
"""
    :-----.
  .'       `.
 / (o)       \\????,
(__,          \\_.'/
""",
    ]
    whale_mask = [
"""
             C C
           CCCCCCC
           C  C  C
        BBBBBBB
      BB       BB
B    B       BWB B
BBBBB          BBBB
""",
"""
   C C
 CCCCCCC
 C  C  C
    BBBBBBB
  BB       BB
 B BWB       B    B
BBBB          BBBBB
""",
    ]
    water_spout = [
"""


   :
""",
"""

   :
   :
""",
"""
  . .
  -:-
   :
""",
"""
  . .
 .-:-.
   :
""",
"""
  . .
'.-:-.`
'  :  '
""",
"""

 .- -.
;  :  ;
""",



"""


;     ;
""",
    ]
    dir = int(random.random() * 2)
    x = None
    speed = 1
    spout_align = None
    whale_anim = []
    whale_anim_mask = []
    if dir:
        spout_align = 1
        speed *= -1
        x = anim.width() - 2
    else:
        spout_align = 11
        x = -18
    for _ in range(1, 6):
        whale_anim.append('\n\n\n' + whale_image[dir])
        whale_anim_mask.append(whale_mask[dir])
    for spout_frame in water_spout:
        whale_frame = whale_image[dir]
        aligned_spout_frame = ('\n' + ' ' * spout_align).join(spout_frame.split('\n'))
        whale_frame = aligned_spout_frame + whale_image[dir]
        whale_anim.append(whale_frame)
        whale_anim_mask.append(whale_mask[dir])
    anim.new_entity(
        color=whale_anim_mask,
        shape=whale_anim,
        auto_trans=1,
        position=[x, 0, depth['water_gap2']],
        default_color='WHITE',
        callback_args=[speed, 0, 0, 1],
        die_offscreen=1,
        death_cb=random_object,
    )


def add_monster(*parm):
    if new_monster:
        add_new_monster(*parm)
    else:
        add_old_monster(*parm)


def add_new_monster(old_ent, anim):
    monster_image = [
        [
"""
         _???_?????????????????????_???_???????_a_a
       _{.`=`.}_??????_???_??????_{.`=`.}_????{/ ''\\_
 _????{.'  _  '.}????{.`'`.}????{.'  _  '.}??{|  ._oo)
{ \\??{/  .'?'.  \\}??{/ .-. \\}??{/  .'?'.  \\}?{/  |
""",
"""
                      _???_????????????????????_a_a
  _??????_???_??????_{.`=`.}_??????_???_??????{/ ''\\_
 { \\????{.`'`.}????{.'  _  '.}????{.`'`.}????{|  ._oo)
  \\ \\??{/ .-. \\}??{/  .'?'.  \\}??{/ .-. \\}???{/  |
""",
        ],
        [
"""
   a_a_???????_???_?????????????????????_???_
 _/'' \\}????_{.`=`.}_??????_???_??????_{.`=`.}_
(oo_.  |}??{.'  _  '.}????{.`'`.}????{.'  _  '.}????_
    |  \\}?{/  .'?'.  \\}??{/ .-. \\}??{/  .'?'.  \\}??/ }
""",
"""
   a_a_????????????????????_   _
 _/'' \\}??????_???_??????_{.`=`.}_??????_???_??????_
(oo_.  |}????{.`'`.}????{.'  _  '.}????{.`'`.}????/ }
    |  \\}???{/ .-. \\}??{/  .'?'.  \\}??{/ .-. \\}??/ /
""",
        ],
    ]
    monster_mask = [
"""                                                W W





""",
"""
   W W




""",
    ]
    dir = int(random.random() * 2)
    x = None
    speed = 2
    if dir:
        speed *= -1
        x = anim.width() - 2
    else:
        x = -54
    monster_anim_mask = []
    for _ in range(1, 3):
        monster_anim_mask.append(monster_mask[dir])
    anim.new_entity(
        shape=monster_image[dir],
        auto_trans=1,
        color=monster_anim_mask,
        position=[x, 2, depth['water_gap2']],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=1,
        default_color='GREEN',
    )


def add_old_monster(old_ent, anim):
    monster_image = [
        [
"""
                                                          ____
            __??????????????????????????????????????????/   o  \\
          /    \\????????_?????????????????????_???????/     ____ >
  _??????|  __  |?????/   \\????????_????????/   \\????|     |
 | \\?????|  ||  |????|     |?????/   \\?????|     |???|     |
""",
"""
                                                          ____
                                             __?????????/   o  \\
             _?????????????????????_???????/    \\?????/     ____ >
   _???????/   \\????????_????????/   \\????|  __  |???|     |
  | \\?????|     |?????/   \\?????|     |???|  ||  |???|     |
""",
"""
                                                          ____
                                  __????????????????????/   o  \\
 _??????????????????????_???????/    \\????????_???????/     ____ >
| \\??????????_????????/   \\????|  __  |?????/   \\????|     |
 \\ \\???????/   \\?????|     |???|  ||  |????|     |???|     |
""",
"""
                                                          ____
                       __???????????????????????????????/   o  \\
  _??????????_???????/    \\????????_??????????????????/     ____ >
 | \\???????/   \\????|  __  |?????/   \\????????_??????|     |
  \\ \\?????|     |???|  ||  |????|     |?????/   \\????|     |
""",
        ],
        [
"""
    ____
  /  o   \\??????????????????????????????????????????__
< ____     \\???????_?????????????????????_????????/    \\
      |     |????/   \\????????_????????/   \\?????|  __  |??????_
      |     |???|     |?????/   \\?????|     |????|  ||  |?????/ |
""",
"""
    ____
  /  o   \\?????????__
< ____     \\?????/    \\???????_?????????????????????_
      |     |???|  __  |????/   \\????????_????????/   \\???????_
      |     |???|  ||  |???|     |?????/   \\?????|     |?????/ |
""",
"""
    ____
  /  o   \\????????????????????__
< ____     \\???????_????????/    \\???????_??????????????????????_
      |     |????/   \\?????|  __  |????/   \\????????_??????????/ |
      |     |???|     |????|  ||  |???|     |?????/   \\???????/ /
""",
"""
    ____
  /  o   \\???????????????????????????????__
< ____     \\??????????????????_????????/    \\???????_??????????_
      |     |??????_????????/   \\?????|  __  |????/   \\???????/ |
      |     |????/   \\?????|     |????|  ||  |???|     |?????/ /
""",
        ],
    ]
    monster_mask = [
"""

                                                            W



""",
"""

     W



""",
    ]
    dir = int(random.random() * 2)
    x = None
    speed = 2
    if dir:
        speed *= -1
        x = anim.width() - 2
    else:
        x = -64
    monster_anim_mask = []
    for _ in range(1, 5):
        monster_anim_mask.append(monster_mask[dir])
    anim.new_entity(
        shape=monster_image[dir],
        auto_trans=1,
        color=monster_anim_mask,
        position=[x, 2, depth['water_gap2']],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=1,
        default_color='GREEN',
    )


def add_big_fish(*parm):
    if new_fish:
        if int(random.random() * 3) > 1:
            add_big_fish_2(*parm)
        else:
            add_big_fish_1(*parm)
    else:
        add_big_fish_1(*parm)


def add_big_fish_1(old_ent, anim):
    big_fish_image = [
"""

 ______
`""-.  `````-----.....__
      `.  .      .       `-.
        :     .     .       `.
 ,?????:   .    .          _ :
: `.???:                  (@) `._
 `. `..'     .     =`-.       .__)
   ;     .        =  ~  :     .-"
 .' .'`.   .    .  =.-'  `._ .'
: .'???:               .   .'
 '???.'  .    .     .   .-'
   .'____....----''.'=.'
   ""?????????????.'.'
               ''"'`
""",
"""
                           ______
          __.....-----'''''  .-""'
       .-'       .      .  .'
     .'       .     .     :
    : _          .    .   :?????,
 _.' (@)                  :???.' :
(__.       .-'=     .     `..' .'
 "-.     :  ~  =        .     ;
   `. _.'  `-.=  .    .   .'`. `.
     `.   .               :???`. :
       `-.   .     .    .  `.???`
          `.=`.``----....____`.
            `.`.?????????????""
              '`"``
""",
    ]
    big_fish_mask = [
"""

 111111
11111  11111111111111111
    11  2      2       111
      1     2     2       11
1     1   2    2          1 1
1 11   1                  1W1 111
11 1111     2     1111       1111
  1     2        1  1  1     111
11 1111   2    2  1111  111 11
1 11   1               2   11
1   11  2    2     2   111
  111111111111111111111
  11             1111
              11111
""",
"""
                           111111
          11111111111111111  11111
       111       2      2  11
     11       2     2     1
    1 1          2    2   1     1
 111 1W1                  1   11 1
1111       1111     2     1111 11
 111     1  1  1        2     1
   11 111  1111  2    2   1111 11
     11   2               1   11 1
       111   2     2    2  11   1
          111111111111111111111
            1111             11
              11111
""",
    ]
    dir = int(random.random() * 2)
    x = None
    speed = 3
    if dir:
        x = anim.width() - 1
        speed *= -1
    else:
        x = -34
    max_height = 9
    min_height = anim.height() - 15
    y = int(random.random() * (min_height - max_height)) + max_height
    color_mask = rand_color(big_fish_mask[dir])
    anim.new_entity(
        shape=big_fish_image[dir],
        auto_trans=1,
        color=color_mask,
        position=[x, y, depth['shark']],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=1,
        default_color='YELLOW',
    )


def add_big_fish_2(old_ent, anim):
    big_fish_image = [
"""
                _ _ _
             .='\\ \\ \\`"=,
           .'\\ \\ \\ \\ \\ \\ \\
\\'=._?????/ \\ \\ \\_\\_\\_\\_\\_\\
\\'=._'.??/\\ \\,-"`- _ - _ - '-.
  \\`=._\\|'.\\/- _ - _ - _ - _- \\
  ;"= ._\\=./_ -_ -_ \\{`"=_    @ \\
   ;="_-_=- _ -  _ - \\{"=_"-     \\
   ;_=_--_.,          \\{_.='   .-/
  ;.="` / ';\\        _.     _.-`
  /_.='/ \\/ /;._ _ _\\{.-;`/"`
/._=_.'???'/ / / / /\\{.= /
/.=' ??????`'./_/_.=`\\{_/
""",
"""
            _ _ _
        ,="`/ / /'=.
       / / / / / / /'.
      /_/_/_/_/_/ / / \\?????_.='/
   .-' - _ - _ -`"-,/ /\\??.'_.='/
  / -_ - _ - _ - _ -\\/.'|/_.=`/
 / @    _="`\} _- _- _\\.=/_. =";
/     -"_="\} - _  - _ -=_-_"=;
\\-.   '=._\}          ,._--_=_;
 `-._     ._        /;' \\ `"=.;
     `"\\`;-.\}_ _ _.;\\ \\/ \\'=._\\
        \\ =.\}\\ \\ \\ \\ \\'???'._=_.\\
         \\_\}`=._\\_\\.'`???????'=.\\
""",
    ]
    big_fish_mask = [
"""

                1 1 1
             1111 1 11111
           111 1 1 1 1 1 1
11111     1 1 1 11111111111
1111111  11 111112 2 2 2 2 111
  111111111112 2 2 2 2 2 2 22 1
  111 1111 12 22 22 11111    W 1
   11111112 2 2  2 2 111111     1
   111111111          11111   111
  11111 11111        11     1111
  111111 11 1111 1 111111111
1111111   11 1 1 1 1111 1
1111       1111111111111
""",
"""
            1 1 1
        11111 1 1111
       1 1 1 1 1 1 111
      11111111111 1 1 1     11111
   111 2 2 2 2 211111 11  1111111
  1 22 2 2 2 2 2 2 211111111111
 1 W    11111 22 22 2111111 111
1     111111 2 2  2 2 21111111
111   11111          111111111
 1111     11        111 1 11111
     111111111 1 1111 11 111111
        1 1111 1 1 1 11   1111111
         1111111111111       1111
""",
    ]
    dir = int(random.random() * 2)
    x = None
    speed = 2.5
    if dir:
        x = anim.width() - 1
        speed *= -1
    else:
        x = -33
    max_height = 9
    min_height = anim.height() - 14
    y = int(random.random() * (min_height - max_height)) + max_height
    color_mask = rand_color(big_fish_mask[dir])
    anim.new_entity(
        shape=big_fish_image[dir],
        auto_trans=1,
        color=color_mask,
        position=[x, y, depth['shark']],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=1,
        default_color='YELLOW',
    )


def init_random_objects():
    return [
        add_ship,
        add_whale,
        add_monster,
        add_big_fish,
        add_shark,
    ]


random_objects = init_random_objects()


def random_object(dead_object, anim):
    sub = int(random.random() * len(random_objects))
    random_objects[sub](dead_object, anim)


def dprint(*args):
    with open('debug', 'a') as D:
        D.write(' '.join(str(a) for a in args) + '\n')


def sighandler(sig, frame):
    if sig == signal.SIGINT:
        quit_prog()
    else:
        quit_prog("Exiting with SIG{}".format(sig))


def quit_prog(mesg=None):
    if mesg is not None:
        sys.stderr.write(mesg + '\n')
    sys.exit(0)


def initialize():
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGABRT]:
        signal.signal(sig, sighandler)


def center(width, mesg):
    l = len(mesg)
    if l < width:
        return ' ' * int((width - len(mesg)) / 2) + mesg
    elif l > width:
        return mesg[:width - l - 3] + "..."
    else:
        return mesg


def rand_color(color_mask):
    colors = ['c', 'C', 'r', 'R', 'y', 'Y', 'b', 'B', 'g', 'G', 'm', 'M']
    for i in range(1, 10):
        color = colors[int(random.random() * (len(colors) - 1))]
        color_mask = color_mask.replace(str(i), color)
    return color_mask


def version_message():
    print("asciiquarium {}".format(version))
    sys.exit(0)


def run(stdscr):
    initialize()
    anim = Animation(stdscr)
    curses.halfdelay(1)
    anim.color(1)
    start_time = time.time()
    paused = 0
    while True:
        add_environment(anim)
        add_castle(anim)
        add_all_seaweed(anim)
        add_all_fish(anim)
        random_object(None, anim)
        anim.redraw_screen()
        nexttime = 0
        while True:
            try:
                in_char = stdscr.getch()
            except Exception:
                in_char = -1
            if in_char != -1:
                in_char = chr(in_char).lower()
            else:
                in_char = ''
            if in_char == 'q':
                quit_prog()
            elif in_char == 'r':
                break
            elif in_char == 'p':
                paused = not paused
            if not paused:
                anim.animate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='classic mode')
    parser.add_argument('--version', action='version', version='asciiquarium {}'.format(version))
    args = parser.parse_args()
    global new_fish, new_monster
    if args.c:
        new_fish = 0
        new_monster = 0
    curses.wrapper(run)


if __name__ == '__main__':
    main()
