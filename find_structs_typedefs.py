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

import os
import re
import shutil
import pathlib
import glob
import itertools
import functools
from xmap import XMap

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

    def at_file_error(self, msg):
        raise RuntimeError(f"At {self._filename}:{self._line_num+1}: {msg}")

    def location(self):
        return f"{self._filename}:{self._line_num+1}"

# typedef struct
# typedef union
# typedef enum
# typedef funcptr
# struct
# union
# enum

TYPEDEF_STRUCT_DECL = 0
TYPEDEF_STRUCT_DEF = 1

class ExternConstDecl:
    __slots__ = ("name", "contents", "dependencies")

    def __init__(self, name, contents, dependencies):
        self.name = name
        self.contents = contents
        self.dependencies = tuple(dependencies)

class TypedefStructDecl:
    __slots__ = ("name", "contents", "source", "filename", "include_filename", "full_filename", "header_guard")

    def __init__(self, name, contents, source):
        self.name = name
        self.contents = contents
        self.source = source

class TypedefStructDef:
    __slots__ = ("name", "contents", "source", "dependencies", "filename", "include_filename", "full_filename", "header_guard")

    def __init__(self, name, contents, source, dependencies):
        self.name = name
        self.contents = contents
        self.source = source
        self.dependencies = tuple(dependencies)

class EnumDef:
    __slots__ = ("name", "contents", "include_filename")

    def __init__(self, name, contents):
        self.name = name
        self.contents = contents
        self.include_filename = "\"enums.h\""

dummy_enum_def = EnumDef("<enum>", "")

class FuncTypeDef:
    __slots__ = ("name", "contents", "dependencies", "filename", "include_filename", "full_filename", "header_guard")

    def __init__(self, name, contents, dependencies):
        self.name = name
        self.contents = contents
        self.dependencies = tuple(dependencies)

class FuncDecl:
    __slots__ = ("name", "contents", "dependencies")

    def __init__(self, name, contents, dependencies):
        self.name = name
        self.contents = contents
        self.dependencies = tuple(dependencies)

class NitroSDKType:
    __slots__ = ("name", "include_filename")

    def __init__(self, name, include_filename):
        self.name = name
        self.include_filename = include_filename

class HeaderInfo:
    __slots__ = ("filename", "basename", "objs", "includes", "resolved")

    def __init__(self, filename):
        self.filename = filename
        self.basename = pathlib.Path(filename).name
        #print(f"self.basename: {self.basename}")
        self.objs = []
        self.includes = []
        self.resolved = False

ov_addr_regex = re.compile(r"^ov([0-9]+)_[0-9A-F]{8}")

class FuncDeclHeader:
    __slots__ = ("name", "contents", "filename", "include_filename", "full_filename", "header_guard", "contents_list", "dependencies")

    def __init__(self, filename):
        self.filename = filename
        self.name = str(pathlib.Path(self.filename).with_suffix(''))
        self.contents = ""
        if self.filename.startswith("unk"):
            include_filename_no_quotes = self.filename
        else:
            match_obj = ov_addr_regex.match(self.filename)
            if match_obj is None:
                raise RuntimeError(f"Found unsanitized filename {self.filename} in FuncDeclHeader!")
            overlay = int(match_obj.group(1))
            include_filename_no_quotes = f"overlay{overlay:03d}/{self.filename}"

        self.include_filename = f"\"{include_filename_no_quotes}\""

        self.full_filename = f"include/{include_filename_no_quotes}"
        self.header_guard = f"POKEPLATINUM_{self.name.upper()}_H"
        self.contents_list = []
        self.dependencies = []

    def add_func_decl(self, func_decl, symbol):
        self.contents_list.append((symbol.full_addr, func_decl.contents))
        self.dependencies.extend(func_decl.dependencies)

    def gen_header_and_write(self, object_name_to_object):
        if len(self.contents_list) == 0:
            return

        sorted_contents_list = tuple(x[1] for x in sorted(self.contents_list, key=lambda x: x[0]))
        self.contents = "".join(sorted_contents_list)
        return gen_header(self, object_name_to_object, "h_")

class PartitionedHeaderObjs:
    __slots__ = ("defs", "decls", "enums")

    def __init__(self, objs, filename):
        self.defs = {}
        self.decls = {}
        self.enums = {}
        for obj in objs:
            if isinstance(obj, TypedefStructDecl):
                old_obj = self.decls.get(obj.name)
                if old_obj is not None:
                    raise RuntimeError(f"{filename}: {obj.name} already in self.decls! old_obj.full_filename: {old_obj.full_filename}, obj.full_filename: {obj.full_filename}")
                self.decls[obj.name] = obj
            elif isinstance(obj, (TypedefStructDef, FuncTypeDef)):
                if obj.name in self.defs:
                    raise RuntimeError()
                self.defs[obj.name] = obj
            elif isinstance(obj, EnumDef):
                self.enums[obj.name] = obj
            else:
                raise RuntimeError(f"Unknown header obj type!: type(obj): {type(obj).__name__}")

struct_union_enum = set(("struct", "union", "enum"))

sdk_types = set((
    "fx64c", "fx64", "fx32", "fx16", "u8", "u16", "u32", "s8", "s16", "s32", "u64", "s64", "vu8", "vu16", "vu32", "vu64", "vs8", "vs16", "vs32", "vs64", "f32", "vf32", "REGType8", "REGType16", "REGType32", "REGType64", "REGType8v", "REGType16v", "REGType32v", "REGType64v", "BOOL", "int", "short", "long", "double", "float", "void", "char"
))

func_decl_hardcodes = {
    #"SPL_LoadTexByCallbackFunction": ("SPLManager",),
    #"SPL_LoadTexPlttByCallbackFunction": ("SPLManager",),
    #"SPL_CreateWithInitialize": ("SPLManager", "SPLEmitter_t"),
    #"CRYPTO_SetAllocator": (),
    "ov4_021D2170": (),
    "ov4_021D2EF4": (),
}

func_decl_ignored_files = ("/spl.h", "/rc4.h", "crypto/util.h", "/poke_net_gds.h", "/spl_field.h")

