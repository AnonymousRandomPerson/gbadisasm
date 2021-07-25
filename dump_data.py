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

import struct
import pathlib
import collections
from xmap import XMap, OvAddr

MAINROM = 0
BASEROM = 1

class BinFile:
    __slots__ = ("_rom_filename", "_output_filename", "_output", "_rom_file", "_pos_stack", "_xmap")

    def __init__(self, rom_type, output_filename_base):
        if rom_type == MAINROM:
            self._rom_filename = "../master_cpuj00/bin/ARM9-TS/Rom/main.srl"
            output_filename_suffix = "-main"
        else:
            self._rom_filename = "pokeplatinum_us.nds"
            output_filename_suffix = ""

        output_filename_base_path = pathlib.Path(output_filename_base)
        self._output_filename = f"{output_filename_base_path.stem}{output_filename_suffix}{output_filename_base_path.suffix}"

        self._output = ""
        self._output += f"// {self._rom_filename}\n"
        self._pos_stack = collections.deque()

    def __enter__(self):
        self._rom_file = open(self._rom_filename, "rb")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._rom_file:
            self._rom_file.close()

    def virtual_seek_static(self, offset):
        self._rom_file.seek(offset - 0x2000000 + 0x4000)

    def virtual_tell_static(self):
        return self._rom_file.tell() + 0x2000000 - 0x4000

    #def virtual_seek_overlay(self, offset, overlay):
    #    if self._xmap is None:
    #        self._xmap = XMap("../master_cpuj00/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")

    @property
    def xmap(self):
        return self._output

    def seek(self, pos):
        self._rom_file.seek(pos)

    def tell(self):
        return self._rom_file.tell()

    def push_pos_static(self):
        self._pos_stack.append(self.virtual_tell_static())

    def pop_pos_static(self):
        self.virtual_seek_static(self._pos_stack.pop())

    def read_byte(self):
        return ord(self._rom_file.read(1))

    def read_ascii_char(self):
        return self._rom_file.read(1).decode("ascii")

    def read_hword(self):
        return struct.unpack("<H", self._rom_file.read(2))[0]

    def read_word(self):
        return struct.unpack("<I", self._rom_file.read(4))[0]

    def output_bytes(self, count):
        for i in range(count):
            self._output += f"\t.byte 0x{self.read_byte():x}\n"

    def output_hwords(self, count):
        for i in range(count):
            self._output += f"\t.hword 0x{self.read_hword():x}\n"

    def output_words(self, count):
        for i in range(count):
            self._output += f"\t.word 0x{self.read_word():x}\n"

    def output_bytes_list(self, count, tab=0, pad=True, space_after_comma=True, trailing_comma=False, hex_format=True):
        self.output_list(self.read_byte, count, 2, tab, pad, space_after_comma, trailing_comma, hex_format)

    def output_hwords_list(self, count, tab=0, pad=True, space_after_comma=True, trailing_comma=False, hex_format=True):
        self.output_list(self.read_hword, count, 4, tab, pad, space_after_comma, trailing_comma, hex_format)

    def output_list(self, datafunc, count, padsize, tab=0, pad=True, space_after_comma=True, trailing_comma=False, hex_format=True):
        tab_str = "\t" * tab
        self._output += tab_str
        for i in range(count):
            if hex_format:
                if pad:
                    self._output += f"0x{{:0{padsize}x}},".format(datafunc())
                else:
                    self._output += f"0x{datafunc():x},"
            else:
                if pad:
                    self._output += f"{{:0{padsize}d}},".format(datafunc())
                else:
                    self._output += f"{datafunc()},"

            if space_after_comma:
                self._output += " "

        if not trailing_comma:
            if space_after_comma:
                self._output = self._output[:-2]
            else:
                self._output = self._output[:-1]

        self._output += "\n"

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, output):
        self._output = output

    def write_to_file(self):
        with open(self._output_filename, "w+") as f:
            f.write(self._output)

    @staticmethod
    def run_dump_func_for_rom(dump_func, output_filename, rom_type):
        with BinFile(rom_type, output_filename) as rom:
            try:
                dump_func(rom)
                rom.write_to_file()
            except Exception as e:
                raise RuntimeError(f"Exception occurred! pos: {rom.virtual_tell_static():07x}, loadpos: 0x{rom.tell():x}") from e

    @staticmethod
    def run_dump_func(dump_func, output_filename, do_mainrom=False):
            if do_mainrom:
                BinFile.run_dump_func_for_rom(dump_func, output_filename, MAINROM)

            BinFile.run_dump_func_for_rom(dump_func, output_filename, BASEROM)
    
