# SIC/XE Assembler

A complete implementation of a SIC/XE (Simplified Instructional Computer - Extended) assembler written in Python.

## Features

- **Two-Pass Assembly**: Implements the standard two-pass assembly algorithm
- **Complete Instruction Support**: Handles all SIC/XE instruction formats (1, 2, 3, and 4)
- **Addressing Modes**: Supports immediate (#), indirect (@), simple, and indexed (,X) addressing
- **Object Code Generation**: Produces standard SIC/XE object program format (H, T, M, E records)
- **Error Handling**: Comprehensive error detection and reporting
- **Modular Design**: Well-structured code with separate modules for different functionalities

## Project Structure

```
sicxe_assembler/
│
├── assembler/                # Main package directory
│   ├── __init__.py          # Package initialization
│   ├── constants.py         # Opcodes, registers, and constants
│   ├── utils.py             # Utility functions
│   ├── pass1.py             # Pass 1 implementation
│   └── pass2.py             # Pass 2 implementation
│
├── main.py                  # Entry point script
├── output/                  # Generated output files
├── in.txt                   # Input assembly file
└── README.md               # This file
```

## Usage

1. Place your SIC/XE assembly code in `in.txt`
2. Run the assembler:
   ```bash
   python main.py --data in.txt
   ```
3. Check the `output/` directory for generated files:
   - `intermediate.txt`: Preprocessed assembly code
   - `symbTable.txt`: Symbol table with addresses
   - `out_pass1.txt`: Pass 1 annotated listing
   - `out_pass2.txt`: Pass 2 annotated listing with object code
   - `HTME.txt`: Final object program

## Supported Instructions

### Format 1 (1 byte)
- FIX, FLOAT, HIO, NORM, SIO, TIO

### Format 2 (2 bytes)
- ADDR, CLEAR, COMPR, DIVR, MULR, RMO, SHIFTL, SHIFTR, SUBR, SVC, TIXR

### Format 3/4 (3/4 bytes)
- ADD, AND, COMP, DIV, J, JEQ, JGT, JLT, JSUB, LDA, L