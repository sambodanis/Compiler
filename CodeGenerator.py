import itertools
import IRTree
import Memory


class CodeGenerator:
    #todo give variables scopes to give start and endpoints of when
    #todo to reassign them. maybe do a variables to registers
    #todo run through after each variable's scope ends.

    _real_conditions = {'<', '>=', '!=', '=='}

    def __init__(self, ir):
        self._lines = ir
        self._conditions = {'<', '>', '<=', '>=', '!=', '=='}
        self._reserved_words = {'write', 'writeln', 'writes', 'read', 'Goto', 'ifZ', 'Alloc'} | self._conditions
        if ir:
            # Determine the top register and then iterate through all lines and allocate a specific register to
            # every variable

            # Filter the list of all strings in the IR to only contain temps
            # Sort those temps by their number and pick the largest.
            top_register = int(
                sorted([x for line in self._lines for x in line
                        if len(x) > 0 and x[0] == '_'], key=lambda t: int(t[2:]))[-1][2:])
            # Counter that increments by 1 with every call
            count = lambda c=itertools.count(top_register + 1): next(c)
            #
            self._variable_map = {line[0]: ['R' + str(count())]
                                  for line in self._lines if line[0][0] not in ['_', '~', '[']
            and line[0] not in self._reserved_words}

            self._max_register = count()
        self._string_map = {line[0]: 0 for line in self._lines if self._is_string(line)}

        #self._array_map = {}
        self._assembly = []
        self._assembly.append('MOVIR R0 0.0')
        self._assembly.append('DATA 10')
        self._assembly.append('DATA 0')
        self._last_condition = (None, None)
        self._last_array_c = -1
        self._arrays = {}
        self._PC = 2
        self._free_registers = set()
        #self.memory = Memory.Memory(ir)

    def generate_code(self):
        if not self._lines:
            self._assembly.append("HALT")
            return []
        for i, line in enumerate(self._lines):
            if line:
                comment = ' ; ' + ' '.join(line)
                t = self._code_for_line(self._temps_to_registers(line))
                assembly_for_line = ' '.join(t)
                self._assembly.append(assembly_for_line + comment)
                print line, assembly_for_line
            else:
                print 'why no line?'
        self._assembly.append("HALT")
        return self._assembly

    def print_assembly_to_file(self, n):
        with open('Assembly/testAss' + n + '.ass', 'w') as out_file:
            if self._assembly:
                out_file.write("\n".join(self._assembly))
            out_file.write('\n')

    def _store(self, line):
        #print line, self._variable_map
        data = line[3]
        element = 'R' + str(line[1][3:-1])
        offset = str(filter(lambda x: x[0] == line[0], self._variable_map.values())[0][1])

        code = ['STORE', data, element, offset]
        #print ' '.join(code)
        return code

    def _load(self, line):
        load_loc = line[0]
        element = 'R' + str(line[3][3:-1])
        offset = str(filter(lambda x: x[0] == line[2], self._variable_map.values())[0][1])
        code = ['LOAD', load_loc, element, offset]
        #print line, code
        return code

    def _alloc(self, line):
        if self._PC % 4 != 0:
            for i in range(4 - (self._PC % 4)):
                self._assembly.append(' '.join(['DATA', '0']))
                self._inc_pc()
                # Set counter for current var
        self._last_array_c = self._PC
        for i in range(int(line[3])):
            for j in range(4):
                self._assembly.append(' '.join(['DATA', '0']))
                self._inc_pc()
        return ''

    def _if(self, line):
        r, condition = self._last_condition
        #print self._last_condition, self._label_from_label([line[3]])[:-1]
        code = [condition, r, self._label_from_label([line[3]])[:-1]]
        return code

    def _condition(self, line):
        code = ['SUBR', line[0], line[2] if line[3] in self._real_conditions else line[4],
                line[4] if line[3] in self._real_conditions else line[2]]
        condition = condition_for_condition(line[3])
        #print line
        self._last_condition = (line[0], condition)
        return code

    def _write(self, line):
        #print line
        if len(line) == 3:
            element = 'R' + str(line[2][3:-1])
            load_loc = element
            offset = str(filter(lambda x: x[0] == line[1], self._variable_map.values())[0][1])
            self._assembly.append(' '.join(['LOAD', load_loc, element, offset]))
            #print ['LOAD', load_loc, element, offset]
            #code = ['WRR', line[1] if line[1][0] != '[' else 'R' + str(line[1][3:-1])]
            code = ['WRR', load_loc]
        else:
            code = ['WRR', line[1] if line[1][0] != '[' else 'R' + str(line[1][3:-1])]
        return code

    def _assign(self, line):
        if line[0][0] == 'R' and line[2][0] == 'R':
            code = ['ADDR', line[0], 'R0', line[2]]
            if self._last_array_c:
                filter(lambda x: x[0] == line[0], self._variable_map.values())[0].append(self._last_array_c)
                self._last_array_c = None
        else:
            code = ['MOVIR', line[0], line[2]]
        return code

    def _string(self, line):
        curr_pc = self._PC
        for letter in line[2][1:-1]:
            self._assembly.append(' '.join(['DATA', str(ord(letter)), ';', str(self._PC)]))
            self._inc_pc()
        self._assembly.append(' '.join(['DATA', '0']))
        self._inc_pc()
        self._string_map[line[0]] = str(curr_pc)
        #code = ' '.join(['MOVIR', line[0], str(float(curr_pc))])
        return ''

    def _get_arr(self, v_name, elem_t):
        load_loc = self._register()
        element = 'R' + str(elem_t[3:-1])
        offset = str(self._variable_map[v_name][1])
        #print load_loc, element, offset
        self._assembly.append(' '.join(['LOAD', load_loc, element, offset]))
        return load_loc

    def _code_for_line(self, line):
        code = ''
        if True in [x[0] == '[' for x in line]:  # If array access
            new_l = []
            right_side = False
            for i, x in enumerate(line):
                if x == '=':
                    right_side = True
                    new_l.append('=')
                elif x[0] == '[' and right_side:
                    new_r = self._get_arr(line[i-1], x)
                    new_l = new_l[:-1]
                    new_l.append(new_r)
                else:
                    new_l.append(x)
            line = new_l

        for i, v in enumerate(line):  # Swap any variables with their temporary register value
            if v in self._variable_map:
                line[i] = self._variable_map[v][0]
            #print line
        if 'read' in line:
            code = ['RDR', line[1]]
        elif len(line) == 4 and line[1][0] == '[':
            return self._store(line)
        elif len(line) == 4 and line[3][0] == '[':
            return self._load(line)
        elif len(line) == 4 and line[2] == 'Alloc':
            return self._alloc(line)
        elif self._is_label(line):
            code = [self._label_from_label(line)]
        elif line[0] == 'ifZ':
            return self._if(line)
        elif len(set(line) & self._conditions) > 0:
            return self._condition(line)
        elif line[0] == 'Goto':
            code = ['JMP', self._label_from_label([line[1]])[:-1]]
        elif '+' in line:
            code = ['ADDR', line[0], line[2], line[4]]
        elif '-' in line:
            code = ['SUBR', line[0], line[2], line[4]]
        elif '*' in line:
            code = ['MULR', line[0], line[2], line[4]]
        elif '/' in line:
            code = ['DIVR', line[0], line[2], line[4]]
        elif 'write' in line:
            return self._write(line)
        elif len(line) == 3 and line[1] == '=' and not self._is_string(line):
            return self._assign(line)
        elif line[0] == 'writeln':
            code = ['WRS', '0']
        elif line[0] == 'writes':
            code = ['WRS', self._string_map[line[1]]]
        elif self._is_string(line):
            return self._string(line)
        return code


    @staticmethod
    def _is_variable(v):
        return v[0] != 'R'

    @staticmethod
    def _is_label(v):
        return v[0][0] == '~'

    @staticmethod
    def _label_from_label(v):
        #print v
        for k in v:
            if k[0] == '~':
                return k[1:] + ':'
                #    pass
                #return v[0][1:] + ':'

    @staticmethod
    def _is_string(v):
        return True in [x[0] == '\'' for x in v]

    @staticmethod # May not be static if want to incorporate register pool
    def _temps_to_registers(line):
        for i, l in enumerate(line):
            if l[0] == '_':
                line[i] = 'R' + l[2:]
        return line

    def _inc_pc(self):
        self._PC += 1

    def _register(self):
        if len(self._free_registers) == 0:
            r = self._max_register
            self._max_register += 1
            return 'R' + str(r)
        else:
            return self._free_registers.pop()
        #return None

        #def _variables_to_registers(self):
        #    for i in range(2):
        #        for i, line in enumerate(self._assembly):
        #            new_line = line.split()
        #            for j, var in enumerate(new_line):
        #                if var in self._variable_map:
        #                    #print 'b', new_line
        #                    new_line[j] = self._variable_map[var]
        #                    #print 'a', new_line
        #            self._assembly[i] = ' '.join(new_line)


def condition_for_condition(c):
    #'<', '>', '<=', '>=', '!=', '=='
    if c == '<':
        return 'BLTZR'
    elif c == '>':
        return 'BLTZR'  # not real
    elif c == '<=':
        return 'BGEZR'  # not real
    elif c == '>=':
        return 'BGEZR'
    elif c == '!=':
        return 'BNEZR'
    elif c == '==':
        return 'BEQZR'
