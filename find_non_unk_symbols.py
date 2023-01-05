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

unk_func_regex = re.compile(r"^(?:sub|(?:Unk_)?ov([0-9]+)|Unk)_([0-9A-F]{8})$")
unk_symbol_7_digit_regex = re.compile(r"^(?:sub|ov[0-9]+)_([0-9A-F]{7})$")
anon_data_regex = re.compile(r"^v[0-9]+\$[0-9]{5}$")

def is_7_digit_unk_symbol(symbol_name):
    match_obj = unk_symbol_7_digit_regex.match(symbol_name)
    if match_obj:
        return True
    else:
        return False

def is_wanted_non_unk_symbol(symbol, symbol_name):
    if unk_func_regex.match(symbol_name):
        return False
    elif symbol_name.startswith("inline"):
        return False
    elif symbol.section == ".version":
        return False
    elif "$" in symbol_name:
        return False
    elif symbol_name.startswith("FunctionRODATA_"):
        return False
    elif symbol_name.startswith("__func__"):
        return False
    elif anon_data_regex.match(symbol_name):
        return False
    elif symbol.archive == "libdwcutil.a":
        if symbol_name == "DWC_StartUtility":
            return True
        else:
            return False
    elif symbol.archive == "libjn_spl.a":
        return False
    elif symbol.archive == "libdwcbm.a":
        if symbol_name == "DWC_BM_Init":
            return True
        else:
            return False
    elif symbol.filename == "cpp_todo":
        return False
    #elif symbol.section in (".rodata", ".bss", ".data"):
    #    return False
    else:
        return True

def main():
    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    non_unk_symbol_outputs = []
    non_unk_symbols = collections.defaultdict(list)
    unk_symbols_7_digit = []
    output = ""
    output += "== multiple symbol names ==\n"

    for symbol_name, symbols in xmap.symbols_by_name.items():
        if len(symbols) > 1:
            output += "".join(f"{symbol}\n" for symbol in symbols)
        elif is_7_digit_unk_symbol(symbol_name):
            unk_symbols_7_digit.append(symbols[0])
        for symbol in symbols:
            if is_wanted_non_unk_symbol(symbol, symbol_name):
                symbol_output_pt1 = f"{symbol_name}: {symbol.full_addr}"
                if symbol.archive is not None:
                    symbol_archive_filename_part = f"({symbol.archive} {symbol.filename})"
                else:
                    symbol_archive_filename_part = f"({symbol.filename})"

                symbol_output = f"{symbol_output_pt1: <32}{symbol_archive_filename_part}"

                non_unk_symbol_outputs.append(symbol_output)
                non_unk_symbols[symbol_name].append(symbol)

    output += "\n== 7 digit unk symbols ==\n"
    output += "".join(f"{unk_symbol}\n" for unk_symbol in unk_symbols_7_digit)
    output += "\n== Desired non-unk symbols ==\n"
    output += "\n".join(non_unk_symbol_outputs) + "\n"

    with open("find_non_unk_symbols_out.dump", "w+") as f:
        f.write(output)

    #os.chdir("../pokeplatinum")
    #
    #for symbol_name, symbols in non_unk_symbols.items():
    #    for i, symbol in enumerate(symbols):
    #        if symbol.full_addr.overlay != -1:
    #            continue
    #        if symbol.section not in (".text", ".itcm", ".dtcm", ".dtcm.bss"):
    #            raise RuntimeError(f"Found non-text symbol! symbol.name: {symbol.name}, symbol.section: {symbol.section}")
    #
    #        symbol_name_as_unk = f"sub_{symbol.full_addr.addr:08X}"
    #        if len(symbols) == 1:
    #            new_symbol_name = symbol.name
    #        else:
    #            new_symbol_name = f"{symbol.name}_dup{i + 1}"
    #            #if symbol.name[-1].isdigit():
    #            #    
    #            #else:
    #            #    new_symbol_name = f"{symbol.name}_dup{i + 1}"
    #
    #        replace_cmd = ["./replace.sh", symbol_name_as_unk, new_symbol_name]
    #        print(replace_cmd)
    #        subprocess.run(replace_cmd)

if __name__ == "__main__":
    main()
