# =============================================================================
# MIT License
# 
# Copyright (c) 2022 luckytyphlosion
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

import glob
import re

class LineReader:
    __slots__ = ("_line_num", "_lines", "_filename")
    def __init__(self, lines, filename):
        self._lines = lines
        self._filename = filename
        self._line_num = 0

    def __iter__(self):
        while self._line_num < len(self._lines):
            yield self._lines[self._line_num]
            self._line_num += 1

    def __getitem__(self, index):
        return self._lines[index]

    def __len__(self):
        return len(self._lines)

    @property
    def cur_line(self):
        return self._lines[self._line_num]

    def next(self):
        self._line_num += 1
        return self._lines[self._line_num]

    @property
    def line_num(self):
        return self._line_num

    @property
    def filename(self):
        return self._filename

    def at_file_error(self, msg):
        raise RuntimeError(f"At {self._filename}:{self._line_num+1}: {msg}")

    def location(self):
        return f"{self._filename}:{self._line_num+1}"

    def clear_cur_line(self):
        self._lines[self._line_num] = ""

func_decl_ignored_files = ("/spl.h", "/rc4.h", "crypto/util.h", "/poke_net_gds.h", "/spl_field.h")
typedef_regex = re.compile(r"^typedef\s+(\w+)")
functype_regex = re.compile(r"^typedef(?:\s+const)?\s+\w+\s+\*?\s*\(\s*\*?\s*(\w+)\s*\)\s*\((.+)\)\s*;\s*$")
typedef_struct_decl_regex = re.compile(r"^typedef\s+struct\s+(\w+)\s+(\w+);")
struct_name_regex = re.compile(r"^struct\s+(\w+)\s*{")
typedef_struct_def_regex = re.compile(r"^typedef\s+struct\s+(\w+)\s*{")
functype_struct_field_regex = re.compile(r"^(\w+)\s+\*?\s*\(\s*\*?\s*(\w+)\s*\)\s*\((.+)\)\s*;")
func_decl_regex = re.compile(r"^(?!(?:typedef\s+|extern\s+|FS_EXTERN_OVERLAY))(?:static\s+)?(?:const\s+)?(?:struct|union|enum\s+)?(?!static\s+)(\w+)\s+(?:\*+\s*)?(\w+)\((.*)\)\s*;\s*")
func_def_regex = re.compile(r"^(?!typedef)(?:static\s+)?(?:const\s+)?(?:struct|union|enum\s+)?(\w+)\s+(?:\*+\s*)?(\w+) \((.*)\)$")
unk_padding_reserved_offset_regex = re.compile(r"^(?:(?:(?:unk|padding|reserved|unused|val[0-9]+)_[0-9A-Fa-f]+|val[0-9]+)(?:_(?:[0-9]|[1-2][0-9]|3[0-1]))?|padding2?|dummy)(?:_val[0-9]+(?:_[0-9]+)?)?(?:\[(?:[0-9]+|0x[0-9A-Fa-f]+)\])*(?:\s*:\s*(?:[0-9]|[1-2][0-9]|3[0-1]))?(?:\s+ATTRIBUTE_ALIGN\([0-9]+\))?;")
bitfield_only_regex = re.compile(r"^\s*:\s*(?:[0-9]|[1-2][0-9]|3[0-1]);")
comma_regex = re.compile(r"\s*,\s*")
unk_obj_parts_regex = re.compile(r"^Unk(?:Struct|FuncPtr|Union|Enum)_(?:ov([0-9]+)_)?([0-9A-F]{8})(.+)?$")
struct_union_enum_end_definition_regex = re.compile(r"^}\s?((\w|,|\s)+);")
lib_dependency_prefix_regex = re.compile("^(?:(?:NNS|DWC|GX|PPW_|WM|MIC|SND|RTC|UnkSPL|CRYPTORC4|FS|OS|VCT)\w*[a-z]|MATHRandContext)")
unk_func_regex = re.compile(r"^(?:include(?:_unk|_data)?(?:_ov[0-9]+)?|inline(?:_ov[0-9]+)?|sub|ov[0-9]+)_([0-9A-F]{1,8})")

