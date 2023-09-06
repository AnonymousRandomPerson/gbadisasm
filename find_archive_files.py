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

def find_all_archive_files():
    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    output = ""
    archive_files = {}

    for full_addr, symbol in xmap.symbols_by_addr.items():
        if symbol.archive is not None and symbol.archive not in archive_files:
            archive_files[symbol.archive] = symbol.full_addr

    sorted_archive_files = sorted(archive_files.items(), key=lambda x: x[1])

    output += "".join(f"{archive_file_and_first_addr[0]}\n" for archive_file_and_first_addr in sorted_archive_files)

    with open("find_archive_files_out.dump", "w+") as f:
        f.write(output)

def find_archive_files_with_source():
    with open("find_library_files_out.dump", "r") as f:
        archive_files = f.readlines()

    os.chdir("../00jupc_retsam")
    nitrosdk_libs = []
    notfound_nitrosdk_libs = []
    nitrodwc_libs = []
    notfound_nitrodwc_libs = []
    unknown_libs = []

    for archive_file in archive_files:
        archive_file = archive_file.strip()
        if archive_file == "":
            continue

        if archive_file.startswith("== Unknown libraries end =="):
            break

        cmd = ["find", ".", "-type", "f", "-name", archive_file]
        print(cmd)
        find_results = subprocess.check_output(cmd).decode("utf-8")
        if "NitroSDK" in find_results:
            found_libs = nitrosdk_libs
            notfound_libs = notfound_nitrosdk_libs
            lib_dirname = archive_file.replace("lib", "").replace(".a", "")
            sdk_dirname = "NitroSDK"
        elif "NitroDWC" in find_results:
            found_libs = nitrodwc_libs
            notfound_libs = notfound_nitrodwc_libs
            lib_dirname = archive_file.replace("libdwc", "").replace(".a", "")
            sdk_dirname = "NitroDWC"
        else:
            lib_dirname = None

        if lib_dirname is not None:
            cmd = ["find", f"sdk/{sdk_dirname}/build/libraries", "-type", "d", "-name", lib_dirname]
            print(cmd)
            find_results = subprocess.check_output(cmd).decode("utf-8").strip()
            if len(find_results) > 0:
                found_libs.append(archive_file)
            else:
                notfound_libs.append(archive_file)
        else:
            unknown_libs.append(archive_file)

    os.chdir("../ndsdisasm")

    output = ""
    output += "== Found NitroSDK libs ==\n"
    output += "\n".join(nitrosdk_libs) + "\n"
    output += "== Not Found NitroSDK libs ==\n"
    output += "\n".join(notfound_nitrosdk_libs) + "\n"
    output += "== Found NitroDWC libs ==\n"
    output += "\n".join(nitrodwc_libs) + "\n"
    output += "== Not Found NitroDWC libs ==\n"
    output += "\n".join(notfound_nitrodwc_libs) + "\n"
    output += "== Unknown libs ==\n"
    output += "\n".join(unknown_libs) + "\n"

    with open("find_archive_files_with_source_out.dump", "w+") as f:
        f.write(output)

def main():
    MODE = 1
    if MODE == 0:
        find_all_archive_files()
    elif MODE == 1:
        find_archive_files_with_source()
    else:
        print("No mode selected!")


if __name__ == "__main__":
    main()
