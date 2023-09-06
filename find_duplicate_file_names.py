# =============================================================================
# Copyright (c) 2022 luckytyphlosion
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# =============================================================================


import pathlib
import os
import re
import subprocess
import collections

from xmap import XMap

def find_all_filenames():
    #xmap = XMap("../pokeplatinum/build/platinum.us/main.nef.xMAP", ".main")
    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    output = ""
    filenames = collections.defaultdict(list)

    cur_filename = ""

    for full_addr, symbol in xmap.symbols_by_addr.items():
        if symbol.section != ".text":
            continue

        if cur_filename != symbol.filename:
            filenames[symbol.filename].append(symbol.archive if symbol.archive is not None else "None")
            cur_filename = symbol.filename

    duplicate_filenames = filter(lambda x: len(x[1]) > 1, filenames.items())

    output += "".join(f"{duplicate_filename_info[0]}: {', '.join(duplicate_filename_info[1])}\n" for duplicate_filename_info in duplicate_filenames)

    with open("find_duplicate_file_names.dump", "w+") as f:
        f.write(output)

def main():
    MODE = 0
    if MODE == 0:
        find_all_filenames()
    else:
        print("No mode selected!")


if __name__ == "__main__":
    main()
