# =============================================================================
# Copyright (c) 2023 luckytyphlosion
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
import subprocess
import glob

triple_plus_newline_regex = re.compile(r"\n\n\n+")
extern_c_regex = re.compile(r"^extern\s+\"C\"", flags=re.MULTILINE)
if_elif_define_include_regex = re.compile(r"^(#\s*(?:if|elif|define|include|ifdef|ifndef|undef))\s+", flags=re.MULTILINE)

def main():
    #with open("msl_source_files.dump", "r") as f:
    #    source_files = f.read().strip().splitlines()

    for filename in glob.glob("../00jupc_retsam/sdk/cw/ARM_EABI_Support/**/*.h", recursive=True):
        if "MSL_C++" in filename:
            continue
        output_filename = filename.replace("00jupc_retsam", "00jupc_retsam")
        command = ("uncrustify", "-c", "1tbs2.cfg", "-f", filename, "-o", output_filename, "--no-backup", "-l", "C")
        #print(command)
        subprocess.run(command, check=True)

        with open(output_filename, "r", encoding="iso-8859-1") as f:
            contents = f.read()

        output = triple_plus_newline_regex.sub("\n\n", contents).strip() + "\n"
        output = extern_c_regex.sub("extern \"C\"", output)
        output = if_elif_define_include_regex.sub(r"\g<1> ", output)

        with open(output_filename, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
