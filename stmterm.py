# Squarified treemap generator for the terminal
# Samuel Bauman 2021
# Based on https://www.win.tue.nl/~vanwijk/stm.pdf

import curses
import time
import sys

vertical_shrink = 2


def get_term_size(stdscr):
    global term_size_x, term_size_y
    term_size_y, term_size_x = stdscr.getmaxyx()


def worst(item, items_sum, row_sum, bounds):
    row_sum += item
    if bounds[2] > (bounds[3] * vertical_shrink):
        width = max((row_sum / (row_sum + items_sum)) * bounds[2], 1)
        height = max((item / row_sum) * bounds[3], 1)
        result = width / (height * vertical_shrink)
    else:
        width = max((item / row_sum) * bounds[2], 1)
        height = max((row_sum / (row_sum + items_sum)) * bounds[3], 1)
        result = (height * vertical_shrink) / width
    return abs(result - 1.0)


def squarify(stdscr, items, row, bounds, row_names, names):
    row_sum = sum(row)
    items_sum = sum(items)
    item_size = items.pop(0)
    item_name = names.pop(0)
    vertical = bounds[2] > (bounds[3] * vertical_shrink)
    shrink = round((row_sum / (row_sum + items_sum)) *
            (bounds[2] if vertical else bounds[3]))

    if vertical:
        next_row_bounds = [bounds[0] + shrink, bounds[1],
                bounds[2] - shrink, bounds[3]]
    else:
        next_row_bounds = [bounds[0], bounds[1] + shrink,
                bounds[2], bounds[3] - shrink]

    existing_row = worst(item_size, items_sum, row_sum, bounds)
    next_row = worst(item_size, max(items_sum - row_sum, 0), 0,
            next_row_bounds)
    add_to_next_row = existing_row > next_row

    if add_to_next_row:
        draw_row(stdscr, items_sum, row, bounds, row_names)
        row.clear()
        row_names.clear()

    row.append(item_size)
    row_names.append(item_name)

    if items:
        squarify(stdscr, items, row,
                next_row_bounds if add_to_next_row else bounds, row_names,
                names)
    else:
        draw_row(stdscr, 0, row, next_row_bounds if len(row) == 1 else bounds,
                row_names)


def draw_row(stdscr, items_sum, row, bounds, row_names):
    pos = 0
    row_sum = sum(row)
    bounds = list(map(round,bounds))
    vertical = bounds[2] > (bounds[3] * vertical_shrink)
    row_width = (row_sum / (row_sum + items_sum)) * (bounds[2] if vertical else
            bounds[3])

    for i in range(len(row)):
        if vertical:
            rect = [bounds[0],
                    bounds[1] + pos,
                    row_width,
                    (row[i] / row_sum) * (bounds[3] - pos)]
        else:
            rect = [bounds[0] + pos,
                    bounds[1],
                    (row[i] / row_sum) * (bounds[2] - pos),
                    row_width]
        row_sum = row_sum - row[i]
        rect = [round(n) for n in rect]
        draw_rectangle(stdscr, rect, row_names[i])
        pos = pos + (rect[3] if vertical else rect[2])


def draw_rectangle(stdscr, b, s):
    stdscr.hline(b[1], b[0], curses.ACS_HLINE, b[2] - 1)
    stdscr.hline(b[1] + b[3] - 1, b[0], curses.ACS_HLINE, b[2] - 1)
    stdscr.vline(b[1], b[0], curses.ACS_VLINE, b[3] - 1)
    stdscr.vline(b[1], b[0] + b[2] - 1, curses.ACS_VLINE, b[3] - 1)
    stdscr.addch(b[1], b[0], curses.ACS_ULCORNER)
    stdscr.addch(b[1], b[0] + b[2] - 1, curses.ACS_URCORNER)
    stdscr.addch(b[1] + b[3] - 1, b[0], curses.ACS_LLCORNER)
    stdscr.addch(b[1] + b[3] - 1, b[0] + b[2] - 1, curses.ACS_LRCORNER)
    if s:
        try:
            stdscr.addstr(b[1], b[0] + 1, s);
        except:
            pass


def display_squarified_treemap(stdscr, items, names):
    if items:
        squarify(
            stdscr      = stdscr,
            items       = items,
            row         = [],
            bounds      = [0, 0, term_size_x-1, term_size_y-1],
            row_names   = [],
            names       = names
            )


def main(stdscr):
    global term_size_x, term_size_y
    curses.use_default_colors()
    get_term_size(stdscr)
    stdscr.clear()
    items, names = [], []
    if not sys.stdin.isatty():
        input_stream = sys.stdin
        for line in input_stream:
            item, name = line.rstrip("\n").split("\t")
            if (int(item) > 0):
                items.append(int(item))
                names.append(str(name))
        if items:
            char_size = sum(items) / (term_size_x * term_size_y)
            for i in range(len(items)):
                if items[i] < (char_size * 4):
                    items[i], names[i] = sum(items[i:]), "s"
                    items = items[:i+1]
                    break
    else:
        items = [6, 6, 4, 3, 2, 2, 1]
        names = ["six_1","six_2","four","three","two_1","two_2","one"]

    display_squarified_treemap(stdscr, items, names)
    stdscr.refresh()
    time.sleep(4)


curses.wrapper(main)
