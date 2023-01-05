dummy_macros_str = """DWC_SetConnectApType
DWC_SetReportLevel
DWC_Printf
DWC_SetSendDelay
DWC_SetRecvDelay
DWC_SetSendDrop
DWC_SetRecvDrop
VIBi_FatalError
MB_COMM_TYPE_OUTPUT
MB_COMM_WMEVENT_OUTPUT
MB_OUTPUT
MB_DEBUG_OUTPUT
MB_FAKE_OUTPUT
MBFi_PrintMBCallbackType
MBFi_PrintMBCommCallbackType
MIi_WARNING_ADDRINTCM
SDK_ASSERT
SDK_NULL_ASSERT
SDK_MINMAX_ASSERT
SNDi_LockMutex
SNDi_UnlockMutex
WBT_DEBUG_OUTPUT0
WBT_DEBUG_OUTPUT1
WBT_DEBUG_OUTPUT2
WM_DPRINTF_DATASHARING
WM_DPRINTF_CALLBACK
WM_DPRINTF_AIDBITMAP
WM_DLOG
WM_DLOGF
WM_DLOG_DATASHARING
WM_DLOGF_DATASHARING
WM_DLOG_CALLBACK
WM_DLOGF_CALLBACK
WM_DLOGF2_CALLBACK
WM_DLOG_AIDBITMAP
WM_DLOGF_AIDBITMAP
WM_WARNING
WM_ASSERT
WM_ASSERTMSG
WM_DPRINTF
WMi_Printf
WMi_Warning
printf
SDK_ALIGN4_ASSERT
SDK_ASSERTMSG
GX_BGMODE_WARNING1
GX_BGMODE_WARNING2
GX_BGMODE_WARNING3
GXS_BGMODE_WARNING1
GXS_BGMODE_WARNING2
GXS_BGMODE_WARNING3
SDK_TASSERTMSG
SDK_WARNING
SDK_TWARNING
SDK_MIN_ASSERT
SDK_MAX_ASSERT
SDK_FATAL_ERROR
SDK_TFATAL_ERROR
SDK_INTERNAL_ERROR
SDK_TINTERNAL_ERROR
SDK_ALIGN2_ASSERT
OS_CheckIrqStack
OS_PutString
OSi_Warning
OSi_TWarning
OS_PutChar
OS_VPrintf
OS_Printf
OS_Warning
OS_TVPrintf
OS_TVPrintfEx
OS_TPrintf
OS_TPrintfEx
OS_TWarning
OS_InitPrintServer
OS_PrintServer
OS_CheckStack
UT_AssertAsserted
UT_AssertNotAsserted
UT_Assert
UT_AssertEq
UT_AssertNe
UT_AssertMemPtrEq
UT_AssertMemPtrNe
UT_AssertMemEq
UT_AssertMemNe
WFS_DEBUG_OUTPUT
WCMi_Printf
WCMi_Warning
NNS_ALIGN4_ASSERT
NNS_MINMAX_ASSERT
NNS_MAX_ASSERT
NNS_NULL_ASSERT
NNS_WARNING
NNS_ASSERTMSG
NNS_ASSERT
NNS_McsPollingIdle
NNS_McsClearBuffer
NNS_GFD_WARNING
NNSI_G2D_DEBUGMSG1
NNSI_G2D_DEBUGMSG0
FillNoUseMemory
FillFreeMemory
"""

import subprocess

def main():
    dummy_macros = dummy_macros_str.strip().splitlines()
    output_good = []
    output_bad = []

    for dummy_macro in dummy_macros:
        print(f"Searching for {dummy_macro}!")
        found_uses = subprocess.check_output(["ggrep", dummy_macro]).decode("utf-8", "replace")
        found_uses_as_list = found_uses.strip().splitlines()
        any_uses_in_src = any(x.startswith("src/") for x in found_uses_as_list)
        num_found_uses = len(found_uses_as_list)
        if any_uses_in_src:
            cur_output = f"{dummy_macro} (in src)\n"#f"Found {num_found_uses} uses of {dummy_macro}!\n"
        else:
            cur_output = f"{dummy_macro}\n"#f"Found {num_found_uses} uses of {dummy_macro}!\n"            
        if num_found_uses > 3:
            output_good.append(cur_output)
        else:
            output_bad.append(cur_output)

    output = ""
    output += "== More than 3 lines ==\n"
    output += "".join(output_good)
    output += "== not More than 3 lines ==\n"
    output += "".join(output_bad)

    with open("find_used_dummy_macros_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
