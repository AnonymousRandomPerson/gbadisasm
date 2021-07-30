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

class AddrFile:
    __slots__ = ("addr", "file")
    def __init__(self, addr, file):
        self.addr = addr
        self.file = file

def main():
    output = ""
    addr_files = []

    with open("addr_to_file.dump", "r") as f:
        for line in f:
            line = line.strip()
            filenum, addr, filename = line.split()
            addr_files.append(AddrFile(int(addr, 16), filename))

    addr_files_sorted = sorted(addr_files, key=lambda x: x.addr)
    output = "\n".join(f"{addr_file.file} \\" for addr_file in addr_files_sorted) + "\n"

    with open("fix_file_order_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
