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
import functools
import re
import os

from xmap import OvAddr

unk_func_regex = re.compile(r"^(?:sub|ov([0-9]+))_([0-9A-F]{8})$")

class MinimalUnkSymbol:
    __slots__ = ("name", "full_addr")

    def __init__(self, name):
        self.name = name

        match_obj = unk_func_regex.match(self.name)
        if match_obj:
            overlay_str = match_obj.group(1)
            overlay = int(overlay_str) if overlay_str is not None else -1
            addr = int(match_obj.group(2), 16)
            self.full_addr = OvAddr(overlay, addr)
        elif self.name == "_start":
            self.full_addr = OvAddr(-1, 0x2000800)
        else:
            raise RuntimeError()

def main():
    os.chdir("../pokeplatinum")

    for include_filename in glob.glob("asm/include/*.inc"):
        with open(include_filename, "r") as f:
            lines_as_list = f.read().strip().splitlines()

        unk_symbols = [MinimalUnkSymbol(line.split(maxsplit=1)[1]) for line in set(lines_as_list)]
        sorted_unk_symbols = sorted(unk_symbols, key=lambda x: x.full_addr)

        output = "".join(f".public {unk_symbol.name}\n" for unk_symbol in sorted_unk_symbols)

        with open(include_filename, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
