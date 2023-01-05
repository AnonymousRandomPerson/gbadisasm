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
import itertools
import pathlib
from xmap import XMap
import collections
import functools
import re

multiple_sdk_filenames_to_correct_archive = {
    "list.o": "libnnsfnd.a",
    "util.o": ('libnnsg3d.a', 'libwcm.a'),
    "mem.o": "libnnsg3d.a",
    "main.o": "libnnssnd.a",
    "stream.o": "libnnssnd.a",
    "heap.o": "libnnssnd.a",
    "search.o": -1
}

multiple_sdk_filenames = {"list.o", "util.o", "mem.o", "main.o", "stream.o", "heap.o", "search.o"}

IS_UTIL_O = 1

class SDKSource:
    __slots__ = ("src_filename", "src_filename_no_repo", "archive_filename", "object_basename", "archive_and_object_filename")

    def __init__(self, src_filename, archive_filename, object_basename):
        self.src_filename = src_filename
        self.src_filename_no_repo = src_filename.replace("../00jupc_retsam/", "")
        self.archive_filename = archive_filename
        self.object_basename = object_basename
        self.archive_and_object_filename = f"{archive_filename}:{object_basename}"

#class TruncatedObjectFilename:
#    __slots__ = ("archive_and_object_filename", "object_filename"):
#
#    def __init__(self, archive_and_object_filename, object_filename):
#        self.archive_and_object_filename = archive_and_object_filename
#        self.object_filename = object_filename
#
#    def __key(self):
#        return (self.archive_and_object_filename, self.object_filename)
#
#    def __hash__(self):
#        return hash(self.__key())
#
#    def __eq__(self, other):
#        if isinstance(other, OvAddr):
#            return self.__key() == other.__key()
#        return NotImplemented

func_def_regex = re.compile(r"^(?!typedef)(?:static\s+)?(?:const\s+)?(?:struct|union|enum\s+)?(\w+)\s+(?:\*+\s*)?(\w+)\((.*)\)(?:\s*{)?\s*$")