def dump_scrcmd_ptrs(rom):
    rom.virtual_seek_static(0x020EAC58)
    rom.output_words(0x348)

def dump_archive_file_table(rom):
    rom.virtual_seek_static(0x2100498)
    rom.output += "static const char*\tArchiveFileTable[]={\n"

    for i in range(195):
        ptr = rom.read_word()
        #print(f"ptr: {ptr - 0x2000000 + 0x4000:07x}")
        rom.push_pos_static()
        rom.virtual_seek_static(ptr)
        rom.output += "\t{\""
        #print(f"i: {i}")
        while True:
            c = rom.read_ascii_char()
            #print(c)
            if c == "\0":
                break
            rom.output += c

        rom.output += "\"},\n"
        rom.pop_pos_static()

    rom.output += "};\n"

def dump_gage_parts_txt(rom):
    rom.seek(0x210b6c)
    rom.output += "ALIGN4 const u8 gage_parts[] = {\n"
    for i in range(0x4d + 1):
        rom.output += f"//0x{i:x}\n"
        for j in range(4):
            rom.output_bytes_list(8, tab=1, pad=False)

    rom.output += "};\n\n"

def dump_shift_symbol(rom):
    rom.seek(0x3a2498)
    rom.output += "shift:\n"
    for i in range(4):
        rom.output += f"\t.hword "
        rom.output_hwords_list(8, tab=0, pad=False)

def dump_shift_val_symbol(rom):
    rom.seek(0x3a36f8)
    rom.output += "shift_val:\n"
    rom.output += f"\t.hword "
    rom.output_hwords_list(8, tab=0, pad=False)

    rom.output += f"\t.hword "
    rom.output_hwords_list(6, tab=0, pad=False)

def dump_stafflist(rom):
    rom.seek(0x3aa964)
    define_output = ""

    for i in range(0xed):
        strid = rom.read_hword()
        define_output += f"#define ENDING_STRID_{strid:04d}\t\t({strid})\n"
        rom.output += f"\t{{ ENDING_STRID_{strid:04d}, {rom.read_hword(): >5}, {'TRUE' if rom.read_hword() == 1 else 'FALSE'} }},\n"

    rom.output += f"// === msg_stafflist.h ===\n"
    rom.output += define_output

def dump_newsdraw_title_bmpdata(rom):
    rom.seek(0x3e8b80)
    for i in range(4):
        rom.output += "\t{\n"
        rom.output += f"\t\t{rom.read_byte()},\n"
        rom.output += f"\t\t{rom.read_byte()},\n"
        rom.output += f"\t\t{rom.read_byte()},\n"
        rom.output += f"\t\t{rom.read_byte()},\n"
        rom.output += f"\t\t{rom.read_hword()},\n" # cgx
        rom.output += f"\t\t{rom.read_byte()},\n" # pal
        rom.output += f"\t\t{rom.read_byte()}, {rom.read_byte()},\n" # dx
        rom.output += f"\t\t{rom.read_byte()},\n"
        rom.seek(rom.tell() + 2)
        rom.output += f"\t\t0x{rom.read_word():08x},\n"
        rom.output += "\t},\n"
        #rom.seek(rom.tell() + 7)

