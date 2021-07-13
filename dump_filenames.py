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

def main():
    output = ""
    #START_ADDR = 0xfece0
    #END_ADDR = 0x100498
    START_ADDR = 0xfece0
    END_ADDR = 0x10042C

    with open("arm9_main.bin", "rb") as f:
        f.seek(START_ADDR)
        cur_addr = START_ADDR
        terminator_state = False
        while cur_addr < END_ADDR:
            byte = f.read(1)
            if byte == b"\0":
                if not terminator_state:
                    output += "\n"
                    terminator_state = True
            else:
                terminator_state = False
                c = byte.decode("ascii")
                output += c

            cur_addr += 1


    with open("dump_filenames_main_out.txt", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