def main():
    sdk_c_filenames = (
        glob.glob("../00jupc_retsam/sdk/NitroSDK/build/libraries/**/*.c", recursive=True)
        + glob.glob("../00jupc_retsam/sdk/NitroSystem/build/libraries/**/*.c", recursive=True)
        + glob.glob("../00jupc_retsam/sdk/NitroWiFi/build/libraries/**/*.c", recursive=True)
        + glob.glob("../00jupc_retsam/sdk/NitroDWC/build/libraries/**/*.c", recursive=True)
    )
    sdk_c_filenames_tracker = {filename: None for filename in sdk_c_filenames}

    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")
    xmap_nodead = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main2.nef.xMAP", ".main")

    symbols_by_archive_and_object_filename = collections.defaultdict(list)
    nodead_symbol_names_by_archive_and_object_filename = collections.defaultdict(set)

    object_basename_to_archive = {}
    truncated_object_filenames = collections.defaultdict(set)

    all_archive_filenames = set()
    for symbols in xmap.symbols_by_name.values():
        for symbol in symbols:
            if symbol.archive is not None:
                archive_and_object_filename = f"{symbol.archive}:{symbol.filename}"
                if not symbol.filename.endswith(".o"):
                    truncated_object_filenames[symbol.filename].add(archive_and_object_filename)
                symbols_by_archive_and_object_filename[archive_and_object_filename].append(symbol)
                correct_archive = multiple_sdk_filenames_to_correct_archive.get(symbol.filename)
                if isinstance(correct_archive, str):
                    object_basename_to_archive[symbol.filename] = correct_archive
                elif isinstance(correct_archive, tuple):
                    object_basename_to_archive[symbol.filename] = IS_UTIL_O
                elif correct_archive == -1:
                    object_basename_to_archive[symbol.filename] = -1
                elif correct_archive is None:
                    object_basename_to_archive[symbol.filename] = symbol.archive

    for symbols in xmap_nodead.symbols_by_name.values():
        for symbol in symbols:
            if symbol.archive is not None and not symbol.name.startswith("FunctionRODATA_") and not "$" in symbol.name:
                archive_and_object_filename = f"{symbol.archive}:{symbol.filename}"                
                nodead_symbol_names_by_archive_and_object_filename[archive_and_object_filename].add(symbol.name)

    #output = ""

    #sorted_truncated_object_filenames = sorted(truncated_object_filenames.items(), key=lambda x: x[0], reverse=True)
    #
    #for truncated_object_filename, truncated_object_filenames_and_archives in sorted_truncated_object_filenames:
    #    output += f"{truncated_object_filename}: {truncated_object_filenames_and_archives}\n"
    #    #if len(truncated_object_filenames_and_archives) > 1:
    #    #    output += f"Ambiguous truncated object filename {truncated_object_filename}! possibilities: {truncated_object_filenames_and_archives}\n"
    #
    #with open("truncated_object_filenames.dump", "w+") as f:
    #    f.write(output)

    for filename in sdk_c_filenames:
        object_basename = pathlib.Path(filename).with_suffix(".o").name.lower()
        corresponding_archive = object_basename_to_archive.get(object_basename[:15])
        if corresponding_archive is not None:
            if object_basename == IS_UTIL_O:
                if "NitroSystem" in filename:
                    corresponding_archive = "libnnsg3d.a"
                else:
                    corresponding_archive = "libwcm.a"
            elif object_basename == -1:
                corresponding_archive = None

        if corresponding_archive is not None:
            sdk_c_filenames_tracker[filename] = SDKSource(filename, corresponding_archive, object_basename)

    not_found_sdk_c_srcs = []
    found_sdk_c_srcs = []

    for filename, sdk_source in sdk_c_filenames_tracker.items():
        if sdk_source is None:
            not_found_sdk_c_srcs.append(filename)
        else:
            found_sdk_c_srcs.append(sdk_source)

    output = []
    output.append(f"== Not found SDK C sources ==\n")
    output.extend(f"{sdk_c_src.replace('../00jupc_retsam/', '')}\n" for sdk_c_src in not_found_sdk_c_srcs)

    #output.append("\n\n")
    #output.append("== Found SDK C sources ==\n")
    #output.extend(f"{sdk_c_src.src_filename}\n" for sdk_c_src in found_sdk_c_srcs)
    #output.append("\n")
    complete_sdk_c_srcs_output = []
    incomplete_sdk_c_srcs_output = []

    warning_output = []

    for sdk_c_src in found_sdk_c_srcs:
        #all_src_functions = set()

        #with open(sdk_c_src.src_filename, "r") as f:
        #    lines = f.readlines()
        #
        ##if sdk_c_src.src_filename == "../00jupc_retsam/sdk/NitroSDK/build/libraries/card/ARM9/src/card_pullOut.c":
        ##    is_card_pullout = True
        ##else:
        ##    is_card_pullout = False
        #
        #for line in lines:
        #    #if is_card_pullout:
        #    #    print(line)
        #
        #    if line.strip() == "":
        #        continue
        #
        #    match_obj = func_def_regex.match(line.replace("const ", ""))
        #    if match_obj:
        #        function_name = match_obj.group(2)
        #        all_src_functions.add(function_name)
        #    #elif line.startswith("void CARD_InitPulledOutCallback(void)"):
        #    #    raise RuntimeError(line)

        symbols = symbols_by_archive_and_object_filename[sdk_c_src.archive_and_object_filename]
        final_symbol_names = set(symbol.name for symbol in symbols if not symbol.name.startswith("FunctionRODATA_") and not "$" in symbol.name)
        all_symbol_names = nodead_symbol_names_by_archive_and_object_filename[sdk_c_src.archive_and_object_filename]

        #for symbol in symbols:
        #    if symbol.section == ".text":
        #        if symbol.name not in all_src_functions:
        #            warning_output.append(f"Warning: {symbol.name} in XMap but not found in src file {sdk_c_src.src_filename}!\n")
        #        final_functions.add(symbol.name)

        deadstripped_functions = sorted(all_symbol_names - final_symbol_names)
        all_symbol_names_len = len(all_symbol_names)
        final_symbol_names_len = len(final_symbol_names)

        if len(deadstripped_functions) > 0:
            incomplete_sdk_c_srcs_output.append(f"=== {sdk_c_src.src_filename} deadstripped symbols ({all_symbol_names_len} -> {final_symbol_names_len}) ===\n")
            incomplete_sdk_c_srcs_output.extend(f"{deadstripped_symbol}\n" for deadstripped_symbol in deadstripped_functions)
            incomplete_sdk_c_srcs_output.append("\n")
        else:
            complete_sdk_c_srcs_output.append(f"{sdk_c_src.src_filename}\n")

    output.append("== C files with no deadstripping ==\n")
    output.extend(complete_sdk_c_srcs_output)
    output.append("\n")
    output.append("== C files with deadstripping ==\n")
    output.extend(incomplete_sdk_c_srcs_output)

    with open("find_sdk_coverage_out.dump", "w+") as f:
        f.write("".join(output))

    #with open("find_sdk_coverage_warning_out.dump", "w+") as f:
    #    f.write("".join(warning_output))

if __name__ == "__main__":
    main()
