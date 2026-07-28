#!/usr/bin/env python3
"""
Asciiquarium - An aquarium animation in ASCII art
Python translation of the Perl original by Kirk Baucom.
"""

import sys
import os
import time
import random
import curses
import signal

VERSION = "1.1"

COLOR_MAP = {
    'c': curses.COLOR_CYAN,
    'C': curses.COLOR_CYAN,
    'r': curses.COLOR_RED,
    'R': curses.COLOR_RED,
    'y': curses.COLOR_YELLOW,
    'Y': curses.COLOR_YELLOW,
    'b': curses.COLOR_BLUE,
    'B': curses.COLOR_BLUE,
    'g': curses.COLOR_GREEN,
    'G': curses.COLOR_GREEN,
    'm': curses.COLOR_MAGENTA,
    'M': curses.COLOR_MAGENTA,
    'w': curses.COLOR_WHITE,
    'W': curses.COLOR_WHITE,
}

COLOR_NAMES = ['c', 'C', 'r', 'R', 'y', 'Y', 'b', 'B', 'g', 'G', 'm', 'M']
COLOR_PAIRS = {}
_next_pair = 1

def get_color_pair(fg_char):
    global _next_pair
    if fg_char not in COLOR_PAIRS:
        fg = COLOR_MAP.get(fg_char, curses.COLOR_WHITE)
        curses.init_pair(_next_pair, fg, 0)
        COLOR_PAIRS[fg_char] = _next_pair
        _next_pair += 1
    return curses.color_pair(COLOR_PAIRS[fg_char])


class Entity:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', '')
        self.shape = kwargs.get('shape', '')
        self.position = list(kwargs.get('position', [0, 0, 0]))
        self.default_color = kwargs.get('default_color', 'WHITE')
        self.color_mask = kwargs.get('color', None)
        self.callback = kwargs.get('callback', None)
        self.callback_args = list(kwargs.get('callback_args', [])) if kwargs.get('callback_args') else []
        self.die_time = kwargs.get('die_time', None)
        self.die_offscreen = kwargs.get('die_offscreen', False)
        self.die_frame = kwargs.get('die_frame', None)
        self.death_cb = kwargs.get('death_cb', None)
        self.physical = kwargs.get('physical', False)
        self.coll_handler = kwargs.get('coll_handler', None)
        self.auto_trans = kwargs.get('auto_trans', False)
        self.transparent = kwargs.get('transparent', None)
        self.depth_val = kwargs.get('depth', 0)
        self.alive = True
        self.frame = 0
        self.frame_acc = 0.0
        self.width = 0
        self.height = 0
        self._parse_shape()
        self.X = self.position[0]
        self.Y = self.position[1]
        self.WIDTH = self.width
        self.HEIGHT = self.height

    def _parse_shape(self):
        if isinstance(self.shape, list):
            first = self.shape[0] if self.shape else ''
            lines = first.split('\n')
            self.width = max(len(l) for l in lines) if lines else 0
            self.height = len(lines)
        elif isinstance(self.shape, str):
            lines = self.shape.split('\n')
            self.width = max(len(l) for l in lines) if lines else 0
            self.height = len(lines)
        else:
            self.width = 0
            self.height = 0

    def get_shape_lines(self):
        if isinstance(self.shape, list):
            idx = min(self.frame, len(self.shape) - 1)
            return self.shape[idx].split('\n')
        elif isinstance(self.shape, str):
            return self.shape.split('\n')
        return []

    def get_mask_lines(self):
        if self.color_mask is None:
            return None
        if isinstance(self.color_mask, list):
            idx = min(self.frame, len(self.color_mask) - 1)
            return self.color_mask[idx].split('\n')
        elif isinstance(self.color_mask, str):
            return self.color_mask.split('\n')
        return None

    def position_tuple(self):
        return (self.position[0], self.position[1], self.position[2])

    def size(self):
        return (self.width, self.height)

    def kill(self):
        self.alive = False

    def move_entity(self, anim):
        args = self.callback_args
        if len(args) >= 2:
            dx = args[0] if args[0] is not None else 0
            dy = args[1] if args[1] is not None else 0
        else:
            dx = 0
            dy = 0

        anim_speed = args[3] if len(args) > 3 else 0

        if dx != 0 or dy != 0:
            self.position[0] += dx
            self.position[1] += dy
            self.X = self.position[0]
            self.Y = self.position[1]

        if anim_speed > 0 and isinstance(self.shape, list) and len(self.shape) > 1:
            self.frame_acc += anim_speed
            while self.frame_acc >= 1.0:
                self.frame_acc -= 1.0
                self.frame = (self.frame + 1) % len(self.shape)

        if self.die_offscreen:
            if self.position[0] + self.width < 0 or self.position[0] > anim.width:
                self.kill()
            if self.position[1] + self.height < 0 or self.position[1] > anim.height:
                self.kill()

        if self.die_frame is not None:
            self.die_frame -= 1
            if self.die_frame <= 0:
                self.kill()

        return 1


