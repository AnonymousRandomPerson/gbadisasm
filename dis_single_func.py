# =============================================================================
# MIT License
# 
# Copyright (c) 2021 luckytyphlosion
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# =============================================================================

import argparse
import subprocess
import re
import xmap
from xmap import OvAddr
import yaml

flag_set_insn_regex = re.compile(r"^(\t(?:adc|add|and|asr|bic|cmn|eor|lsl|lsr|mov|mul|mvn|neg|orr|ror|sbc|sub))s\b", flags=re.MULTILINE)
blx_regex = re.compile(r"^\tblx (?!r([0-9])\b)", flags=re.MULTILINE)
rsb_regex = re.compile(r"^\trsb (\w+, \w+), #0", flags=re.MULTILINE) # neg \1
ldm_stm_regex = re.compile(r"^\t(ldm|stm)\b", flags=re.MULTILINE) # \0ia
#ldm_stm_regex_2 = re.compile(r"^((ldm|stm)ia \w+),/\1!,/
mul_arg_regex = re.compile(r"^\t(mul \w+, \w+), \w+", flags=re.MULTILINE)#/\1/
ldr_str_no_offset_regex = re.compile(r"^\t((?:ldr|str) r[0-7]), \[(r[0-7])\]")
find_pools_regex = re.compile(r"^\t(ldr r[0-7]), (_[0-9A-F]{8}) // =0x([0-9A-F]{8})", flags=re.MULTILINE)
remove_ldr_labels_regex = re.compile(r"^(_[0-9A-F]{8}: \.4byte 0x[0-9A-F]{8})", flags=re.MULTILINE)

class FuncAddr:
    __slots__ = ("name", "addr")

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr

def multiple_replace(input, rep_dict):
    if len(rep_dict) == 0:
        return input

    pattern = re.compile("\\b" + "\\b|\\b".join([re.escape(k) for k in sorted(rep_dict, key=len, reverse=True)]) + "\\b", flags=re.DOTALL)
    def multiple_replace_lambda(x):
        return rep_dict[x.group(0)]

    return pattern.sub(multiple_replace_lambda, input)

def dis_function(input_addr, rom_file, func_name, is_arm, fix_pools):
    if is_arm:
        func_type_str = "arm_func"
    else:
        func_type_str = "thumb_func"

    cfg_output = f"{func_type_str} 0x{input_addr:07x} {func_name}\n"
    with open("dis_single_func.cfg", "w+") as f:
        f.write(cfg_output)

    output = subprocess.check_output(["./ndsdisasm", rom_file, "-c", "dis_single_func.cfg"])
    lines = output.splitlines(keepends=True)

    func_label = f"{func_name}:"

    kept_lines = []
    for i, line in enumerate(lines):
        line = line.decode("utf-8")
        if line.startswith(func_label):
            func_label_line = line
            func_label_line_index = i
            break
    else:
        raise RuntimeError(f"Could not find function {func_name} in ndsdisasm output!")

    output = ""

    output += f"\n\t{func_type_str}_start {func_name}\n"
    output += func_label_line
    func_end_macro = f"\t{func_type_str}_end"
    for line in lines[func_label_line_index+1:]:
        line = line.decode("utf-8")
        output += line
        if line.startswith(func_end_macro):
            break

    output = output.replace("@", "//").replace(".align 2, 0", "// .align 2, 0")

    output = flag_set_insn_regex.sub(r"\1", output)
    output = blx_regex.sub(r"\tbl ", output)
    output = rsb_regex.sub(r"\tneg \1", output)
    output = ldm_stm_regex.sub(r"\g<0>ia", output)
    output = mul_arg_regex.sub(r"\t\1", output)
    output = ldr_str_no_offset_regex.sub(r"\t\1, [\2, #0]", output)

    if fix_pools:
        output, pool_values = find_collect_replace_pools(output)
        output = remove_ldr_labels_regex.sub(r"// \1", output)

    return output, pool_values

