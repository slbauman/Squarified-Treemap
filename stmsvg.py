# Squarified treemap SVG generator
# Samuel Bauman 2021
# Based on https://www.win.tue.nl/~vanwijk/stm.pdf
#
# Run the following command to generate a SVG squarified treemap of the working
# directory and subfolders:
#
# du -abd4 | python /path/to/stmsvg.py > /path/to/out.svg
#
# If python crashes due to exceeding the recursion depth, uncomment the two 
# following lines:
# import sys
# sys.setrecursionlimit(10000)

import fileinput

svg_width = 1800
svg_height = 900

dir_fill_colors = ["#EF476F", "#FFD166", "#05D6A0", "#118AB2"]


def worst(item, items_sum, row_sum, bounds):
    w = (row_sum / (row_sum + items_sum)) * max(bounds[3], bounds[2])
    h = (item / row_sum) * min(bounds[3], bounds[2])
    return abs((w / h) - 1.0)


def squarify(items, row, bounds, row_names, names, result = []):
    row_sum, items_sum = sum(row), sum(items)
    item_size, item_name = items.pop(0), names.pop(0)
    vertical = bounds[2] > bounds[3]
    shrink = (row_sum / (row_sum + items_sum)) * (bounds[2] if vertical else bounds[3])

    if vertical:
        next_row_bounds = [bounds[0] + shrink, bounds[1],
                bounds[2] - shrink, bounds[3]]
    else:
        next_row_bounds = [bounds[0], bounds[1] + shrink,
                bounds[2], bounds[3] - shrink]

    existing_row = worst(item_size, items_sum, row_sum + item_size, bounds)
    next_row = worst(item_size, items_sum, 0 + item_size,
            next_row_bounds)
    add_to_next_row = existing_row > next_row

    if add_to_next_row:
        result += draw_row(items_sum, row, bounds, row_names)
        row.clear()
        row_names.clear()

    row.append(item_size)
    row_names.append(item_name)
    if items:
        return squarify(items, row,
                next_row_bounds if add_to_next_row else bounds, row_names,
                names, result)
    else:
        result += draw_row(0, row,
            next_row_bounds if len(row) == 1 else bounds, row_names)
        return result


def draw_row(items_sum, row, bounds, row_names):
    pos = 0
    row_sum = sum(row)
    vertical = bounds[2] > bounds[3]
    row_width = (row_sum / (row_sum + items_sum)) * (bounds[2] if vertical else
            bounds[3])
    result = []
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
        result.append([row_names[i].split('/')[-1], rect])
        pos = pos + (rect[3] if vertical else rect[2])
    return result


def draw_rectangle(b, name, p_size, depth):
    global svg_header, svg_content, svg_rect_template, svg_text_template, dir_size;
    svg_new_rect = svg_rect_template.format(x = b[0], y = b[1], w = b[2],
            h = b[3], sw = p_size,
            col = dir_fill_colors[depth % len(dir_fill_colors)])
    svg_new_rect += svg_text_template.format(x = b[0], y = b[1] + b[3],
            text = name.replace("&", "&amp;"), size = p_size * 100)
    svg_content += svg_new_rect


def add_nested_item(target, path, item):
    if path[0] not in target: target[path[0]] = {}
    if len(path) > 1:
        if 'c' not in target[path[0]]: target[path[0]]['c'] = {}
        add_nested_item(target[path[0]]['c'], path[1:], item)
    else: target[path[0]]['s'] = item


def squarify_nested(items, bounds, depth = 0):
    sizes = [int(items['c'][i]['s']) for i in items['c']]
    names = list(items['c'].keys())
    sizes, names = [list(t) for t in zip(*sorted(zip(sizes, names)))]
    sizes.reverse()
    names.reverse()
    rects = squarify(sizes, [], bounds, [], names, [])
    for rect in rects:
        p_size = ((rect[1][2] + rect[1][3]) / (svg_width + svg_height)) * 2
        draw_rectangle(rect[1], rect[0], p_size, depth)
        if 'c' in items['c'][rect[0]]:
            squarify_nested(items['c'][rect[0]],
                    [
                        rect[1][0] + (p_size * 10),
                        rect[1][1] + (p_size * 10),
                        rect[1][2] - (p_size * 20),
                        rect[1][3] - (p_size * 20)
                    ], depth + 1)

def main():
    global svg_header, svg_content, svg_rect_template, svg_text_template, dir_size;
    svg_template =  """<?xml version="1.0" standalone="no"?><svg version="1.1"
    width="{w}" height="{h}" style="background-color:black"
    xmlns="http://www.w3.org/2000/svg"><style>text{{font-family:
        monospace; }}</style>{content}</svg>"""

    svg_rect_template = """<rect x="{x}" y="{y}" width="{w}" height="{h}"
    fill="{col}" stroke="black" stroke-width="{sw}"></rect>"""

    svg_text_template = """<text x="{x}" y="{y}" fill="black"
    font-size="{size}%">{text}</text>"""
    svg_content = ""

    items = {}
    with fileinput.input() as f_input:
        for line in [l.rstrip('\n').split('\t') for l in f_input]:
            if int(line[0]) > 0:
                add_nested_item(items, line[1].split('/'), line[0])

    dir_size = int(items[list(items.keys())[0]]['s'])
    squarify_nested(items[list(items.keys())[0]],
            [0, 0, svg_width, svg_height])

    print (svg_template.format(content = svg_content, w = svg_width,
        h = svg_height))

main()
