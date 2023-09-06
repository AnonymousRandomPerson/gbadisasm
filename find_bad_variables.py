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
import pathlib

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

func_def_regex = re.compile(r"^(?!typedef)(?:static\s+)?(?:const\s+)?(?:struct|union|enum\s+)?(\w+)\s+(?:\*+\s*)?(\w+) \((.*)\)$")

unk_variable_regex = re.compile(r"^(?:v[0-9]+|unk_[0-9A-F]+|[Uu]nk_(?:ov[0-9]+_)?[0-9A-F]{8})$")
variable_def_regex = re.compile(r"^(?!typedef|return|goto)(?:static\s+)?(?:const\s+)?(?:struct|union|enum\s+)?(\w+)\s+(\w+)((?:,\s*\w+)*)(?:\[(?:[0-9]+|0x[0-9A-Fa-f]+|)\])*(?:;|\s+=\s+[^;]+;|\s+=\s+{)")
variable_anon_struct_regex = re.compile(r"^\s*}\s*(\w+)\s*\s*=\s*")
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
okay_non_unk_variables = {"i", "dummy", "dummy2"}
file_specific_okay_non_unk_variables = {
    "unk_0209BDF8.c": {"result"},
    "unk_02014000.c": {"count"},
    "ov33_02256474.c": {"x", "y"},
    "ov42_022561C0.c": {"x", "y"},
    "ov87_021D106C.c": {"x", "y"}
}


def main():
    full_output = []

    for filename in glob.glob("../pokeplatinum/src/**/*.c", recursive=True):
        with open(filename, "r") as f:
            lines = f.readlines()

        file_output = []
        line_reader = LineReader(lines, filename)
        basename = pathlib.Path(filename).name
        #output.append()
        
        for line in line_reader:
            match_obj = func_def_regex.match(line.replace("const ", ""))
            if match_obj:
                func_name = match_obj.group(2)
                function_output = []

                while True:
                    line = line_reader.next()
                    if line.startswith("}"):
                        break

                    line_stripped = line.strip().replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("unsigned ", "").replace("*", "").strip()
                    match_obj = variable_def_regex.match(line_stripped)
                    if match_obj:
                        variables_str = match_obj.group(2) + match_obj.group(3)
                        variables = variables_str.split(", ")
                        bad_variables = []
                        for variable in variables:
                            variable = variable.strip()
                            if not unk_variable_regex.match(variable) and variable not in okay_non_unk_variables:
                                okay_variables_for_file = file_specific_okay_non_unk_variables.get(basename)
                                if okay_variables_for_file is None or variable not in okay_variables_for_file:
                                    bad_variables.append(variable)

                        if len(bad_variables) > 0:
                            function_output.append(f"{line_reader.location()}: variables {', '.join(bad_variables)} are bad.\n")
                            #function_output.append(f"    original line: {line[:-1]}\n")
                    else:
                        match_obj = variable_anon_struct_regex.match(line)
                        if match_obj:
                            print(f"anon struct var: {match_obj.group(1)}")

                if len(function_output) > 0:
                    file_output.append(f"=== In function {func_name} ===\n")
                    file_output.extend(function_output)
                    file_output.append("\n")

        if len(file_output) > 0:
            full_output.append(f"== In file {filename} ==\n")
            full_output.extend(file_output)
            full_output.append("\n")


    if len(full_output) > 0:
        print("Found bad variables!")

    with open("find_bad_variables_out.dump", "w+") as f:
        f.write("".join(full_output))

if __name__ == "__main__":
    main()
