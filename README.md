# Squarified Treemap

Display a squarified treemap in the terminal using curses from the current
directory.

`du -d1 -ab | sort -n -r | tail -n +2 | python /path/to/stmterm.py`

Generate an squarified treemap SVG file from the current directory and 
subdirectories.

`du -abd4 | python /path/to/stmsvg.py > /path/to/out.svg`

Algorithm based on: [Bruls, Huizing, van Wijk Squarified Treemaps](https://www.win.tue.nl/~vanwijk/stm.pdf)
