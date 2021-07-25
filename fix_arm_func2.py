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

import re

push_regex = re.compile(r"^\tpush([a-z]{2})", flags=re.MULTILINE)
pop_regex = re.compile(r"^\tpop([a-z]{2})", flags=re.MULTILINE)
lsl_lsr_regex = re.compile(r"^\t(lsl|lsr|asr)(s?)((?:eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?) (\w{2}, \w{2}), (#(?:0x)?[0-9a-f]{1,2})$", flags=re.MULTILINE)
#ldm_stm_ib_regex = re.compile(r"^\t(ldm|stm)ib(\w{2})\b", flags=re.MULTILINE)
ldm_stm_regex = re.compile(r"^\t(ldm|stm)((?:eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?)\b", flags=re.MULTILINE)
ldm_stm_cond_regex = re.compile(r"^\t(ldm|stm)((?:\w{2})?)(eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)\b", flags=re.MULTILINE)
lsl_lsr_reg_regex = re.compile(r"^\t(lsl|lsr)(s?)((?:eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)?) (\w{2}, \w{2}), (\w{2})", flags=re.MULTILINE)
#lsl_lsr_reg_cond_regex = re.compile(r"^\t(lsl|lsr)(s?) (\w{2}, \w{2}), (\w{2})", flags=re.MULTILINE)
ldr_str_cond_regex = re.compile(r"^\t(ldr|str)(b|h|sb)(eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)\b", flags=re.MULTILINE)

#"eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le"

header = """	.include "macros.inc"
	.include "global.inc"
	.section .text
	.balign 4, 0
"""

functions_set = set(["FUN_020D3068", "FUN_020E1F6C", "FUN_020C4DB0", "FUN_020E2178", "FUN_020E1F6C", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020C4CF4", "FUN_020C4CF4", "FUN_020C4DB0", "FUN_020C4DB0", "FUN_020C4CF4", "FUN_020C4CF4", "FUN_020C331C", "FUN_020C3214"])
import dis_single_func
from xmap import XMap, OvAddr

extern_funcs = []

def fix_unk_funs(output):
    xmap_file = XMap("../master_cpuj00/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")
    functions = list(functions_set)
    replacements = {}
    todo_output = ""

    for function in functions:
        function_addr = int(function[4:], 16)
        full_addr = OvAddr(-1, function_addr)
        symbol = xmap_file.symbols_by_addr.get(full_addr, None)
        if symbol is not None:
            got_symbol = True
        else:
            full_addr = OvAddr(4, function_addr)
            symbol = xmap_file.symbols_by_addr.get(full_addr, None)
            if symbol is None:
                got_symbol = False
            got_symbol = True

        if got_symbol:
            if symbol.name == "std::__vector_common<true>::throw_length_error()":
                name = "_ZNSt15__vector_commonILb1EE18throw_length_errorEv"
            elif symbol.name == "cpp_20E3FD4":
                name = "_ZnamRKSt9nothrow_t"
            elif symbol.name == "cpp_20E4000":
                name = "_ZdaPv"
            else:
                name = symbol.name

            replacements[function] = name
        else:
            todo_output += f"{function}\n"
            #replacements.append(Replacement(function, )

    replacements2 = {}

    for extern_func in extern_funcs:
        symbol = xmap_file.symbols_by_name.get(extern_func, [])[0]
        from_func = f"FUN_{symbol.full_addr.addr:08X}"
        
        if from_func not in output:
            from_func = f"ov66_{symbol.full_addr.addr:07X}"
            if from_func not in output:
                todo_output += f"{symbol.name} {symbol.full_addr.addr:07x}\n"
                found_from_func = False
            else:
                found_from_func = True
        else:
            found_from_func = True

        if found_from_func:
            replacements2[from_func] = symbol.name

    output = dis_single_func.multiple_replace(output, replacements)
    output = dis_single_func.multiple_replace(output, replacements2)

    global_inc_output = ""
    for replacement in replacements.values():
        global_inc_output += f".extern {replacement}\n"

    for replacement in replacements2.values():
        global_inc_output += f".global {replacement}\n"
        
    with open("../master_cpuj00/src/library/crypto/global.inc", "w+") as f:
        f.write(global_inc_output)

    return output, todo_output

footer = """
	.rodata
p_16:
	.byte 0, 8, 1, 1, 1, 16, 1, 0, 0, 0

	.balign 4, 0
p_2:
	.byte 0, 8, 1, 1, 1, 1, 1, 0, 0, 0

	.balign 4, 0
p_4:
	.byte 0, 8, 1, 1, 1, 4, 1, 0, 0, 0

	.balign 4, 0
bits_7808:
	.byte 0, 1, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4

	.balign 4, 0
shift:
	.hword 0x6, 0x1, 0x2, 0x1, 0x3, 0x1, 0x2, 0x1
	.hword 0x4, 0x1, 0x2, 0x1, 0x3, 0x1, 0x2, 0x1
	.hword 0x5, 0x1, 0x2, 0x1, 0x3, 0x1, 0x2, 0x1
	.hword 0x4, 0x1, 0x2, 0x1, 0x3, 0x1, 0x2, 0x1

	.data

	.balign 4, 0
shift_val:
	.hword 0xdf37, 0x223, 0xdf36, 0x223, 0xdf34, 0x223, 0xdf30, 0x223
	.hword 0xdf28, 0x223, 0xdf18, 0x223, 0xdef8, 0x223
"""

def main():
    with open("libcrypto_in.s", "r") as f:
        input = f.read()

    output = header + input
    output = push_regex.sub(r"\tstm\1fd sp!,", output)
    output = pop_regex.sub(r"\tldm\1ia sp!,", output)
    output = lsl_lsr_regex.sub(r"\tmov\2\3 \4, \1 \5", output)
    output = lsl_lsr_reg_regex.sub(r"\tmov\2\3 \4, \1 \5", output)
    #output = ldm_stm_ib_regex.sub(r"\t\1\2ib", output)
    output = ldm_stm_regex.sub(r"\t\1\2ia", output)
    output = ldm_stm_cond_regex.sub(r"\t\1\3\2", output)
    output = ldr_str_cond_regex.sub(r"\t\1\3\2", output)
    output = output.replace("\tpush", "\tstmfd sp!,").replace("\tpop", "\tldmia sp!,").replace("@", "//").replace(".4byte", ".word")

    output, todo_output = fix_unk_funs(output)

    output = output.replace("0x0223DEC4", "p_16")
    output = output.replace("0x0223DED0", "p_2")
    output = output.replace("0x0223DEDC", "p_4")
    output = output.replace("0x0223DEE8", "bits_7808")
    output = output.replace("0x0223F158", "shift_val")

    #lines = output.splitlines(keepends=True)

    #for i, line in enumerate(lines):
    #    if line.startswith("\tarm_func_start ov66_22483C4"):
    #        output_stop_index = i
    #        break
    #
    #output = "".join(lines[:i])
    output += footer

    #output = output.replace("\tlsr", "\tlsrs")

    #output = output.replace("popeq", "ldmeqia sp!,")
    #    .replace("popne", "ldmneia sp!,")
    #    .replace("pople", "ldmleia sp!,")
    #    .replace("pople", "ldmleia sp!,")
    #    .replace("pop", "ldmia sp!,")
    #    .replace("push", "stmfd sp!,")
    #    .replace

    with open("../master_cpuj00/src/library/crypto/libcrypto_ov97.s", "w+") as f:
        f.write(output)

    with open("ov97_todo_funs.dump", "w+") as f:
        f.write(todo_output)

if __name__ == "__main__":
    main()