class Animation:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self._entities = []
        self._color_enabled = True
        self.width = 0
        self.height = 0
        self.frame_count = 0
        self._update_term_size()
        curses.curs_set(0)

    def _update_term_size(self):
        self.height, self.width = self.stdscr.getmaxyx()

    def update_term_size(self):
        self._update_term_size()

    def color(self, val):
        self._color_enabled = val

    def new_entity(self, **kwargs):
        ent = Entity(**kwargs)
        self._entities.append(ent)
        return ent

    def add_entity(self, entity):
        self._entities.append(entity)

    def remove_all_entities(self):
        self._entities = []

    def del_entity(self, entity):
        if entity in self._entities:
            self._entities.remove(entity)

    def get_entities_of_type(self, etype):
        return [e for e in self._entities if e.type == etype]

    def _render_entity(self, ent):
        if not ent.alive:
            return
        lines = ent.get_shape_lines()
        mask_lines = ent.get_mask_lines()
        x = int(round(ent.position[0]))
        y = int(round(ent.position[1]))
        default_color = ent.default_color
        transparent = ent.transparent
        sh, sw = self.height, self.width

        for row_idx, line in enumerate(lines):
            screen_y = y + row_idx
            if screen_y < 0 or screen_y >= sh:
                continue
            mask_row = mask_lines[row_idx] if mask_lines and row_idx < len(mask_lines) else ''
            for col_idx, ch in enumerate(line):
                screen_x = x + col_idx
                if screen_x < 0 or screen_x >= sw:
                    continue
                if transparent and ch == transparent:
                    continue
                if ch == ' ' or ch == '\r':
                    continue
                if mask_row and col_idx < len(mask_row) and mask_row[col_idx] != ' ':
                    mask_ch = mask_row[col_idx]
                    if mask_ch in COLOR_MAP:
                        pair = get_color_pair(mask_ch)
                        self.stdscr.addch(screen_y, screen_x, ch, pair)
                    else:
                        self.stdscr.addch(screen_y, screen_x, ch)
                else:
                    if default_color and default_color in COLOR_MAP:
                        pair = get_color_pair(default_color[0].lower() if default_color.isupper() else default_color[0])
                        self.stdscr.addch(screen_y, screen_x, ch, pair)
                    else:
                        pair = get_color_pair('W')
                        self.stdscr.addch(screen_y, screen_x, ch, pair)

    def redraw_screen(self):
        self.stdscr.erase()
        self._render_all()
        self.stdscr.refresh()

    def _render_all(self):
        sorted_ents = sorted([e for e in self._entities if e.alive],
                             key=lambda e: e.position[2] if len(e.position) > 2 else 0)
        for ent in sorted_ents:
            self._render_entity(ent)

    def animate(self):
        self.frame_count += 1
        dead = []
        for ent in self._entities:
            if not ent.alive:
                dead.append(ent)
                continue
            if ent.callback:
                ent.callback(ent, self)
            elif ent.callback_args:
                ent.move_entity(self)
            if ent.die_time and time.time() >= ent.die_time:
                ent.kill()
            if not ent.alive:
                dead.append(ent)
        for ent in dead:
            if ent.death_cb:
                ent.death_cb(ent, self)
        self._entities = [e for e in self._entities if e.alive]
        self.stdscr.erase()
        self._render_all()
        self.stdscr.refresh()


new_fish = True
new_monster = True

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


def rand_color(color_mask):
    colors = ['c', 'C', 'r', 'R', 'y', 'Y', 'b', 'B', 'g', 'G', 'm', 'M']
    result = ''
    for ch in color_mask:
        if ch.isdigit() and '1' <= ch <= '9':
            result += random.choice(colors)
        else:
            result += ch
    return result


