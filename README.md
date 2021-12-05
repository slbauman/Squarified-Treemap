# Squarified Treemap
Will generate a squarified treemap and display it in the terminal using 
curses. It will also generate a squarified treemap based on data piped to the 
script. For example, you can pass the size and names of the files in the 
current working directory with the following command:

`du -d1 -ab | sort -n -r | tail -n +2 | python /path/to/stm.py`

Algorithm based on: [Bruls, Huizing, van Wijk Squarified Treemaps](https://www.win.tue.nl/~vanwijk/stm.pdf)