typedef_regex = re.compile(r"^typedef\s+(\w+)")
struct_union_enum_end_definition_regex = re.compile(r"^}\s?((\w|,|\s)+);")
typedef_struct_decl_regex = re.compile(r"^typedef\s+struct\s+(\w+)\s+(\w+);")
functype_regex = re.compile(r"^typedef(?:\s+const)?\s+\w+\s+\*?\s*\(\s*\*?\s*(\w+)\s*\)\s*\((.+)\)\s*;\s*$")
equal_regex = re.compile(r"\s*=\s*")
comma_regex = re.compile(r"\s*,\s*")
struct_name_regex = re.compile(r"^struct\s+(\w+)\s*{")
typedef_struct_def_regex = re.compile(r"^typedef\s+struct\s+(\w+)\s*{")
word_regex = re.compile(r"^\w+$")
eightchar_hex_regex = re.compile(r"^[0-9A-F]{8}")
include_regex = re.compile(r"#include\s+\"([^\"]+)\"")
library_include_regex = re.compile(r"#include\s+<([^\"]+)>")
ov_regex = re.compile(r"ov([0-9]+)")
gf_lib_type_regex = re.compile(r"^(?:SPL|CRYPTORC4|DWC_LOBBY|pDWC_LOBBY)")
object_regex = re.compile(r"(?<!typedef\sstruct\s)(?!}\s*)(Unk(Struct|FuncPtr|Union|Enum)_(?:ov[0-9]+_)?[0-9A-F]{8}\w*\b)(?!;)")
#local_object_regex = re.compile(r"^\s*}\s*(Unk(Struct|FuncPtr|Union|Enum)_(?:ov[0-9]+_)?[0-9A-F]{8}\w*\b)\s*;")
unk_obj_parts_regex = re.compile(r"^Unk(?:Struct|FuncPtr|Union)_(?:ov([0-9]+)_)?([0-9A-F]{8})(.+)?$")
unk_obj_filename_parts_regex = re.compile(r"^(?:\"|<)?(?:struct|funcptr|union)_(?:ov([0-9]+)_)?([0-9A-F]{8})([^\.]+)?\.h(?:\"|>)?$")
functype_struct_field_regex = re.compile(r"^(\w+)\s+\*?\s*\(\s*\*?\s*(\w+)\s*\)\s*\((.+)\)\s*;")
func_decl_regex = re.compile(r"^(?!(?:extern\s+|FS_EXTERN_OVERLAY))(?:struct|union|enum\s+)?(\w+)\s*\*?\s*(\w+)\((.+)\)\s*;\s*$")
extern_const_symbol_regex = re.compile(r"^extern\s+const\s+(\w+)\s+(\w+)(.+);\s*$")

nitro_sdk_types = (
    NitroSDKType("WMBssDesc", "<nitro/wm.h>"),
    NitroSDKType("VecFx32", "<nitro/fx/fx.h>"),
    NitroSDKType("VecFx16", "<nitro/fx/fx.h>"),
    NitroSDKType("MtxFx44", "<nitro/fx/fx.h>"),
    NitroSDKType("MtxFx43", "<nitro/fx/fx.h>"),
    NitroSDKType("MtxFx33", "<nitro/fx/fx.h>"),
    NitroSDKType("MtxFx22", "<nitro/fx/fx.h>"),
    NitroSDKType("RTCDate", "<nitro/rtc.h>"),
    NitroSDKType("RTCTime", "<nitro/rtc.h>"),
    NitroSDKType("WMscanParam", "<nitro/wm.h>"),
    NitroSDKType("WMbssDesc", "<nitro/wm.h>"),
    NitroSDKType("GXDispMode", "<nitro/gx.h>"),
    NitroSDKType("GXBGMode", "<nitro/gx.h>"),
    NitroSDKType("GXBG0As", "<nitro/gx.h>"),
    NitroSDKType("GXCaptureSize", "<nitro/gx.h>"),
    NitroSDKType("GXCaptureMode", "<nitro/gx.h>"),
    NitroSDKType("GXCaptureSrcA", "<nitro/gx.h>"),
    NitroSDKType("GXCaptureSrcB", "<nitro/gx.h>"),
    NitroSDKType("GXCaptureDest", "<nitro/gx.h>"),
    NitroSDKType("GXRgb", "<nitro/gx.h>"),
    NitroSDKType("GXPolygonMode", "<nitro/gx.h>"),
    NitroSDKType("MATHRandContext32", "<nitro/math.h>"),
    NitroSDKType("OSArenaId", "<nitro/os.h>"),
    NitroSDKType("TPData", "<nitro.h>"),
    NitroSDKType("FSOverlayID", "<nitro/fs.h>"),
)

hardcoded_struct_deps = {
    "UnkStruct_ov97_0223685C": ["UnkStruct_ov97_02236380_sub1", "UnkStruct_ov97_02236380_sub2", "UnkStruct_ov97_02236380_sub3", "UnkStruct_ov97_02236380_sub4"],
    "UnkStruct_02073C74_sub1": ["UnkStruct_02075454", "UnkStruct_02075454_1", "UnkStruct_02075454_2", "UnkStruct_02075454_3"]
}