def add_environment(anim):
    water_line_segment = [
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',
        '^^^^ ^^^  ^^^   ^^^    ^^^^      ',
        '^^^^      ^^^^     ^^^    ^^     ',
        '^^      ^^^^      ^^^    ^^^^^^  '
    ]
    segment_size = len(water_line_segment[0])
    segment_repeat = int(anim.width / segment_size) + 1
    for i in range(len(water_line_segment)):
        water_line_segment[i] = water_line_segment[i] * segment_repeat
    for i in range(len(water_line_segment)):
        anim.new_entity(
            name="water_seg_{}".format(i),
            type="waterline",
            shape=water_line_segment[i],
            position=[0, i + 5, depth['water_line{}'.format(i)]],
            default_color='CYAN',
            depth=22,
            physical=True,
        )


def add_castle(anim):
    castle_image = """
               T~~
               |
              /^\\
             /   \\
 _   _   _  /     \\  _   _   _
[ ]_[ ]_[ ]/ _   _ \[ ]_[ ]_[ ]
|_=__-_ =_|_[ ]_[ ]_|_=-___-__|
 | _- =  | =_ = _    |= _=   |
 |= -[]  |- = _ =    |_-=_[] |
 | =_    |= - ___    | =_ =  |
|=  []- |-  /| |\\   |=_ =[] |
|- =_   | =| | | |  |- = -  |
|_______|__|_|_|_|__|_______|"""

    castle_mask = """
                RR

              yyy
             y   y
            y     y
           y       y



              yyy
             yy yy
            y y y y
            yyyyyyy"""

    anim.new_entity(
        name="castle",
        shape=castle_image,
        color=castle_mask,
        position=[anim.width - 32, anim.height - 13, depth['castle']],
        default_color='BLACK',
    )


def add_all_seaweed(anim):
    seaweed_count = int(anim.width / 15)
    for _ in range(seaweed_count):
        add_seaweed(None, anim)


def add_seaweed(old_seaweed, anim):
    seaweed_image = ['', '']
    height = int(random.random() * 4) + 3
    for i in range(1, height + 1):
        left_side = i % 2
        right_side = 1 - left_side
        seaweed_image[left_side] += "(\n"
        seaweed_image[right_side] += " )\n"
    x = int(random.random() * (anim.width - 2)) + 1
    y = anim.height - height
    anim_speed = random.random() * 0.05 + 0.25
    anim.new_entity(
        name='seaweed{}'.format(random.random()),
        shape=seaweed_image,
        position=[x, y, depth['seaweed']],
        callback_args=[0, 0, 0, anim_speed],
        die_time=time.time() + int(random.random() * 4 * 60) + (8 * 60),
        death_cb=add_seaweed,
        default_color='green',
    )


def add_bubble(fish, anim):
    cb_args = fish.callback_args
    fish_size = fish.size()
    fish_pos = fish.position
    bubble_pos = list(fish_pos)
    if cb_args and len(cb_args) > 0 and cb_args[0] > 0:
        bubble_pos[0] += fish_size[0]
    bubble_pos[1] += int(fish_size[1] / 2)
    bubble_pos[2] -= 1
    anim.new_entity(
        shape=['.', 'o', 'O', 'O', 'O'],
        type='bubble',
        position=bubble_pos,
        callback_args=[0, -1, 0, 0.1],
        die_offscreen=True,
        physical=True,
        coll_handler=bubble_collision,
        default_color='CYAN',
    )


def bubble_collision(bubble, anim):
    for col_obj in anim._entities:
        if col_obj.alive and col_obj.type == 'waterline':
            if _check_collision(bubble, col_obj):
                bubble.kill()
                return


def _check_collision(a, b):
    ax = int(round(a.position[0]))
    ay = int(round(a.position[1]))
    aw = a.width
    ah = a.height
    bx = int(round(b.position[0]))
    by = int(round(b.position[1]))
    bw = b.width
    bh = b.height
    if ax + aw <= bx or bx + bw <= ax:
        return False
    if ay + ah <= by or by + bh <= ay:
        return False
    return True


def add_all_fish(anim):
    screen_size = (anim.height - 9) * anim.width
    fish_count = int(screen_size / 350)
    for _ in range(fish_count):
        add_fish(None, anim)


def add_fish(old_fish, anim):
    if new_fish:
        if int(random.random() * 12) > 8:
            add_new_fish(old_fish, anim)
        else:
            add_old_fish(old_fish, anim)
    else:
        add_old_fish(old_fish, anim)


