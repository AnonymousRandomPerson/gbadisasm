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

bad_nl_files = ("lib/include/nnsys_win32.h", "lib/include/nnsys_prefix.h", "lib/include/nnsys/snd/waveout.h", "lib/include/nnsys/snd/stream.h", "lib/include/nnsys/snd/sndarc_stream.h", "lib/include/nnsys/snd/sndarc_player.h", "lib/include/nnsys/snd/sndarc_loader.h", "lib/include/nnsys/snd/sndarc.h", "lib/include/nnsys/snd/seqdata.h", "lib/include/nnsys/snd/resource_mgr.h", "lib/include/nnsys/snd/player.h", "lib/include/nnsys/snd/output_effect.h", "lib/include/nnsys/snd/main.h", "lib/include/nnsys/snd/heap.h", "lib/include/nnsys/snd/fader.h", "lib/include/nnsys/snd/config.h", "lib/include/nnsys/snd/capture.h", "lib/include/nnsys/snd.h", "lib/include/nnsys/misc.h", "lib/include/nnsys/mcs/ringBuffer.h", "lib/include/nnsys/mcs/print.h", "lib/include/nnsys/mcs/fileIOcommon.h", "lib/include/nnsys/mcs/fileIObase.h", "lib/include/nnsys/mcs/config.h", "lib/include/nnsys/mcs/baseCommon.h", "lib/include/nnsys/mcs/base_win32.h", "lib/include/nnsys/mcs/base.h", "lib/include/nnsys/mcs.h", "lib/include/nnsys/inline.h", "lib/include/nnsys/gfd/VramTransferMan/gfd_VramTransferManager.h", "lib/include/nnsys/gfd/VramManager/gfd_VramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_TexVramMan_Types.h", "lib/include/nnsys/gfd/VramManager/gfd_PlttVramMan_Types.h", "lib/include/nnsys/gfd/VramManager/gfd_LinkedListVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_LinkedListTexVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_LinkedListPlttVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_FrameTexVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_FramePlttVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_BitArrayTexVramMan.h", "lib/include/nnsys/gfd/VramManager/gfd_BitArrayPlttVramMan.h", "lib/include/nnsys/gfd/gfd_common.h", "lib/include/nnsys/gfd.h", "lib/include/nnsys/g3d/util_inline.h", "lib/include/nnsys/g3d/util.h", "lib/include/nnsys/g3d/sbc_inline.h", "lib/include/nnsys/g3d/sbc.h", "lib/include/nnsys/g3d/model_inline.h", "lib/include/nnsys/g3d/model.h", "lib/include/nnsys/g3d/mem.h", "lib/include/nnsys/g3d/kernel_inline.h", "lib/include/nnsys/g3d/kernel.h", "lib/include/nnsys/g3d/glbstate_inline.h", "lib/include/nnsys/g3d/glbstate.h", "lib/include/nnsys/g3d/gecom_inline.h", "lib/include/nnsys/g3d/gecom.h", "lib/include/nnsys/g3d/config.h", "lib/include/nnsys/g3d/cgtool/xsi.h", "lib/include/nnsys/g3d/cgtool/si3d.h", "lib/include/nnsys/g3d/cgtool/maya.h", "lib/include/nnsys/g3d/cgtool/basic.h", "lib/include/nnsys/g3d/cgtool/3dsmax.h", "lib/include/nnsys/g3d/cgtool.h", "lib/include/nnsys/g3d/binres/res_struct_accessor_inline.h", "lib/include/nnsys/g3d/binres/res_struct_accessor_anm.h", "lib/include/nnsys/g3d/binres/res_struct_accessor.h", "lib/include/nnsys/g3d/binres/res_struct.h", "lib/include/nnsys/g3d/binres/res_print.h", "lib/include/nnsys/g3d/anm/nsbva.h", "lib/include/nnsys/g3d/anm/nsbtp.h", "lib/include/nnsys/g3d/anm/nsbta.h", "lib/include/nnsys/g3d/anm/nsbma.h", "lib/include/nnsys/g3d/anm/nsbca.h", "lib/include/nnsys/g3d/anm.h", "lib/include/nnsys/g3d/1mat1shp.h", "lib/include/nnsys/g3d.h", "lib/include/nnsys/g2d/load/g2d_NSC_load.h", "lib/include/nnsys/g2d/load/g2d_NMC_load.h", "lib/include/nnsys/g2d/load/g2d_NFT_load.h", "lib/include/nnsys/g2d/load/g2d_NEN_load.h", "lib/include/nnsys/g2d/load/g2d_NCL_load.h", "lib/include/nnsys/g2d/load/g2d_NCG_load.h", "lib/include/nnsys/g2d/load/g2d_NCE_load.h", "lib/include/nnsys/g2d/load/g2d_NAN_load.h", "lib/include/nnsys/g2d/g2di_SplitChar.h", "lib/include/nnsys/g2d/g2di_Char.h", "lib/include/nnsys/g2d/g2di_AssertUtil.h", "lib/include/nnsys/g2d/g2d_TextCanvas.h", "lib/include/nnsys/g2d/g2d_SRTControl.h", "lib/include/nnsys/g2d/g2d_Softsprite.h", "lib/include/nnsys/g2d/g2d_Screen.h", "lib/include/nnsys/g2d/g2d_RendererCore.h", "lib/include/nnsys/g2d/g2d_Renderer.h", "lib/include/nnsys/g2d/g2d_PaletteTable.h", "lib/include/nnsys/g2d/g2d_OamSoftwareSpriteDraw.h", "lib/include/nnsys/g2d/g2d_OAMEx.h", "lib/include/nnsys/g2d/g2d_OAM_Types.h", "lib/include/nnsys/g2d/g2d_OAM.h", "lib/include/nnsys/g2d/g2d_Node.h", "lib/include/nnsys/g2d/g2d_MultiCellAnimation.h", "lib/include/nnsys/g2d/g2d_Load.h", "lib/include/nnsys/g2d/g2d_Image.h", "lib/include/nnsys/g2d/g2d_Font.h", "lib/include/nnsys/g2d/g2d_Entity.h", "lib/include/nnsys/g2d/g2d_Data.h", "lib/include/nnsys/g2d/g2d_CullingUtility.h", "lib/include/nnsys/g2d/g2d_config.h", "lib/include/nnsys/g2d/g2d_CharCanvas.h", "lib/include/nnsys/g2d/g2d_CellTransferManager.h", "lib/include/nnsys/g2d/g2d_CellAnimation.h", "lib/include/nnsys/g2d/g2d_Animation_inline.h", "lib/include/nnsys/g2d/g2d_Animation.h", "lib/include/nnsys/g2d/fmt/g2d_Vec_data.h", "lib/include/nnsys/g2d/fmt/g2d_SRTControl_data.h", "lib/include/nnsys/g2d/fmt/g2d_Screen_data.h", "lib/include/nnsys/g2d/fmt/g2d_Oam_data.h", "lib/include/nnsys/g2d/fmt/g2d_MultiCell_data.h", "lib/include/nnsys/g2d/fmt/g2d_Font_data.h", "lib/include/nnsys/g2d/fmt/g2d_Entity_data.h", "lib/include/nnsys/g2d/fmt/g2d_Common_data.h", "lib/include/nnsys/g2d/fmt/g2d_Character_data.h", "lib/include/nnsys/g2d/fmt/g2d_Cell_data.h", "lib/include/nnsys/g2d/fmt/g2d_Anim_data.h", "lib/include/nnsys/g2d.h", "lib/include/nnsys/fnd/unitheap.h", "lib/include/nnsys/fnd/list.h", "lib/include/nnsys/fnd/heapcommon.h", "lib/include/nnsys/fnd/frameheap.h", "lib/include/nnsys/fnd/expheap.h", "lib/include/nnsys/fnd/config.h", "lib/include/nnsys/fnd/archive.h", "lib/include/nnsys/fnd/allocator.h", "lib/include/nnsys/fnd.h", "lib/include/nitroWiFi_noso.h", "lib/include/nitroWiFi/wcm.h", "lib/include/nitroWiFi/ssl.h", "lib/include/nitroWiFi/socl.h", "lib/include/nitroWiFi/socket.h", "lib/include/nitroWiFi/soc_stub.h", "lib/include/nitroWiFi/soc_errcode.h", "lib/include/nitroWiFi/soc.h", "lib/include/nitroWiFi/so2soc.h", "lib/include/nitroWiFi/iw2wcm.h", "lib/include/nitroWiFi/cps.h", "lib/include/nitroWiFi.h", "lib/include/ninet/nwbase/md5.h", "lib/include/ninet/iw/iw_wm.h", "lib/include/ninet/ip.h", "lib/include/ninet.h")

import os

def main():
    os.chdir("../pokeplatinum")

    for filename in bad_nl_files:
        with open(filename, "r") as f:
            contents = f.read()

        with open(filename, "w+") as f:
            f.write(contents)

if __name__ == "__main__":
    main()
