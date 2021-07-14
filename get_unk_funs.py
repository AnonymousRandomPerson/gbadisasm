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

functions = set(["FUN_020A44C8", "FUN_020A450C", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D7780", "FUN_020C4DB0", "FUN_021D77C4", "FUN_021D76E8", "FUN_021D76E8", "FUN_021D77C4", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_021D77C4", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D50D8", "FUN_021EA840", "FUN_020D8C44", "FUN_020D8C44", "FUN_021D806C", "FUN_020CC218", "FUN_020C1B18", "FUN_020C3FA0", "FUN_021DB408", "FUN_020C3FA0", "FUN_020D8B60", "FUN_021EA840", "FUN_020C1B18", "FUN_020C1B18", "FUN_020D8B60", "FUN_020D8B60", "FUN_021DB414", "FUN_020D8D14", "FUN_020D5190", "FUN_020D8D14", "FUN_020D5190", "FUN_020D8D14", "FUN_020D8D14", "FUN_020C3FA0", "FUN_020C3FA0", "FUN_020C3FA0", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D77C4", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020D5124", "FUN_021D77C4", "FUN_020D8B60", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D50D8", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D8B60", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D5190", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D7350", "FUN_020D3DA0", "FUN_020D50B8", "FUN_020D50D8", "FUN_020D50B8", "FUN_021D77C4", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_021D77C4", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020D5124", "FUN_020D50B8", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_021D77C4", "FUN_020C4DB0", "FUN_020E4000", "FUN_020E3FD4", "FUN_020C4DB0", "FUN_020C4DB0", "FUN_020E2178", "FUN_021D806C", "FUN_020CC218", "FUN_020E2178", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_020E2178", "FUN_020E2178", "FUN_020E2178", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_020DFBDC", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020E2178", "FUN_020E2178", "FUN_020D50D8", "FUN_020D50D8", "FUN_020E2178", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_020E2178", "FUN_020D50D8", "FUN_020D50D8", "FUN_020D50D8", "FUN_020DFBDC", "FUN_020DFBDC", "FUN_020E2178", "FUN_020D50D8", "FUN_020DACAC", "FUN_020DACAC", "FUN_020DAD44", "FUN_020C4CF4", "FUN_021DB408", "FUN_020D8B60", "FUN_020D5124", "FUN_020D50B8", "FUN_020D5124", "FUN_021D806C", "FUN_020CC218", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_021D806C", "FUN_020CC218", "FUN_020D5190", "FUN_020D5190", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_020D50B8", "FUN_020D5124", "FUN_021D77C4", "FUN_020DFBDC", "FUN_020DFBDC", "FUN_020D50B8", "FUN_020D5124", "FUN_020DFBDC", "FUN_021D77C4", "FUN_021D77C4", "FUN_020DAE0C", "FUN_020D8C44", "FUN_020D50D8", "FUN_021D806C", "FUN_020CC218", "FUN_020C4CF4", "FUN_021D806C", "FUN_020CC218", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D8B60", "FUN_020C4CF4", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D7780", "FUN_021D77C4", "FUN_021D7780", "FUN_021D77C4", "FUN_021D77C4", "FUN_021EA840", "FUN_020DAE0C", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D7350", "FUN_020D3DA0", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_021D77C4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D78B0", "FUN_021E9A8C", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9B50", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_020D50B8", "FUN_020D8B60", "FUN_021D7880", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D50B8", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_021E9C2C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021E9E40", "FUN_021E9E40", "FUN_021E9BBC", "FUN_020D407C", "FUN_021E9BBC", "FUN_021E9BC4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8C44", "FUN_021EA598", "FUN_021EA224", "FUN_021E9A8C", "FUN_021EA364", "FUN_020D407C", "FUN_021EA364", "FUN_021E9B50", "FUN_020D407C", "FUN_020D8C44", "FUN_021E9C2C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D8C44", "FUN_021E9F18", "FUN_021E9DB0", "FUN_021EA4F4", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_021EA638", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_021EA3D8", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA840", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_020D5124", "FUN_021EA840", "FUN_021EA8AC", "FUN_021EA8AC", "FUN_021D7880", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_021D7880", "FUN_020D5124", "FUN_020D8C44", "FUN_021D78B0", "FUN_021D7880", "FUN_021D7880", "FUN_021D7880", "FUN_021D78B0", "FUN_020D8D14", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_021D7880", "FUN_021D78B0", "FUN_020D8D14", "FUN_021EA8AC", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020DF9B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA8A4", "FUN_021D7880", "FUN_020D5124", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_020D8C44", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_021D78B0", "FUN_021EA8A8", "FUN_020D8C44", "FUN_021EA898", "FUN_020D407C", "FUN_020D8C44", "FUN_020D407C", "FUN_020D8C44", "FUN_020D407C", "FUN_021D78B0", "FUN_021EA8A8", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D7510", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EA898", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D407C", "FUN_020D407C", "FUN_020D7510", "FUN_020D407C", "FUN_020D7510", "FUN_020D7510", "FUN_020D8B60", "FUN_020D7510", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D7510", "FUN_020D7510", "FUN_020D8B60", "FUN_020D8D14", "FUN_020D8B60", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8D14", "FUN_021EA898", "FUN_020D8B60", "FUN_020D8E5C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7880", "FUN_021D78B0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021D7894", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D50D8", "FUN_020D407C", "FUN_020D5124", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8C44", "FUN_021EAF1C", "FUN_0220854C", "FUN_021EACDC", "FUN_021EAD78", "FUN_021EACF0", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAD04", "FUN_021EACF0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021EAA74", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAE48", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_021EAE04", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_020D50B8", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D74D0", "FUN_020D407C", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7894", "FUN_020D8B60", "FUN_021D7880", "FUN_020D8B7C", "FUN_020D407C", "FUN_020D407C", "FUN_020D8B60", "FUN_021D7880", "FUN_020D8B7C", "FUN_020D90B0", "FUN_020D8F58", "FUN_021D78B0", "FUN_020D8F58", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D407C", "FUN_020D8B60", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D7880", "FUN_020D50B8", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_021D78B0", "FUN_020D5124", "FUN_020D5124", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020D407C", "FUN_020E2178", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8C44", "FUN_021D7780", "FUN_021EB0F0", "FUN_021D77C4", "FUN_020D8C44", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_020D8C44", "FUN_020DACAC", "FUN_021E558C", "FUN_021D7708", "FUN_021D7724", "FUN_021E5960", "FUN_021E55F0", "FUN_021E5960", "FUN_021E55F0", "FUN_021D77C4", "FUN_021D78B0", "FUN_021E55B0", "FUN_021D77C4", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D74E8", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_020D8B60", "FUN_021D7780", "FUN_020D7510", "FUN_020D8B60", "FUN_020D8B60", "FUN_021D77C4", "FUN_020D50B8", "FUN_020D8B60"])

from xmap import XMap, OvAddr

class Replacement:
    __slots__ = ("from_str", "to")
    def __init__(self, from_str, to):
        self.from_str = from_str
        self.to = to

def main():
    xmap_file = XMap("../master_cpuj00/bin/ARM9-TS/Rom/main.nef.xMAP", ".main")
    functions = list(functions)
    replacements = []

    for function in functions:
        function_addr = int(function[4:], 16)
        full_addr = OvAddr(-1, function_addr)
        symbol = xmap_file.symbols_by_addr.get(full_addr, None)
        if symbol is not None:
            got_symbol = True
        else:
            full_addr = OvAddr(4, function_addr)
            symbol = xmap_file.symbols_by_addr.get(full_addr, None)
            if symbol is None:
                got_symbol = False
            got_symbol = True

        if got_symbol:
            replacements.append(Replacement(function, symbol.name)
        else:
            output += f"{function}\n"
            #replacements.append(Replacement(function, )

    with open
    #output = "\n".join(list(functions)) + "\n"

    #with open("get_unk_funs_out.dump", "w+") as f:
    #    f.write(output)
    
if __name__ == "__main__":
    main()
