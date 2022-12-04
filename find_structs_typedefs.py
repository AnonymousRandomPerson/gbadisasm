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
from xmap import XMap, OvAddr
import json
import time

OUTPUT_PREFIX = "../00jupc_retsam2"
DEBUG = False

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

    def clear_cur_line(self):
        self._lines[self._line_num] = ""

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
    __slots__ = ("name", "contents", "dependencies", "filename", "include_filename", "full_filename", "header_guard")

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
        self.contents_list.append((symbol.full_addr, func_decl))
        self.dependencies.extend(func_decl.dependencies)

    def update_funcname_to_header_filename_mapping(self, funcname_to_header_filename):
        for symbol_full_addr, func_decl in self.contents_list:
            funcname_to_header_filename[func_decl.name] = self.include_filename

    def gen_header_and_write(self, object_name_to_object):
        if len(self.contents_list) == 0:
            return

        sorted_contents_list = tuple(x[1].contents for x in sorted(self.contents_list, key=lambda x: x[0]))
        self.contents = "".join(sorted_contents_list)
        return gen_header(self, object_name_to_object, "h_")

class HeaderInfo:
    __slots__ = ("filename", "basename", "objs", "includes", "resolved")

    def __init__(self, filename):
        self.filename = filename
        self.basename = pathlib.Path(filename).name
        #print(f"self.basename: {self.basename}")
        self.objs = []
        self.includes = []
        self.resolved = False

class PartitionedHeaderObjs:
    __slots__ = ("defs", "decls", "funcdecls", "enums")

    def __init__(self, objs, filename):
        self.defs = {}
        self.decls = {}
        self.funcdecls = {}
        self.enums = {}

        for obj in objs:
            if isinstance(obj, (TypedefStructDecl, ExternConstDecl)):
                old_obj = self.decls.get(obj.name)
                if old_obj is not None:
                    raise RuntimeError(f"{filename}: {obj.name} already in self.decls! old_obj.full_filename: {old_obj.full_filename}, obj.full_filename: {obj.full_filename}")
                self.decls[obj.name] = obj
            elif isinstance(obj, (TypedefStructDef, FuncTypeDef)):
                if obj.name in self.defs:
                    raise RuntimeError()
                self.defs[obj.name] = obj
            elif isinstance(obj, FuncDecl):
                old_obj = self.decls.get(obj.name)
                if old_obj is not None:
                    if old_obj.contents != obj.contents:
                        raise RuntimeError(f"{obj.name} already in funcdecls!")
                else:
                    self.funcdecls[obj.name] = obj
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
unk_obj_filename_parts_regex = re.compile(r"^(?:\"|<)?(?:(?:overlay[0-9]+|struct_defs|struct_decls|functypes|constdata)/)?(?:struct_|funcptr_|union_|unk_)?(?:ov([0-9]+)_)?([0-9A-F]{8})([^\.]+)?\.h(?:\"|>)?$")
functype_struct_field_regex = re.compile(r"^(\w+)\s+\*?\s*\(\s*\*?\s*(\w+)\s*\)\s*\((.+)\)\s*;")
func_decl_regex = re.compile(r"^(?!(?:static\s+|extern\s+|FS_EXTERN_OVERLAY))(?:const\s+)?(?:struct|union|enum\s+)?(\w+)\s+(?:\*+\s*)?(\w+)\((.*)\)\s*;\s*")
extern_const_symbol_regex = re.compile(r"^extern\s+const\s+(\w+)\s+(?:\*+\s*)?(?:const\s+)?(\w+)(.*);\s*$")
unk_func_regex = re.compile(r"(?:sub|ov([0-9]+))_([0-9A-F]{1,8})")
fs_overlay_id_regex = re.compile(r"FS_OVERLAY_ID\(\s*(\w+)\s*\)")
fs_extern_overlay_regex = re.compile(r"^FS_EXTERN_OVERLAY\(\s*(\w+)\s*\)")
struct_field_needs_def_regex = re.compile(r"^(?:struct\s+|union\s+)?\w+\s+\w+(\[[^\]]+\])*;")

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

