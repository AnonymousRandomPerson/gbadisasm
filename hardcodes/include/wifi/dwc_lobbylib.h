#ifndef POKEPLATINUM_DWC_LOBBYLIB_H
#define POKEPLATINUM_DWC_LOBBYLIB_H

#include <ppwlobby/ppw_lobby.h>
#include "enums.h"

typedef void (* pDWC_LOBBY_UserInCallBack)(s32 userid, const void * cp_profile, void * p_work, BOOL mydata);
typedef void (* pDWC_LOBBY_UserOutCallBack)(s32 userid, void * p_work);
typedef void (* pDWC_LOBBY_UserProfileUpDateCallBack)(s32 userid, const void * cp_profile, void * p_work);
typedef void (* pDWC_LOBBY_EventCallBack)(PPW_LOBBY_TIME_EVENT event, void * p_work);
typedef void (* pDWC_LOBBY_CheckProfileCallBack)(const void * cp_profile, u32 profile_size, void * p_work);
typedef void (* pDWC_LOBBY_MsgDataRecvCallBack)(s32 userid, const void * cp_data, u32 size, void * p_work);

typedef struct {
    pDWC_LOBBY_UserInCallBack p_user_in;
    pDWC_LOBBY_UserOutCallBack p_user_out;
    pDWC_LOBBY_UserProfileUpDateCallBack p_profile_update;
    pDWC_LOBBY_EventCallBack p_event;
    pDWC_LOBBY_CheckProfileCallBack p_check_profile;
} DWC_LOBBY_CALLBACK;

typedef struct {
    pDWC_LOBBY_MsgDataRecvCallBack p_func;
    u32 size;
} DWC_LOBBY_MSGCOMMAND;

typedef struct {
    u32 num;
    const s32 * cp_tbl;
} DWC_LOBBY_CHANNEL_USERID;

void ov66_022324F0(u32 param0, UnkStruct_021C0794 * param1, u32 param2, const DWC_LOBBY_CALLBACK * param3, void * param4);
void ov66_02232598(void);
DWC_LOBBY_CHANNEL_STATE ov66_022325D8(void);
PPW_LOBBY_ERROR ov66_022326DC(void);
s32 ov66_0223270C(PPW_LOBBY_ERROR param0);
BOOL ov66_02232714(const void * param0);
BOOL ov66_02232720(const void * param0, u32 param1);
BOOL ov66_02232804(void);
void ov66_0223282C(void);
BOOL ov66_02232854(void);
DWC_LOBBY_CHANNEL_STATE ov66_0223287C(void);
BOOL ov66_022328CC(void);
s32 ov66_022328F0(void);
void ov66_02232908(const void * param0);
const void * ov66_0223293C(s32 param0);
void ov66_0223295C(s32 param0, s64 * param1);
s32  ov66_02232988(void);
s32  ov66_022329E4(s32 param0);
BOOL ov66_02232A48(DWC_LOBBY_SUBCHAN_TYPE param0);
DWC_LOBBY_SUBCHAN_LOGIN_RESULT ov66_02232A84(void);
BOOL ov66_02232AA4(void);
BOOL ov66_02232AD4(void);
BOOL ov66_02232B00(DWC_LOBBY_SUBCHAN_TYPE param0);
void ov66_02232B20(DWC_LOBBY_CHANNEL_USERID * param0);
void ov66_02232B4C(DWC_LOBBY_CHANNEL_USERID * param0);
u32 ov66_02232B78(s32 param0);
u32 ov66_02232B8C(s32 param0);
s32 ov66_02232BA0(u32 param0);
s32 ov66_02232BB4(u32 param0);
void ov66_02232BC8(s64 * param0);
u32 ov66_02232BEC(DWC_LOBBY_ROOMDATA_TYPE param0);
BOOL ov66_02232C8C(void);
BOOL ov66_02232CB8(void);
u16 ov66_02232CD4(u8 param0);
u8 ov66_02232D00(u8 param0);
void ov66_02232D30(const DWC_LOBBY_MSGCOMMAND * param0, u32 param1, void * param2);
void ov66_02232D60(const DWC_LOBBY_MSGCOMMAND * param0, u32 param1, void * param2);
void ov66_02232D90(void);
void ov66_02232DC8(void);
void ov66_02232E00(u32 param0, const void * param1, u32 param2);
void ov66_02232E5C(u32 param0, s32 param1, const void * param2, u32 param3);
void ov66_02232EBC(u32 param0, const void * param1, u32 param2);
BOOL ov66_02232F38(DWC_LOBBY_MG_TYPE param0, u32 param1);
void ov66_02233064(void);
void ov66_022330CC(void);
BOOL ov66_02233128(void);
void ov66_0223361C(void);
BOOL ov66_02233164(void);
BOOL ov66_02233184(DWC_LOBBY_MG_TYPE param0);
BOOL ov66_022331A4(DWC_LOBBY_MG_TYPE param0);
u32 ov66_022331E4(DWC_LOBBY_MG_TYPE param0);
u32 ov66_02233224(DWC_LOBBY_MG_TYPE param0);
BOOL ov66_02233260(DWC_LOBBY_MG_TYPE param0);
s32 ov66_022332F8(DWC_LOBBY_MG_TYPE param0);
s32 ov66_02233340(void);
BOOL ov66_02233374(void);
BOOL ov66_02233394(s32 param0);
s32 ov66_022333BC(s32 param0);
void ov66_022333E4(s32 param0);
DWC_LOBBY_ANKETO_STATE ov66_02233434(void);
s32 ov66_02233454(DWC_LOBBY_ANKETO_DATA param0);
u16 * ov66_02233538(DWC_LOBBY_ANKETO_MESSAGE param0);
BOOL ov66_022335C0(DWC_LOBBY_ANKETO_LANGUAGE_DATA param0, u32 param1);

#endif // POKEPLATINUM_DWC_LOBBYLIB_H
