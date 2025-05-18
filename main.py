import argparse
from assembler.intermediate import generate_intermediate_file
from assembler.pass1 import pass1
from assembler.pass2 import pass2

def main():
    parser = argparse.ArgumentParser(description="SIC/XE Assembler (Pass 1 & 2)")
    parser.add_argument('--data', type=str, default='input/in.txt', help='Input assembly file')
    args = parser.parse_args()

    print("Generating intermediate.txt...")
    generate_intermediate_file(input_file=args.data)

    print("Running Pass 1...")
    symbol_table, location_list, intermediate_lines = pass1()

    print("Running Pass 2...")
    pass2(symbol_table, location_list, intermediate_lines)

    print("Files generated in /output: intermediate.txt, out_pass1.txt, symbTable.txt, out_pass2.txt, HTME.txt")

if __name__ == '__main__':
    main()
