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


import subprocess
import itertools
import glob
import re

triple_plus_newline_regex = re.compile(r"\n\n\n+")

def main():
    for filename in itertools.chain(glob.glob("../00jupc_retsam/sdk/NitroDWC/include/**/*.h", recursive=True)):
        #command = ("uncrustify", "-c", "1tbs2.cfg", "-f", filename, "-o", filename, "--no-backup", "-l", "C")
        #print(command)
        #subprocess.run(command, check=True)
        with open(filename, "r") as f:
            contents = f.read()

        output = triple_plus_newline_regex.sub("\n\n", contents).strip() + "\n"

        with open(filename, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
