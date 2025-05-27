"""
Main module for SIC/XE Assembler
Orchestrates the assembly process
"""
import os
import sys
import argparse
from SICXE.utils import create_intermediate_file
from SICXE.pass1 import pass1, write_pass1_output, write_symbol_table
from SICXE.pass2 import pass2, write_pass2_output, write_htme_output

def main():
    """Main function to run the assembler"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='SIC/XE Assembler')
    parser.add_argument('--data', required=True, help='Input assembly file path')
    parser.add_argument('--output', default='output', help='Output directory (default: output)')
    
    args = parser.parse_args()
    input_file = args.data
    output_dir = args.output
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        return False
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create intermediate file
        print("Creating intermediate file...")
        intermediate_file = os.path.join(output_dir, "Output/intermediate.txt")
        intermediate_lines = create_intermediate_file(input_file, intermediate_file)
        
        # Pass 1
        print("Running Pass 1...")
        symbol_table, start_addr, program_length, program_name, pass1_output = pass1(intermediate_lines)
        
        # Write Pass 1 outputs
        write_pass1_output(pass1_output, os.path.join(output_dir, "out_pass1.txt"))
        write_symbol_table(symbol_table, os.path.join(output_dir, "symbTable.txt"))
        
        # Pass 2
        print("Running Pass 2...")
        pass2_output, text_records, modification_records = pass2(
            intermediate_lines, symbol_table, start_addr, program_length, program_name)
        
        # Write Pass 2 outputs
        write_pass2_output(pass2_output, os.path.join(output_dir, "out_pass2.txt"))
        
        # Determine entry point
        entry_point = symbol_table.get(program_name) if program_name else start_addr
        
        # Write HTME output
        write_htme_output(program_name, start_addr, program_length, text_records, 
                         modification_records, entry_point, os.path.join(output_dir, "HTME.txt"))
        
        print("\n" + "="*50)
        print("Assembly completed successfully!")
        print("="*50)
        print(f"Program Name: {program_name or 'N/A'}")
        print(f"Start Address: {format(start_addr, '06X')}")
        print(f"Program Length: {format(program_length, '06X')} ({program_length} bytes)")
        print(f"Symbols Defined: {len(symbol_table)}")
        print(f"Text Records: {len(text_records)}")
        print(f"Modification Records: {len(modification_records)}")
        print(f"\nOutput files generated in '{output_dir}':")
        print("  - intermediate.txt")
        print("  - symbTable.txt")
        print("  - out_pass1.txt")
        print("  - out_pass2.txt")
        print("  - HTME.txt")
        
    except Exception as e:
        print(f"Assembly failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)