def add_new_fish(old_fish, anim):
    fish_images = [
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
      }\\
\\  .'  `\\
}}<   ( 6>
/  `,  .'
      }/
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
   {/
 /'  `.  /
<6 )   >{{
 `.  ,'  \\
   \\{
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
            \\'`.
             )  \\
(`.??????_.-`' ' '`-.
 \\ `.??.`        (o) \\_
  >  ><     (((       (
 / .`??`._      /_|  /'
(.`???????`-. _  _.-`
            /__/

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
        `"--(/"`
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
 `"\\)--"`
""",
"""
    22222
 112111121    66
14 77     1116 6
1  77    1111666
 11331111
""",
    ]
    add_fish_entity(anim, fish_images)


def add_old_fish(old_fish, anim):
    fish_images = [
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
  \\\\\\;;:::::::o
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
    add_fish_entity(anim, fish_images)


def add_fish_entity(anim, fish_images):
    colors = ['c', 'C', 'r', 'R', 'y', 'Y', 'b', 'B', 'g', 'G', 'm', 'M']
    fish_num = int(random.random() * (len(fish_images) // 2))
    fish_index = fish_num * 2
    speed = random.random() * 2 + 0.25
    fish_depth = int(random.random() * (depth['fish_end'] - depth['fish_start'])) + depth['fish_start']
    color_mask = fish_images[fish_index + 1]
    color_mask = color_mask.replace('4', 'W')
    color_mask = rand_color(color_mask)

    if fish_num % 2:
        speed *= -1

    fish_obj = Entity(
        type='fish',
        shape=fish_images[fish_index],
        auto_trans=True,
        color=color_mask,
        position=[0, 0, fish_depth],
        callback=fish_callback,
        callback_args=[speed, 0, 0],
        die_offscreen=True,
        death_cb=add_fish,
        physical=True,
        coll_handler=fish_collision,
    )

    max_height = 9
    min_height = anim.height - fish_obj.HEIGHT
    fish_obj.Y = int(random.random() * (min_height - max_height)) + max_height
    fish_obj.position[1] = fish_obj.Y
    if fish_num % 2:
        fish_obj.X = anim.width - 2
    else:
        fish_obj.X = 1 - fish_obj.WIDTH
    fish_obj.position[0] = fish_obj.X
    anim.add_entity(fish_obj)


def fish_callback(fish, anim):
    if int(random.random() * 100) > 97:
        add_bubble(fish, anim)
    return fish.move_entity(anim)


def fish_collision(fish, anim):
    for col_obj in anim._entities:
        if col_obj.alive and col_obj.type == 'teeth' and fish.HEIGHT <= 5:
            if _check_collision(fish, col_obj):
                add_splat(anim, col_obj.position[0], col_obj.position[1], col_obj.position[2])
                fish.kill()
                return


def add_splat(anim, x, y, z):
    splat_images = [
        """

   .
  ***
   '
""",
        """

 ",*;`
 "*,**
 *\"'~'
""",
        """
  , ,
 " ","'
 *\" *'\"
  \" ; .
""",
        """* ' , ' `
' ` * . '
 ' `' \",'
* ' \" * .
\" * ', '
"""
    ]
    anim.new_entity(
        shape=splat_images,
        position=[x - 4, y - 2, z - 2],
        default_color='RED',
        callback_args=[0, 0, 0, 0.25],
        transparent=' ',
        die_frame=15,
    )


def add_shark(old_ent, anim):
    shark_images = [
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
 '???????????'-'""",
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
                                      `-`???????????`"""
    ]

    shark_masks = [
        """




                                           cR

                                          cWWWWWWWW


""",
        """




        Rc

  WWWWWWWWc


"""
    ]

    dir_val = int(random.random() * 2)
    x = -53
    y = int(random.random() * (anim.height - (10 + 9))) + 9
    teeth_x = -9
    teeth_y = y + 7
    speed = 2
    if dir_val:
        speed *= -1
        x = anim.width - 2
        teeth_x = x + 9

    anim.new_entity(
        type='teeth',
        shape='*',
        position=[teeth_x, teeth_y, depth['shark'] + 1],
        depth=depth['fish_end'] - depth['fish_start'],
        callback_args=[speed, 0, 0],
        physical=True,
    )

    anim.new_entity(
        type='shark',
        color=shark_masks[dir_val],
        shape=shark_images[dir_val],
        position=[x, y, depth['shark']],
        default_color='CYAN',
        callback_args=[speed, 0, 0],
        die_offscreen=True,
        death_cb=shark_death,
    )


def shark_death(shark, anim):
    teeth_list = anim.get_entities_of_type('teeth')
    for obj in teeth_list:
        anim.del_entity(obj)
    random_object(shark, anim)


def add_ship(old_ent, anim):
    ship_images = [
        """
     |    |    |
    )_)  )_)  )_)
   )___))___))___)\\
  )____)____)_____)\\\\
_____|____|____|____\\\\\\__
\\                   /""",
        """
         |    |    |
        (_(  (_(  (_(
      /(___((___((___(
    //(_____(____(____(
__///____|____|____|_____
    \\                   /"""
    ]

    ship_masks = [
        """
     y    y    y

                  w
                   ww
yyyyyyyyyyyyyyyyyyyywwwyy
y                   y""",
        """
         y    y    y

      w
    ww
yywwwyyyyyyyyyyyyyyyyyyyy
    y                   y"""
    ]

    dir_val = int(random.random() * 2)
    x = -24
    speed = 1
    if dir_val:
        speed *= -1
        x = anim.width - 2

    anim.new_entity(
        color=ship_masks[dir_val],
        shape=ship_images[dir_val],
        position=[x, 0, depth['water_gap1']],
        default_color='WHITE',
        callback_args=[speed, 0, 0],
        die_offscreen=True,
        death_cb=random_object,
    )


def add_whale(old_ent, anim):
    whale_images = [
        """
        .-----:
      .'       `.
,????/       (o) \\
\\`._/          ,__)""",
        """
    :-----.
  .'       `.
 / (o)       \\????,
(__,          \\_.'/"""
    ]

    whale_masks = [
        """
             C C
           CCCCCCC
           C  C  C
        BBBBBBB
      BB       BB
B    B       BWB B
BBBBB          BBBB""",
        """
   C C
 CCCCCCC
 C  C  C
    BBBBBBB
  BB       BB
 B BWB       B    B
BBBB          BBBBB"""
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



;     ;"""
    ]

    dir_val = int(random.random() * 2)
    speed = 1
    spout_align = 1
    if dir_val:
        speed *= -1
        x = anim.width - 2
        spout_align = 1
    else:
        spout_align = 11
        x = -18

    whale_anim = []
    whale_anim_mask = []
    for _ in range(5):
        whale_anim.append("\n\n\n" + whale_images[dir_val])
        whale_anim_mask.append(whale_masks[dir_val])

    for spout_frame in water_spout:
        whale_frame = whale_images[dir_val]
        spout_lines = spout_frame.split('\n')
        aligned_lines = []
        for line in spout_lines:
            aligned_lines.append(' ' * spout_align + line)
        aligned_spout_frame = '\n'.join(aligned_lines)
        whale_frame = aligned_spout_frame + whale_images[dir_val]
        whale_anim.append(whale_frame)
        whale_anim_mask.append(whale_masks[dir_val])

    anim.new_entity(
        color=whale_anim_mask,
        shape=whale_anim,
        position=[x, 0, depth['water_gap2']],
        default_color='WHITE',
        callback_args=[speed, 0, 0, 1],
        die_offscreen=True,
        death_cb=random_object,
    )


def add_monster(old_ent, anim):
    if new_monster:
        add_new_monster(old_ent, anim)
    else:
        add_old_monster(old_ent, anim)


def add_new_monster(old_ent, anim):
    monster_images = [
        [
"""
         _???_?????????????????????_???_???????_a_a
       _{.`=`.}_??????_???_??????_{.`=`.}_????{/ ''\\_
 _????{.'  _  '.}????{.`'`.}????{.'  _  '.}??{|  ._oo)
{ \\??{/  .'?'.  \\}??{/ .-. \\}??{/  .'?'.  \\}?{/  |""",
"""
                       _???_????????????????????_a_a
  _??????_???_??????_{.`=`.}_??????_???_??????{/ ''\\_
 { \\????{.`'`.}????{.'  _  '.}????{.`'`.}????{|  ._oo)
  \\ \\??{/ .-. \\}??{/  .'?'.  \\}??{/ .-. \\}???{/  |"""
        ],
        [
"""
   a_a_???????_???_?????????????????????_???_
 _/'' \\}????_{.`=`.}_??????_???_??????_{.`=`.}_
(oo_.  |}??{.'  _  '.}????{.`'`.}????{.'  _  '.}????_
    |  \\}?{/  .'?'.  \\}??{/ .-. \\}??{/  .'?'.  \\}??/ }""",
"""
   a_a_????????????????????_   _
 _/'' \\}??????_???_??????_{.`=`.}_??????_???_??????_
(oo_.  |}????{.`'`.}????{.'  _  '.}????{.`'`.}????/ }
    |  \\}???{/ .-. \\}??{/  .'?'.  \\}??{/ .-. \\}??/ /"""
        ]
    ]

    monster_masks = [
        """                                                W W

""",
        """   W W

"""
    ]

    dir_val = int(random.random() * 2)
    speed = 2
    if dir_val:
        speed *= -1
        x = anim.width - 2
    else:
        x = -54

    monster_anim_mask = []
    for _ in range(2):
        monster_anim_mask.append(monster_masks[dir_val])

    anim.new_entity(
        shape=monster_images[dir_val],
        color=monster_anim_mask,
        position=[x, 2, depth['water_gap2']],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color='GREEN',
    )


def add_old_monster(old_ent, anim):
    monster_images = [
        [
"""
                                                          ____
            __??????????????????????????????????????????/   o  \\
          /    \\????????_?????????????????????_???????/     ____ >
  _??????|  __  |?????/   \\????????_????????/   \\????|     |
 | \\?????|  ||  |????|     |?????/   \\?????|     |???|     |""",
"""
                                                          ____
                                             __?????????/   o  \\
             _?????????????????????_???????/    \\?????/     ____ >
   _???????/   \\????????_????????/   \\????|  __  |???|     |
  | \\?????|     |?????/   \\?????|     |???|  ||  |???|     |""",
"""
                                                          ____
                                  __????????????????????/   o  \\
 _??????????????????????_???????/    \\????????_???????/     ____ >
| \\??????????_????????/   \\????|  __  |?????/   \\????|     |
 \\ \\???????/   \\?????|     |???|  ||  |????|     |???|     |""",
"""
                                                          ____
                       __???????????????????????????????/   o  \\
  _??????????_???????/    \\????????_??????????????????/     ____ >
 | \\???????/   \\????|  __  |?????/   \\????????_??????|     |
  \\ \\?????|     |???|  ||  |????|     |?????/   \\????|     |"""
        ],
        [
"""
    ____
  /  o   \\??????????????????????????????????????????__
< ____     \\???????_?????????????????????_????????/    \\
      |     |????/   \\????????_????????/   \\?????|  __  |??????_
      |     |???|     |?????/   \\?????|     |????|  ||  |?????/ |""",
"""
    ____
  /  o   \\?????????__
< ____     \\?????/    \\???????_?????????????????????_
      |     |???|  __  |????/   \\????????_????????/   \\???????_
      |     |???|  ||  |???|     |?????/   \\?????|     |?????/ |""",
"""
    ____
  /  o   \\????????????????????__
< ____     \\???????_????????/    \\???????_??????????????????????_
      |     |????/   \\?????|  __  |????/   \\????????_??????????/ |
      |     |???|     |????|  ||  |???|     |?????/   \\???????/ /""",
"""
    ____
  /  o   \\???????????????????????????????__
< ____     \\??????????????????_????????/    \\???????_??????????_
      |     |??????_????????/   \\?????|  __  |????/   \\???????/ |
      |     |????/   \\?????|     |????|  ||  |???|     |?????/ /"""
        ]
    ]

    monster_masks = [
        """

                                                            W


""",
        """

     W


"""
    ]

    dir_val = int(random.random() * 2)
    speed = 2
    if dir_val:
        speed *= -1
        x = anim.width - 2
    else:
        x = -64

    monster_anim_mask = []
    for _ in range(4):
        monster_anim_mask.append(monster_masks[dir_val])

    anim.new_entity(
        shape=monster_images[dir_val],
        color=monster_anim_mask,
        position=[x, 2, depth['water_gap2']],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color='GREEN',
    )


def add_big_fish(old_ent, anim):
    if new_fish:
        if int(random.random() * 3) > 1:
            add_big_fish_2(old_ent, anim)
        else:
            add_big_fish_1(old_ent, anim)
    else:
        add_big_fish_1(old_ent, anim)


def add_big_fish_1(old_ent, anim):
    big_fish_images = [
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
               ''"'`""",
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
              '`"``"""
    ]

    big_fish_masks = [
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
               11111""",
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
              11111"""
    ]

    dir_val = int(random.random() * 2)
    speed = 3
    if dir_val:
        x = anim.width - 1
        speed *= -1
    else:
        x = -34
    max_height = 9
    min_height = anim.height - 15
    y = int(random.random() * (min_height - max_height)) + max_height
    color_mask = rand_color(big_fish_masks[dir_val])

    anim.new_entity(
        shape=big_fish_images[dir_val],
        color=color_mask,
        position=[x, y, depth['shark']],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=True,
        default_color='YELLOW',
    )


def add_big_fish_2(old_ent, anim):
    big_fish_images = [
        """
                _ _ _
             .='\\ \\ \\`"=,
           .'\\ \\ \\ \\ \\ \\ \\
\\'=._?????/ \\ \\ \\_\\_\\_\\_\\_\\
\\'=._'.??/\\ \\,-"`- _ - _ - '-.
  \\`=._\\|'.\\/- _ - _ - _ - _- \\
  ;"= ._\\=./_ -_ -_ {`"=_    @ \\
   ;="_-_=- _ -  _ - {"=_"-     \\
   ;_=_--_.,          {_.='   .-/
  ;.="` / ';\\        _.     _.-`
  /_.='/ \\/ /;._ _ _{.-;`/""
/._=_.'???'/ / / / /{.= /
/.=' ??????`'./_/_.=`{_/""",
        """
            _ _ _
        ,="`/ / /'=.
       / / / / / / /'.
      /_/_/_/_/_/ / / \\?????_.='/
   .-' - _ - _ -`"-,/ /\\??.'_.='/
  / -_ - _ - _ - _ -\\/.'|/_.=`/
 / @    _="`} _- _- _\\.=/_. =";
/     -"_="} - _  - _ -=_-_"=;
\\-.   '=._}          ,._--_=_;
 `-._     ._        /;' \\ `"=.;
     `"\\`;-.}_ _ _.;\\ \\/ \\'=._\\
        \\ =.}\\ \\ \\ \\ \\'???'._=_.\\
         \\_}`=._\\_\\.'`???????'=.\\"""
    ]

    big_fish_masks = [
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
1111       1111111111111""",
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
         1111111111111       1111"""
    ]

    dir_val = int(random.random() * 2)
    speed = 2.5
    if dir_val:
        x = anim.width - 1
        speed *= -1
    else:
        x = -33
    max_height = 9
    min_height = anim.height - 14
    y = int(random.random() * (min_height - max_height)) + max_height
    color_mask = rand_color(big_fish_masks[dir_val])

    anim.new_entity(
        shape=big_fish_images[dir_val],
        color=color_mask,
        position=[x, y, depth['shark']],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=True,
        default_color='YELLOW',
    )


random_object_funcs = []


def init_random_objects():
    global random_object_funcs
    random_object_funcs = [
        add_ship,
        add_whale,
        add_monster,
        add_big_fish,
        add_shark,
    ]
    return random_object_funcs


def random_object(dead_object, anim):
    sub = int(random.random() * len(random_object_funcs))
    random_object_funcs[sub](dead_object, anim)


def quit_program(mesg=None):
    if mesg:
        print(mesg, file=sys.stderr)
    sys.exit(0)


def main(stdscr):
    global new_fish, new_monster

    new_fish = True
    new_monster = True

    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c')
    except getopt.GetoptError:
        opts = []

    for opt, val in opts:
        if opt == '-c':
            new_fish = False
            new_monster = False

    init_random_objects()

    anim = Animation(stdscr)
    anim.color(1)

    start_time = time.time()
    paused = False

    while True:
        add_environment(anim)
        add_castle(anim)
        add_all_seaweed(anim)
        add_all_fish(anim)
        random_object(None, anim)

        anim.redraw_screen()

        inner_loop = True
        while inner_loop:
            stdscr.timeout(100)
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                quit_program()

            if key != -1:
                ch = chr(key).lower()
                if ch == 'q':
                    quit_program()
                elif ch == 'r':
                    inner_loop = False
                elif ch == 'p':
                    paused = not paused

            if not paused:
                anim.animate()

        anim.update_term_size()
        anim.remove_all_entities()


if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        quit_program()