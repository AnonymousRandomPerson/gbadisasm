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


import subprocess
import itertools
import glob
import re
import os
import shutil

triple_plus_newline_regex = re.compile(r"\n\n\n+")
extern_c_regex = re.compile(r"^extern\s+\"C\"", flags=re.MULTILINE)
if_elif_define_include_regex = re.compile(r"^(#\s*(?:if|elif|define|include|ifdef|ifndef|undef))\s+", flags=re.MULTILINE)
files_to_fix_as_str = r"""
C:\Users\User\Documents\GitHub\pokeplatinum\lib\include\nnsys\g2d\g2d_Image.h
"""

found_sdk_c_filenames_str = r"""
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/ARM9/src/card_pullOut.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/ARM9/src/card_request.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/common/src/card_backup.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/common/src/card_common.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/common/src/card_rom.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/card/common/src/card_spi.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/cp/src/cp_context.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_backup.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_AT29LV512.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_common.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_LE26FV10N1TS-10.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_LE39FW512.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_MX29L010.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_flash_MX29L512.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_proc.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_sram.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/ARM9/src/ctrdg_task.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/ctrdg/common/src/ctrdg.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_archive.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_command.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_command_default.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_file.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_overlay.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fs/common/src/fs_rom.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_atanidx.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_cp.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_mtx22.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_mtx33.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_mtx43.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_mtx44.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_sincos.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_trig.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/fx/src/fx_vec.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g2.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g3.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g3b.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g3imm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g3x.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/g3_util.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gx.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gxasm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gxstate.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gx_bgcnt.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gx_load2d.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gx_load3d.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/gx/src/gx_vramcnt.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/math/common/src/crc.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/math/common/src/dgt.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/math/common/src/math.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/math/common/src/qsort.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_block.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_cache.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_common.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_fileinfo.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_gameinfo.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_parent.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_task.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mb/src/mb_wm_base.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_dma.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_dma_card.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_dma_gxcommand.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_dma_hblank.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_init.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_swap.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_uncompress.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_wram.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_cache.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_protectionRegion.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_protectionUnit.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_tcm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_terminate_proc.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_vramExclusive.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_alarm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_alloc.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_arena.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_context.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_emulator.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_entropy.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_exception.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_init.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_interrupt.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_irqHandler.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_irqTable.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_message.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_mutex.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_ownerInfo.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_printf.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_reset.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_spinLock.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_system.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_thread.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_tick.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_timer.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_valarm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/pxi/common/src/pxi_fifo.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/pxi/common/src/pxi_init.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/rtc/ARM9/src/convert.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/rtc/ARM9/src/external.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/rtc/ARM9/src/internal.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/ARM9/src/snd_interface.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_alarm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_bank.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_command.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_main.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_util.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/snd/common/src/snd_work.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/spi/ARM9/src/mic.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/spi/ARM9/src/pm.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/spi/ARM9/src/tp.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/std/common/src/std_sprintf.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/std/common/src/std_string.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_dcf.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_ds.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_etc.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_ks.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_mp.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_standard.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_sync.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wm/ARM9/src/wm_system.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/wvr/ARM9/src/wvr.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/allocator.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/archive.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/expheap.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/frameheap.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/heapcommon.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/list.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/fnd/src/unitheap.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Animation.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_CellAnimation.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_CellTransferManager.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_CharCanvas.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Font.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Image.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_MultiCellAnimation.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Node.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_OAM.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_OamSoftwareSpriteDraw.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_PaletteTable.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Renderer.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_RendererCore.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_Softsprite.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_SRTControl.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/g2d_TextCanvas.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/internal/g2di_BitReader.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/internal/g2di_Mtx32.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/internal/g2di_SplitChar.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_Load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NAN_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NCG_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NCL_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NFT_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NMC_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NOB_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g2d/src/load/g2d_NSC_load.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/1mat1shp.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/gecom.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/glbstate.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/kernel.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/mem.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/model.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/sbc.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/util.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm/nsbca.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm/nsbma.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm/nsbta.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm/nsbtp.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/anm/nsbva.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/binres/res_struct_accessor.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/binres/res_struct_accessor_anm.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool/3dsmax.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool/basic.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool/maya.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool/si3d.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/g3d/src/cgtool/xsi.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfdi_LinkedListVramMan_Common.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_FramePlttVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_FrameTexVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_LinkedListPlttVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_LinkedListTexVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_PlttVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramManager/gfd_TexVramMan.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/gfd/src/VramTransferMan/gfd_VramTransferManager.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/capture.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/fader.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/heap.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/main.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/player.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/resource_mgr.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/seqdata.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/sndarc.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/sndarc_loader.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/sndarc_player.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/sndarc_stream.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/stream.c
../00jupc_retsam/sdk/NitroSystem/build/libraries/snd/src/waveout.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/soc.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_bind.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_cleanup.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_close.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_command.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_const.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_create.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_list.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_listen_accept.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_misc.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_poll.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_read.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_resolve.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_shutdown.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_ssl.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_startup.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/soc/src/socl_write.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/stubs/md5/src/dummy_md5.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/wcm/src/aplist.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/wcm/src/cpsif.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/wcm/src/system.c
../00jupc_retsam/sdk/NitroWiFi/build/libraries/wcm/src/util.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/account/src/dwc_account.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/account/src/dwc_init.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_common.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_connectinet.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_error.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_friend.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_ghttp.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_login.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_main.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_match.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_memfunc.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_nasfunc.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_nd.c
../00jupc_retsam/sdk/NitroDWC/build/libraries/base/src/dwc_transport.c
"""

ignore_uncrustify_files_str = r"""
../00jupc_retsam/sdk/NitroSDK/build/libraries/math/common/src/qsort.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_memory.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/mi/common/src/mi_uncompress.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/ARM9/src/os_cache.c
../00jupc_retsam/sdk/NitroSDK/build/libraries/os/common/src/os_context.c
"""

def main():
    #files_to_fix = files_to_fix_as_str.strip().replace("\\", "/").replace("C:/", "/mnt/c/").split("\n")
    #ignore_uncrustify_files = set(ignore_uncrustify_files_str.strip().splitlines())
    MODE = 0
    if MODE == 0:
        uncrustify_src_files = glob.glob("../pokeplatinum/lib/NitroSDK/src/**/*.[ch]", recursive=True)
    else:
        print("No mode selected!")
        return
    #found_sdk_c_filenames_str.strip().split("\n"):
    #("../pokeplatinum/include/global/global.h",):
    #itertools.chain(glob.glob("../pokeplatinum/lib/include/**/*.h", recursive=True)):

    for filename in uncrustify_src_files:
        output_filename = filename#filename.replace("00jupc_retsam", "00jupc_retsam2")
        if True:#filename not in ignore_uncrustify_files:
            command = ("uncrustify", "-c", "1tbs2.cfg", "-f", filename, "-o", output_filename, "--no-backup", "-l", "C")
            #print(command)
            subprocess.run(command, check=True)
        else:
            if filename != output_filename:
                shutil.copyfile(filename, output_filename)

        with open(output_filename, "r") as f:
            contents = f.read()

        output = triple_plus_newline_regex.sub("\n\n", contents).strip() + "\n"
        output = extern_c_regex.sub("extern \"C\"", output)
        output = if_elif_define_include_regex.sub(r"\g<1> ", output)

        with open(output_filename, "w+") as f:
            f.write(output)

if __name__ == "__main__":
    main()
