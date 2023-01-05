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

import collections
from xmap import XMap

def gen_symbols_by_archive_object_filename(xmap):
    symbols_by_archive_and_object_filename = collections.defaultdict(list)
    for symbols in xmap.symbols_by_name.values():
        for symbol in symbols:
            if symbol.archive is None:
                archive_and_object_filename = f"None:{symbol.filename}"
            else:
                archive_and_object_filename = f"{symbol.archive}:{symbol.filename}"
            symbols_by_archive_and_object_filename[archive_and_object_filename].append(symbol)

    return symbols_by_archive_and_object_filename

def main():
    xmap = XMap("../pokeplatinum/build/platinum.us/main.nef.xMAP", ".main")
    xmap_nodead = XMap("../pokeplatinum/build/platinum.us/main2.nef.xMAP", ".main")

    symbols_by_archive_object_filename = gen_symbols_by_archive_object_filename(xmap)
    symbols_by_archive_object_filename_nodead = gen_symbols_by_archive_object_filename(xmap_nodead)

    undeadstripped_files_output = []
    deadstripped_files_output = []

    for archive_and_object_filename, symbols_nodead in symbols_by_archive_object_filename_nodead.items():
        symbols = symbols_by_archive_object_filename.get(archive_and_object_filename)
        if symbols is None:
            symbols_set = set()
        else:
            symbols_set = set(symbol.name for symbol in symbols if not symbol.name.startswith("FunctionRODATA_") and not "$" in symbol.name)

        symbols_nodead_set = set(symbol.name for symbol in symbols_nodead if not symbol.name.startswith("FunctionRODATA_") and not "$" in symbol.name)
        deadstripped_symbols = sorted(symbols_nodead_set - symbols_set)
        nodead_symbols_set_len = len(symbols_nodead_set)
        symbols_set_len = len(symbols_set)

        if len(deadstripped_symbols) > 0:
            deadstripped_files_output.append(f"=== {archive_and_object_filename} deadstripped symbols ({nodead_symbols_set_len} -> {symbols_set_len}) ===\n")
            deadstripped_files_output.extend(f"{deadstripped_symbol}\n" for deadstripped_symbol in deadstripped_symbols)
            deadstripped_files_output.append("\n")
        else:
            undeadstripped_files_output.append(f"{archive_and_object_filename}\n")

    output = []
    output.append("== Deadstripped files ==\n")
    output.extend(deadstripped_files_output)
    output.append("\n== Undeadstripped files ==\n")
    output.extend(undeadstripped_files_output)

    with open("compare_nodead_out.dump", "w+") as f:
        f.write("".join(output))

if __name__ == "__main__":
    main()