NEWLINE = "\n"

sdk_types = {
    "fx64c", "fx64", "fx32", "fx16", "u8", "u16", "u32", "s8", "s16", "s32", "u64", "s64", "vu8", "vu16", "vu32", "vu64", "vs8", "vs16", "vs32", "vs64", "f32", "vf32", "REGType8", "REGType16", "REGType32", "REGType64", "REGType8v", "REGType16v", "REGType32v", "REGType64v", "BOOL", "int", "short", "long", "double", "float", "void", "char", "MtxFx32",
    "VecFx32",
    "VecFx16",
    "MtxFx44",
    "MtxFx43",
    "MtxFx33",
    "MtxFx22", "TPData", "MATHCRC16Table", "NNS_G2D_VRAM_TYPE"
}
struct_union_enum = {"struct", "union", "enum"}
good_struct_fields = {
    "unk_30[10 + 1];",
    "val2_reserved_01_7 : 1;",
    "unk_14A[8 + 1];",
    "unk_00_val2_unk_00;",
    "unk_00_val2_unk_01;",
    "unk_00_val2_unk_02;",
    "unk_00_val2_unk_03;",
    "unk_20[sizeof(UnkStruct_ov97_02236380_sub1)",
    "sizeof(UnkStruct_ov97_02236380_sub2)",
    "sizeof(UnkStruct_ov97_02236380_sub3)",
    "sizeof(UnkStruct_ov97_02236380_sub4)];",
    "unk_C8_val1_unk_00_0 : 1;",
    "unk_C8_val1_unk_00_1 : 1;",
    "unk_08_val1_unk_00_0 : 1;",
    "unk_08_val1_unk_00_1 : 1;",
    "unk_08_val1_unk_00_2 : 1;",
    "unk_08_val1_unk_00_3 : 1;",
    "unk_08_val1_unk_00_4 : 1;",
    "unk_08_val1_unk_00_5 : 1;",
    "unk_08_val1_unk_00_6 : 1;",
    "unk_08_val1_unk_00_7 : 1;",
    "unk_08_val1_unk_00_8 : 1;",
    "unk_08_val1_unk_00_9 : 1;",
    "unk_08_val1_unk_00_10 : 1;",
    "unk_08_val1_unk_00_11 : 1;",
    "unk_08_val1_unk_00_12 : 1;",
    "unk_08_val1_unk_00_13 : 1;",
    "unk_0C[50 + 1];",
    "unk_08[sizeof(UnkStruct_02075454)",
    "sizeof(UnkStruct_02075454_1)",
    "sizeof(UnkStruct_02075454_2)",
    "sizeof(UnkStruct_02075454_3)];",
    "unk_04[];",
    "unk_04[NELEMS(Unk_ov19_021DFDF0)];",
    "unk_08[NELEMS(Unk_ov19_021DFDF0)];",
    "unk_84_val1_unk_00;",
    "unk_84_val1_unk_02;",
    "unk_04_val1_unk_00;",
    "unk_04_val1_unk_02;",
    "unk_04_val1_unk_04;",
    "unk_04_val1_unk_06;",
    "unk_0C_val1_unk_00;",
    "unk_0C_val1_unk_02;",
    "unk_0C_val1_unk_04;",
    "unk_0C_val1_unk_06;",
    "unk_04_val1_unk_00;",
    "unk_04_val1_unk_02;",
    "unk_04_val1_unk_04;",
    "unk_04_val1_unk_06;",
    "unk_0C_val1_unk_00;",
    "unk_0C_val1_unk_02;",
    "unk_0C_val1_unk_04;",
    "unk_0C_val1_unk_06;",
    "unk_04_val1_unk_00;",
    "unk_04_val1_unk_02;",
    "unk_04_val1_unk_04;",
    "unk_04_val1_unk_06;",
    "unk_0C_val1_unk_00;",
    "unk_0C_val1_unk_02;",
    "unk_0C_val1_unk_04;",
    "unk_0C_val1_unk_06;",
}

