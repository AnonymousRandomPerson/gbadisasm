# =============================================================================
# Copyright (c) 2021 luckytyphlosion
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

LOOKING_FOR_OVERLAY_START = 0
LOOKING_FOR_MINUS = 1
IN_MINUS_DIFF = 2

CUR_OVERLAY = 66
CUR_OVERLAY_START = 0x2fe200
CUR_OVERLAY_END = 0x32bc00
CUR_OVERLAY_RAM = 0x222dce0

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
    os.chdir("../master_cpuj00")
    subprocess.run(["./compare.sh"])

    longest_shift = 0
    #cur_shift = 0
    state = LOOKING_FOR_OVERLAY_START
    shifts = []

    with open("diff/compare_dump.dump", "r") as f:
        for i in range(2):
            next(f)

        for line in f:
            #print(line)
            if state == LOOKING_FOR_OVERLAY_START:
                try:
                    cur_addr = int(line[1:9], 16)
                    if is_addr_in_ov_range(cur_addr):
                        state = LOOKING_FOR_MINUS
                except ValueError:
                    continue

            if state == LOOKING_FOR_MINUS:
                if line[0] == "-":
                    cur_shift = 1
                    cur_shift_addr = int(line[1:9], 16)
                    if is_addr_in_ov_range(cur_shift_addr):
                        cur_shift_addr = convert_load_to_virt(cur_shift_addr)
                        state = IN_MINUS_DIFF
                    else:
                        print(f"cur_shift_addr: 0x{cur_shift_addr:07x}")
                        break
            elif state == IN_MINUS_DIFF:
                if line[0] == "-":
                    cur_addr = int(line[1:9], 16)
                    if is_addr_in_ov_range(cur_addr):
                        cur_shift += 1
                    else:
                        shifts.append(Shift(cur_shift, cur_shift_addr))
                        state = LOOKING_FOR_MINUS
                else:
                    shifts.append(Shift(cur_shift, cur_shift_addr))
                    state = LOOKING_FOR_MINUS

    if state == IN_MINUS_DIFF:
        shifts.append(Shift(cur_shift, cur_shift_addr))

    xmap_file = XMap("bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    #print(shifts)
    shifts = filter(lambda x: x.count >= 10, shifts)
    #print(list(shifts))
    best_shift = sorted(shifts, key=lambda x: x.addr)[0]
    best_shift_full_addr = OvAddr(CUR_OVERLAY, best_shift.addr)

    prev_symbol = None
    #sorted_symbols_by_addr = 

    for full_addr, symbol in xmap_file.symbols_by_addr.items():
        if full_addr >= best_shift_full_addr:
            chosen_symbol = prev_symbol
            next_symbol = symbol
            break
        prev_symbol = symbol

    if len(sys.argv) == 2 and sys.argv[1] == "-f":
        chosen_symbol_file_output = f" in {find_file(chosen_symbol)}"
        next_symbol_file_output = f" in {find_file(next_symbol)}"
    else:
        chosen_symbol_file_output = ""
        next_symbol_file_output = ""

    output = ""
    output += f"possible shift at {best_shift.addr:07x} with symbol {chosen_symbol.name}{chosen_symbol_file_output} (load addr: {convert_virt_to_load(best_shift.addr):07x})!\n"
    output += f"(next symbol: {next_symbol.name}{next_symbol_file_output})\n"
    print(output)

if __name__ == "__main__":
    main()
