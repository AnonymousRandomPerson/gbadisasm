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
start_of_text_newlines_regex = re.compile(r"^\n+")

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " " # note: a space and not an empty string
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

def main():
    with open("msl_source_files.dump", "r") as f:
        source_files = [f"../00jupc_retsam/sdk/cw/ARM_EABI_Support/{filename}" for filename in f.read().strip().splitlines()]

    for filename in source_files + glob.glob("../00jupc_retsam/sdk/cw/ARM_EABI_Support/**/*.h", recursive=True):
        if "MSL_C++" in filename or filename.endswith(".cpp"):
            continue
        output_filename = filename.replace("00jupc_retsam", "00jupc_retsam")

        command = ("uncrustify", "-c", "1tbs2.cfg", "-f", filename, "-o", output_filename, "--no-backup", "-l", "C")
        #print(command)
        subprocess.run(command, check=True)

        with open(output_filename, "r", encoding="iso-8859-1") as f:
            contents = f.read()

        output = comment_remover(contents)
        output = start_of_text_newlines_regex.sub("", output)
        output = triple_plus_newline_regex.sub("\n\n", output).strip() + "\n"

        with open(output_filename, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
