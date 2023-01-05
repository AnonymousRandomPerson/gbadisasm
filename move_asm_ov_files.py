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

import glob
import re
import shutil
import pathlib

overlay_number_regex = re.compile(r"^\t.include \"include/(ov([0-9]+)_[0-9A-F]{8}(?:_arm|_thumb)?.inc)\"")
lsf_overlay_object_regex = re.compile(r"^\tObject asm/(ov([0-9]+)_[0-9A-F]{8}(?:_arm|_thumb)?.o)")

def main():
    SRC_DIR = "../pokeplatinum"
    DEST_DIR = "../pokeplatinum"

    for filename in glob.glob(f"{SRC_DIR}/asm/ov*.s"):
        filepath = pathlib.Path(filename)
        with open(filepath, "r") as f:
            lines = f.readlines()

        include_filename = None

        for i, line in enumerate(lines):
            if line.startswith("\t.include \"include/ov"):
                match_obj = overlay_number_regex.match(line)
                try:
                    overlay_number = int(match_obj.group(2), 10)
                except:
                    raise RuntimeError(line)
                include_filename = match_obj.group(1)

                lines[i] = f"\t.include \"overlay{overlay_number:03d}/{include_filename}\"\n"
                break

        overlay_dirpath = pathlib.Path(f"{DEST_DIR}/asm/overlay{overlay_number:03d}")
        overlay_dirpath.mkdir(parents=True, exist_ok=True)
        filename_base = filepath.name
        overlay_asm_dest_filepath = overlay_dirpath / filename_base
        output = "".join(lines)

        with open(overlay_asm_dest_filepath, "w+") as f:
            f.write(output)

        dest_filepath = pathlib.Path(f"{DEST_DIR}/asm/{filename_base}")

        dest_filepath.unlink()

        if include_filename is not None:
            shutil.move(f"{DEST_DIR}/asm/include/{include_filename}", f"{DEST_DIR}/asm/overlay{overlay_number:03d}/{include_filename}")

    with open(f"{SRC_DIR}/main.lsf", "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        match_obj = lsf_overlay_object_regex.match(line)
        if match_obj:
            obj_filename = match_obj.group(1)
            overlay_num = int(match_obj.group(2), 10)
            lines[i] = f"\tObject asm/overlay{overlay_num:03d}/{obj_filename}\n"

    output = "".join(lines)
    with open(f"{DEST_DIR}/main.lsf", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
