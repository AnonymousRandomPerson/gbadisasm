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

import json

def main():
    # 02244A18
    output = ""
    #{
    #    " ": "space",
    #    "!": "excl",
    #    "#": "numsign",
    #    "$": "dollar",
    #    "%": "percent",
    #    "&": "amp",
    #    "'": "apos",
    #    "(": "leftparen",
    #    ")":

    alphanumeric_underscore = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz09123456789_"
    cfg_output = ""
    symbol_dict = {}

    with open("ov66.xmap", "r") as f:
        for line in f:
            if line.strip() == "":
                continue

            try:
                if "libdwcppwlobby.a" in line:
                    line_up_to_exc_lib, filename = line.split("(libdwcppwlobby.a", maxsplit=1)
                    library = "libdwcppwlobby.a"
                elif "libdwcilobby.a" in line:
                    line_up_to_exc_lib, filename = line.split("(libdwcilobby.a", maxsplit=1)
                    library = "libdwcilobby.a"
                else:
                    raise RuntimeError()
            except ValueError as e:
                raise RuntimeError(f"line: {line}") from e

            filename = filename.strip().split()[0]

            try:
                addr, size, section, symbol = line_up_to_exc_lib.strip().split(maxsplit=3)
            except ValueError as e:
                raise RuntimeError(f"line: {line}, line_up_to_exc_lib: {line_up_to_exc_lib.strip()}") from e

            addr = int(addr, 16)
            if addr > 0x02244A18:
                break

            if symbol[0] == "$":
                continue

            new_symbol = ""
            for c in symbol:
                if c in alphanumeric_underscore:
                    new_symbol += c
                else:
                    new_symbol += "_"
                    #new_symbol += f"_u_{ord(c):02x}_"

            cfg_output += f"arm_func 0x{addr:07x} ov66_{addr:07X}\n"
            symbol_dict[addr] = {
                "symbol": symbol,
                "new_symbol": new_symbol,
                "addr": addr,
                "size": size,
                "section": section,
                "library": library,
                "filename": filename,
            }

    cfg_output += f"arm_func 0x22588f4 ov66_22588F4\n"
    with open("ov66.json", "w+") as f:
        json.dump(symbol_dict, f, indent=2)

    with open("ov66.cfg", "w+") as f:
        f.write(cfg_output)

if __name__ == "__main__":
    main()
