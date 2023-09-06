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

import os
import glob
import regex as re

paren_num_regex = re.compile(r"(?<!(?:...if\s|while\s|.....\w))(-?)\((-?(?:[0-9]+|0x[0-9a-fA-F]+))\)")
gf_assert_str1_regex = re.compile(r"\bGF_ASSERT\(([^\n]*\"[^\n]*)\);", flags=re.MULTILINE)
remove_hex_padding_regex = re.compile(r"\b0x0+([1-9A-Fa-f][0-9A-Fa-f]*|0)\b")
pad_button_regex = re.compile(r"\((PAD_(?:BUTTON_(?:A|B|SELECT|START|R|L|X|Y)|KEY_(?:RIGHT|LEFT|UP|DOWN)))\)")

def remove_num_parens_check_minus(match_obj):
    minus_before_paren = match_obj.group(1)
    num = match_obj.group(2)
    if num[0] == "-" and minus_before_paren == "-":
        return num[1:]
    else:
        return f"{minus_before_paren}{num}"

def remove_num_parens_do_replacements(src_dir, dest_dir):
    replaced_any_file = False

    for filename in glob.glob(f"../{src_dir}/src/**/*.c", recursive=True) + glob.glob(f"../{src_dir}/include/**/*.h", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()
    
        output, num_replacements = paren_num_regex.subn(remove_num_parens_check_minus, contents)
    
        if num_replacements > 0:
            with open(filename.replace(src_dir, dest_dir), "w+") as f:
                f.write(output)
    
            filename_no_dir = filename.replace(f'../{src_dir}/', '')
            print(f"Processed {filename_no_dir}: {num_replacements} replacements")
            replaced_any_file = True

    return replaced_any_file

def remove_num_parens():
    cur_round = 1
    replaced_any_file = remove_num_parens_do_replacements("00jupc_retsam", "00jupc_retsam")
    if not replaced_any_file:
        return

    while True:
        print(f"cur_round: {cur_round}")
        replaced_any_file = remove_num_parens_do_replacements("00jupc_retsam", "00jupc_retsam")

        if not replaced_any_file:
            break
        cur_round += 1

def remove_gf_assert_str(match_obj):
    gf_assert_contents = match_obj.group(1)
    gf_assert_parts = gf_assert_contents.split("&&")
    if len(gf_assert_parts) == 1:
        return "GF_ASSERT(\"FALSE\");"
    elif len(gf_assert_parts) == 2:
        gf_assert_parts[0] = gf_assert_parts[0].strip()
        gf_assert_parts[1] = gf_assert_parts[1].strip()
        part0_is_0 = gf_assert_parts[0] == "0"
        part1_is_0 = gf_assert_parts[1] == "0"
        
        if '"' in gf_assert_parts[0]:
            if part1_is_0:
                gf_assert_parts = ["FALSE"]
            else:
                gf_assert_parts = [gf_assert_parts[1]]
                #gf_assert_parts[0] = "FALSE"
        elif '"' in gf_assert_parts[1]:
            if part0_is_0:
                gf_assert_parts = ["FALSE"]
            else:
                gf_assert_parts = [gf_assert_parts[0]]
                #gf_assert_parts[1] = "FALSE"
        else:
            raise RuntimeError()
   
        new_gf_assert_contents = f"GF_ASSERT({' && '.join(gf_assert_parts)});"
        return new_gf_assert_contents
    else:
        raise RuntimeError()

def remove_gf_strings():
    for filename in glob.glob("../00jupc_retsam/src/**/*.c", recursive=True) + glob.glob("../00jupc_retsam/include/**/*.h", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = gf_assert_str1_regex.subn(remove_gf_assert_str, contents)
        if num_replacements > 0:
            with open(filename.replace("00jupc_retsam", "00jupc_retsam"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../00jupc_retsam/', '')}: {num_replacements} replacements")
            #break

        #if len(all_gf_assert_contents) != 0:
        #    #print(filename)
        #    #break
        #    #print(f"matches: \"{matches}\"")
        #    for gf_assert_contents in all_gf_assert_contents:
        #        new_gf_assert_parts = []
        #        gf_assert_parts = gf_assert_contents.split("&&")
        #        if len(gf_assert_parts) > 2:
        #            print(f"large gf assert: {gf_assert_contents}")
        #        elif len(gf_assert_parts) == 1:
        #            print(f"small gf assert: {gf_assert_contents}")
        #        else:
        #            if '"' in gf_assert_parts[0] and '"' in gf_assert_parts[1]:
        #                print(f"multiple quote in gf assert: {gf_assert_contents}")

                #for gf_assert_part in gf_assert_parts:
                #    if gf_assert_part
            #match_str = "\n".join(matches)
            #print(match_str)
            #break

def remove_hex_padding():
    for filename in glob.glob("../00jupc_retsam/src/**/*.c", recursive=True) + glob.glob("../00jupc_retsam/include/**/*.h", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = remove_hex_padding_regex.subn(r"0x\g<1>", contents)
        if num_replacements > 0:
            with open(filename.replace("00jupc_retsam", "00jupc_retsam"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../00jupc_retsam/', '')}: {num_replacements} replacements")
            #break

def remove_pad_button_parens():
    for filename in glob.glob("../00jupc_retsam/src/**/*.c", recursive=True) + glob.glob("../00jupc_retsam/include/**/*.h", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = pad_button_regex.subn(r"\g<1>", contents)
        if num_replacements > 0:
            with open(filename.replace("00jupc_retsam", "00jupc_retsam"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../00jupc_retsam/', '')}: {num_replacements} replacements")
            #break

def generic_replace(input_regex, replacement_template):
    for filename in glob.glob("../00jupc_retsam/src/**/*.c", recursive=True) + glob.glob("../00jupc_retsam/include/**/*.h", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = input_regex.subn(replacement_template, contents)
        if num_replacements > 0:
            with open(filename.replace("00jupc_retsam", "00jupc_retsam"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../00jupc_retsam/', '')}: {num_replacements} replacements")
            #break

def generic_replace_pokeplatinum_asm(input_regex, replacement_template):
    for filename in glob.glob("../pokeplatinum/asm/**/*.s", recursive=True) + glob.glob("../pokeplatinum/lib/**/*.s", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = input_regex.subn(replacement_template, contents)
        if num_replacements > 0:
            with open(filename.replace("pokeplatinum", "pokeplatinum"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../pokeplatinum/', '')}: {num_replacements} replacements")
            #break

dummy_macros_str = """
DWC_SetReportLevel
SDK_ASSERT
SDK_MINMAX_ASSERT
SDK_ASSERTMSG
OS_PutString
OS_TVPrintf
VCT_SetReportLevel
NNS_G3D_ASSERTMSG
"""

terminate_macros_str = """
OSi_Panic
OS_Panic
OS_TPanic
OSi_TPanic
"""

dummy_macros_regex = re.compile(r"^\s*(?:DWC_SetReportLevel|SDK_ASSERT|SDK_MINMAX_ASSERT|SDK_ASSERTMSG|OS_PutString|OS_TVPrintf|VCT_SetReportLevel|NNS_G3D_ASSERTMSG)\([^)(]*(?:\([^)(]*(?:\([^)(]*(?:\([^)(]*\)[^)(]*)*\)[^)(]*)*\)[^)(]*)*\);\n", flags=re.VERSION1|re.MULTILINE)
terminate_macros_regex = re.compile(r"(?:OSi_Panic|OS_Panic|OS_TPanic|OSi_TPanic)\([^)(]*(?:\([^)(]*(?:\([^)(]*(?:\([^)(]*\)[^)(]*)*\)[^)(]*)*\)[^)(]*)*\)")

def remove_dummied_macros():
    dummy_macros = dummy_macros_str.strip().splitlines()
    terminate_macros = terminate_macros_str.strip().splitlines()
    for filename in glob.glob("../pokeplatinum/src/**/*.c", recursive=True):
        with open(filename, "r") as f:
            contents = f.read()

        output, num_replacements = dummy_macros_regex.subn("", contents)
        output, num_replacements2 = terminate_macros_regex.subn(r"OS_Terminate()", output)
        num_replacements += num_replacements2

        if num_replacements > 0:
            with open(filename.replace("pokeplatinum", "pokeplatinum"), "w+") as f:
                f.write(output)

            print(f"Processed {filename.replace('../pokeplatinum/', '')}: {num_replacements} replacements")
            #break

def fix_asm_comments():
    with open("asm_comment_files.dump", "r") as f:
        asm_comment_files = f.read().split(" ")

    os.chdir("../pokeplatinum")

    for asm_comment_file in asm_comment_files:
        with open(asm_comment_file, "r") as f:
            contents = f.read()

        output = contents.replace(";", "//")

        with open(asm_comment_file, "w+") as f:
            f.write(output)

def main():
    MODE = 7

    if MODE == 0:
        remove_num_parens()
    elif MODE == 1:
        remove_gf_strings()
    elif MODE == 2:
        remove_hex_padding()
    elif MODE == 3:
        remove_pad_button_parens()
    elif MODE == 4:
        generic_replace(re.compile(r"while \(1\)"), r"while (TRUE)")
    elif MODE == 5:
        generic_replace(re.compile(r"\bCTRDG_IsPulledOut\(\) == 1\b"), r"CTRDG_IsPulledOut() == TRUE")
    elif MODE == 6:
        remove_dummied_macros()
    elif MODE == 7:
        fix_asm_comments()
    elif MODE == 8:
        generic_replace_pokeplatinum_asm(
            re.compile(r"^\t(ldr|str)\s+(r[0-7]|sb|sl|fp|ip|sp|lr),\s*\[\s*(r[0-7]|sb|sl|fp|ip|sp|lr),\s*#0\s*\]\s*,\s*#", flags=re.MULTILINE),
            r"\t\g<1> \g<2>, [\g<3>], #"
        )
    else:
        print("No mode selected!")

if __name__ == "__main__":
    main()
