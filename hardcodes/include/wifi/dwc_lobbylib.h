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

#endif // POKEPLATINUM_DWC_LOBBYLIB_H
