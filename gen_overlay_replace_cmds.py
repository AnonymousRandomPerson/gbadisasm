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

import json
import os
import subprocess
import re

def main():
    with open("overlaymap.json", "r") as f:
        overlaymap = json.load(f)

    os.chdir("../00jupc_retsam")

    with open("make_prog_files", "r") as f:
        prog_files = f.read()
    #
    #overlay_vars = overlay_var_regex.findall(prog_files)
    #print(f"overlay_vars: {overlay_vars}")

    for overlay_id, overlay_value in overlaymap.items():
        new_overlay_id = f"overlay{overlay_value}"
        overlay_id_replace_cmd = fr"""sed -i 's/FS_OVERLAY_ID({overlay_id})/FS_OVERLAY_ID({new_overlay_id})/' $(git grep -lwr "FS_OVERLAY_ID({overlay_id})")"""
        extern_overlay_replace_cmd = fr"""sed -i 's/FS_EXTERN_OVERLAY({overlay_id})/FS_EXTERN_OVERLAY({new_overlay_id})/' $(git grep -lwr "FS_EXTERN_OVERLAY({overlay_id})")"""
        print(overlay_id_replace_cmd)
        print(extern_overlay_replace_cmd)
        subprocess.run(overlay_id_replace_cmd, shell=True)
        subprocess.run(extern_overlay_replace_cmd, shell=True)
        prog_files = re.sub(fr"\bSRCS_OVERLAY_{overlay_id.upper()}\b", f"SRCS_OVERLAY_OVERLAY{overlay_value}", prog_files)

    with open("make_prog_files_new.mk", "w+") as f:
        f.write(prog_files)

if __name__ == "__main__":
    main()