def validate_xmap_functions(xmap):
    duplicate_func_names = ""

    for symbol_name, symbols in xmap.symbols_by_name.items():
        if symbols[0].section == ".text" and symbols[0].archive is None and symbol_name not in ("NitroStaticInit", "inline_ov61_0222C3B0_sub"):
            if len(symbols) != 1:
                duplicate_func_names += f"multiple {symbol_name}: " + ", ".join(f"{symbol.full_addr}" for symbol in symbols) + "\n"

            for symbol in symbols:
                if len(symbols) != 1:
                    #print(f"symbol.name: {symbol.name}")
                    continue
                match_obj = unk_func_regex.search(symbol.name)
                if match_obj:
                    overlay_str = match_obj.group(1)
                    overlay = int(overlay_str) if overlay_str is not None else -1
                    addr = int(match_obj.group(2), 16)
                    ov_addr = OvAddr(overlay, addr)
                    if ov_addr != symbol.full_addr:
                        if symbol.full_addr.overlay == -1:
                            correct_symbol_name = f"sub_{symbol.full_addr.addr:08X}"
                        else:
                            correct_symbol_name = f"ov{symbol.full_addr.overlay}_{symbol.full_addr.addr:08X}"
                        duplicate_func_names += f"./replace.sh {symbol.name} {correct_symbol_name}\n"
                elif symbol.name == "ov5_021D15B4":
                    print("ov5_021D15B4")

    if duplicate_func_names != "":
        raise RuntimeError(f"Multiple same symbol names and/or wrong symbol addresses detected!\n\n{duplicate_func_names}")

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
            needs_def = False
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
                needs_def = struct_field_needs_def_regex.match(stripped_field_keep_asterisk) is not None
            else:
                dependency = None

            if dependency is not None:
                if word_regex.match(dependency):
                    if needs_def:
                        dependencies.append(f"!{dependency}")
                    else:
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

def set_object_filenames_and_return_guard(obj, suffix, non_overlay_prefix):
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

    if obj_name.startswith("Unk_"):
        obj_name = obj_name.replace("Unk_", "Const_")

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
        include_filename = f"{non_overlay_prefix}/{filename_base}"
    
    full_filename = f"include/{include_filename}"
    header_guard = f"POKEPLATINUM_{filename_root.upper()}_H"
    
    obj.filename = filename_base
    if include_filename in ("struct_defs/union_020225E0.h", "struct_defs/union_02022594.h"):
        obj.include_filename = "\"struct_defs/union_02022594_020225E0.h\""
    else:
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

def generate_includes(dependency_full_filenames, output):
    unique_dependency_full_filenames = tuple(frozenset(dependency_full_filenames))
    non_unk_object_header_filenames = []
    unk_objects = []

    for dependency_full_filename in unique_dependency_full_filenames:
        try:
            unk_object = UnkObject.from_filename(dependency_full_filename)
            unk_objects.append(unk_object)
        except ValueError:
            non_unk_object_header_filenames.append(dependency_full_filename)
            output.append(f"Non-unk: {dependency_full_filename}\n")

    sorted_unique_includes = [unk_object.name for unk_object in sorted(unk_objects, key=functools.cmp_to_key(unk_obj_cmp_function))]
    dependencies_as_str = "".join(f"#include {sorted_unique_include}\n" for sorted_unique_include in sorted_unique_includes)
    if len(non_unk_object_header_filenames) != 0:
        dependencies_as_str += "\n" + "".join(f"#include {non_unk_object_header_filename}\n" for non_unk_object_header_filename in non_unk_object_header_filenames)

    return dependencies_as_str, output

def gen_header(obj, object_name_to_object, debug_prefix="", object_name_to_typedef_struct_def=None):
    output = []

    if is_gf_lib_type(obj):
        return ""

    dependency_full_filenames = []
    new_dependencies = []

    for dependency in obj.dependencies:
        force_def = False
        if object_name_to_typedef_struct_def is not None:
            if dependency[0] == "!":
                dependency = dependency[1:]
                force_def = True

            new_dependencies.append(dependency)

        object_name_to_typedef_struct_def
        dependency_obj = None

        if dependency == "<enum>":
            dependency_obj = dummy_enum_def
        elif force_def:
            dependency_obj = object_name_to_typedef_struct_def.get(dependency)
            if dependency_obj is None:
                if dependency.endswith("_t"):
                    dependency_obj = object_name_to_typedef_struct_def.get(dependency[:-2])
                else:
                    dependency_obj = object_name_to_typedef_struct_def.get(f"{dependency}_t")
                    if dependency_obj is not None and "_t.h" in dependency_obj.include_filename:
                        dependency_full_filenames.append(
                            dependency_obj.include_filename.replace("_t.h", "_decl.h").replace("struct_defs", "struct_decls")
                        )

        if dependency_obj is None:
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
                output.append(f"Non-decl: {dependency_obj.include_filename}\n")
        except AttributeError:
            raise RuntimeError(f"Dependency {dependency} has no include_filename for obj {obj.name}!")

    if object_name_to_typedef_struct_def is not None:
        obj.dependencies = tuple(new_dependencies)

    dependencies_as_str, output = generate_includes(dependency_full_filenames, output)

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
    if not DEBUG:
        debug_prefix = ""

    full_filepath = pathlib.Path(f"{OUTPUT_PREFIX}/{debug_prefix}{obj.full_filename}")
    full_filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(full_filepath, "w+") as f:
        f.write(contents)

    return output

