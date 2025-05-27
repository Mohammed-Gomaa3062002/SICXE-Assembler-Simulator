"""
Pass 1 of SIC/XE Assembler
Builds symbol table and calculates addresses
Enhanced to handle Format 3X conditional instructions
"""
import os
from .utils import parse_line, parse_operand, is_number, calculate_byte_length, format_hex
from .constants import OPCODES, DIRECTIVES

def parse_format3x_line(line):
    """
    Enhanced parser for Format 3X instructions
    Handles conditional instructions like: CADD A, BUFFER, Z
    """
    line = line.strip()
    if not line or line.startswith(';'):
        return None, None, None
    
    # Remove comments
    if ';' in line:
        line = line[:line.index(';')].strip()
    
    parts = line.split()
    if not parts:
        return None, None, None
    
    # Check if first part is a label (doesn't start with instruction)
    label = None
    opcode_start = 0
    
    # If line starts with whitespace, no label
    if not line[0].isspace():
        # First word might be a label
        first_word = parts[0]
        # Check if it's a known opcode/directive
        base_opcode = first_word[1:] if first_word.startswith('+') else first_word
        if base_opcode not in OPCODES and first_word not in DIRECTIVES:
            label = first_word
            opcode_start = 1
    
    if opcode_start >= len(parts):
        return label, None, None
    
    opcode = parts[opcode_start]
    
    # Handle operands - everything after opcode
    operand = None
    if opcode_start + 1 < len(parts):
        # Join remaining parts with spaces, then clean up
        operand_parts = parts[opcode_start + 1:]
        operand = ' '.join(operand_parts)
        # Remove extra spaces around commas
        operand = ','.join([part.strip() for part in operand.split(',')])
    
    return label, opcode, operand

def pass1(intermediate_lines):

    




    """Execute Pass 1 of the assembler with enhanced Format 3X support"""
    symbol_table = {}
    locctr = 0
    start_addr = 0
    program_name = None
    pass1_output = []
    base_addr = None
    
    for line_num, line in enumerate(intermediate_lines, 1):
        original_line = line
        
        # Try enhanced parsing first for Format 3X
        try:
            label, opcode, operand = parse_format3x_line(line)
        except:
            # Fall back to original parsing
            label, opcode, operand = parse_line(line)
        
        # Skip empty lines or lines that couldn't be parsed
        if not opcode:
            if line.strip():  # Only add non-empty lines to output
                pass1_output.append(f"{format_hex(locctr, 4)} {original_line}")
            continue
        
        # Handle START directive
        if opcode == 'START':
            if operand and is_number(operand):
                start_addr = int(operand)
                locctr = start_addr
            if label:
                program_name = label
            pass1_output.append(f"{format_hex(locctr, 4)} {original_line}")
            continue
        
        # Store current location counter
        current_locctr = locctr
        
        # Add label to symbol table
        if label:
            if label in symbol_table:
                raise ValueError(f"Duplicate label: {label} at line {line_num}")
            symbol_table[label] = current_locctr
        
        # Handle directives
        if opcode in DIRECTIVES:
            if opcode == 'END':
                pass1_output.append(f"{format_hex(current_locctr, 4)} {original_line}")
                break
            elif opcode == 'WORD':
                locctr += 3
            elif opcode == 'RESW':
                if operand and is_number(operand):
                    locctr += int(operand) * 3
                else:
                    raise ValueError(f"Invalid RESW operand: {operand} at line {line_num}")
            elif opcode == 'RESB':
                if operand and is_number(operand):
                    locctr += int(operand)
                else:
                    raise ValueError(f"Invalid RESB operand: {operand} at line {line_num}")
            elif opcode == 'BYTE':
                locctr += calculate_byte_length(operand)
            elif opcode == 'BASE':
                # BASE directive doesn't affect locctr
                pass
            elif opcode == 'NOBASE':
                # NOBASE directive doesn't affect locctr
                pass
        
        # Handle instructions (including Format 3X conditional instructions)
        elif opcode in OPCODES or (opcode and opcode.startswith('+')):
            base_opcode = opcode[1:] if opcode and opcode.startswith('+') else opcode
            
            # Handle conditional opcodes (Format 3X)
            if base_opcode.startswith('C') and len(base_opcode) > 1:
                # Check if it's a conditional version of a known opcode
                unconditional_opcode = base_opcode[1:]  # Remove 'C' prefix
                if unconditional_opcode in OPCODES:
                    # This is a Format 3X conditional instruction
                    locctr += 3  # Format 3X is 3 bytes
                elif base_opcode in OPCODES:
                    # It's a regular opcode that happens to start with 'C'
                    opcode_info = OPCODES[base_opcode]
                    format_num = opcode_info[1]
                    
                    if opcode and opcode.startswith('+'):
                        locctr += 4  # Format 4
                    elif format_num == 1:
                        locctr += 1
                    elif format_num == 2:
                        locctr += 2
                    else:
                        locctr += 3  # Format 3
                else:
                    raise ValueError(f"Invalid conditional opcode: {base_opcode} at line {line_num}")
            
            elif base_opcode not in OPCODES:
                raise ValueError(f"Invalid opcode: {base_opcode} at line {line_num}")
            
            else:
                # Regular instruction
                opcode_info = OPCODES[base_opcode]
                format_num = opcode_info[1]
                
                if opcode and opcode.startswith('+'):
                    # Format 4
                    locctr += 4
                elif format_num == 1:
                    locctr += 1
                elif format_num == 2:
                    locctr += 2
                else:
                    # Format 3
                    locctr += 3
        else:
            raise ValueError(f"Invalid opcode or directive: {opcode} at line {line_num}")
        
        pass1_output.append(f"{format_hex(current_locctr, 4)} {original_line}")
    
    program_length = locctr - start_addr
    
    return symbol_table, start_addr, program_length, program_name, pass1_output

def write_pass1_output(pass1_output, filename):
    """Write Pass 1 output to file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for line in pass1_output:
            f.write(line + '\n')

def write_symbol_table(symbol_table, filename):
    """Write symbol table to file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        f.write("Symbol Table:\n")
        f.write("Symbol\tAddress\n")
        f.write("-" * 20 + "\n")
        for symbol, address in sorted(symbol_table.items()):
            f.write(f"{symbol}\t{format_hex(address, 4)}\n")