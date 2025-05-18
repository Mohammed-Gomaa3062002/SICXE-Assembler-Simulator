INSTRUCTION_SIZE = {
    'START': 0, 'END': 0, 'BYTE': -1, 'WORD': 3, 'RESB': -1, 'RESW': -1,
    'RSUB': 3, 'LDA': 3, 'STA': 3, 'LDX': 3, 'ADD': 3, 'SUB': 3,
    'MUL': 3, 'DIV': 3, 'COMP': 3, 'J': 3, 'JEQ': 3, 'JGT': 3, 
    'JLT': 3, 'JSUB': 3, 'TIX': 3,
}

OPCODES_HEX = {
    'LDA': '00', 'STA': '0C', 'LDX': '04', 'ADD': '18', 'SUB': '1C',
    'MUL': '20', 'DIV': '24', 'COMP': '28', 'J': '3C', 'JEQ': '30',
    'JGT': '34', 'JLT': '38', 'JSUB': '48', 'RSUB': '4C', 'TIX': '2C',
}