swi_num_to_name = {
    0: "SoftReset",
    6: "Halt",
    4: "WaitIntr",
    5: "WaitVBlankIntr",
    9: "Div",
    13: "Sqrt",
    11: "CpuSet",
    12: "CpuSetFast",
    16: "UnpackBits",
    17: "UncompressLZ8",
    18: "UncompressLZ16FromDevice",
    0x13: "UncompressHuffmanFromDevice",
    0x14: "UncompressRL8",
    0x15: "UncompressRL16FromDevice",
    #0x16: "Diff8bitUnFilterWrite8bit",
    #0x18: "Diff16bitUnFilter",
    3: "WaitByLoop",
    14: "GetCRC16",
    15: "IsMmemExpanded",
}
    
def dump_libsyscall(rom):
    rom.virtual_seek_static(0x2000000)

    cur_col = 0
    rom.output += "  "
    i = 0

    while i < 0x400:
        hword = rom.read_hword()
        if 0xdf00 <= hword <= 0xdf1f and hword != 0xdf1d and rom.virtual_tell_static() != 0x20005e2:
            if rom.output[-2] == ",":
                rom.output = rom.output[:-2]
            
            swi_num = hword & 0xff
            swi_name = swi_num_to_name[swi_num]
            rom.output += f"\n\n\t.thumb\n\t.global SVC_{swi_name}\nSVC_{swi_name}:\n\tswi {swi_num}"
            #rom.output += f"\n\tswi {hword & 0xff}"
            #rom.push_pos_static()
            while True:
                next_hword = rom.read_hword()
                i += 1
                if next_hword == 0x4770:
                    rom.output += f"\n\tbx lr\n"
                    break
                elif next_hword == 0x1c08:
                    rom.output += f"\n\tmov r0, r1"
                else:
                    raise RuntimeError()

            cur_col = 0
        else:
            if cur_col == 0:
                if rom.output[-2] == ",":
                    rom.output = rom.output[:-2]
                rom.output += "\n\t.byte "

            rom.output += f"0x{hword & 0xff:02x}, 0x{hword >> 8:02x}, "
            cur_col += 2
            if cur_col == 16:
                cur_col = 0
        i += 1
           
    rom.output += "\n"

class DupWord:
    __slots__ = ("ptr", "count")

    def __init__(self, ptr, count):
        self.ptr = ptr
        self.count = count

def dump_pms_word(rom):
    rom.virtual_seek_static(0x020E5538)
    dup_words = []

    for i in range(12):
        ptr = rom.read_word()
        count = rom.read_word()
        dup_words.append(DupWord(ptr, count))
        rom.output += f"\t{{ DupWord_{i:02d}, {count} }},\n"

    rom.output += "\n"

    for i, dup_word in enumerate(dup_words):
        rom.virtual_seek_static(dup_word.ptr)
        rom.output += f"static const PMS_WORD DupWord_{i:02d}[] = {{\n"
        rom.output_hwords_list(dup_word.count, tab=1, pad=False, space_after_comma=False, trailing_comma=True, hex_format=False)
        rom.output += f"}};\n\n"

def main():
    MODE = 8
    if MODE == 0:
        BinFile.run_dump_func(dump_scrcmd_ptrs, "scrcmd_ptrs.dump", do_mainrom=True)
    elif MODE == 1:
        BinFile.run_dump_func(dump_archive_file_table, "archive_file_table.dump", do_mainrom=False)
    elif MODE == 2:
        BinFile.run_dump_func(dump_gage_parts_txt, "gage_parts_txt.dump", do_mainrom=False)
    elif MODE == 3:
        BinFile.run_dump_func(dump_shift_symbol, "shift_symbol.dump", do_mainrom=False)
    elif MODE == 4:
        BinFile.run_dump_func(dump_shift_val_symbol, "shift_val_symbol.dump", do_mainrom=False)
    elif MODE == 5:
        BinFile.run_dump_func(dump_stafflist, "stafflist.dump", do_mainrom=False)
    elif MODE == 6:
        BinFile.run_dump_func(dump_newsdraw_title_bmpdata, "newsdraw_title_bmpdata.dump")
    elif MODE == 7:
        BinFile.run_dump_func(dump_libsyscall, "libsyscall.s")
    elif MODE == 8:
        BinFile.run_dump_func(dump_pms_word, "pms_word.dump")
    else:
        print(f"Unknown MODE {MODE}!")

if __name__ == "__main__":
    main()
