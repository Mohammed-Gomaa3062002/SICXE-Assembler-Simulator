"""
Pass 2 of SIC/XE Assembler
Generates object code and output files
Enhanced to handle multi-operand instructions
"""
import os
from .utils import (parse_line, parse_operand, is_number, format_hex, 
                  byte_to_object_code, calculate_displacement)
from .constants import OPCODES, REGISTERS, DIRECTIVES

def pass2(intermediate_lines, symbol_table, start_addr, program_length, program_name):
    """Execute Pass 2 of the assembler"""
    locctr = start_addr
    pass2_output = []
    text_records = []
    modification_records = []
    current_text_record = []
    current_text_start = None
    current_text_length = 0
    base_addr = None
    
    for line_num, line in enumerate(intermediate_lines, 1):
        original_line = line
        
        try:
            label, opcode, operand = parse_line(line)
        except Exception as e:
            # Skip problematic lines but add them to output
            pass2_output.append(f"{format_hex(locctr, 4)} {original_line:<30} ERROR: {str(e)}")
            continue
        
        # Skip empty lines
        if not opcode:
            if line.strip():
                pass2_output.append(f"{format_hex(locctr, 4)} {original_line:<30}")
            continue
        
        # Handle START directive
        if opcode == 'START':
            pass2_output.append(f"{format_hex(locctr, 4)} {original_line:<30}")
            if operand and is_number(operand):
                locctr = int(operand)
            continue
        
        current_locctr = locctr
        object_code = ""
        
        # Handle directives
        if opcode in DIRECTIVES:
            if opcode == 'END':
                pass2_output.append(f"{format_hex(current_locctr, 4)} {original_line:<30}")
                break
            elif opcode == 'WORD':
                if operand and is_number(operand):
                    object_code = format_hex(int(operand), 6)
                    locctr += 3
                else:
                    raise ValueError(f"Invalid WORD operand: {operand}")
            elif opcode == 'RESW':
                if operand and is_number(operand):
                    locctr += int(operand) * 3
                else:
                    raise ValueError(f"Invalid RESW operand: {operand}")
                # Flush current text record for RESW
                if current_text_record:
                    text_records.append(create_text_record(current_text_start, current_text_record))
                    current_text_record = []
                    current_text_start = None
                    current_text_length = 0
            elif opcode == 'RESB':
                if operand and is_number(operand):
                    locctr += int(operand)
                else:
                    raise ValueError(f"Invalid RESB operand: {operand}")
                # Flush current text record for RESB
                if current_text_record:
                    text_records.append(create_text_record(current_text_start, current_text_record))
                    current_text_record = []
                    current_text_start = None
                    current_text_length = 0
            elif opcode == 'BYTE':
                object_code = byte_to_object_code(operand)
                locctr += len(object_code) // 2
            elif opcode == 'BASE':
                if operand in symbol_table:
                    base_addr = symbol_table[operand]
                elif is_number(operand):
                    base_addr = int(operand)
                else:
                    raise ValueError(f"Invalid BASE operand: {operand}")
        
        # Handle instructions
        elif opcode in OPCODES or opcode.startswith('+'):
            base_opcode = opcode[1:] if opcode.startswith('+') else opcode
            
            # Handle conditional opcodes (like CADD) - special processing
            if base_opcode.startswith('C') and len(base_opcode) > 1:
                unconditional_opcode = base_opcode[1:]  # Remove 'C' prefix
                if unconditional_opcode in OPCODES and base_opcode not in OPCODES:
                    # This is a conditional instruction - treat as the base instruction
                    print(f"Warning: Line {line_num}: Treating {base_opcode} as conditional {unconditional_opcode}")
                    base_opcode = unconditional_opcode
            
            if base_opcode not in OPCODES:
                print(f"Warning: Line {line_num}: Unknown opcode {base_opcode}, generating NOP")
                object_code = "000000"  # Generate a NOP-like instruction
                locctr += 3
            else:
                opcode_info = OPCODES[base_opcode]
                opcode_hex = opcode_info[0]
                format_num = opcode_info[1]
                
                try:
                    if opcode.startswith('+'):
                        # Format 4
                        object_code = generate_format4_code(opcode_hex, operand, symbol_table, 
                                                          current_locctr, modification_records)
                        locctr += 4
                    elif format_num == 1:
                        # Format 1
                        object_code = opcode_hex
                        locctr += 1
                    elif format_num == 2:
                        # Format 2
                        object_code = generate_format2_code(opcode_hex, operand)
                        locctr += 2
                    else:
                        # Format 3
                        object_code = generate_format3_code(opcode_hex, operand, symbol_table, 
                                                          current_locctr, base_addr, locctr)
                        locctr += 3
                except Exception as e:
                    print(f"Warning: Line {line_num}: Error generating object code for {opcode}: {e}")
                    # Generate a default object code to continue processing
                    if format_num == 1:
                        object_code = opcode_hex
                        locctr += 1
                    elif format_num == 2:
                        object_code = opcode_hex + "00"
                        locctr += 2
                    else:
                        object_code = opcode_hex + "0000"
                        locctr += 3
        
        # Add to text record if we have object code
        if object_code:
            object_code_bytes = len(object_code) // 2
            
            # Check if we need to start a new text record
            if (current_text_start is None or 
                current_text_length + object_code_bytes > 30 or
                current_locctr != current_text_start + current_text_length):
                
                # Flush current text record
                if current_text_record:
                    text_records.append(create_text_record(current_text_start, current_text_record))
                
                # Start new text record
                current_text_record = [object_code]
                current_text_start = current_locctr
                current_text_length = object_code_bytes
            else:
                # Add to current text record
                current_text_record.append(object_code)
                current_text_length += object_code_bytes
        
        pass2_output.append(f"{format_hex(current_locctr, 4)} {original_line:<30} {object_code}")
    
    # Flush final text record
    if current_text_record:
        text_records.append(create_text_record(current_text_start, current_text_record))
    
    return pass2_output, text_records, modification_records

