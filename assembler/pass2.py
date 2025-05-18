from .constants import OPCODES_HEX

def generate_object_code(opcode, operand, symbol_table):
    if opcode == 'BYTE':
        if operand.startswith("C'"):
            return ''.join(format(ord(c), '02X') for c in operand[2:-1])
        elif operand.startswith("X'"):
            return operand[2:-1]
    elif opcode == 'WORD':
        return format(int(operand), '06X')
    elif opcode == 'RSUB':
        return OPCODES_HEX[opcode] + '0000'
    elif opcode in OPCODES_HEX:
        address = symbol_table.get(operand, '0000')
        return OPCODES_HEX[opcode] + address
    return '------'

def pass2(symbol_table, location_list, intermediate_lines):
    with open('output/out_pass2.txt', 'w') as out2, open('output/HTME.txt', 'w') as htme:
        htme.write('H^COPY^001000^00103A\n')
        text_records = []
        current_record = ''
        current_address = ''

        for loc, line in zip(location_list, intermediate_lines):
            parts = line.strip().split()
            if len(parts) == 3:
                label, opcode, operand = parts
            elif len(parts) == 2:
                opcode, operand = parts
            else:
                opcode = parts[0]
                operand = ''

            obj_code = generate_object_code(opcode.upper(), operand, symbol_table)
            out2.write(f"{loc}  {line}  ==>  {obj_code}\n")

            if obj_code != '------':
                if not current_record:
                    current_address = loc
                current_record += obj_code

        htme.write(f"T^{current_address}^{format(len(current_record)//2, '02X')}^{current_record}\n")
        htme.write('E^001000\n')
