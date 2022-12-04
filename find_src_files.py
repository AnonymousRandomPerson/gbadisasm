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

import os
from xmap import XMap
import re
import shutil
import pathlib

def main():
    with open("src_files_in.txt", "r") as f:
        src_files_as_list = f.read().splitlines()

    src_files = {k: list() for k in src_files_as_list if k != ""}

    for dpath, dnames, fnames in os.walk("../00jupc_retsam/src"):
        for i, (fname, fname_full) in enumerate((fname, os.path.join(dpath, fname)) for fname in fnames):
            if fname.endswith(".c"):
                if fname not in src_files:
                    pass
                    #print(f"Skipping {fname_full}!")
                else:
                    src_files[fname].append(fname_full)
                    #print(f"Found {fname} at {fname_full}!")

    good_src_files = ""
    missing_src_files = ""
    ambiguous_src_files = ""

    for k, v in src_files.items():
        if len(v) == 0:
            missing_src_files += f"Could not find src file for {k}!\n"
        elif len(v) > 1:
            ambiguous_src_files += f"{k} has multiple files: " + ", ".join(v) + "\n"
        else:
            good_src_files += f"{k}: {v[0]}\n"

    output = ""
    output += "== Good src files ==\n"
    output += f"{good_src_files}\n"
    output += "== Ambiguous src files ==\n"
    output += f"{ambiguous_src_files}\n"
    output += "== Missing src files ==\n"
    output += f"{missing_src_files}\n"

    with open("find_src_files_out.dump", "w+") as f:
        f.write(output)

    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    output = ""
    rodata_only_files = frozenset((
        "fieldobj_movedata.o",
        "opening_call.o",
        "fieldobj_drawdata.o",
        "field_effect_data.o",
        "slot_data.o"
    ))

    with open("../00jupc_retsam/make_prog_files", "r", encoding="ascii", errors="replace") as f:
        prog_files = f.read()

    for base_src_file, full_src_files in src_files.items():
        if len(full_src_files) == 0:
            print(f"{base_src_file} has no full src file!")
            continue

        obj_file = base_src_file.replace(".c", ".o")
        symbols_by_filename = xmap.symbols_by_filename.get(obj_file)
        if symbols_by_filename is None:
            print(f"{obj_file} missing in XMap!")
        else:
            text_symbols_by_filename = sorted(filter(lambda x: x.section == ".text", symbols_by_filename), key=lambda x: x.full_addr)
            if len(text_symbols_by_filename) != 0:
                first_symbol = text_symbols_by_filename[0]
            elif obj_file in rodata_only_files:
                rodata_symbols_by_filename = sorted(filter(lambda x: x.section == ".rodata", symbols_by_filename), key=lambda x: x.full_addr)
                first_symbol = rodata_symbols_by_filename[0]
            else:
                first_symbol = None

            if first_symbol is not None:
                if first_symbol.full_addr.overlay == -1:
                    sanitized_filename = f"unk_{first_symbol.full_addr.addr:08X}.c"
                else:
                    sanitized_filename = f"overlay{first_symbol.full_addr.overlay:03d}/ov{first_symbol.full_addr.overlay}_{first_symbol.full_addr.addr:08X}.c"
                    pathlib.Path(f"../00jupc_retsam/src/overlay{first_symbol.full_addr.overlay:03d}").mkdir(parents=True, exist_ok=True)

                output += f"{full_src_files[0]} -> src/{sanitized_filename}\n"
                shutil.move(full_src_files[0], f"../00jupc_retsam/src/{sanitized_filename}")
                prog_file_regex = re.compile(fr"\$\([A-Z]+\)(\\\w+)?\\{re.escape(base_src_file)}", flags=re.MULTILINE)
                (prog_files, num_replacements) = prog_file_regex.subn(sanitized_filename, prog_files, count=1)
                if num_replacements == 0:
                    print(f"Could not find {base_src_file} in make_prog_files!")

    with open("make_prog_files_out.mk", "w+", encoding="ascii", errors="replace") as f:
        f.write(prog_files)

    with open("sanitized_src_files_out.txt", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
