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

import re
import os
import pathlib
import shutil

include_regex = re.compile(r"^#include\s+\"([^\"]+)\"")
seen_filenames = set()

def copy_includes_for_file(filenames):
    new_files = []

    for filename in filenames:
        print(filename)
        if filename in seen_filenames:
            continue

        seen_filenames.add(str(filename))

        with open(filename, "r") as f:
            for line in f:
                match_obj = include_regex.match(line)
                if match_obj:
                    include_filename = match_obj.group(1)
                    include_src_filepath = pathlib.Path(f"00jupc_retsam/include/{include_filename}")
                    include_dest_filepath = pathlib.Path(f"pokeplatinum/include/{include_filename}")
                    include_dest_filepath.parent.mkdir(parents=True, exist_ok=True)

                    if not include_dest_filepath.is_file():
                        shutil.copyfile(include_src_filepath, include_dest_filepath)
                        new_files.append(str(include_src_filepath))

    return new_files

def main():
    os.chdir("..")

    new_files = ("ndsdisasm/copy_includes_in.h",)
    while new_files:
        new_files = copy_includes_for_file(new_files)
                        
if __name__ == "__main__":
    main()
