#ifndef POKEPLATINUM_POKE_NET_GDS_H
#define POKEPLATINUM_POKE_NET_GDS_H

#include "overlay062/struct_ov62_022349A8_sub1.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub1.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub2.h"
#include "overlay062/struct_ov62_0223D518_sub1.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub3.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub4.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub5.h"
#include "overlay062/struct_ov62_022349A8_sub3_sub5.h"

#ifdef __cplusplus
extern "C" {
#endif

BOOL POKE_NET_GDS_Initialize(UnkStruct_ov62_022349A8_sub1 * _auth);
void POKE_NET_GDS_Release();
void POKE_NET_GDS_SetThreadLevel(unsigned long _level);
int POKE_NET_GDS_GetStatus();
int POKE_NET_GDS_GetLastErrorCode();
BOOL POKE_NET_GDS_Abort();
BOOL POKE_NET_GDS_DebugMessageRequest(char * _message, void * _response);
BOOL POKE_NET_GDS_DressupShotRegist(UnkStruct_ov62_022349A8_sub3_sub1 * _data, void * _response);
BOOL POKE_NET_GDS_DressupShotGet(long _pokemonno, void * _response);
BOOL POKE_NET_GDS_BoxShotRegist(long _groupno, UnkStruct_ov62_022349A8_sub3_sub2 * _data, void * _response);
BOOL POKE_NET_GDS_BoxShotGet(long _groupno, void * _response);
BOOL POKE_NET_GDS_RankingGetType(void * _response);
BOOL POKE_NET_GDS_RankingUpdate(UnkStruct_ov62_0223D518_sub1 * _data, void * _response);
void * POKE_NET_GDS_GetResponse();
long POKE_NET_GDS_GetResponseSize();
long POKE_NET_GDS_GetResponseMaxSize(long _reqno);
BOOL POKE_NET_GDS_BattleDataRegist(UnkStruct_ov62_022349A8_sub3_sub3 * _data, void * _response);
BOOL POKE_NET_GDS_BattleDataSearchCondition(UnkStruct_ov62_022349A8_sub3_sub4 * _condition, void * _response);
BOOL POKE_NET_GDS_BattleDataSearchRanking(UnkStruct_ov62_022349A8_sub3_sub5 * _condition, void * _response);
BOOL POKE_NET_GDS_BattleDataSearchExRanking(UnkStruct_ov62_022349A8_sub3_sub5 * _condition, void * _response);
BOOL POKE_NET_GDS_BattleDataGet(u64 _code, u32 _sver, void * _response);
BOOL POKE_NET_GDS_BattleDataFavorite(u64 _code, void * _response);

#ifdef __cplusplus
}
#endif

#endif // POKEPLATINUM_POKE_NET_GDS_H
