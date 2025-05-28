"""
Utility functions for SIC/XE Assembler
Enhanced to handle multi-operand instructions
"""
import re
import os
from .constants import OPCODES, REGISTERS, DIRECTIVES

def create_intermediate_file(input_file, output_file):
    """Remove comments and line numbers from input file"""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    intermediate_lines = []
    for line in lines:
        # Remove line numbers at the beginning
        line = re.sub(r'^\d+\s+', '', line.strip())
        
        # Remove comments (everything after ;)
        line = re.sub(r';.*$', '', line).strip()
        
        if line:  # Only add non-empty lines
            intermediate_lines.append(line)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        for line in intermediate_lines:
            f.write(line + '\n')
    
    return intermediate_lines

def parse_line(line):
    """Parse assembly line into components"""
    line = line.strip()
    if not line:
        return None, None, None
    
    # Split by whitespace, but preserve strings in quotes
    parts = []
    current_part = ""
    in_quotes = False
    quote_char = None
    
    i = 0
    while i < len(line):
        char = line[i]
        if char in ("'", '"') and not in_quotes:
            in_quotes = True
            quote_char = char
            current_part += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current_part += char
        elif char.isspace() and not in_quotes:
            if current_part:
                parts.append(current_part)
                current_part = ""
        else:
            current_part += char
        i += 1
    
    if current_part:
        parts.append(current_part)
    
    if not parts:
        return None, None, None
    
    # Check if first part is a label (not an opcode or directive)
    label = None
    opcode = None
    operand = None
    
    first_part_upper = parts[0].upper()
    
    # Check if it's an opcode (including format 4 with +)
    is_opcode = (first_part_upper in OPCODES or 
                first_part_upper in DIRECTIVES or 
                (first_part_upper.startswith('+') and first_part_upper[1:] in OPCODES))
    
    if is_opcode:
        # No label
        opcode = first_part_upper
        operand = ' '.join(parts[1:]) if len(parts) > 1 else None
    else:
        # Has label
        label = parts[0]
        if len(parts) > 1:
            opcode = parts[1].upper()
            operand = ' '.join(parts[2:]) if len(parts) > 2 else None
    
    return label, opcode, operand

def parse_operand(operand):
    """Parse operand to determine addressing mode and value - Enhanced for multi-operand instructions"""
    if not operand:
        return None, 'simple', False
    
    # Remove spaces for initial processing
    operand_clean = operand.replace(' ', '')
    
    # Handle multi-operand instructions (like CADD X,LENGTH,N)
    if ',' in operand_clean:
        operands = [op.strip() for op in operand.split(',')]
        
        # For multi-operand instructions, we'll use the first operand as primary
        # and handle the rest as special cases
        primary_operand = operands[0]
        
        # Check for indexed addressing on primary operand
        indexed = False
        if len(operands) > 1 and operands[-1].upper() == 'X':
            indexed = True
            # Remove the X from operands list
            operands = operands[:-1]
            if len(operands) == 1:
                primary_operand = operands[0]
        
        # For instructions like CADD X,LENGTH,N, treat as a special multi-operand format
        # We'll return the first meaningful symbol/value
        for op in operands:
            op = op.strip()
            if op and not op.upper() in REGISTERS:
                # This is likely a symbol or value, use it as the target
                return parse_single_operand(op, indexed)
        
        # If all operands are registers or empty, use the first one
        return parse_single_operand(primary_operand, indexed)
    
    else:
        return parse_single_operand(operand, False)

def parse_single_operand(operand, indexed=False):
    """Parse a single operand for addressing mode and value"""
    if not operand:
        return None, 'simple', indexed
    
    # Remove spaces
    operand = operand.replace(' ', '')
    
    # Check for indexed addressing (,X) if not already set
    if not indexed and operand.upper().endswith(',X'):
        indexed = True
        operand = operand[:-2]
    
    # Check addressing mode
    mode = 'simple'
    value = operand
    
    if operand.startswith('#'):
        mode = 'immediate'
        value = operand[1:]
    elif operand.startswith('@'):
        mode = 'indirect'
        value = operand[1:]
    
    return value, mode, indexed

def is_number(s):
    """Check if string represents a number"""
    if not s:
        return False
    try:
        int(s)
        return True
    except ValueError:
        # Try hexadecimal
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

def calculate_displacement(target_addr, pc_addr, base_addr=None):
    """Calculate displacement for PC-relative or base-relative addressing"""
    # Try PC-relative first
    pc_disp = target_addr - pc_addr
    if -2048 <= pc_disp <= 2047:
        return pc_disp, 'pc'
    
    # Try base-relative if base is set
    if base_addr is not None:
        base_disp = target_addr - base_addr
        if 0 <= base_disp <= 4095:
            return base_disp, 'base'
    
    # If neither works, return direct addressing (will need modification record)
    return target_addr, 'direct'

def format_hex(value, length):
    """Format value as hex string with specified length"""
    if value < 0:
        # Handle negative numbers with two's complement
        value = (1 << (length * 4)) + value
    return format(value, f'0{length}X')

def byte_to_object_code(operand):
    """Convert BYTE directive operand to object code"""
    if operand.startswith("C'") and operand.endswith("'"):
        # Character constant
        text = operand[2:-1]
        return ''.join(format(ord(c), '02X') for c in text)
    elif operand.startswith("X'") and operand.endswith("'"):
        # Hexadecimal constant
        hex_str = operand[2:-1]
        # Pad with 0 if odd length
        if len(hex_str) % 2 == 1:
            hex_str += '0'
        return hex_str.upper()
    else:
        raise ValueError(f"Invalid BYTE operand: {operand}")

def calculate_byte_length(operand):
    """Calculate length of BYTE directive in bytes"""
    if operand.startswith("C'") and operand.endswith("'"):
        return len(operand[2:-1])
    elif operand.startswith("X'") and operand.endswith("'"):
        hex_str = operand[2:-1]
        return (len(hex_str) + 1) // 2  # Round up for odd length
    else:
        raise ValueError(f"Invalid BYTE operand: {operand}")