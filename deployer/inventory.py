#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from json import dumps, loads
import os

# -----------------------------
# Main
# -----------------------------


def main():
    inventory_filename = 'inventory.json'
    exists_inventory_json_file = os.path.isfile(inventory_filename)

    if not exists_inventory_json_file:
        print("You need to build inventory first")
        exit(-1)
    else:
        inventory_file = loads(open(inventory_filename, 'r').read())
        print(dumps(inventory_file, indent=4))


if __name__ == '__main__':
    main()
