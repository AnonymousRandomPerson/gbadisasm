#ifndef POKEPLATINUM_SYSTEM_MACROS_H
#define POKEPLATINUM_SYSTEM_MACROS_H

#define XtOffset(p_type, field)          ((unsigned int)&(((p_type )NULL)->field))
#define NELEMS(array)                   (sizeof(array) / sizeof(array[0]))
#define ROUND_UP(value, alignment)      (((u32)(value) + (alignment - 1)) & ~(alignment - 1))
#define ROUND_DOWN(value, alignment)    ((u32)(value) & ~(alignment - 1))

#endif // POKEPLATINUM_SYSTEM_MACROS_H