def generate_format2_code(opcode_hex, operand):
    """Generate object code for Format 2 instructions"""
    if not operand:
        return opcode_hex + "00"
    
    # Handle multi-operand format 2 instructions
    if ',' in operand:
        # Parse registers
        regs = [reg.strip().upper() for reg in operand.split(',')]
        reg1 = regs[0] if len(regs) > 0 else None
        reg2 = regs[1] if len(regs) > 1 else None
        
        if reg1 and reg1 not in REGISTERS:
            raise ValueError(f"Invalid register: {reg1}")
        if reg2 and reg2 not in REGISTERS:
            raise ValueError(f"Invalid register: {reg2}")
        
        reg1_code = REGISTERS[reg1] if reg1 else 0
        reg2_code = REGISTERS[reg2] if reg2 else 0
        
        return opcode_hex + format(reg1_code, 'X') + format(reg2_code, 'X')
    else:
        # Single register
        reg = operand.strip().upper()
        if reg not in REGISTERS:
            raise ValueError(f"Invalid register: {reg}")
        
        reg_code = REGISTERS[reg]
        return opcode_hex + format(reg_code, 'X') + "0"

def generate_format3_code(opcode_hex, operand, symbol_table, current_addr, base_addr, next_addr):
    """Generate object code for Format 3 instructions"""
    if not operand:
        # Instructions like RSUB with no operand
        return opcode_hex + "0000"
    
    try:
        value, mode, indexed = parse_operand(operand)
    except Exception as e:
        print(f"Warning: Error parsing operand '{operand}': {e}")
        # For multi-operand instructions that can't be parsed normally,
        # try to extract the first valid symbol
        if ',' in operand:
            operands = [op.strip() for op in operand.split(',')]
            for op in operands:
                if op and op.upper() not in REGISTERS and not op.upper() in ['N', 'Z']:
                    value = op
                    mode = 'simple'
                    indexed = False
                    break
            else:
                # No valid symbol found, use default
                value = '0'
                mode = 'immediate'
                indexed = False
        else:
            raise e
    
    # Calculate flags
    n = 1  # indirect addressing flag
    i = 1  # immediate addressing flag
    x = 1 if indexed else 0
    b = 0  # base-relative flag
    p = 0  # PC-relative flag
    e = 0  # extended format flag
    
    # Adjust n and i based on addressing mode
    if mode == 'immediate':
        n = 0
        i = 1
    elif mode == 'indirect':
        n = 1
        i = 0
    
    # Calculate target address
    if is_number(value):
        target_addr = int(value)
        disp = target_addr
    elif value in symbol_table:
        target_addr = symbol_table[value]
        disp, addr_mode = calculate_displacement(target_addr, next_addr, base_addr)
        
        if addr_mode == 'pc':
            p = 1
        elif addr_mode == 'base':
            b = 1
        # For direct addressing, we'll use the address as is
    else:
        print(f"Warning: Undefined symbol '{value}', using 0")
        disp = 0
    
    # Ensure displacement fits in 12 bits
    if disp < 0:
        disp = disp & 0xFFF  # Two's complement
    elif disp > 4095:
        disp = disp & 0xFFF  # Truncate to 12 bits
    
    # Build the instruction
    opcode_int = int(opcode_hex, 16)
    flags = (n << 1) | i
    opcode_with_flags = opcode_int | flags
    
    xbpe = (x << 3) | (b << 2) | (p << 1) | e
    
    return format(opcode_with_flags, '02X') + format(xbpe, 'X') + format(disp, '03X')

