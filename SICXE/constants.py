# constants.py
"""
Constants for SIC/XE Assembler
Contains opcodes, registers, and other constants needed for assembly
"""

# SIC/XE Instruction opcodes with format information
# Format: opcode -> (hex_value, format_number)
OPCODES = {
    # Format 3/4 instructions
    'CADD': ('18', 3),  # Conditional ADD
    'ADD': ('18', 3),
    'ADDF': ('58', 3),
    'ADDR': ('90', 2),
    'AND': ('40', 3),
    'CLEAR': ('B4', 2),
    'CLOAD': ('08', 3),  # Conditional LOAD - added missing instruction
    'COMP': ('28', 3),
    'COMPF': ('88', 3),
    'COMPR': ('A0', 2),
    'DIV': ('24', 3),
    'DIVF': ('64', 3),
    'DIVR': ('9C', 2),
    'J': ('3C', 3),
    'JEQ': ('30', 3),
    'JGT': ('34', 3),
    'JLT': ('38', 3),
    'JSUB': ('48', 3),
    'LDA': ('00', 3),
    'LDB': ('68', 3),
    'LDCH': ('50', 3),
    'LDF': ('70', 3),
    'LDL': ('08', 3),
    'LDS': ('6C', 3),
    'LDT': ('74', 3),
    'LDX': ('04', 3),
    'MUL': ('20', 3),
    'MULF': ('60', 3),
    'MULR': ('98', 2),
    'OR': ('44', 3),
    'RD': ('D8', 3),
    'RMO': ('AC', 2),
    'RSUB': ('4C', 3),
    'SHIFTL': ('A4', 2),
    'SHIFTR': ('A8', 2),
    'STA': ('0C', 3),
    'STB': ('78', 3),
    'STCH': ('54', 3),
    'STF': ('80', 3),
    'STI': ('D4', 3),
    'STL': ('14', 3),
    'STS': ('7C', 3),
    'STSW': ('E8', 3),
    'STT': ('84', 3),
    'STX': ('10', 3),
    'SUB': ('1C', 3),
    'SUBF': ('5C', 3),
    'SUBR': ('94', 2),
    'SVC': ('B0', 2),
    'TD': ('E0', 3),
    'TIX': ('2C', 3),
    'TIXR': ('B8', 2),
    'WD': ('DC', 3),
    
    # Format 1 instructions
    'FIX': ('C4', 1),
    'FLOAT': ('C0', 1),
    'HIO': ('F4', 1),
    'NORM': ('C8', 1),
    'SIO': ('F0', 1),
    'TIO': ('F8', 1),
}

# Register codes for Format 2 instructions
REGISTERS = {
    'A': 0,
    'X': 1,
    'L': 2,
    'B': 3,
    'S': 4,
    'T': 5,
    'F': 6,
    'PC': 8,
    'SW': 9,
    'Z': 0,  # Added Z register (sometimes used as synonym for A register)
}

# Assembler directives
DIRECTIVES = {
    'START', 'END', 'BYTE', 'WORD', 'RESB', 'RESW', 'BASE', 'NOBASE'
}