def parse_struct_or_union(line_reader, is_typedef=True):
    empty_typedef_structs_part = ""

    cur_struct = line_reader.cur_line
    if not is_typedef:
        match_obj = struct_name_regex.match(cur_struct)
        if not match_obj:
            line_reader.at_file_error(f"struct name regex failed! line: {cur_struct}")
        struct_name = match_obj.group(1)
    else:
        match_obj = typedef_struct_def_regex.match(cur_struct)
        if match_obj:
            typedef_struct_source = match_obj.group(1)
        else:
            empty_typedef_structs_part += f"{line_reader.location()}: Typedef struct no name\n"
            typedef_struct_source = None

    dependencies = []

    while True:
        line = line_reader.next()
        stripped_line = line.strip()
        cur_struct += line
        if line.startswith("}"):
            break
            #if "{" in line:
            #    if not line.endswith("{\n"):
            #        open_bracket_in_struct_def += f"{line_reader.location()}: {line}\n"
        elif stripped_line != "" and not stripped_line[-1] == "{" and not stripped_line.startswith("}"):
            stripped_field_keep_asterisk = line.replace("const", "").replace("volatile", "").replace("unsigned", "").strip()
            match_obj = functype_struct_field_regex.match(stripped_field_keep_asterisk)
            if match_obj:
                is_functype_struct_field = True
                field_type = match_obj.group(1)
                functype_args = match_obj.group(3)
            else:
                is_functype_struct_field = False
                try:
                    stripped_field = stripped_field_keep_asterisk.replace("*", "").strip()
                    field_type, rest_of_field = stripped_field.split(maxsplit=1)
                except ValueError:
                    line_reader.at_file_error(f"Bad struct/union field split: {line}")

            if field_type in struct_union_enum:
                if is_functype_struct_field:
                    line_reader.at_file_error(f"functype struct field returning struct/union/enum! line: {line}")

                dependency = rest_of_field.split(maxsplit=1)[0]
            elif field_type not in sdk_types:
                dependency = field_type
            else:
                dependency = None

            if dependency is not None:
                if word_regex.match(dependency):
                    dependencies.append(dependency)
                else:
                    empty_typedef_structs_part += f"{line_reader.location()}: Bad type {dependency}\n"

            if is_functype_struct_field:
                if is_typedef:
                    common_struct_name = typedef_struct_source
                else:
                    common_struct_name = struct_name

                empty_typedef_structs_part += f"{line_reader.location()}: Functype struct field detected\n"
                functype_args_split = comma_regex.split(functype_args)
                non_sdk_type_args = []
                for arg in functype_args_split:
                    stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("*", "").strip()
                    stripped_arg_split = stripped_arg.split()
                    if len(stripped_arg_split) not in (1, 2):
                        line_reader.at_file_error(f"functype has arg with more than two parts! line: {line}")
                    else:
                        arg_type = stripped_arg_split[0]

                    if arg_type not in sdk_types and arg_type != common_struct_name:
                        non_sdk_type_args.append(arg_type)

                dependencies.extend(non_sdk_type_args)

    if is_typedef:
        match_obj = struct_union_enum_end_definition_regex.match(line)
        if not match_obj:
            empty_typedef_structs_part += f"{line_reader.location()}, empty typedef struct (line: {line[:-1]})\n"
            typedef_struct_def = None
        else:
            typedef_struct_name = match_obj.group(1)
            hardcoded_deps = hardcoded_struct_deps.get(typedef_struct_name)
            if hardcoded_deps is not None:
                dependencies = hardcoded_deps
            if typedef_struct_name == typedef_struct_source:
                raise RuntimeError(f"typedef struct name == source! name & source: {typedef_struct_name}")
            if "," in typedef_struct_name:
                empty_typedef_structs_part += f"{line_reader.location()}: Comma in struct name {typedef_struct_name}!"
                typedef_struct_names = comma_regex.split(typedef_struct_name)
                typedef_struct_def = []
                for typedef_struct_name in typedef_struct_names:
                    typedef_struct_def.append(TypedefStructDef(typedef_struct_name, cur_struct, typedef_struct_source, dependencies))
            else:
                typedef_struct_def = TypedefStructDef(typedef_struct_name, cur_struct, typedef_struct_source, dependencies)
    else:
        typedef_struct_def = TypedefStructDef(struct_name, cur_struct, None, dependencies)

    return typedef_struct_def, empty_typedef_structs_part

        #if not typedef_struct_name.startswith("Unk"):
        #    print(f"Found non Unk struct: {typedef_struct_name}")
        #else:
        #    typedef_struct_header_name = f"{typedef_struct_name[3:].lower()}.h"
        #    found_typedef_struct_header_names += f"{typedef_struct_name} -> {typedef_struct_header_name}\n"

def parse_enum(line_reader, is_typedef=True):
    cur_enum = line_reader.cur_line
    cur_enum_values = ""
    while True:
        line = line_reader.next()
        stripped_line = line.strip()
        cur_enum += line
        if line.startswith("}"):
            break
            #if "{" in line:
            #    if not line.endswith("{\n"):
            #        open_bracket_in_struct_def += f"{line_reader.location()}: {line}\n"
        elif stripped_line != "":
            enum_name_and_value = equal_regex.split(stripped_line, maxsplit=1)
            if len(enum_name_and_value) == 2:
                enum_value = enum_name_and_value[1]
                cur_enum_values += f"{line_reader.location()}: {enum_value}\n"
            #try:
            #    field_type, rest_of_field = line.strip().split(maxsplit=1)
            #except ValueError:
            #    line_reader.at_file_error(f"Bad struct/union field split: {line}")
            #
            #if field_type in struct_union_enum:
            #    struct_union_enum_type = rest_of_field.split(maxsplit=1)[0]
            #    dependencies.append(struct_union_enum_type)
            #elif field_type not in sdk_types:
            #    dependencies.append(field_type)

    if is_typedef:
        match_obj = struct_union_enum_end_definition_regex.match(line)
        if not match_obj:
            cur_enum_values += f"{line_reader.location()}: empty enum struct (line: {line[:-1]})\n"
            #empty_typedef_structs_part = f"{line_reader.location()}, "
            #typedef_struct_def = None
            enum_name = None
        else:
            #empty_typedef_structs_part = None
            enum_name = match_obj.group(1)

        enum_def = EnumDef(enum_name, cur_enum)
    else:
        enum_def = EnumDef(None, cur_enum)

    return enum_def, cur_enum_values

def remove_duplicate_objs(objs):
    unduped_objs_dict = {id(obj): obj for obj in objs}
    return tuple(unduped_objs_dict.values())

def set_object_filenames_and_return_guard(obj, suffix):
    obj_name = obj.name
    if obj_name.startswith("SPL"):
        obj.include_filename = "\"library/spl.h\""
        return None
    elif obj_name.startswith("CRYPTORC4"):
        obj.include_filename = "<nitrocrypto/crypto/rc4.h>"
        return None
    elif obj_name.startswith("DWC_LOBBY") or obj_name.startswith("pDWC_LOBBY"):
        obj.include_filename = "\"wifi/dwc_lobbylib.h\""
        return None
    elif not obj_name.startswith("Unk"):
        raise RuntimeError(f"{obj_name} does not start with Unk!")

    split_name = obj_name.split("_")
    name_new_parts = []
    
    for part in split_name:
        part = part.replace("Unk", "")
        if not eightchar_hex_regex.match(part):
            part = part.lower()
        name_new_parts.append(part)
    
    filename_root = f"{'_'.join(name_new_parts)}{suffix}"
    filename_base = f"{filename_root}.h"
    match_obj = ov_regex.search(obj_name)
    if match_obj:
        include_filename = f"overlay{int(match_obj.group(1), 10):03d}/{filename_base}"
    else:
        include_filename = f"{filename_base}"
    
    full_filename = f"include/{include_filename}"
    header_guard = f"POKEPLATINUM_{filename_root.upper()}_H"
    
    obj.filename = filename_base
    obj.include_filename = f"\"{include_filename}\""
    obj.full_filename = full_filename
    obj.header_guard = header_guard

    return header_guard