def parse_struct_or_union(line_reader, output, bad_dependencies):
    contains_struct_name = line_reader.cur_line[:-1]
    #print(f"{line_reader.location()}: struct def start")
    bad_struct_fields = []

    line = line_reader.cur_line

    if line.startswith("struct") or line.startswith("union"):
        match_obj = struct_name_regex.match(line)
        if match_obj is None:
            if not line_reader.filename.endswith("ov60_0221F968.c"):
                line_reader.at_file_error(f"struct name regex failed! line: {line}")
            else:
                struct_name = None
        else:
            struct_name = match_obj.group(1)

        is_typedef = False
    elif line.startswith("typedef"):
        match_obj = typedef_struct_def_regex.match(line)
        if match_obj:
            struct_name = match_obj.group(1)
        else:
            struct_name = None
        is_typedef = True
    else:
        line_reader.at_file_error("")

    found_dependencies = []

    while True:
        line = line_reader.next()
        if line.startswith("}"):
            break

        stripped_line = line.strip()
        if stripped_line != "" and not stripped_line[-1] == "{" and not stripped_line.startswith("}"):
            stripped_field_keep_asterisk = line.replace("struct", "").replace("const", "").replace("volatile", "").replace("unsigned", "").strip()
            match_obj = functype_struct_field_regex.match(stripped_field_keep_asterisk)
            if match_obj:
                field_type = match_obj.group(1)
                functype_args = match_obj.group(3)
                functype_args_split = comma_regex.split(functype_args)
                non_param_param_names = []
                for arg in functype_args_split:
                    stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("unsigned ", "").replace("*", "").strip()
                    stripped_arg_split = stripped_arg.split()
                    if len(stripped_arg_split) == 2:
                        param_name = stripped_arg_split[1]
                        if not param_name.startswith("param") and param_name != "func":
                            non_param_param_names.append(param_name)
                    elif len(stripped_arg_split) != 1:
                        raise RuntimeError()
                if len(non_param_param_names) != 0:
                    output.append(f"{contains_struct_name} has functype with bad args: {', '.join(non_param_param_names)}\n")
            else:
                try:
                    stripped_field = stripped_field_keep_asterisk.replace("*", "").strip()
                    field_type, rest_of_field = stripped_field.split(maxsplit=1)
                except ValueError:
                    line_reader.at_file_error(f"Bad struct/union field split: {line}")

                if field_type in struct_union_enum:
                    if False:
                        line_reader.at_file_error(f"functype struct field returning struct/union/enum! line: {line}")

                    dependency = rest_of_field.split(maxsplit=1)[0]
                else:
                    dependency = field_type

                rest_of_field = rest_of_field.strip()

                if not unk_padding_reserved_offset_regex.match(rest_of_field) and not bitfield_only_regex.match(rest_of_field) and rest_of_field not in good_struct_fields:
                    bad_struct_fields.append(rest_of_field)
                found_dependencies.append(dependency)

    if struct_name is not None:
        found_dependencies.append(struct_name)

    if is_typedef:
        match_obj = struct_union_enum_end_definition_regex.match(line)
        if match_obj:
            typedef_struct_name = match_obj.group(1)
            if "," in typedef_struct_name:
                found_dependencies.extend(real_typedef_struct_name.strip() for real_typedef_struct_name in typedef_struct_name.split(","))
            else:
                found_dependencies.append(typedef_struct_name.strip())
        else:
            typedef_struct_name = None

    for found_dependency in found_dependencies:
        if found_dependency in sdk_types or lib_dependency_prefix_regex.match(found_dependency) is not None:
            continue
        elif not unk_obj_parts_regex.match(found_dependency):
            bad_dependencies.add(found_dependency)

    if len(bad_struct_fields) != 0:
        output.append(f"Bad struct fields:\n{NEWLINE.join(bad_struct_fields)}\n")


func_decl_hardcodes = {
    "ov4_021D2170", "ov4_021D2EF4", "SPL_LoadTexByCallbackFunction",
    "SPL_LoadTexPlttByCallbackFunction", 
    "SPL_CreateWithInitialize", "CRYPTO_SetAllocator", "ov19_021D60FC"
}

