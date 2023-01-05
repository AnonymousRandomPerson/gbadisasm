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

import pathlib
import os

empty_inc_files = ["unk_021D0D40.inc", "dtcm.inc", "ov101_021D94D8.inc", "ov114_02260038.inc", "ov115_02265A18.inc", "ov12_02226998.inc", "ov12_022384F0.inc", "ov18_02244C2C.inc", "ov18_02244C84.inc", "ov18_02245E50.inc", "ov21_021D1F90.inc", "ov23_0225426C.inc", "ov23_0225429C.inc", "ov4_021D75D4.inc", "ov4_02203798.inc", "ov4_022058A0.inc", "ov4_02208208.inc", "ov4_02211D9C.inc", "ov4_02216670.inc", "ov4_02216AB8.inc", "ov4_02216BA0.inc", "ov4_02216CC0.inc", "ov4_02216DD8.inc", "ov4_02217270.inc", "ov4_0221A13C.inc", "ov5_021F0E84.inc", "ov5_021FAF40.inc", "ov5_021FF6B8.inc", "ov6_022477B8.inc", "ov60_02229B20.inc", "ov61_0222E478.inc", "ov65_02236474.inc", "ov66_0225B6D4.inc", "ov83_0223D144.inc", "ov97_022337FC.inc", "overlay0.inc", "overlay103.inc", "overlay15.inc", "overlay2.inc", "overlay3.inc", "overlay89.inc", "unk_0201E010.inc", "unk_0202414C.inc", "unk_020241F0.inc", "unk_02039A58.inc", "unk_020573FC.inc", "unk_0205DAC8.inc", "unk_020923C0.inc", "unk_02098988.inc", "unk_020A2238.inc", "unk_020A490C.inc", "unk_020A4A34.inc", "unk_020A5A2C.inc", "unk_020A5A3C.inc", "unk_020A727C.inc", "unk_020A8180.inc", "unk_020AB040.inc", "unk_020AE47C.inc", "unk_020B5EA4.inc", "unk_020BB368.inc", "unk_020BB44C.inc", "unk_020BD17C.inc", "unk_020BDBC8.inc", "unk_020BDEEC.inc", "unk_020BF03C.inc", "unk_020BF4AC.inc", "unk_020C11A8.inc", "unk_020C1274.inc", "unk_020C2728.inc", "unk_020C2BB0.inc", "unk_020C3508.inc", "unk_020C351C.inc", "unk_020C353C.inc", "unk_020C3774.inc", "unk_020C42C4.inc", "unk_020C4AF0.inc", "unk_020C4F40.inc", "unk_020C4F48.inc", "unk_020C5CF0.inc", "unk_020C5EEC.inc", "unk_020C95B0.inc", "unk_020C977C.inc", "unk_020C99FC.inc", "unk_020D2FE4.inc", "unk_020D4070.inc", "unk_020D51D0.inc", "unk_020D753C.inc", "unk_020D76A0.inc", "unk_020D8B60.inc", "unk_020DAE20.inc", "unk_020DCE64.inc", "unk_020DE05C.inc", "unk_020DE084.inc", "unk_020DF7D4.inc", "unk_020DFF84.inc", "unk_020E0088.inc", "unk_020E00D4.inc", "unk_020E012C.inc", "unk_020E01B8.inc", "unk_020E0234.inc", "unk_020E0598.inc", "unk_020E0D24.inc", "unk_020E12F8.inc", "unk_020E16BC.inc", "unk_020E1740.inc", "unk_020E1774.inc", "unk_020E17B4.inc", "unk_020E1F1C.inc", "unk_020E1F3C.inc", "unk_020E1F6C.inc", "unk_020E2178.inc", "unk_020E235C.inc", "unk_020E28B8.inc", "unk_020E2980.inc", "unk_020E402C.inc", "unk_020E454C.inc", "unk_020E4C40.inc", "unk_020EDBAC.inc", "unk_020F6824.inc", "unk_020F983C.inc", "unk_020FE5DC.inc", "unk_020FE764.inc", "unk_020FE99C.inc", "unk_02100F3C.inc", "unk_021015AC.inc", "unk_021015BC.inc", "unk_021D03E0.inc", "unk_021D0920.inc"]

def main():
    os.chdir("../pokeplatinum")
    for empty_inc_file in empty_inc_files:
        asm_file = f"asm/{pathlib.Path(empty_inc_file).with_suffix('.s')}"

        with open(asm_file, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if empty_inc_file in line:
                lines[i] = ""
                break

        output = "".join(lines)
        with open(asm_file, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
