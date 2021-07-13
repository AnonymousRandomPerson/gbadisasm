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

MAINROM = 0
BASEROM = 1

class BinFile:
    __slots__ = ("_rom_filename", "_output_filename", "_output", "_rom_file", "_pos_stack")

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

    def output_bytes_list(self, count, tab=0, pad=True):
        tab_str = "\t" * tab
        self._output += tab_str
        for i in range(count):
            if pad:
                self._output += f"0x{self.read_byte():02x},"
            else:
                self._output += f"0x{self.read_byte():x},"

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
    def run_dump_func(dump_func, output_filename, do_mainrom=True):
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

def main():
    MODE = 2
    if MODE == 0:
        BinFile.run_dump_func(dump_scrcmd_ptrs, "scrcmd_ptrs.dump")
    elif MODE == 1:
        BinFile.run_dump_func(dump_archive_file_table, "archive_file_table.dump", do_mainrom=False)
    elif MODE == 2:
        BinFile.run_dump_func(dump_gage_parts_txt, "gage_parts_txt.dump", do_mainrom=False)
    else:
        print(f"Unknown MODE {MODE}!")

if __name__ == "__main__":
    main()
