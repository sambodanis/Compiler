import IRTree


class CodeGenerator:

    def __init__(self, ir):
        self._lines = ir
        self._assembly = []
        self._assembly.append('MOVIR R0 0.0')
        self._assembly.append('DATA 10')
        self._assembly.append('DATA 0')

        #self._assembly.append('MOVI R1 10.0')
        #self._assembly.append('STORE R1 R0 0')



    def generate_code(self):
        #for l in self._lines:
        #    print l
        # Append to not delete default registers
        self._assembly += [self._code_for_line(self._temps_to_registers(line.split())) for line in self._lines if line]
        self._assembly.append("HALT")
        return self._assembly

    def print_assembly_to_file(self, n):
        with open('Assembly/testAss' + n + '.ass', 'w') as out_file:
            out_file.write("\n".join(self._assembly))
            out_file.write('\n')

    def _code_for_line(self, line):
        #print line
        code = ''
        if '+' in line:
            code = ' '.join(['ADDR', line[0], line[2], line[4]])
        elif '-' in line:
            code = ' '.join(['SUBR', line[0], line[2], line[4]])
        elif '*' in line:
            code = ' '.join(['MULR', line[0], line[2], line[4]])
        elif '/' in line:
            code = ' '.join(['DIVR', line[0], line[2], line[4]])
        elif 'write' in line:
            code = ' '.join(['WRR', line[1]])
        elif len(line) == 3 and line[1] == '=':
            code = ' '.join(['MOVIR', line[0], line[2]])
        elif line[0] == 'writeln':
            code = ' '.join(['WRS', '0'])
        return code

    @staticmethod # May not be static if want to incorporate register pool
    def _temps_to_registers(line):
        for i, l in enumerate(line):
            if l[0] == '_':
                line[i] = 'R' + l[2:]
        return line