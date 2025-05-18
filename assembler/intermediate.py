def generate_intermediate_file(input_file='input/in.txt', output_file='output/intermediate.txt'):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line.startswith('.') or not line:
                continue
            parts = line.split()
            if parts[0].isdigit():
                parts = parts[1:]
            outfile.write(' '.join(parts) + '\n')
