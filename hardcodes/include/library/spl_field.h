#ifndef POKEPLATINUM_SPL_FIELD_H
#define POKEPLATINUM_SPL_FIELD_H

#include "spl_particle.h"

struct SPLEmitter_t;

void spl_calc_gravity(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);
void spl_calc_random(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);
void spl_calc_magnet(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);
void spl_calc_spin(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);
void spl_calc_scfield(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);
void spl_calc_convergence(const void * p_obj, SPLParticle * p_ptcl, VecFx32 * p_acc, struct SPLEmitter_t * p_emtr);

#endif // POKEPLATINUM_SPL_FIELD_H