def create_xmap():
    return xmap.XMap("../master_cpuj00/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

class BaseromSyms:
    __slots__ = ("functions", "data")

    def __init__(self, filename="baserom_syms.yml"):
        with open(filename, "r") as f:
            baserom_syms = yaml.safe_load(f)

        self.functions = baserom_syms.get("functions", {})
        self.data = baserom_syms.get("data", {})

        self.mangle_todos()

    def mangle_todos(self):
        for from_name, to_name in self.functions.items():
            if to_name == "TODO":
                self.functions[from_name] = f"NitroMain // {from_name}" #f"TODO__fixme_FUN_{addr:08X}"

def fix_baserom_symbols(output, baserom_syms):
    rep_dict = {}
    for addr, name in baserom_syms.data.items():
        if type(addr) is not int:
            addr = int(addr, 16)
        rep_dict[f"0x{addr:08X}"] = name

    output = multiple_replace(output, rep_dict)
    return output

def fix_calls(output, xmap_file, baserom_syms, cutoff_addr=0x21D0000):
    lines = output.splitlines(keepends=True)
    func_addrs = set()

    for line in lines:
        if line.startswith("\tbl FUN_"):
            line = line.strip()
            func_addr = FuncAddr(line[3:], int(line[7:], 16))
            func_addrs.add(func_addr)

    cutoff_funcs = {}
    if baserom_syms is not None:
        rep_dict = dict(baserom_syms.functions)
    else:
        rep_dict = {}

    for func_addr in func_addrs:
        if func_addr.addr < cutoff_addr:
            ov_addr = OvAddr(-1, func_addr.addr)
            symbol = xmap_file.symbols_by_addr.get(ov_addr)
            if symbol is None:
                print(f"Warning: unknown function found! (unkfunc: {func_addr.name}")
            else:
                rep_dict[func_addr.name] = symbol.name
        else:
            cutoff_funcs[func_addr.name] = True

    cutoff_funcs = [func for func in cutoff_funcs.keys() if func not in rep_dict]
    output = multiple_replace(output, rep_dict)
    #output = output.replace("TODO__fix_me", "NitroMain // UNK_FUNC_FIX_ME")
    return output, cutoff_funcs

def find_collect_replace_pools(input):
    pool_values = set()

    def collect_pool_values(x):
        nonlocal pool_values
        pool_value = int(x.group(3), 16)
        pool_values.add(pool_value)
        return f"\t{x.group(1)}, =0x{x.group(3)} // {x.group(2)}"

    output = find_pools_regex.sub(collect_pool_values, input)
    return output, pool_values

def sub_pool_symbols(output, xmap_file, pool_values, cutoff_addr=0x21D0000):
    rep_dict = {}

    for pool_value in pool_values:
        if 0x2000000 <= pool_value < cutoff_addr:
            ov_addr = OvAddr(-1, pool_value)
            symbol = xmap_file.symbols_by_addr.get(ov_addr)
            if symbol is None:
                print(f"Warning: unknown symbol found! (addr: {pool_value:07x})")
            else:
                print(f"symbol.name: {symbol.name}")
                rep_dict[f"0x{pool_value:08X}"] = symbol.name

    output = multiple_replace(output, rep_dict)
    return output

def main(input_addr, baserom_file, mainrom_file, func_name, mainrom_output_file, baserom_output_file, is_arm, skip_mainrom, fix_pools, xmap_file=None):
    br_output, br_pool_values = dis_function(input_addr, baserom_file, func_name, is_arm, fix_pools)
    if xmap_file is None:
        xmap_file = create_xmap()
    baserom_syms = BaseromSyms()

    br_output, unk_funcs = fix_calls(br_output, xmap_file, baserom_syms, cutoff_addr=input_addr)
    if fix_pools:
        br_output = fix_baserom_symbols(br_output, baserom_syms)

    output = ""
    
    unk_funcs_str = "\n".join(unk_funcs)
    output += f"Unknown functions in baserom:\n{unk_funcs_str}\n"

    if not skip_mainrom:
        mr_output, mr_pool_values = dis_function(input_addr, mainrom_file, func_name, is_arm, fix_pools)
        mr_output, overlay_funcs = fix_calls(mr_output, xmap_file, None)
        mr_output = sub_pool_symbols(mr_output, xmap_file, mr_pool_values)
        overlay_funcs_str = '\n'.join(overlay_funcs)
        output += f"Overlay functions in mainrom:\n{overlay_funcs_str}\n"

        with open(mainrom_output_file, "w+") as f:
            f.write(mr_output)

    with open(baserom_output_file, "w+") as f:
        f.write(br_output)

    with open("missing_funcs.txt", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    BASEROM_FILE_DEFAULT = "pokeplatinum_us.nds"
    MAINROM_FILE_DEFAULT = "../master_cpuj00/bin/ARM9-TS/Rom/main.srl"

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input-addr", dest="input_addr", default=None)
    ap.add_argument("-b", "--baserom-file", dest="baserom_file", default=BASEROM_FILE_DEFAULT)
    ap.add_argument("-m", "--mainrom-file", dest="mainrom_file", default=MAINROM_FILE_DEFAULT)
    ap.add_argument("-f", "--func_name", dest="func_name", default=None)
    #ap.add_argument("-o", "--baserom-output-file", dest="baserom_output_file", default=None)
    #ap.add_argument("-u", "--mainrom-output-file", dest="mainrom_output_file", default=None)
    ap.add_argument("-a", "--arm", dest="arm", action="store_true", default=False)
    ap.add_argument("-s", "--skip-mainrom", dest="skip_mainrom", action="store_true", default=False)
    ap.add_argument("-x", "--fix-pools", dest="fix_pools", action="store_true", default=False)
    args = ap.parse_args()

    xmap_file = create_xmap()

    if args.input_addr is not None:
        input_addr = int(args.input_addr, 16)
    else:
        if args.func_name is None:
            raise RuntimeError("Must specify at least one of --input-addr or --func-name!")

        func_symbol = xmap_file.symbols_by_name[args.func_name][0]
        input_addr = func_symbol.full_addr.addr
        print(f"Using symbol with address {input_addr:07x} in filename {func_symbol.filename}!")

    if args.func_name is not None:
        func_name = args.func_name
    else:
        func_name = f"sub_{input_addr:07X}"

    #if args.output_file is not None:
    #    output_file = args.output_file
    #else:
    #    output_file = f"{func_name}.dump"

    mainrom_output_file = f"{func_name}-main.s"
    baserom_output_file = f"{func_name}.s"

    main(input_addr, args.baserom_file, args.mainrom_file, func_name, mainrom_output_file, baserom_output_file, args.arm, args.skip_mainrom, args.fix_pools)
