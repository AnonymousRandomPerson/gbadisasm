
enum LabelType
{
    LABEL_ARM_CODE,
    LABEL_THUMB_CODE,
    LABEL_DATA,
    LABEL_POOL,
    LABEL_JUMP_TABLE,
};

extern uint8_t *gInputFileBuffer;
extern size_t gInputFileBufferSize;
extern uint32_t ROM_LOAD_ADDR;
extern uint32_t gRomStart;
extern uint32_t gRamStart;

// disasm.c
int disasm_add_label(uint32_t addr, uint8_t type, char *name);
void disasm_disassemble(void);