def is_gf_lib_type(obj):
    obj_name = obj.name
    return gf_lib_type_regex.match(obj_name) is not None

class UnkObject:
    __slots__ = ("name", "overlay", "addr", "suffix")

    def __init__(self, name, overlay, addr, suffix):
        self.name = name
        self.overlay = -1 if overlay is None else int(overlay)
        self.addr = int(addr, 16)
        self.suffix = "" if suffix is None else suffix

    @classmethod
    def from_obj_name(cls, obj_name):
        match_obj = unk_obj_parts_regex.match(obj_name)
        if match_obj is None:
            raise ValueError(f"unk_object {obj_name} does not match unk object parts regex!")
        
        return cls(obj_name, match_obj.group(1), match_obj.group(2), match_obj.group(3))

    @classmethod
    def from_filename(cls, filename):
        match_obj = unk_obj_filename_parts_regex.match(filename)
        if match_obj is None:
            raise ValueError(f"unk_object {filename} does not match unk_obj_filename_parts_regex!")

        return cls(filename, match_obj.group(1), match_obj.group(2), match_obj.group(3))

def unk_obj_cmp_function(a, b):
    if a.name == b.name:
        return 0

    if a.overlay < b.overlay:
        return -1
    elif a.overlay > b.overlay:
        return 1
    else:
        if a.addr < b.addr:
            return -1
        elif a.addr > b.addr:
            return 1
        else:
            if a.suffix < b.suffix:
                return -1
            elif a.suffix > b.suffix:
                return 1
            else:
                return 0

#mic_types = set(("MICResult", "MICAutoParam"))

def gen_header(obj, object_name_to_object, debug_prefix=""):
    output = ""

    if is_gf_lib_type(obj):
        return ""

    dependency_full_filenames = []

    for dependency in obj.dependencies:
        if dependency == "<enum>":
            dependency_obj = dummy_enum_def
        else:
            dependency_obj = object_name_to_object.get(dependency)

        if dependency_obj is None:
            if dependency.startswith("NNS") or dependency == "MtxFx32":
                dependency_obj = NitroSDKType(dependency, "<nnsys.h>")
            elif dependency.startswith("DWC"):
                dependency_obj = NitroSDKType(dependency, "<dwc.h>")
            elif dependency.startswith("GX"):
                dependency_obj = NitroSDKType(dependency, "<nitro/gx.h>")
            elif dependency.startswith("PPW_"):
                dependency_obj = NitroSDKType(dependency, "<ppwlobby/ppw_lobby.h>")
            elif dependency.startswith("WM"):
                dependency_obj = NitroSDKType(dependency, "<nitro/wm.h>")
            elif dependency.endswith("_t"):
                dependency_obj = object_name_to_object.get(dependency[:-2])
            elif dependency.startswith("MATHRandContext"):
                dependency_obj = NitroSDKType(dependency, "<nitro/math.h>")
            elif dependency.startswith("MIC"):
                dependency_obj = NitroSDKType(dependency, "<nitro/spi.h>")
            elif dependency.startswith("SND"):
                dependency_obj = NitroSDKType(dependency, "<nitro/snd.h>")

            if dependency_obj is None:
                raise RuntimeError(f"Cannot find dependency {dependency} for obj {obj.name}!")

            object_name_to_object[dependency] = dependency_obj
        try:
            dependency_full_filenames.append(dependency_obj.include_filename)
            #dependencies_as_str += f"#include {}\n"
            if not dependency_obj.include_filename.endswith("_decl.h\""):
                output += f"Non-decl: {dependency_obj.include_filename}\n"
        except AttributeError:
            raise RuntimeError(f"Dependency {dependency} has no include_filename for obj {obj.name}!")

    unique_dependency_full_filenames = tuple(frozenset(dependency_full_filenames))
    non_unk_object_header_filenames = []
    unk_objects = []

    for dependency_full_filename in unique_dependency_full_filenames:
        try:
            unk_object = UnkObject.from_filename(dependency_full_filename)
            unk_objects.append(unk_object)
        except ValueError:
            non_unk_object_header_filenames.append(dependency_full_filename)
            output += f"Non-unk: {dependency_full_filename}\n"

    sorted_unique_includes = [unk_object.name for unk_object in sorted(unk_objects, key=functools.cmp_to_key(unk_obj_cmp_function))]
    dependencies_as_str = "".join(f"#include {sorted_unique_include}\n" for sorted_unique_include in sorted_unique_includes)
    if len(non_unk_object_header_filenames) != 0:
        dependencies_as_str += "\n" + "".join(f"#include {non_unk_object_header_filename}\n" for non_unk_object_header_filename in non_unk_object_header_filenames)

    try:
        header_guard = obj.header_guard
    except AttributeError:
        raise RuntimeError(f"Object {obj.name} has no header_guard! type(obj): {type(obj).__name__}")

    if dependencies_as_str != "":
        dependencies_as_str = "\n" + dependencies_as_str

    contents = f"""\
#ifndef {header_guard}
#define {header_guard}
{dependencies_as_str}
{obj.contents.strip()}

#endif // {header_guard}
"""
    full_filepath = pathlib.Path(f"{debug_prefix}{obj.full_filename}")
    full_filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(full_filepath, "w+") as f:
        f.write(contents)

    return output

special_headers = set((
    "nnsys.h", "src/data/arc_tool.dat"
))

def get_header_objs(header_info, header_infos):
    calculated_header_objs = get_header_objs_helper(header_info, header_infos, set())
    calculated_header_objs_dict = {id(header_obj): header_obj for header_obj in calculated_header_objs}
    return PartitionedHeaderObjs(calculated_header_objs_dict.values(), header_info.filename)

