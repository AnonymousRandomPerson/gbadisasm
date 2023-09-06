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
from wcmatch import glob as wcmatch_glob
import pathlib

triple_plus_newline_regex = re.compile(r"\n\n\n+")
extern_c_regex = re.compile(r"^extern\s+\"C\"", flags=re.MULTILINE)
if_elif_define_include_regex = re.compile(r"^(#\s*(?:if|elif|define|include|ifdef|ifndef|undef))\s+", flags=re.MULTILINE)
only_comment_regex = re.compile(r"^\s*//.*$", flags=re.MULTILINE)
trailing_comment_regex = re.compile(r"^(.*?)\s*//.*$", flags=re.MULTILINE)

# from https://stackoverflow.com/questions/844681/python-regex-question-stripping-multi-line-comments-but-maintaining-a-line-brea

comment_re = re.compile(
    r'(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)

def comment_replacer(match):
    start,mid,end = match.group(1,2,3)
    if mid is None:
        # single line comment
        return ''
    elif start is not None or end is not None:
        # multi line comment at start or end of a line
        return ''
    elif '\n' in mid:
        # multi line comment with line break
        return '\n'
    else:
        # multi line comment without line break
        return ' '

def remove_comments(text):
    return comment_re.sub(comment_replacer, text)

def main():
    #with open("msl_source_files.dump", "r") as f:
    #    source_files = f.read().strip().splitlines()

    for filename in wcmatch_glob.glob("../retsam_00jupc/sdk/NitroDWC/build/libraries/{ilobby,ppwlobby}/{include/**/*.h,src/*.cpp}", flags=(wcmatch_glob.GLOBSTAR | wcmatch_glob.BRACE | wcmatch_glob.NEGATE)):
        print(f"Uncrustifying {filename}!")
        with open(filename, "r", encoding="shift_jis") as f:
            contents = f.read()

        output_filename = filename#.replace("../retsam_00jupc/sdk/NitroDWC/build/libraries/", "uncrustify_ilobby_out/")
        pathlib.Path(output_filename).parent.mkdir(exist_ok=True, parents=True)

        with open(output_filename, "w+", encoding="utf8") as f:
            f.write(contents)

        command = ("uncrustify", "-c", "1tbs2.cfg", "-f", output_filename, "-o", output_filename, "--no-backup", "-l", "C")
        subprocess.run(command, check=True)

        #command = ("uncrustify", "-c", "cxx_template.cfg", "-f", output_filename, "-o", output_filename, "--no-backup", "-l", "CPP")
        #subprocess.run(command, check=True)
        
        #print(command)
        # cp932
        # shift_jisx0213

        with open(output_filename, "r", encoding="iso-8859-1") as f:
            contents = f.read()

        output = only_comment_regex.sub("\n", contents)
        output = trailing_comment_regex.sub(r"\g<1>", output)
        output = remove_comments(output)
        output = triple_plus_newline_regex.sub("\n\n", output).strip() + "\n"
        output = extern_c_regex.sub("extern \"C\"", output)
        output = if_elif_define_include_regex.sub(r"\g<1> ", output)
        output = output.replace("\t", "    ")
        #output = output.replace("< ", "<")
        #output = output.replace(" >", ">")

        with open(output_filename, "w+", encoding="shift_jis") as f:
            f.write(output)

if __name__ == "__main__":
    main()
