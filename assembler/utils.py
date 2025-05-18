from .constants import INSTRUCTION_SIZE

def get_instruction_size(opcode, operand):
    if opcode == 'WORD':
        return 3
    elif opcode == 'RESW':
        return 3 * int(operand)
    elif opcode == 'RESB':
        return int(operand)
    elif opcode == 'BYTE':
        if operand.startswith("C'"):
            return len(operand) - 3
        elif operand.startswith("X'"):
            return (len(operand) - 3) // 2
    elif opcode in INSTRUCTION_SIZE:
        return INSTRUCTION_SIZE[opcode]
    return 0
