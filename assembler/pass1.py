from .utils import get_instruction_size

symbol_table = {}
location_list = []
intermediate_lines = []

def pass1(intermediate_path='output/intermediate.txt'):
    with open(intermediate_path, 'r') as file:
        lines = file.readlines()

    locctr = 0
    start_address = 0
    symbol_table.clear()
    location_list.clear()
    intermediate_lines.clear()

    first_line = lines[0].strip().split()
    if len(first_line) == 3 and first_line[1].upper() == 'START':
        start_address = int(first_line[2], 16)
        locctr = start_address
        location_list.append(hex(locctr)[2:].zfill(4))
        intermediate_lines.append(lines[0].strip())
        lines = lines[1:]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 3:
            label, opcode, operand = parts
            if label in symbol_table:
                print(f"Error: Duplicate symbol {label}")
            else:
                symbol_table[label] = hex(locctr)[2:].zfill(4)
        elif len(parts) == 2:
            opcode, operand = parts
        else:
            opcode = parts[0]
            operand = ""

        location_list.append(hex(locctr)[2:].zfill(4))
        intermediate_lines.append(line)
        locctr += get_instruction_size(opcode.upper(), operand)

    with open('output/out_pass1.txt', 'w') as out1:
        for loc, line in zip(location_list, intermediate_lines):
            out1.write(f"{loc}  {line}\n")

    with open('output/symbTable.txt', 'w') as symb_file:
        for label, address in symbol_table.items():
            symb_file.write(f"{label}  {address}\n")

    return symbol_table, location_list, intermediate_lines
