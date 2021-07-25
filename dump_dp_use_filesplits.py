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
from xmap import XMap, OvAddr

GET_FILE_AND_ADDR = 0
LOOKING_FOR_END_OF_FILE = 1

bad_archives = ("libc.a", "stdlibmwcc.a", "libvct.a", "libcps.a", "libdwcnhttp.a", "libdwcutil.a")


class FileSplit:
    __slots__ = ("start", "end", "is_bad")

    def __init__(self, start, end, is_bad):
        self.start = start
        self.end = end
        self.is_bad = is_bad

def full_addr_to_compact_str(full_addr):
    if full_addr.overlay != -1:
        return f"{full_addr.overlay}:{full_addr.addr:07x}"
    else:
        return f"{full_addr.addr:07x}"

def main():
    xmap = XMap("pm_dp_ose.nef.xMAP", ".main")
    cur_file = None
    cur_split_start = None
    state = GET_FILE_AND_ADDR
    filesplits = []
    
    for full_addr, symbol in xmap.symbols_by_addr.items():
        if state == LOOKING_FOR_END_OF_FILE:
            if symbol.filename != cur_file:
                if cur_split_start.overlay == -1:
                    cur_split_end = symbol.full_addr
                else:
                    overlay_text_end = OvAddr(cur_split_start.overlay, xmap.overlay_text_end_addrs[cur_split_start.overlay])
                    if symbol.full_addr < overlay_text_end:
                        cur_split_end = symbol.full_addr
                    else:
                        cur_split_end = overlay_text_end

                is_bad = cur_archive in bad_archives
                filesplits.append(FileSplit(cur_split_start, cur_split_end, is_bad))
                state = GET_FILE_AND_ADDR
            else:
                continue

        if state == GET_FILE_AND_ADDR:
            if symbol.section == ".text":
                cur_file = symbol.filename
                cur_archive = symbol.archive
                cur_split_start = full_addr if full_addr.addr != 0x2000072 else OvAddr(-1, 0x2000000)
                state = LOOKING_FOR_END_OF_FILE

    output = "overlay numbers are in decimal, addresses are in hex\n===============================\n"
    output += "\n".join(f"file with start={full_addr_to_compact_str(filesplit.start)}, end={full_addr_to_compact_str(filesplit.end)}{' KNOWN BAD FILESPLIT' if filesplit.is_bad else ''}" for filesplit in filesplits)
    output += "\n"

    with open("dump_dp_us_filesplits_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