ignored_func_defs = {"ov4_021D2170", "ov4_021D2EF4", "ov19_021D60FC", "ov97_0222DF70", "ov97_02231088"}

def main():
    full_output = []

    for filename in glob.glob("../00jupc_retsam/include/**/*.h", recursive=True) + glob.glob("../00jupc_retsam/src/**/*.c", recursive=True):
        with open(filename, "r") as f:
            lines = f.readlines()

        output = []
        bad_dependencies = set()
        line_reader = LineReader(lines, filename)
        #output.append()

        for line in line_reader:
            match_obj = functype_regex.match(line)
            if match_obj:
                functype_name = match_obj.group(1)
                functype_args = match_obj.group(2)
                functype_args_split = comma_regex.split(functype_args)
                non_param_param_names = []
                for arg in functype_args_split:
                    stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("*", "").strip()
                    stripped_arg_split = stripped_arg.split()
                    if len(stripped_arg_split) == 2:
                        param_name = stripped_arg_split[1]
                        if not param_name.startswith("param") and param_name != "func":
                            non_param_param_names.append(param_name)
                    elif len(stripped_arg_split) != 1:
                        raise RuntimeError()

                if len(non_param_param_names) != 0:
                    output.append(f"{functype_name} has bad param names: {', '.join(non_param_param_names)}\n")
            else:
                is_struct_or_union_def = False
                match_obj = typedef_regex.match(line)
                if match_obj:
                    typedef_type = match_obj.group(1)
                    if typedef_type in ("struct", "union") and line.endswith("{\n"):
                        is_struct_or_union_def = True
                elif (line.startswith("struct") or line.startswith("union")) and not line.endswith(";\n") and "(" not in line:
                    is_struct_or_union_def = True

                if is_struct_or_union_def:
                    parse_struct_or_union(line_reader, output, bad_dependencies)
                else:
                    match_obj = func_decl_regex.match(line.replace("const ", ""))
                    functype_args = ""
                    if match_obj:
                        functype_name = match_obj.group(2)

                        if functype_name not in func_decl_hardcodes:
                            functype_args = match_obj.group(3)
                    else:
                        match_obj = func_def_regex.match(line.replace("const ", ""))
                        if match_obj:
                            functype_name = match_obj.group(2)
                            if functype_name not in ignored_func_defs:
                                functype_args = match_obj.group(3)

                    if functype_args != "":
                        if not unk_func_regex.match(functype_name) and not filename.endswith("spl.h") and not filename.endswith("poke_net_gds.h") and not filename.endswith("rc4.h") and not filename.endswith("sign.h") and functype_name not in {"NitroStaticInit", "NitroMain"}:
                            output.append(f"{line_reader.location()}: {functype_name} is non-unk!\n")
                        functype_args_split = comma_regex.split(functype_args)
                        non_param_param_names = []

                        for arg in functype_args_split:
                            stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("unsigned ", "").replace("*", "").strip()
                            stripped_arg_split = stripped_arg.split()
                            if len(stripped_arg_split) == 2:
                                param_name = stripped_arg_split[1]
                                if not param_name.startswith("param") and param_name not in {"func", "dummy", "dummy1", "dummy2"}:
                                    non_param_param_names.append(param_name)
                            elif len(stripped_arg_split) != 1:
                                line_reader.at_file_error(f"arg: {arg}")

                        if len(non_param_param_names) != 0:
                            output.append(f"{functype_name} has bad param names: {', '.join(non_param_param_names)}\n")
                    

        if len(bad_dependencies) != 0:
            output.append(f"Bad types:\n{NEWLINE.join(bad_dependencies)}\n")

        if len(output) != 0:
            full_output.append(f"\n== {filename} ==\n")
            full_output.extend(output)

    with open("check_non_sanitized_fields_out.dump", "w+") as f:
        f.write("".join(full_output))

if __name__ == "__main__":
    main()