def generate_format4_code(opcode_hex, operand, symbol_table, current_addr, modification_records):
    """Generate object code for Format 4 instructions"""
    if not operand:
        return opcode_hex + "000000"
    
    value, mode, indexed = parse_operand(operand)
    
    # Calculate flags
    n = 1  # indirect addressing flag
    i = 1  # immediate addressing flag
    x = 1 if indexed else 0
    b = 0  # base-relative flag (not used in format 4)
    p = 0  # PC-relative flag (not used in format 4)
    e = 1  # extended format flag
    
    # Adjust n and i based on addressing mode
    if mode == 'immediate':
        n = 0
        i = 1
    elif mode == 'indirect':
        n = 1
        i = 0
    
    # Calculate target address
    if is_number(value):
        target_addr = int(value)
    elif value in symbol_table:
        target_addr = symbol_table[value]
        # Add modification record for symbol references
        if mode == 'simple' or mode == 'indirect':
            mod_addr = current_addr + 1  # Address of the address field
            modification_records.append(f"M^{format_hex(mod_addr, 6)}^05")
    else:
        print(f"Warning: Undefined symbol '{value}', using 0")
        target_addr = 0
    
    # Build the instruction
    opcode_int = int(opcode_hex, 16)
    flags = (n << 1) | i
    opcode_with_flags = opcode_int | flags
    
    xbpe = (x << 3) | (b << 2) | (p << 1) | e
    
    return format(opcode_with_flags, '02X') + format(xbpe, 'X') + format(target_addr, '05X')

def create_text_record(start_addr, object_codes):
    """Create a text record from object codes"""
    combined_code = ''.join(object_codes)
    length = len(combined_code) // 2
    return f"T^{format_hex(start_addr, 6)}^{format_hex(length, 2)}^{combined_code}"

def write_pass2_output(pass2_output, filename):
    """Write Pass 2 output to file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        for line in pass2_output:
            f.write(line + '\n')

def write_htme_output(program_name, start_addr, program_length, text_records, 
                     modification_records, entry_point, filename):
    """Write HTME output to file"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as f:
        # Header record
        prog_name = (program_name or "PROG").ljust(6)[:6]
        f.write(f"H^{prog_name}^{format_hex(start_addr, 6)}^{format_hex(program_length, 6)}\n")
        
        # Text records
        for record in text_records:
            f.write(record + '\n')
        
        # Modification records
        for record in modification_records:
            f.write(record + '\n')
        
        # End record
        entry_addr = entry_point if entry_point is not None else start_addr
        f.write(f"E^{format_hex(entry_addr, 6)}\n")