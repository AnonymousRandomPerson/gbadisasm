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

import re
from itertools import zip_longest

def grouper(iterable, n, fillvalue=None):
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

jt_offset_regex = re.compile(r"^\t\.2byte _([0-9A-F]{8}) - _([0-9A-F]{8})")

def main():
    with open("fix_jumptable_input.txt", "r") as f:
        original_lines = f.readlines()

    offsets = []
    lines = []

    for line in original_lines:
        if line.strip() != "":
            lines.append(line)

    for line in lines:
        match_obj = jt_offset_regex.match(line)
        end = int(match_obj.group(1), 16)
        start = int(match_obj.group(2), 16)
        offset = end - start - 2
        offsets.append(offset)

    output = ""

    if len(offsets) & 1 == 1:
        output += f"\t.hword {offsets[0]:04x} // BAD_OFFSET_FIXME\n"
        start_index = 1
    else:
        start_index = 0

    #print(offsets[start_index:])

    for lo_offset, hi_offset in grouper(offsets[start_index:], 2):
        output += f"\tdcd 0x{lo_offset | (hi_offset << 16):08x}\n"

    for offset, line in zip(offsets, lines):
        offset_as_str = f"0x{offset:x}"
        output += f"\t// {offset_as_str: >6} // {line[1:]}"

    with open("fix_jumptable_out.txt", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
