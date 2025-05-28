"""
Pass 1 of SIC/XE Assembler
Builds symbol table and calculates addresses
Fixed to handle proper line parsing
"""
import os
from .utils import parse_line, parse_operand, is_number, calculate_byte_length, format_hex
from .constants import OPCODES, DIRECTIVES

def enhanced_parse_line(line):
    """
    Enhanced line parser that correctly handles SIC/XE assembly format
    """
    line = line.strip()
    if not line or line.startswith(';'):
        return None, None, None
    
    # Remove comments
    if ';' in line:
        line = line[:line.index(';')].strip()
    
    if not line:
        return None, None, None
    
    # Split by whitespace
    parts = line.split()
    if not parts:
        return None, None, None
    
    label = None
    opcode = None
    operand = None
    
    # Determine if the line starts with a label
    # A line starts with a label if it doesn't start with whitespace
    # and the first word is not a known opcode or directive
    original_line = line
    starts_with_whitespace = original_line and original_line[0].isspace()
    
    if not starts_with_whitespace and len(parts) >= 2:
        # Check if first part could be a label
        first_word = parts[0].upper()
        second_word = parts[1].upper()
        
        # If second word is a known opcode/directive, first word is a label
        is_second_opcode = (second_word in OPCODES or 
                           second_word in DIRECTIVES or 
                           (second_word.startswith('+') and second_word[1:] in OPCODES))
        
        if is_second_opcode:
            label = parts[0]
            opcode = parts[1].upper()
            operand = ' '.join(parts[2:]) if len(parts) > 2 else None
        else:
            # First word might be an opcode
            is_first_opcode = (first_word in OPCODES or 
                              first_word in DIRECTIVES or 
                              (first_word.startswith('+') and first_word[1:] in OPCODES))
            
            if is_first_opcode:
                opcode = first_word
                operand = ' '.join(parts[1:]) if len(parts) > 1 else None
            else:
                # Treat first word as label if we can't determine opcode
                label = parts[0]
                if len(parts) > 1:
                    opcode = parts[1].upper()
                    operand = ' '.join(parts[2:]) if len(parts) > 2 else None
    
    elif len(parts) >= 1:
        # Line starts with whitespace or has only one part
        first_word = parts[0].upper()
        is_first_opcode = (first_word in OPCODES or 
                          first_word in DIRECTIVES or 
                          (first_word.startswith('+') and first_word[1:] in OPCODES))
        
        if is_first_opcode:
            opcode = first_word
            operand = ' '.join(parts[1:]) if len(parts) > 1 else None
        else:
            # Could be a label on its own line
            label = parts[0]
    
    return label, opcode, operand

def pass1(intermediate_lines):
    """Execute Pass 1 of the assembler"""
    symbol_table = {}
    locctr = 0
    start_addr = 0
    program_name = None
    pass1_output = []
    base_addr = None
    
    for line_num, line in enumerate(intermediate_lines, 1):
        original_line = line
        
        # Use enhanced parsing
        try:
            label, opcode, operand = enhanced_parse_line(line)
        except Exception as e:
            # Fall back to original parsing if enhanced fails
            try:
                label, opcode, operand = parse_line(line)
            except:
                # Skip problematic lines but add them to output
                if line.strip():
                    pass1_output.append(f"{format_hex(locctr, 4)} {original_line}")
                continue
        
        # Skip empty lines or lines that couldn't be parsed
        if not opcode:
            if line.strip():  # Only add non-empty lines to output
                pass1_output.append(f"{format_hex(locctr, 4)} {original_line}")
            continue
        
        # Handle START directive
        if opcode == 'START':
            if operand:
                if is_number(operand):
                    start_addr = int(operand)
                    locctr = start_addr
                else:
                    # Try to parse as hex
                    try:
                        start_addr = int(operand, 16)
                        locctr = start_addr
                    except ValueError:
                        raise ValueError(f"Line {line_num}: Invalid START operand: {operand}")
            
            if label:
                program_name = label
            
            pass1_output.append(f"{format_hex(locctr, 4)} {original_line}")
            continue
        
        # Store current location counter
        current_locctr = locctr
        
        # Add label to symbol table
        if label:
            if label in symbol_table:
                raise ValueError(f"Line {line_num}: Duplicate label: {label}")
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
                    raise ValueError(f"Line {line_num}: Invalid RESW operand: {operand}")
            elif opcode == 'RESB':
                if operand and is_number(operand):
                    locctr += int(operand)
                else:
                    raise ValueError(f"Line {line_num}: Invalid RESB operand: {operand}")
            elif opcode == 'BYTE':
                try:
                    locctr += calculate_byte_length(operand)
                except Exception as e:
                    raise ValueError(f"Line {line_num}: Invalid BYTE operand: {operand}")
            elif opcode == 'BASE':
                # BASE directive doesn't affect locctr
                pass
            elif opcode == 'NOBASE':
                # NOBASE directive doesn't affect locctr
                pass
        
        # Handle instructions
        elif opcode in OPCODES or (opcode and opcode.startswith('+')):
            base_opcode = opcode[1:] if opcode and opcode.startswith('+') else opcode
            
            # Handle conditional opcodes (like CADD)
            if base_opcode.startswith('C') and len(base_opcode) > 1:
                # Check if it's a conditional version of a known opcode
                unconditional_opcode = base_opcode[1:]  # Remove 'C' prefix
                if unconditional_opcode in OPCODES:
                    # This is a conditional instruction - treat as Format 3
                    locctr += 3
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
                    raise ValueError(f"Line {line_num}: Invalid conditional opcode: {base_opcode}")
            
            elif base_opcode not in OPCODES:
                raise ValueError(f"Line {line_num}: Invalid opcode: {base_opcode}")
            
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
            # Handle unknown opcodes more gracefully
            print(f"Warning: Line {line_num}: Unknown opcode or directive: {opcode}")
            # Skip this line but add it to output
            pass1_output.append(f"{format_hex(current_locctr, 4)} {original_line}")
            continue
        
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