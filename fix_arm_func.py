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
lsl_lsr_reg_regex = re.compile(r"^\t(lsl|lsr)(s?) (\w{2}, \w{2}), (\w{2})", flags=re.MULTILINE)
ldr_str_cond_regex = re.compile(r"^\t(ldr|str)(b|h|sb)(eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le)\b", flags=re.MULTILINE)

#"eq|ne|cs|lo|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le"

header = """	.include "macros.inc"
	.include "global.inc"
	.section .text
	.balign 4, 0
"""

functions_set = set(["FUN_020A44C8", "FUN_020A450C", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D7780", "FUN_020C4DB0", "FUN_021D77C4", "FUN_021D76E8", "FUN_021D76E8", "FUN_021D77C4", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_021D77C4", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D50D8", "FUN_021EA840", "FUN_020D8C44", "FUN_020D8C44", "FUN_021D806C", "FUN_020CC218", "FUN_020C1B18", "FUN_020C3FA0", "FUN_021DB408", "FUN_020C3FA0", "FUN_020D8B60", "FUN_021EA840", "FUN_020C1B18", "FUN_020C1B18", "FUN_020D8B60", "FUN_020D8B60", "FUN_021DB414", "FUN_020D8D14", "FUN_020D5190", "FUN_020D8D14", "FUN_020D5190", "FUN_020D8D14", "FUN_020D8D14", "FUN_020C3FA0", "FUN_020C3FA0", "FUN_020C3FA0", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D77C4", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020D5124", "FUN_021D77C4", "FUN_020D8B60", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D50D8", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D8B60", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D5190", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D50B8", "FUN_020D50D8", "FUN_020D50B8", "FUN_021D77C4", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_021D77C4", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020D5124", "FUN_020D50B8", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_021D77C4", "FUN_020C4DB0", "FUN_020E4000", "FUN_020E3FD4", "FUN_020C4DB0", "FUN_020C4DB0", "FUN_020E2178", "FUN_021D806C", "FUN_020CC218", "FUN_020E2178", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_020DFBDC", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020E2178", "FUN_020E2178", "FUN_020D50D8", "FUN_020D50D8", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_020E2178", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_020DFBDC", "FUN_020DFBDC", "FUN_020E2178", "FUN_020D50D8", "FUN_020DACAC", "FUN_020DACAC", "FUN_020DAD44", "FUN_020C4CF4", "FUN_021DB408", "FUN_020D8B60", "FUN_020D5124", "FUN_020D50B8", "FUN_020D5124", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_020D50B8", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020DFBDC", "FUN_020D50B8", "FUN_020D5124", "FUN_020DFBDC", "FUN_021D77C4", "FUN_021D77C4", "FUN_020DAE0C", "FUN_020D8C44", "FUN_020D50D8", "FUN_021D806C", "FUN_020CC218", "FUN_020C4CF4", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D8B60", "FUN_020C4CF4", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D7780", "FUN_021D77C4", "FUN_021D7780", "FUN_021D77C4", "FUN_021D77C4", "FUN_021EA840", "FUN_020DAE0C", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D78B0", "FUN_021E9A8C", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9B50", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_020D50B8", "FUN_020D8B60", "FUN_021D7880", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021E9C2C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9E40", "FUN_021E9E40", "FUN_021E9BBC", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8C44", "FUN_021EA598", "FUN_021EA224", "FUN_021E9A8C", "FUN_021EA364", "FUN_020D407C", "FUN_021EA364", "FUN_021E9B50", "FUN_020D407C", "FUN_020D8C44", "FUN_021E9C2C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D8C44", "FUN_021E9F18", "FUN_021E9DB0", "FUN_021EA4F4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_021EA638", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_021EA3D8", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA840", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_020D5124", "FUN_021EA840", "FUN_021EA8AC", "FUN_021EA8AC", "FUN_021D7880", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_021D7880", "FUN_020D5124", "FUN_020D8C44", "FUN_021D78B0", "FUN_021D7880", "FUN_021D7880", "FUN_021D7880", "FUN_021D78B0", "FUN_020D8D14", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D7880", "FUN_021D78B0", "FUN_020D8D14", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020DF9B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA8A4", "FUN_021D7880", "FUN_020D5124", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_020D8C44", "FUN_021EA898", "FUN_020D407C", "FUN_020D8C44", "FUN_020D407C", "FUN_020D8C44", "FUN_020D407C", "FUN_021D78B0", "FUN_021EA8A8", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D7510", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D7510", "FUN_020D407C", "FUN_020D7510", "FUN_020D7510", "FUN_020D8B60", "FUN_020D7510", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D7510", "FUN_020D7510", "FUN_020D8B60", "FUN_020D8D14", "FUN_020D8B60", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8D14", "FUN_021EA898", "FUN_020D8B60", "FUN_020D8E5C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7894", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D50D8", "FUN_020D407C", "FUN_020D5124", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8C44", "FUN_021EAF1C", "FUN_0220854C", "FUN_021EACDC", "FUN_021EAD78", "FUN_021EACF0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAD04", "FUN_021EACF0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EAA74", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAE48", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAE04", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D74D0", "FUN_020D407C", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7894", "FUN_020D8B60", "FUN_021D7880", "FUN_020D8B7C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_021D7880", "FUN_020D8B7C", "FUN_020D90B0", "FUN_020D8F58", "FUN_021D78B0", "FUN_020D8F58", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D8B60", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D5124", "FUN_020D5124", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020E2178", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8C44", "FUN_021D7780", "FUN_021EB0F0", "FUN_021D77C4", "FUN_020D8C44", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_021E558C", "FUN_021D7708", "FUN_021D7724", "FUN_021E5960", "FUN_021E55F0", "FUN_021E5960", "FUN_021E55F0", "FUN_021D77C4", "FUN_021D78B0", "FUN_021E55B0", "FUN_021D77C4", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D74E8", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_021D7780", "FUN_020D7510", "FUN_020D8B60", "FUN_020D8B60", "FUN_021D77C4", "FUN_020D50B8", "FUN_020D8B60", "FUN_021D7780", "FUN_020D3068", "FUN_020D8E28"])

import dis_single_func
from xmap import XMap, OvAddr

extern_funcs = ["PPW_LobbyGetChannelDataAsync", "PPW_LobbyGetLastError", "PPW_LobbyGetMyUserId", "PPW_LobbyGetSchedule", "PPW_LobbyGetSubChannelState", "PPW_LobbyGetTimeInfo", "PPW_LobbyInitializeAsync", "PPW_LobbyJoinSubChannelAsync", "PPW_LobbyLeaveSubChannel", "PPW_LobbyProcess", "PPW_LobbySendChannelBinaryMessage", "PPW_LobbySendPlayerBinaryMessage", "PPW_LobbySetChannelData", "PPW_LobbyShutdownAsync", "PPW_LobbyStartRecruit", "PPW_LobbyStopRecruit", "PPW_LobbySubmitQuestionnaire", "PPW_LobbyToErrorCode", "PPW_LobbyUpdateMyProfile", "PPW_LobbyUpdateRecruitInfo"]

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
            #print(f"function_addr: {function_addr:07x}")
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
        
    with open("ov66_global.inc", "w+") as f:
        f.write(global_inc_output)

    return output, todo_output

footer = """
	.rodata

	.global ov66_rodata
ov66_rodata:
	// todo
	.rept 240
	.byte 0x69
	.endr

	.data
	.global ov66_data
ov66_data:
	.rept 0x46c
	.byte 0x42
	.endr
"""

def main():
    with open("ov66_in2.s", "r") as f:
        input = f.read()

    output = header + input
    output = push_regex.sub(r"\tstm\1fd sp!,", output)
    output = pop_regex.sub(r"\tldm\1ia sp!,", output)
    output = lsl_lsr_regex.sub(r"\tmov\2\3 \4, \1 \5", output)
    output = lsl_lsr_reg_regex.sub(r"\tmov\2 \3, \1 \4", output)
    #output = ldm_stm_ib_regex.sub(r"\t\1\2ib", output)
    output = ldm_stm_regex.sub(r"\t\1\2ia", output)
    output = ldm_stm_cond_regex.sub(r"\t\1\3\2", output)
    output = ldr_str_cond_regex.sub(r"\t\1\3\2", output)
    output = output.replace("\tpush", "\tstmfd sp!,").replace("\tpop", "\tldmia sp!,").replace("@", "//").replace(".4byte", ".word")

    output, todo_output = fix_unk_funs(output)

    lines = output.splitlines(keepends=True)

    #for i, line in enumerate(lines):
    #    if line.startswith("\tarm_func_start ov66_22483C4"):
    #        output_stop_index = i
    #        break

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

    with open("ov66_new.s", "w+") as f:
        f.write(output)

    with open("ov66_todo_funs.dump", "w+") as f:
        f.write(todo_output)

if __name__ == "__main__":
    main()
