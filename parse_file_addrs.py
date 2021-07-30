# -*- coding: utf-8 -*-

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

bad_addr_conversion = {
    "OSDOBCOO": "05D0BC00",
    "05EOB600": "05E0B600",
    "05E11£00": "05E11E00",
    "03QSEE00": "0395EE00",
    "OOSSQCOO": "00559C00",
    "OOSSAEOO": "0055AE00",
    "OSCADEOO": "05CADE00",
    "03AOC200": "03A0C200",
    "035AOA00": "03EADA00",
    "0H3C5200": "01DCE200"
}

def main():
    output = ""

    with open("file_addrs_input.dump", "r") as f:
        for i, line in enumerate(f, 122):
            line = line.strip()
            try:
                int(line, 16)
                output += f"{i:03d} {line}\n"
            except ValueError:
                output += f"{i:03d} {bad_addr_conversion[line]}\n"
                #output += f"{i:03d} {line} TODO__fix_me\n"

    with open("file_addrs_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