special_headers = set((
    "nnsys.h", "src/data/arc_tool.dat", "string.h", "dwc.h", "fushigi/agbpoke2dppoke.c"
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

def find_all_from_iterable(content, iterable):
    pattern = re.compile("\\b" + "\\b|\\b".join(re.escape(k) if k[0] != "!" else k[1:] for k in iterable) + "\\b", flags=re.DOTALL)
    return frozenset(pattern.findall(content))

system_macros = set(("XtOffset", "NELEMS", "ROUND_UP", "ROUND_DOWN"))
sdkdef_enums = set(("GX_BLEND_BGALL", "GX_BLEND_ALL", "GX_WND_PLANEMASK_BGALL", "GX_WND_PLANEMASK_ALL"))

extra_symbols_look_for = set((
    "GF_ASSERT", "Unk_021BF67C", "Unk_02100844", "Unk_020EE4B8",
    "Unk_ov62_02248F58", "Unk_ov62_022490DC", "Unk_ov62_02249680", "Unk_ov62_0224962C", "Unk_ov62_02249618", "Unk_ov62_02248BD8", "Unk_ov62_02248BF0", "Unk_ov62_02249790", "Unk_ov62_02248C28", "Unk_ov62_02248C50", "Unk_ov62_02248D08", "Unk_ov62_02248D20", "Unk_ov62_02248E24", "Unk_ov62_02248E50",
    r"!inline\w+"
)) | system_macros | sdkdef_enums


UnkStruct_0203CDB0_sub2_t_def_files = set(("ov5_021D0D80.c", "ov5_021D1A94.c", "ov5_021D1C30.c", "ov5_021D5EB8.c", "ov5_021DD6FC.c", "ov5_021DDAE4.c", "ov5_021DDBE8.c", "ov5_021E2338.c", "ov5_021EA714.c", "ov5_021EE75C.c", "ov5_021F007C.c", "ov5_021F8370.c", "ov6_0223E140.c", "ov6_02240C9C.c", "ov6_02248050.c", "ov6_02248948.c", "ov8_02249960.c", "ov9_02249960.c", "ov23_0223E140.c", "ov23_02254A14.c", "unk_0203CC84.c", "unk_0203F6C4.c", "unk_02046C7C.c", "unk_02048DD8.c", "unk_02050568.c", "unk_02055C50.c", "unk_02056B30.c", "unk_0206C0E8.c", "unk_0206C784.c", "unk_0206CCB0.c", "unk_0207160C.c", "unk_02071B10.c", "unk_02071CFC.c"))

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

    xmap = XMap("../00jupc_retsam/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    validate_xmap_functions(xmap)

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
                    header_info.objs.append(enum_def)
                else:
                    match_obj = include_regex.match(line)
                    if match_obj:
                        header_info.includes.append(match_obj.group(1))
                    elif not any(filename.endswith(func_decl_ignore_filename) for func_decl_ignore_filename in func_decl_ignored_files):
                        match_obj = func_decl_regex.match(line.replace("const ", ""))
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
                                if functype_args != "":
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
                            header_info.objs.append(func_decl)
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
                                header_info.objs.append(extern_const_decl)

    all_header_files = tuple(glob.glob("../00jupc_retsam/include/**/*.h", recursive=True))
    find_objects(all_header_files, "header_filename")
    #for header_filename in itertools.chain(glob.glob("../00jupc_retsam/include/**/*.h", recursive=True), c_filenames):
    #for header_filename in :

    output = []
    output.append("== found_typedef_struct_header_names ==\n")
    output.append(found_typedef_struct_header_names)
    output.append("== found_typedef_nonstructs ==\n")
    output.append(found_typedef_nonstructs)
    output.append("== empty_typedef_structs ==\n")
    output.append(empty_typedef_structs)
    output.append("== open_bracket_in_struct_def ==\n")
    output.append(open_bracket_in_struct_def)
    output.append("== enum_locations ==\n")
    output.append(enum_locations)
    output.append("== enum_values ==\n")
    output.append(enum_values)
    output.append("== struct_decl_locations ==\n")
    output.append(struct_decl_locations)
    output.append("== struct_def_locations ==\n")
    output.append(struct_def_locations)
    output.append("== functype_args_locations ==\n")
    output.append(functype_args_locations)
    output.append("== functype_stripped_args ==\n")
    output.append(functype_stripped_args)
    output.append("== probably_func_decl_struct_returns ==\n")
    output.append(probably_func_decl_struct_returns)
    output.append("== probably_func_def_struct_returns ==\n")
    output.append(probably_func_def_struct_returns)

    typedef_struct_decl_names = []
    typedef_struct_def_names = []
    struct_def_names = []
    func_type_def_names = []
    enum_names = []

    output.append("== typedef_struct_decls ==\n")
    for typedef_struct_decl in typedef_struct_decls:
        output.append(f"{typedef_struct_decl.name}: {typedef_struct_decl.source}\n")
        typedef_struct_decl_names.append(typedef_struct_decl.name)

    output.append("== typedef_struct_defs ==\n")
    for typedef_struct_def in typedef_struct_defs:
        output.append(f"{typedef_struct_def.name}: {', '.join(typedef_struct_def.dependencies)}\n")
        typedef_struct_def_names.append(typedef_struct_def.name)

    output.append("== struct_defs ==\n")
    for struct_def in struct_defs:
        output.append(f"{struct_def.name}: {', '.join(struct_def.dependencies)}\n")
        struct_def_names.append(struct_def.name)

    output.append("== func_type_defs ==\n")
    for func_type_def in func_type_defs:
        output.append(f"{func_type_def.name}: {', '.join(func_type_def.dependencies)}\n")
        func_type_def_names.append(func_type_def.name)

    output.append("== enum_defs ==\n")
    for enum_def in enum_defs:
        output.append(f"{enum_def.name}\n")
        enum_names.append(enum_def.name)

    output.append("== extern_const_decls ==\n")
    for extern_const_decl in extern_const_decls:
        output.append(f"{extern_const_decl.name}\n")
        enum_names.append(extern_const_decl.name)

    duplicate_names = set()
    header_obj_names = (frozenset(typedef_struct_decl_names), frozenset(typedef_struct_def_names), frozenset(struct_def_names), frozenset(func_type_def_names))
    for x, y in itertools.combinations(header_obj_names, 2):
        duplicate_names |= x & y

    output.append("== duplicate_names ==\n")
    for duplicate_name in duplicate_names:
        output.append(f"{duplicate_name}\n")

    output.append("== Non-unk names ==\n")

    for name in typedef_struct_decl_names + typedef_struct_def_names + struct_def_names + func_type_def_names + enum_names:
        if name is not None and "Unk" not in name:
            output.append(f"{name}\n")

    object_name_to_object = {}

    output.append("== typedef_struct_decl_filenames ==\n")

    typedef_struct_decl_extra_includes = {
        "struct_02013A04_decl.h": '#include "struct_defs/struct_02013A04_t.h"\n'
    }

    # Create declarations first
    for typedef_struct_decl in typedef_struct_decls:
        typedef_struct_decl_name = typedef_struct_decl.name
        if typedef_struct_decl_name == typedef_struct_decl.source:
            raise RuntimeError(f"typedef_struct_decl source name same as name! name: {typedef_struct_decl_name}, source: {typedef_struct_decl.source}")

        header_guard = set_object_filenames_and_return_guard(typedef_struct_decl, "_decl", "struct_decls")

        obj = object_name_to_object.get(typedef_struct_decl_name)
        #if obj is not None and obj.contents != typedef_struct_decl.contents:
        #    raise RuntimeError(f"typedef_struct_decl_name {typedef_struct_decl_name} already exists in object_name_to_object!")

        #if typedef_struct_decl.name == "UnkStruct_0207CB08":
        #    print(f"UnkStruct_0207CB08 header guard: {typedef_struct_decl.header_guard}")
        object_name_to_object[typedef_struct_decl_name] = typedef_struct_decl

        extra_includes = typedef_struct_decl_extra_includes.get(typedef_struct_decl.filename, "")

        output.append(f"{typedef_struct_decl.full_filename}, {header_guard}\n")
        decl_filename_contents = f"""\
#ifndef {header_guard}
#define {header_guard}
{extra_includes}
{typedef_struct_decl.contents.strip()}

#endif // {header_guard}
"""
        full_filepath = pathlib.Path(f"{OUTPUT_PREFIX}/{typedef_struct_decl.full_filename}")
        full_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(full_filepath, "w+") as f:
            f.write(decl_filename_contents)

    for enum_def in enum_defs:
        if enum_def.name is not None:
            if enum_def.name in object_name_to_object:
                raise RuntimeError()

            object_name_to_object[enum_def.name] = enum_def

    object_name_to_typedef_struct_def = {}

    for typedef_struct_def in typedef_struct_defs:
        # decls have priority over defs
        obj = object_name_to_object.get(typedef_struct_def.name)
        if obj is None:
            object_name_to_object[typedef_struct_def.name] = typedef_struct_def
        else:
            object_name_to_typedef_struct_def[typedef_struct_def.name] = typedef_struct_def
            if isinstance(obj, TypedefStructDef):
                raise RuntimeError(f"{typedef_struct_def.name} has already existing typedef struct def in object_name_to_object!")
        set_object_filenames_and_return_guard(typedef_struct_def, "", "struct_defs")

    for struct_def in struct_defs:
        if struct_def.name in object_name_to_object:
            raise RuntimeError(f"{struct_def.name} already exists in object_name_to_object!")

        object_name_to_object[struct_def.name] = struct_def
        if struct_def.name not in object_name_to_typedef_struct_def:
            object_name_to_typedef_struct_def[struct_def.name] = struct_def

        set_object_filenames_and_return_guard(struct_def, "", "struct_defs")

    for func_type_def in func_type_defs:
        if func_type_def.name in object_name_to_object:
            raise RuntimeError()

        object_name_to_object[func_type_def.name] = func_type_def
        set_object_filenames_and_return_guard(func_type_def, "", "functypes")

    for nitro_sdk_type in nitro_sdk_types:
        object_name_to_object[nitro_sdk_type.name] = nitro_sdk_type

    output.append("== Func type def non decl includes ==\n")

    # create headers for func types
    for func_type_def in func_type_defs:
        output.extend(gen_header(func_type_def, object_name_to_object, "f_"))

    output.append("== Typedef struct def non decl includes ==\n")

    # create headers for typedef struct defs
    for typedef_struct_def in typedef_struct_defs:
        output.extend(gen_header(typedef_struct_def, object_name_to_object, "ts_", object_name_to_typedef_struct_def=object_name_to_typedef_struct_def))

    output.append("==struct def non decl includes ==\n")

    # create headers for struct defs
    for struct_def in struct_defs:
        #if struct_def.name == "UnkStruct_02013A04_t":
        #    print(f"struct_def.full_filename: {struct_def.full_filename}")
        output.extend(gen_header(struct_def, object_name_to_object, "s_", object_name_to_typedef_struct_def=object_name_to_typedef_struct_def))

    output.append("== extern const decl non decl includes ==\n")

    for extern_const_decl in extern_const_decls:
        set_object_filenames_and_return_guard(extern_const_decl, "", "constdata")
        output.extend(gen_header(extern_const_decl, object_name_to_object, "c_"))

    func_decl_headers = {}
    funcname_to_header_filename = {
        "CRYPTO_VerifySignature": '"nitrocrypto/crypto.h"'
    }

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

    output.append("== func_decl non decl includes ==\n")

    for func_decl_header in func_decl_headers.values():
        func_decl_header.update_funcname_to_header_filename_mapping(funcname_to_header_filename)
        output.extend(func_decl_header.gen_header_and_write(object_name_to_object))

    #for c_filename in c_filenames:
        
    # lazy method: find all objects by searching "Unk" object
    # manually add in the rest of the headers

    all_header_defs_decls_intersections = {}
    all_header_objs = {}

    output.append("== Header objs defs & decls intersection==\n")
    for basename, header_info in header_infos.items():
        header_objs = get_header_objs(header_info, header_infos)
        all_header_objs[basename] = header_objs
        defs_decls_intersection = frozenset(header_objs.defs.keys()) & frozenset(header_objs.decls.keys())
        all_header_defs_decls_intersections[basename] = defs_decls_intersection
        if len(defs_decls_intersection) != 0:
            output.append(f"{header_info.filename.replace('../00jupc_retsam/', '')}: {', '.join(def_or_decl_name for def_or_decl_name in defs_decls_intersection)}\n")
        #output.append(f"{basename}: {', '.join(header_obj.name for header_obj in header_objs)}\n")
        #header_guard =

    gflib_header_basenames = []

    for header_file in all_header_files:
        if header_file.startswith("../00jupc_retsam/include/gflib/"):
            gflib_header_basenames.append(pathlib.Path(header_file).name)

    if False:
        NEWLINE = "\n"
        enum_defs_contents = [enum_def.contents for enum_def in enum_defs]
        enum_defs_contents_str = f"""\
#ifndef POKEPLATINUM_ENUMS_H
#define POKEPLATINUM_ENUMS_H

{NEWLINE.join(enum_defs_contents)}
#endif // POKEPLATINUM_ENUMS_H
"""
        pathlib.Path(f"e_include").mkdir(parents=True, exist_ok=True)
        with open(f"e_include/enums.h", "w+") as f:
            f.write(enum_defs_contents_str)
    #else:
    #    pathlib.Path(f"{OUTPUT_PREFIX}/include/overlay062").mkdir(parents=True, exist_ok=True)
    #    pathlib.Path(f"{OUTPUT_PREFIX}/include/constdata").mkdir(parents=True, exist_ok=True)
    #    shutil.copyfile("e_include/enums.h", f"{OUTPUT_PREFIX}/include/enums.h")
    #    shutil.copyfile("e_include/data_021BF67C.h", f"{OUTPUT_PREFIX}/include/data_021BF67C.h")
    #    shutil.copyfile("e_include/const_020EE4B8.h", f"{OUTPUT_PREFIX}/include/constdata/const_020EE4B8.h")
    #    shutil.copyfile("e_include/data_02100844.h", f"{OUTPUT_PREFIX}/include/data_02100844.h")
    #    shutil.copyfile("e_include/ov62_const_funcptr_tables.h", f"{OUTPUT_PREFIX}/include/overlay062/ov62_const_funcptr_tables.h")

    for hardcode in glob.glob("hardcodes/**/*.h", recursive=True):
        hardcode_dest_filepath = pathlib.Path(f"{OUTPUT_PREFIX}/{hardcode.replace('hardcodes/', '')}")
        hardcode_dest_filepath.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(hardcode, hardcode_dest_filepath)

    #def_takes_priority = frozenset(("UnkStruct_0203CDB0",))

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

    find_objects(c_filenames, "c_filename")

    struct_decl_def_obj_names_by_c_filename = {c_filename: frozenset(obj.name for obj in header_info.objs if isinstance(obj, (TypedefStructDecl, TypedefStructDef))) for c_filename, header_info in header_infos.items()}

    #c_file_object_names = []
    #c_file_object_names.extend(typedef_struct_decl.name for typedef_struct_decl in typedef_struct_decls)
    #c_file_object_names.extend(struct_def.name for struct_def in struct_defs)
    #c_file_object_names.extend(typedef_struct_def.name for typedef_struct_def in typedef_struct_defs)

    output.append(f"== c_file_found_declnames ==\n")
    hardcoded_c_file_library_includes = {
        "unk_02000C88.c": ("dwc.h",)
    }

    #manual_c_file_includes = {
    #    "unk_0200112C.c": 

    with open("overlaymap.json", "r") as f:
        overlaymap = json.load(f)

    for c_filename in c_filenames:
        total_start_time = time.time()
        print(f"c_filename: {c_filename}")
        start_time = time.time()
        with open(c_filename, "r") as f:
            lines = f.readlines()
        end_time = time.time()
        print(f"readin: {end_time - start_time}")

        contents = "".join(lines)

        start_time = time.time()
        unk_object_names_types = set(object_regex.findall(contents))
        end_time = time.time()
        print(f"object_regex: {end_time - start_time:.16f}")

        found_local_object_names = []
        c_basename = pathlib.Path(c_filename).name
    
        include_enums = False
        obj_names_for_c_file = struct_decl_def_obj_names_by_c_filename[c_basename]
        #print(f"type(obj_names_for_c_file): {type(obj_names_for_c_file).__name__}")
        for unk_object_name, unk_object_type in unk_object_names_types:
            if unk_object_type == "Enum":
                include_enums = True
            elif unk_object_name in obj_names_for_c_file:
                found_local_object_names.append(unk_object_name)

        found_local_object_names_set = frozenset(found_local_object_names)

        #c_fullname = c_filename.replace("../00jupc_retsam/", "")
        #output.append(f"{c_fullname} all unk objs: {', '.join(unk_object_name for unk_object_name, unk_object_type in unk_object_names_types)}\n")
        #output.append(f"{c_fullname} external objs: {', '.join(unk_object.name for unk_object in unk_objects)}\n")
        #output.append(f"{c_fullname} local objs: {', '.join(found_local_object_names)}\n\n")

        c_full_filename = c_filename.replace('../00jupc_retsam/', '')
        line_reader = LineReader(lines, c_filename)
        c_file_includes = list(gflib_header_basenames)
        c_file_library_includes = ["nitro.h", "stdlib.h", "string.h"]
        c_file_library_includes.extend(hardcoded_c_file_library_includes.get(c_basename, ()))
        special_nonlib_includes = []
        special_includes = []
        fs_extern_overlays = []

        start_time = time.time()
        for line in line_reader:
            #cur_start_time = time.time()
            match_obj = include_regex.match(line)
            if match_obj:
                include_name = match_obj.group(1)
                if include_name in special_headers or include_name.startswith("src/data/"):
                    special_includes.append(include_name)
                    continue
                include_basename = pathlib.Path(include_name).name
                c_file_includes.append(include_basename)
                if include_basename == "arc_tool.h":
                    special_nonlib_includes.append("src/data/arc_tool.dat")

                line_reader.clear_cur_line()
            else:
                match_obj = library_include_regex.match(line)
                if match_obj:
                    c_file_library_includes.append(match_obj.group(1))
                    line_reader.clear_cur_line()
                else:
                    match_obj = fs_extern_overlay_regex.match(line)
                    if match_obj:
                        fs_extern_overlays.append(match_obj.group(1))
                        line_reader.clear_cur_line()

            #if line_reader.line_num >= 300:
            #    break
            #cur_end_time = time.time()
            #print(f"c file line reader iter: {cur_end_time - cur_start_time}")

        end_time = time.time()
        print(f"c file line reader: {end_time - start_time:.16f}")

        fs_extern_overlays_set = set(fs_extern_overlays)
        c_file_decls = {}
        c_file_defs = {}
        c_file_funcdecls = {}

        start_time = time.time()
        for include_basename in c_file_includes:
            cur_header_objs = all_header_objs[include_basename]
            c_file_decls.update(cur_header_objs.decls)
            c_file_defs.update(cur_header_objs.defs)
            #c_file_decls.update({decl.name: decl for decl in cur_header_objs.decls})
            #c_file_defs.extend({cdef.name: cdef for cdef in cur_header_objs.defs})
            c_file_funcdecls.update(cur_header_objs.funcdecls)
            #include_enums |= (len(cur_header_objs.enums) != 0)

        c_file_nonlocal_declnames = frozenset(c_file_decls.keys()) - found_local_object_names_set
        c_file_nonlocal_defnames = frozenset(c_file_defs.keys()) - found_local_object_names_set
        end_time = time.time()

        print(f"get header objs: {end_time - start_time:.16f}")
        #c_file_decls = remove_duplicate_objs(c_file_decls)
        #c_file_defs = remove_duplicate_objs(c_file_defs)
        #c_file_funcdecls = remove_duplicate_objs(c_file_funcdecls)

        c_file_content_includeless = "".join(lines).strip() + "\n"

        start_time = time.time()
        c_file_found_declnames = find_all_from_iterable(c_file_content_includeless, c_file_nonlocal_declnames)
        c_file_found_defnames = find_all_from_iterable(c_file_content_includeless, c_file_nonlocal_defnames)
        c_file_found_funcnames = find_all_from_iterable(c_file_content_includeless, c_file_funcdecls.keys())
        extra_symbols = find_all_from_iterable(c_file_content_includeless, extra_symbols_look_for)

        end_time = time.time()
        print(f"find_all_from_iterable: {end_time - start_time:.16f}")

        c_file_found_decls_defs_intersection = (c_file_found_declnames & c_file_found_defnames)
        c_file_found_only_declnames = c_file_found_declnames - c_file_found_decls_defs_intersection

        #if len(c_file_found_decls_defs_intersection) != 0:
        #    output.append(f"{c_full_filename}: {', '.join(c_file_found_decls_defs_intersection)}\n")

        dependency_full_filenames = []
        for c_file_found_declname in c_file_found_only_declnames:
            c_file_found_decl = c_file_decls[c_file_found_declname]
            dependency_full_filenames.append(c_file_found_decl.include_filename)

        decl_includes_str, output = generate_includes(dependency_full_filenames, output)
        #if c_basename == "unk_0202602C.c":
        #    decl_includes_str.replace("struct_02026030_decl", "struct_02026030")

        dependency_full_filenames = []
        for c_file_found_defname in c_file_found_defnames:
            c_file_found_def = c_file_defs[c_file_found_defname]
            dependency_full_filenames.append(c_file_found_def.include_filename)

        if c_basename in UnkStruct_0203CDB0_sub2_t_def_files:
            dependency_full_filenames.append('"struct_defs/struct_0203CDB0_sub2_t.h"')
        elif c_basename == "unk_0203A9C8.c":
            dependency_full_filenames.append('"struct_defs/struct_0200D0F4.h"')
        elif c_basename in ("unk_0203E724.c", "unk_0203E880.c"):
            dependency_full_filenames.append('"struct_defs/struct_0203E724_t.h"')
        elif c_basename == "unk_0205C22C.c":
            dependency_full_filenames.append('"struct_defs/struct_0203CDB0.h"')

        def_includes_str, output = generate_includes(dependency_full_filenames, output)
        if c_basename in ("unk_0202602C.c", "unk_02026150.c"):
            def_includes_str += '#include "struct_defs/struct_02026030_t.h"\n'

        c_file_func_include_filenames = []

        for c_file_found_funcname in c_file_found_funcnames:
            try:
                c_file_func_include_filenames.append(funcname_to_header_filename[c_file_found_funcname])
            except KeyError:
                output.append(f"KeyError: {c_file_found_funcname}\n")
                continue

        func_includes_str, output = generate_includes(c_file_func_include_filenames, output)
        if include_enums:
            enums_include_str = "#include \"enums.h\"\n"
        else:
            enums_include_str = ""

        inline_added = False
        ov62_const_funcptr_tables_added = False

        for extra_symbol in extra_symbols:
            if extra_symbol == "GF_ASSERT":
                special_nonlib_includes.append("assert.h")
            elif extra_symbol == "Unk_021BF67C":
                special_nonlib_includes.append("data_021BF67C.h")
            elif extra_symbol == "Unk_02100844":
                special_nonlib_includes.append("data_02100844.h")
            elif extra_symbol == "Unk_020EE4B8":
                special_nonlib_includes.append("constdata/const_020EE4B8.h")
            elif extra_symbol in system_macros:
                special_nonlib_includes.append("system_macros.h")
            elif extra_symbol.startswith("Unk_ov62"):
                special_nonlib_includes.append("overlay062/ov62_const_funcptr_tables.h")
                ov62_const_funcptr_tables_added = True
            elif extra_symbol in sdkdef_enums:
                special_nonlib_includes.append("gflib/sdkdef.h")
            elif extra_symbol.startswith("inline") and not inline_added:
                special_nonlib_includes.append("inlines.h")
                inline_added = True

        #special_nonlib_includes_set
        special_nonlib_includes_str = "".join(f"#include \"{special_nonlib_include}\"\n" for special_nonlib_include in special_nonlib_includes)
        c_file_library_includes_unique = {k: True for k in c_file_library_includes}.keys()
        c_file_library_includes_str = "".join(f"#include <{c_file_library_include}>\n" for c_file_library_include in c_file_library_includes_unique)

        used_overlay_ids = fs_overlay_id_regex.findall(c_file_content_includeless)
        fs_extern_overlays_set.update(used_overlay_ids)
        sorted_fs_extern_overlays = sorted(fs_extern_overlays_set, key=lambda x: overlaymap.get(x, 9999))
        fs_extern_overlays_str = "".join(f"FS_EXTERN_OVERLAY({fs_extern_overlay});\n" for fs_extern_overlay in sorted_fs_extern_overlays)

        new_includes = "\n".join(include_str for include_str in (enums_include_str, c_file_library_includes_str, special_nonlib_includes_str, decl_includes_str, def_includes_str, func_includes_str, fs_extern_overlays_str) if include_str != "")
        new_c_file_content = f"{new_includes}\n{c_file_content_includeless}"
        new_c_filepath = pathlib.Path(f"{OUTPUT_PREFIX}/{c_full_filename}")
        new_c_filepath.parent.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        with open(new_c_filepath, "w+") as f:
            f.write(new_c_file_content)
        end_time = time.time()

        total_end_time = time.time()

        print(f"write: {end_time - start_time}\ntotal: {total_end_time - total_start_time:.16f}")
        #output.append(f"{c_full_filename}:\n{decl_includes_str}\n{def_includes_str}\n{}============================================")

    #unk_object_suffixes = set()
    #

    #
    #typedef_struct_decls = []
    #struct_defs = []
    #typedef_struct_defs = []
    #enum_defs = []
    #func_type_defs = []
    #
    #header_infos = {}
    #
    #
    #


    #output.append("== typedef_struct_decls c_filenames ==\n")
    #for typedef_struct_decl in typedef_struct_decls:
    #    output.append(f"{typedef_struct_decl.name}: {typedef_struct_decl.source}\n")
    #    typedef_struct_decl_names.append(typedef_struct_decl.name)
    #
    #output.append("== typedef_struct_defs c_filenames ==\n")
    #for typedef_struct_def in typedef_struct_defs:
    #    output.append(f"{typedef_struct_def.name}: {', '.join(typedef_struct_def.dependencies)}\n")
    #    typedef_struct_def_names.append(typedef_struct_def.name)
    #
    #output.append("== struct_defs c_filenames ==\n")
    #for struct_def in struct_defs:
    #    output.append(f"{struct_def.name}: {', '.join(struct_def.dependencies)}\n")
    #    struct_def_names.append(struct_def.name)
    #
    #output.append("== func_type_defs c_filenames ==\n")
    #for func_type_def in func_type_defs:
    #    output.append(f"{func_type_def.name}: {', '.join(func_type_def.dependencies)}\n")
    #    func_type_def_names.append(func_type_def.name)
    #
    #output.append("== enum_defs c_filenames ==\n")
    #for enum_def in enum_defs:
    #    output.append(f"{enum_def.name}\n")
    #    enum_names.append(enum_def.name)
    #
    #output.append("== Unk objects for C files ==\n")


    
    #output.append("== Unk object suffixes ==\n")
    #
    #for unk_object_suffix in unk_object_suffixes:
    #    output.append(f"{unk_object_suffix}\n")

        #line_reader = LineReader(lines, header_filename)
        #for line in line_reader:
        #    match_obj = include_regex.match(line)

    output_as_str = "".join(output)
    with open("find_structs_typedefs_out.txt", "w+") as f:
        f.write(output_as_str)
        

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
