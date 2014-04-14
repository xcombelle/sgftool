#purpose

From a go file test.sgf create a new file new.test.sgf with various tweaking

compatible with python3.3+


# Usage

    usage: python3 sgftool.py [-h] [--filter] [--limit LIMIT] [--reverse] file


    positional arguments:
      file

    optional arguments:
      -h, --help     show this help message and exit
      --filter       filter coments and variation
      --limit LIMIT  limit the variations to LIMIT depth
      --reverse      reverse the board upside down
  
# Tests

    python3 sgftool_test.py
