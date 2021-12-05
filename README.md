# Squarified Treemap
Will display a squarified treemap in the terminal using curses.
It will also display a squarified treemap based on data piped to the script. 
For example, you can display a squarfied treemap of the current directories 
files with the following command:
`du -d1 -ab | sort -n -r | tail -n +2 | python /path/to/stm.py`