def get_header_objs_helper(header_info, header_infos, processed_includes):
    calculated_header_objs = list(header_info.objs)

    for include in header_info.includes:
        if include in special_headers:
            continue

        sub_header_info = header_infos.get(include)
        if sub_header_info is None:
            base_include = include.rsplit("/", maxsplit=1)[-1]
            sub_header_info = header_infos.get(base_include)
            if sub_header_info is None:
                raise RuntimeError(f"Could not find header_info for header {include} (base include: {base_include})!")

        if include not in processed_includes:
            processed_includes.add(include)
            sub_header_info_objs = get_header_objs_helper(sub_header_info, header_infos, processed_includes)
            calculated_header_objs.extend(sub_header_info_objs)

    return calculated_header_objs

def main():
    found_typedef_struct_header_names = ""
    found_typedef_nonstructs = ""
    empty_typedef_structs = ""
    open_bracket_in_struct_def = ""
    enum_locations = ""
    enum_values = ""
    struct_decl_locations = ""
    struct_def_locations = ""
    probably_func_decl_struct_returns = ""
    probably_func_def_struct_returns = ""
    functype_args_locations = ""
    functype_stripped_args = ""

    typedef_struct_decls = []
    struct_defs = []
    typedef_struct_defs = []
    enum_defs = []
    func_type_defs = []
    func_decls = {}
    extern_const_decls = []

    header_infos = {}

    with open("sanitized_src_files.txt", "r") as f:
        c_filenames = [f"../00jupc_retsam/{c_filename_partial}" for c_filename_partial in f.read().strip().splitlines() if c_filename_partial != "src/overlay060/ov60_0221F968.c"]

    def find_objects(filenames, filename_type):
        nonlocal found_typedef_struct_header_names
        nonlocal found_typedef_nonstructs
        nonlocal empty_typedef_structs
        nonlocal open_bracket_in_struct_def
        nonlocal enum_locations
        nonlocal enum_values
        nonlocal struct_decl_locations
        nonlocal struct_def_locations
        nonlocal probably_func_decl_struct_returns
        nonlocal probably_func_def_struct_returns
        nonlocal functype_args_locations
        nonlocal functype_stripped_args

        nonlocal typedef_struct_decls
        nonlocal struct_defs
        nonlocal typedef_struct_defs
        nonlocal enum_defs
        nonlocal func_type_defs
        nonlocal func_decls

        nonlocal header_infos

        typedef_struct_decl_dup_dict = {}

        for filename in filenames:
            print(f"{filename_type}: {filename}")
            with open(filename, "r") as f:
                lines = f.readlines()
    
            header_info = HeaderInfo(filename.replace("../00jupc_retsam/", ""))
            if header_info.basename in header_infos:
                raise RuntimeError(f"{header_info.basename} already in header_infos!")
    
            header_infos[header_info.basename] = header_info
            #if header_info.basename == "bg_system.h":
            #    print(f"header_infos[bg_system.h]: {header_infos['bg_system.h']}")
    
            line_reader = LineReader(lines, filename)
    
            for line in line_reader:
                match_obj = typedef_regex.match(line)
                if match_obj:
                    typedef_type = match_obj.group(1)
                    if typedef_type in ("struct", "union"):
                        if line.endswith(";\n"):
                            match_obj = typedef_struct_decl_regex.match(line)
                            if not match_obj:
                                line_reader.at_file_error(f"Unexpected typedef struct decl pattern! line: {line}")
                    
                            typedef_struct_source = match_obj.group(1)
                            typedef_struct_decl_name = match_obj.group(2)
                            typedef_struct_decl_old = typedef_struct_decl_dup_dict.get(typedef_struct_decl_name)
                            if typedef_struct_decl_old is not None:
                                if typedef_struct_decl_old.contents != line:
                                    line_reader.at_file_error(f"Found duplicate differing typedef struct decl! old: {typedef_struct_decl_old.contents.strip()}, new: {line.strip()}")
                                typedef_struct_decl = typedef_struct_decl_old
                            else:
                                typedef_struct_decl = TypedefStructDecl(typedef_struct_decl_name, line, typedef_struct_source)
                                typedef_struct_decl_dup_dict[typedef_struct_decl_name] = typedef_struct_decl

                            #if typedef_struct_decl_name in ("UnkStruct_0202CC84",):
                            #    if typedef_struct_decl_name not in found_duplicate_typedef_struct_decls:
                            #        typedef_struct_decl = TypedefStructDecl(typedef_struct_decl_name, line, typedef_struct_source)
                            #        header_info.objs.append(typedef_struct_decl)
                            #        typedef_struct_decls.append(typedef_struct_decl)
                            #        found_duplicate_typedef_struct_decls.add(typedef_struct_decl_name)
                            #else:
                            header_info.objs.append(typedef_struct_decl)
                            typedef_struct_decls.append(typedef_struct_decl)
                        elif line.endswith("{\n"):
                            typedef_struct_def, empty_typedef_structs_part = parse_struct_or_union(line_reader)
                            if typedef_struct_def is not None:
                                if isinstance(typedef_struct_def, list):
                                    typedef_struct_defs.extend(typedef_struct_def)
                                    header_info.objs.extend(typedef_struct_def)
                                else:
                                    typedef_struct_defs.append(typedef_struct_def)
                                    header_info.objs.append(typedef_struct_def)
                            if empty_typedef_structs_part != "":
                                empty_typedef_structs += empty_typedef_structs_part
                        else:
                            line_reader.at_file_error(f"Unknown struct typedef \"{line}\"!")
                    elif typedef_type == "enum":
                        enum_locations += f"{line_reader.location()}: {line}"
                        enum_def, cur_enum_values = parse_enum(line_reader)
                        enum_values += cur_enum_values
                        header_info.objs.append(enum_def)
                        enum_defs.append(enum_def)
                        #EnumDef
                        #pass
                    else:
                        match_obj = functype_regex.match(line)
                        if match_obj:
                            functype_name = match_obj.group(1)
                            functype_args = match_obj.group(2)
                            functype_args_locations += f"{line_reader.location()}: {line}"
                            functype_args_split = comma_regex.split(functype_args)
                            non_sdk_type_args = []
                            for arg in functype_args_split:
                                stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("*", "").strip()
                                stripped_arg_split = stripped_arg.split()
                                if len(stripped_arg_split) not in (1, 2):
                                    line_reader.at_file_error(f"functype has arg with more than two parts! line: {line}")
                                else:
                                    arg_type = stripped_arg_split[0]
    
                                if arg_type not in sdk_types:
                                    non_sdk_type_args.append(arg_type)
    
                            func_type_def = FuncTypeDef(functype_name, line, non_sdk_type_args)
                            if len(non_sdk_type_args) != 0:
                                functype_stripped_args += f"{line_reader.location()}: {', '.join(non_sdk_type_args)}\n"
                            header_info.objs.append(func_type_def)
                            func_type_defs.append(func_type_def)
                        else:
                            line_reader.at_file_error(f"Unknown typedef type \"{line}\"!")
                elif line.startswith("typedef"):
                    found_typedef_nonstructs += line
                elif line.startswith("struct") or line.startswith("union"):
                    if line.endswith(";\n"):
                        if "(" in line:
                            probably_func_decl_struct_returns += f"{line_reader.location()}: {line}"
                        else:
                            struct_decl_locations += f"{line_reader.location()}: {line}"
                    else:
                        if "(" in line:
                            probably_func_def_struct_returns += f"{line_reader.location()}: {line}"
                        else:
                            struct_def_locations += f"{line_reader.location()}: {line}"
                            typedef_struct_def, empty_typedef_structs_part = parse_struct_or_union(line_reader, is_typedef=False)
                            if isinstance(typedef_struct_def, list):
                                struct_defs.extend(typedef_struct_def)
                                header_info.objs.extend(typedef_struct_def)
                            else:
                                struct_defs.append(typedef_struct_def)
                                header_info.objs.append(typedef_struct_def)
    
                elif line.startswith("enum"):
                    enum_locations += f"{line_reader.location()}: {line}\n"
                    enum_def, cur_enum_values = parse_enum(line_reader, is_typedef=False)
                    enum_values += cur_enum_values
                    enum_defs.append(enum_def)
                else:
                    match_obj = include_regex.match(line)
                    if match_obj:
                        header_info.includes.append(match_obj.group(1))
                    elif not any(filename.endswith(func_decl_ignore_filename) for func_decl_ignore_filename in func_decl_ignored_files):
                        match_obj = func_decl_regex.match(line)
                        if match_obj:
                            functype_returntype = match_obj.group(1)
                            functype_name = match_obj.group(2)
                            non_sdk_type_args = []

                            if functype_returntype not in sdk_types:
                                non_sdk_type_args.append(functype_returntype)

                            functype_hardcoded_arg_deps = func_decl_hardcodes.get(functype_name)
                            if functype_hardcoded_arg_deps is not None:
                                non_sdk_type_args.extend(functype_hardcoded_arg_deps)
                            else:
                                functype_args = match_obj.group(3)
                                functype_args_split = comma_regex.split(functype_args)
    
                                for arg in functype_args_split:
                                    stripped_arg = arg.replace("const ", "").replace("volatile ", "").replace("struct ", "").replace("unsigned ", "").replace("*", "").strip()
                                    stripped_arg_split = stripped_arg.split()
                                    if len(stripped_arg_split) not in (1, 2):
                                        line_reader.at_file_error(f"functype has arg with more than two parts! line: {line}")
                                    else:
                                        arg_type = stripped_arg_split[0]
                
                                    if arg_type not in sdk_types:
                                        non_sdk_type_args.append(arg_type)

                            func_decl = FuncDecl(functype_name, line, non_sdk_type_args)
                            old_func_decl = func_decls.get(functype_name)
                            if old_func_decl is not None and old_func_decl.contents != line:
                                line_reader.at_file_error(f"{functype_name} has duplicate func decl! old: {old_func_decl.contents.strip()}, new: {line.strip()}")

                            func_decls[functype_name] = func_decl
                        else:
                            match_obj = extern_const_symbol_regex.match(line)
                            if match_obj:
                                extern_const_type = match_obj.group(1)
                                if extern_const_type not in sdk_types:
                                    dependencies = [extern_const_type]
                                else:
                                    dependencies = []

                                extern_const_name = match_obj.group(2)
                                extern_const_extra = match_obj.group(3)
                                if "U" in extern_const_extra:
                                    dependencies.append("<enum>")

                                extern_const_decl = ExternConstDecl(extern_const_name, line, dependencies)
                                extern_const_decls.append(extern_const_decl)

    find_objects(glob.glob("../00jupc_retsam/include/**/*.h", recursive=True), "header_filename")
    #for header_filename in itertools.chain(glob.glob("../00jupc_retsam/include/**/*.h", recursive=True), c_filenames):
    #for header_filename in :

    output = ""
    output += "== found_typedef_struct_header_names ==\n"
    output += found_typedef_struct_header_names
    output += "== found_typedef_nonstructs ==\n"
    output += found_typedef_nonstructs
    output += "== empty_typedef_structs ==\n"
    output += empty_typedef_structs
    output += "== open_bracket_in_struct_def ==\n"
    output += open_bracket_in_struct_def
    output += "== enum_locations ==\n"
    output += enum_locations
    output += "== enum_values ==\n"
    output += enum_values
    output += "== struct_decl_locations ==\n"
    output += struct_decl_locations
    output += "== struct_def_locations ==\n"
    output += struct_def_locations
    output += "== functype_args_locations ==\n"
    output += functype_args_locations
    output += "== functype_stripped_args ==\n"
    output += functype_stripped_args
    output += "== probably_func_decl_struct_returns ==\n"
    output += probably_func_decl_struct_returns
    output += "== probably_func_def_struct_returns ==\n"
    output += probably_func_def_struct_returns

    typedef_struct_decl_names = []
    typedef_struct_def_names = []
    struct_def_names = []
    func_type_def_names = []
    enum_names = []

    output += "== typedef_struct_decls ==\n"
    for typedef_struct_decl in typedef_struct_decls:
        output += f"{typedef_struct_decl.name}: {typedef_struct_decl.source}\n"
        typedef_struct_decl_names.append(typedef_struct_decl.name)

    output += "== typedef_struct_defs ==\n"
    for typedef_struct_def in typedef_struct_defs:
        output += f"{typedef_struct_def.name}: {', '.join(typedef_struct_def.dependencies)}\n"
        typedef_struct_def_names.append(typedef_struct_def.name)

    output += "== struct_defs ==\n"
    for struct_def in struct_defs:
        output += f"{struct_def.name}: {', '.join(struct_def.dependencies)}\n"
        struct_def_names.append(struct_def.name)

    output += "== func_type_defs ==\n"
    for func_type_def in func_type_defs:
        output += f"{func_type_def.name}: {', '.join(func_type_def.dependencies)}\n"
        func_type_def_names.append(func_type_def.name)

    output += "== enum_defs ==\n"
    for enum_def in enum_defs:
        output += f"{enum_def.name}\n"
        enum_names.append(enum_def.name)

    output += "== extern_const_decls ==\n"
    for extern_const_decl in extern_const_decls:
        output += f"{extern_const_decl.name}\n"
        enum_names.append(extern_const_decl.name)

    duplicate_names = set()
    header_obj_names = (frozenset(typedef_struct_decl_names), frozenset(typedef_struct_def_names), frozenset(struct_def_names), frozenset(func_type_def_names))
    for x, y in itertools.combinations(header_obj_names, 2):
        duplicate_names |= x & y

    output += "== duplicate_names ==\n"
    for duplicate_name in duplicate_names:
        output += f"{duplicate_name}\n"

    output += "== Non-unk names ==\n"

    for name in typedef_struct_decl_names + typedef_struct_def_names + struct_def_names + func_type_def_names + enum_names:
        if name is not None and "Unk" not in name:
            output += f"{name}\n"

    object_name_to_object = {}

    output += "== typedef_struct_decl_filenames ==\n"

    # Create declarations first
    for typedef_struct_decl in typedef_struct_decls:
        typedef_struct_decl_name = typedef_struct_decl.name
        if typedef_struct_decl_name == typedef_struct_decl.source:
            raise RuntimeError(f"typedef_struct_decl source name same as name! name: {typedef_struct_decl_name}, source: {typedef_struct_decl.source}")

        header_guard = set_object_filenames_and_return_guard(typedef_struct_decl, "_decl")

        obj = object_name_to_object.get(typedef_struct_decl_name)
        #if obj is not None and obj.contents != typedef_struct_decl.contents:
        #    raise RuntimeError(f"typedef_struct_decl_name {typedef_struct_decl_name} already exists in object_name_to_object!")

        if typedef_struct_decl.name == "UnkStruct_0207CB08":
            print(f"UnkStruct_0207CB08 header guard: {typedef_struct_decl.header_guard}")
        object_name_to_object[typedef_struct_decl_name] = typedef_struct_decl

        output += f"{typedef_struct_decl.full_filename}, {header_guard}\n"
        decl_filename_contents = f"""\
#ifndef {header_guard}
#define {header_guard}

{typedef_struct_decl.contents.strip()}

#endif // {header_guard}
"""
        full_filepath = pathlib.Path(typedef_struct_decl.full_filename)
        full_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(full_filepath, "w+") as f:
            f.write(decl_filename_contents)

    for enum_def in enum_defs:
        if enum_def.name is not None:
            if enum_def.name in object_name_to_object:
                raise RuntimeError()

            object_name_to_object[enum_def.name] = enum_def

    for typedef_struct_def in typedef_struct_defs:
        # decls have priority over defs
        obj = object_name_to_object.get(typedef_struct_def.name)
        if obj is None:
            object_name_to_object[typedef_struct_def.name] = typedef_struct_def
        elif isinstance(obj, TypedefStructDef):
            raise RuntimeError(f"{typedef_struct_def.name} has already existing typedef struct def in object_name_to_object!")
        set_object_filenames_and_return_guard(typedef_struct_def, "")

    for struct_def in struct_defs:
        if struct_def.name in object_name_to_object:
            raise RuntimeError(f"{struct_def.name} already exists in object_name_to_object!")

        object_name_to_object[struct_def.name] = struct_def
        set_object_filenames_and_return_guard(struct_def, "")

    for func_type_def in func_type_defs:
        if func_type_def.name in object_name_to_object:
            raise RuntimeError()

        object_name_to_object[func_type_def.name] = func_type_def
        set_object_filenames_and_return_guard(func_type_def, "")

    for nitro_sdk_type in nitro_sdk_types:
        object_name_to_object[nitro_sdk_type.name] = nitro_sdk_type

    output += "== Func type def non decl includes ==\n"

    # create headers for func types
    for func_type_def in func_type_defs:
        output += gen_header(func_type_def, object_name_to_object, "f_")

    output += "== Typedef struct def non decl includes ==\n"

    # create headers for typedef struct defs
    for typedef_struct_def in typedef_struct_defs:
        output += gen_header(typedef_struct_def, object_name_to_object, "ts_")

    output += "==struct def non decl includes ==\n"

    # create headers for struct defs
    for struct_def in struct_defs:
        output += gen_header(struct_def, object_name_to_object, "s_")

    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    func_decl_headers = {}

    for func_decl in func_decls.values():
        try:
            symbol_list = xmap.symbols_by_name[func_decl.name]
        except KeyError:
            raise RuntimeError(f"Could not find func_decl in syms! func_decl.contents: {func_decl.contents.strip()}")

        if len(symbol_list) != 1:
            raise RuntimeError(f"symbol {symbol_list} is not len 1!")
        symbol = symbol_list[0]
        if symbol.filename == "libcrypto_ov97.o":
            continue
        header_filename = str(pathlib.Path(symbol.filename).with_suffix(".h"))
        func_decl_header = func_decl_headers.get(header_filename)
        if func_decl_header is None:
            func_decl_header = FuncDeclHeader(header_filename)
            func_decl_headers[header_filename] = func_decl_header

        func_decl_header.add_func_decl(func_decl, symbol)

    output += "== func_decl non decl includes ==\n"

    for func_decl_header in func_decl_headers.values():
        output += func_decl_header.gen_header_and_write(object_name_to_object)

    #for c_filename in c_filenames:
        
    # lazy method: find all objects by searching "Unk" object
    # manually add in the rest of the headers

    all_header_defs_decls_intersections = {}
    all_header_objs = {}

    output += "== Header objs defs & decls intersection==\n"
    for basename, header_info in header_infos.items():
        header_objs = get_header_objs(header_info, header_infos)
        all_header_objs[basename] = header_objs
        defs_decls_intersection = frozenset(header_objs.defs.keys()) & frozenset(header_objs.decls.keys())
        all_header_defs_decls_intersections[basename] = defs_decls_intersection
        if len(defs_decls_intersection) != 0:
            output += f"{header_info.filename.replace('../00jupc_retsam/', '')}: {', '.join(def_or_decl_name for def_or_decl_name in defs_decls_intersection)}\n"
        #output += f"{basename}: {', '.join(header_obj.name for header_obj in header_objs)}\n"
        #header_guard =

    #for c_filename in c_filenames:
    #    with open(c_filename, "r") as f:
    #        lines = f.readlines()
    #
    #    line_reader = LineReader(lines, c_filename)
    #    c_file_includes = []
    #    c_file_library_includes = []
    #
    #    for line in line_reader:
    #        match_obj = include_regex.match(line)
    #        if match_obj:
    #            include_basename = pathlib.Path(match_obj.group(1)).name
    #            c_file_includes.append(include_basename)
    #        else:
    #            match_obj = library_include_regex.match(line)
    #            if match_obj:
    #                c_file_library_includes.append(match_obj.group(1))
    #
    #    c_file_decls = []
    #    c_file_defs = []
    #
    #    for include_basename in c_file_includes:
    #        header_objs = all_header_objs[include_basename]
            

    #unk_object_suffixes = set()
    #
    #found_typedef_struct_header_names = ""
    #found_typedef_nonstructs = ""
    #empty_typedef_structs = ""
    #open_bracket_in_struct_def = ""
    #enum_locations = ""
    #enum_values = ""
    #struct_decl_locations = ""
    #struct_def_locations = ""
    #probably_func_decl_struct_returns = ""
    #probably_func_def_struct_returns = ""
    #functype_args_locations = ""
    #functype_stripped_args = ""
    #
    #typedef_struct_decls = []
    #struct_defs = []
    #typedef_struct_defs = []
    #enum_defs = []
    #func_type_defs = []
    #
    #header_infos = {}
    #
    #find_objects(c_filenames, "c_filename")
    #
    #obj_names_by_c_filename = {c_filename: frozenset(obj.name for obj in header_info.objs) for c_filename, header_info in header_infos.items()}

    #c_file_object_names = []
    #c_file_object_names.extend(typedef_struct_decl.name for typedef_struct_decl in typedef_struct_decls)
    #c_file_object_names.extend(struct_def.name for struct_def in struct_defs)
    #c_file_object_names.extend(typedef_struct_def.name for typedef_struct_def in typedef_struct_defs)
    #c_file_object_names.extend(typedef_struct_def.name for typedef_struct_def in typedef_struct_defs)

    #output += "== typedef_struct_decls c_filenames ==\n"
    #for typedef_struct_decl in typedef_struct_decls:
    #    output += f"{typedef_struct_decl.name}: {typedef_struct_decl.source}\n"
    #    typedef_struct_decl_names.append(typedef_struct_decl.name)
    #
    #output += "== typedef_struct_defs c_filenames ==\n"
    #for typedef_struct_def in typedef_struct_defs:
    #    output += f"{typedef_struct_def.name}: {', '.join(typedef_struct_def.dependencies)}\n"
    #    typedef_struct_def_names.append(typedef_struct_def.name)
    #
    #output += "== struct_defs c_filenames ==\n"
    #for struct_def in struct_defs:
    #    output += f"{struct_def.name}: {', '.join(struct_def.dependencies)}\n"
    #    struct_def_names.append(struct_def.name)
    #
    #output += "== func_type_defs c_filenames ==\n"
    #for func_type_def in func_type_defs:
    #    output += f"{func_type_def.name}: {', '.join(func_type_def.dependencies)}\n"
    #    func_type_def_names.append(func_type_def.name)
    #
    #output += "== enum_defs c_filenames ==\n"
    #for enum_def in enum_defs:
    #    output += f"{enum_def.name}\n"
    #    enum_names.append(enum_def.name)
    #
    #output += "== Unk objects for C files ==\n"

    #for c_filename in c_filenames:
    #    with open(c_filename, "r") as f:
    #        contents = f.read()
    #
    #    unk_object_names_types = set(object_regex.findall(contents))
    #    unk_objects = []
    #    found_local_object_names = []
    #    c_basename = pathlib.Path(c_filename).name
    #
    #    file_has_enum = False
    #    obj_names_for_c_file = obj_names_by_c_filename[c_basename]
    #    #print(f"type(obj_names_for_c_file): {type(obj_names_for_c_file).__name__}")
    #    for unk_object_name, unk_object_type in unk_object_names_types:
    #        if unk_object_type == "Enum":
    #            file_has_enum = True
    #        else:
    #            if unk_object_name not in obj_names_for_c_file:
    #                unk_objects.append(UnkObject(unk_object_name))
    #            else:
    #                found_local_object_names.append(unk_object_name)
    #
    #    for unk_object in unk_objects:
    #        unk_object_suffixes.add(unk_object.suffix)
    #
    #    c_fullname = c_filename.replace("../00jupc_retsam/", "")
    #    output += f"{c_fullname} all unk objs: {', '.join(unk_object_name for unk_object_name, unk_object_type in unk_object_names_types)}\n"
    #    output += f"{c_fullname} external objs: {', '.join(unk_object.name for unk_object in unk_objects)}\n"
    #    output += f"{c_fullname} local objs: {', '.join(found_local_object_names)}\n\n"
    #
    #output += "== Unk object suffixes ==\n"
    #
    #for unk_object_suffix in unk_object_suffixes:
    #    output += f"{unk_object_suffix}\n"

        #line_reader = LineReader(lines, header_filename)
        #for line in line_reader:
        #    match_obj = include_regex.match(line)

    with open("find_structs_typedefs_out.txt", "w+") as f:
        f.write(output)
        

    #typedef_struct_defs
    #typedef_struct_decls = []
    #struct_defs = []
    #typedef_struct_defs = []
    #enum_defs = []


            #elif line.startswith("struct"):
            #    
            #elif line.startswith("typedef"):

if __name__ == "__main__":
    main()
