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
import subprocess
from xmap import XMap, OvAddr
import glob
import pathlib
import sys
import argparse

SKIPPING_UNTIL_0x4800 = 0
LOOKING_FOR_MINUS = 1
IN_MINUS_DIFF = 2

CUR_OVERLAY = 117
CUR_OVERLAY_START = 0x3ffe00
CUR_OVERLAY_END = 0x406a00
CUR_OVERLAY_RAM = 0x2260440

class Range:
    __slots__ = ("start", "end", "overlay")
    def __init__(self, overlay, start, end):
        self.overlay = overlay
        self.start = start
        self.end = end

load_to_virt_conversion_table = (
    Range(-1, 0x4000, 0x105d14),
    Range(4, 0x107e00, 0x151600),
    Range(5, 0x151600, 0x182a00),
    Range(7, 0x18e200, 0x194000),
    Range(13, 0x1c2c00, 0x1cce00),
    Range(17, 0x212200, 0x22c000),
    Range(19, 0x257c00, 0x267600),
    Range(20, 0x267600, 0x26be00),
    Range(21, 0x26be00, 0x285000),
    Range(22, 0x285000, 0x28c200),
    Range(43, 0x2b3200, 0x2b3e00),
    Range(48, 0x2b7600, 0x2b8000),
    Range(52, 0x2b9400, 0x2ba200),
    Range(54, 0x2bac00, 0x2bb400),
    Range(58, 0x2bce00, 0x2bf400),
    Range(61, 0x2cc400, 0x2cfe00),
    Range(62, 0x2cfe00, 0x2ea600),
    Range(64, 0x2ed600, 0x2f2000),
    Range(65, 0x2f2000, 0x2fe200),
    Range(66, 0x2fe200, 0x32bc00),
    Range(70, 0x331000, 0x343200),
    Range(73, 0x347000, 0x349e00),
    Range(76, 0x34c000, 0x350000),
    Range(77, 0x350000, 0x356e00),
    Range(79, 0x358c00, 0x35be00),
    Range(80, 0x35be00, 0x35e600),
    Range(83, 0x361400, 0x366600),
    Range(90, 0x375800, 0x376c00),
    Range(91, 0x376c00, 0x378c00),
    Range(94, 0x37b400, 0x386e00),
    Range(97, 0x38f400, 0x3a3800),
    Range(98, 0x3a3800, 0x3a6a00),
    Range(104, 0x3b9800, 0x3cd600),
    Range(106, 0x3d2000, 0x3d3e00),
    Range(107, 0x3d3e00, 0x3dc800),
    Range(111, 0x3e4e00, 0x3e7a00),
    Range(117, 0x3ffe00, 0x406a00)
)

def is_addr_in_ov_range(addr):
    return CUR_OVERLAY_START <= addr <= CUR_OVERLAY_END

def convert_load_to_virt(addr):
    return addr - CUR_OVERLAY_START + CUR_OVERLAY_RAM

def convert_virt_to_load(addr):
    return addr + CUR_OVERLAY_START - CUR_OVERLAY_RAM
    
class Shift:
    __slots__ = ("count", "addr", "closest_symbol")

    def __init__(self, count, addr):
        self.count = count
        self.addr = addr

def find_file(symbol):
    output = subprocess.check_output(["find", ".", "-name", f"{pathlib.Path(symbol.filename).stem}.c"]).decode("ascii")
    return output[2:-1]
    #return glob.glob(f"**/{pathlib.Path(symbol.filename).stem}.c", recursive=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--show-filename", dest="show_filename", action="store_true", default=False)
    ap.add_argument("-d", "--diff-index", dest="diff_index", type=int, default=0)
    ap.add_argument("chosen_symbol_index", nargs="?", type=int, default=0)
    args = ap.parse_args()

    os.chdir("../master_cpuj00")
    compare_dump = pathlib.Path("diff/compare_dump.dump")
    rom_file = pathlib.Path("bin/ARM9-TS/Rom/main.srl")
    compare_dump_mtime = compare_dump.stat().st_mtime
    rom_file_mtime = rom_file.stat().st_mtime

    if rom_file_mtime >= compare_dump_mtime:
        subprocess.run(["./compare.sh"])

    longest_shift = 0
    #cur_shift = 0
    state = SKIPPING_UNTIL_0x4800
    diffs = []
    which_diff_range = 0
    num_diffs = 0

    with open("diff/compare_dump.dump", "r") as f:
        for i in range(2):
            next(f)

        for line in f:
            if line[1] == "*":
                continue

            #print(line)
            if state == SKIPPING_UNTIL_0x4800:
                #if line.startswith(" 000001b0"):
                #    state = LOOKING_FOR_MINUS
                state = LOOKING_FOR_MINUS

            if state == LOOKING_FOR_MINUS:
                if line[0] == "-":
                    cur_diff_addr = int(line[1:9], 16)
                    diffs.append(cur_diff_addr)
                    state = IN_MINUS_DIFF
                    num_diffs += 1
            elif state == IN_MINUS_DIFF:
                if line[0] != "-":
                    state = LOOKING_FOR_MINUS

    xmap_file = XMap("bin/ARM9-TS/Rom/main.nef.xMAP", ".main")
    chosen_diff = diffs[args.diff_index]
    if 0x106600 <= chosen_diff < 0x107600:
        print(f"diff at {chosen_diff:07x} is in arm9ovltable!")
        return

    for conversion in load_to_virt_conversion_table:
        if 0x106600 <= chosen_diff < 0x107600:
            continue

        if conversion.start <= chosen_diff < conversion.end:
            if conversion.overlay == -1:
                cur_overlay_start_vaddr = 0x2000000
            else:
                cur_overlay_start_vaddr = xmap_file.overlay_start_addrs[conversion.overlay]

            diff_vaddr = chosen_diff - conversion.start + cur_overlay_start_vaddr
            diff_full_addr = OvAddr(conversion.overlay, diff_vaddr)
            break
    else:
        raise RuntimeError(f"Could not find load to virt conversion for address {chosen_diff:x}!")

    for i, (full_addr, symbol) in enumerate(xmap_file.symbols_by_addr.items()):
        if full_addr >= diff_full_addr:
            symbols_by_addr_list = list(xmap_file.symbols_by_addr.values())
            chosen_symbol = symbols_by_addr_list[i - 1 + args.chosen_symbol_index]
            next_symbol = symbols_by_addr_list[i + args.chosen_symbol_index]
            break

    if args.show_filename:
        chosen_symbol_file_output = f" in {find_file(chosen_symbol)}"
        next_symbol_file_output = f" in {find_file(next_symbol)}"
    else:
        chosen_symbol_file_output = ""
        next_symbol_file_output = ""

    output = ""
    output += f"possible diff at {chosen_diff:07x} [{chosen_symbol.full_addr.overlay}:{chosen_symbol.full_addr.addr:07x}] with symbol {chosen_symbol.name}{chosen_symbol_file_output}!\n"
    output += f"(next symbol: {next_symbol.name}{next_symbol_file_output} at {next_symbol.full_addr.overlay}:{next_symbol.full_addr.addr:07x})\n"
    output += f"num_diffs: {num_diffs}\n"
    print(output)

if __name__ == "__main__":
    main()
