labels = {}

pc = 0
registers={
"zero":"00000","ra":"00001","sp":"00010","gp":"00011",
"tp":"00100","t0":"00101","t1":"00110","t2":"00111",
"s0":"01000","s1":"01001",
"a0":"01010","a1":"01011","a2":"01100","a3":"01101",
"a4":"01110","a5":"01111","a6":"10000","a7":"10001",
"s2":"10010","s3":"10011","s4":"10100","s5":"10101",
"s6":"10110","s7":"10111","s8":"11000","s9":"11001",
"s10":"11010","s11":"11011","t3":"11100","t4":"11101",
"t5":"11110","t6":"11111"
}
#Format-(funct7, funct3, opcode)
R_type={
"add":("0000000","000","0110011"),
"sub":("0100000","000","0110011"),
"sll":("0000000","001","0110011"),
"slt":("0000000","010","0110011"),
"sltu":("0000000","011","0110011"),
"xor":("0000000","100","0110011"),
"srl":("0000000","101","0110011"),
"or":("0000000","110","0110011"),
"and":("0000000","111","0110011")
}
#Format-(funct3, opcode)
I_type={
"addi":("000","0010011"),
"sltiu":("011","0010011"),
"lw":("010","0000011"),
"jalr":("000","1100111")}
B_type={
"beq":("000","1100011"),
"bne":("001","1100011"),
"blt":("100","1100011"),
"bge":("101","1100011"),
"bltu":("110","1100011"),
"bgeu":("111","1100011")}
S_type={
"sw":("010","0100011")}
U_type={
"lui":"0110111",
"auipc":"0010111"}
J_type={
"jal":"1101111"}
instruction_type={"add":"R","sub":"R","sll":"R","slt":"R","sltu":"R","xor":"R","srl":"R","or":"R","and":"R",
"addi":"I","sltiu":"I","lw":"I","jalr":"I",
"sw":"S",
"beq":"B","bne":"B","blt":"B","bge":"B","bltu":"B","bgeu":"B",
"lui":"U","auipc":"U",
"jal":"J"}


import sys
instructions = []

def isHalt(line):
    global instructions, pc
    line = line.replace(",", " ")
    line_parts = line.split()

    if(len(line_parts) != 4): return False
    
    ins = line_parts[0]
    rs1 = line_parts[1]
    rs2 = line_parts[2]
    offset = line_parts[3]

    if(ins == 'beq' and rs1 == 'zero' and rs2 == 'zero'):
        if(offset == '0'): return True
        elif(offset in labels):
            if(labels[offset] - pc == 0): return True


    return False

def errorHandling(message):
    print(f"Error occured on line {pc//4 + 1}, {message}")
    sys.exit(1)

def n_bit_binary_converter(n, num):
    global pc
    if num not in range(-1*2**(n-1),2**(n-1)):
        errorHandling("Syntax Error: Immediate out of range")
    
    if num>=0:
        binary_with_extra=bin(num)
        binary_list=binary_with_extra.split("b")
        binary_string=binary_list[1]
    else:
        temp_num=2**n+num
        binary_with_extra=bin(temp_num)
        binary_list=binary_with_extra.split("b")
        binary_string=binary_list[1]
    
    if len(binary_string)<n:
        temp_string="0"*(n-len(binary_string))
        binary=temp_string+binary_string
    else:
        binary=binary_string
    
    return binary

def encode_R(line):
    global pc
    space_line=line.replace(","," ")
    line_parts=space_line.split()

    if(len(line_parts)!=4):
        errorHandling("Syntax Error: Invalid R type Instruction")

    ins=line_parts[0]
    rd=line_parts[1]
    rs1=line_parts[2]
    rs2=line_parts[3]

    if (rd not in registers) or (rs1 not in registers) or (rs2 not in registers):
        errorHandling("Syntax Error: Invalid register")

    funct7=R_type[ins][0]
    funct3=R_type[ins][1]
    opcode=R_type[ins][2]

    machinecode=funct7+registers[rs2]+registers[rs1]+funct3+registers[rd]+opcode

    return machinecode
    
def encode_I(line):
    global pc
    space_line=line.replace(","," ")
    line_parts=space_line.split()	 

    if(line_parts[0] in ("addi","sltiu","jalr")):
        if(len(line_parts)!=4):
            errorHandling("Syntax Error: Invalid I type Instruction")
        ins=line_parts[0]
        rd=line_parts[1]
        rs1=line_parts[2]
        if (rd not in registers) or (rs1 not in registers):
            errorHandling("Syntax Error: Invalid register")
        
        try:
            integer=int(line_parts[3])
        except:
            errorHandling("Syntax Error: Immediate not a valid integer")
        imm=n_bit_binary_converter(12,int(integer))
    else:
        if(len(line_parts)!=3):
            errorHandling("Syntax Error: Invalid R type Instruction")
        ins=line_parts[0]
        rd=line_parts[1]
        operand = line_parts[2]
        if "(" not in operand or ")" not in operand:
            errorHandling("Syntax error: Invalid memory operand")
        replaced_string=line_parts[2].replace(")","")
        extra_string_list=replaced_string.split("(")
        if len(extra_string_list)!=2:
            errorHandling("Syntax error: Invalid memory operand")
        try:
            integer=int(extra_string_list[0])
        except:
            errorHandling("Syntax Error: Immediate not a valid integer")
        imm=n_bit_binary_converter(12,int(extra_string_list[0]))
        rs1=extra_string_list[1]
        if (rs1 not in registers) or (rd not in registers):
            errorHandling("Syntax error: Invalid register")
    
    funct3=I_type[ins][0]
    opcode=I_type[ins][1]

    machinecode=imm+registers[rs1]+funct3+registers[rd]+opcode

    return machinecode

def encode_S(line):
    global pc
    space_line=line.replace(","," ")
    line_parts=space_line.split()

    if(len(line_parts)!=3):
        errorHandling("Syntax Error: Invalid S type Instruction")

    ins=line_parts[0]
    rs2=line_parts[1]
    if rs2 not in registers:
        errorHandling("Syntax error: Invalid register")
    if "(" not in line_parts[2] or ")" not in line_parts[2]:
        errorHandling("Syntax error: Invalid memory operand")
    replaced_string=line_parts[2].replace(")","")
    extra_string_list=replaced_string.split("(")
    if len(extra_string_list)!=2:
        errorHandling("Syntax error: Invalid memory operand")
    try:
        integer=int(extra_string_list[0])
    except:
        errorHandling("Syntax Error: Immediate not a valid integer")
    imm=n_bit_binary_converter(12,integer)
    imm_first=imm[0:7]
    imm_second=imm[7:12]
    rs1=extra_string_list[1]
    if rs1 not in registers:
        errorHandling("Syntax error: Invalid register")
    
    funct3=S_type[ins][0]
    opcode=S_type[ins][1]

    machinecode=imm_first+registers[rs2]+registers[rs1]+funct3+imm_second+opcode

    return machinecode
    
def encode_U(line):
    global pc
    space_line=line.replace(","," ")
    line_parts=space_line.split()

    if(len(line_parts)!=3):
        errorHandling("Syntax Error: Invalid U type Instruction")

    ins=line_parts[0]
    rd=line_parts[1]

    if rd not in registers:
        errorHandling("Syntax error: Invalid register")

    try:
        integer=int(line_parts[2])
    except:
        errorHandling("Syntax Error: Immediate not a valid integer")

    imm=n_bit_binary_converter(20,integer)

    opcode=U_type[ins]

    machinecode=imm+registers[rd]+opcode

    return machinecode

def encode_B(line):
    space_line = line.replace(","," ")
    line_parts = space_line.split()
    funct3, opcode = B_type[line_parts[0]]

    if len(line_parts) != 4:
        errorHandling("Syntax Error: Invalid number of operands.")
    if (line_parts[1] not in registers) or (line_parts[2] not in registers):
        errorHandling("Syntax Error: Invalid register destination.")

    try:
        offset = int(line_parts[3], 0)
    except ValueError:
        if line_parts[3] in labels:
            offset = labels[line_parts[3]] - pc
        else:
            errorHandling("Offset Error: Invalid branch offset!")
        
    if offset % 2 != 0:
        errorHandling("Offset Error: Offset should be a multiple of 2.")
    try:
        imm = n_bit_binary_converter(13, offset)
    except ValueError:
        errorHandling("Immediate out of range for B-type instruction")

    binaryCode = '' + imm[0] + imm[2:8] + registers[line_parts[2]] + registers[line_parts[1]] + funct3 + imm[8:12] + imm[1] + opcode

    return binaryCode

def encode_J(line):
    space_line = line.replace(","," ")
    line_parts = space_line.split()
    if len(line_parts) != 3:
        errorHandling("Syntax Error: Invalid number of operands.")
    if line_parts[1] not in registers:
        errorHandling("Syntax Error: Invalid register destination.")
    opcode = J_type[line_parts[0]]

    try:
        offset = int(line_parts[2], 0)
    except ValueError:
        if line_parts[2] in labels:
            offset = labels[line_parts[2]] - pc
        else:
            errorHandling("Offset Error: Invalid branch offset!")
        
    if offset % 2 != 0:
        errorHandling("Offset Error: Offset should be a multiple of 2.")
    try:
        imm = n_bit_binary_converter(21, offset)
    except ValueError:
        errorHandling("Immediate out of range for J-type instruction")

    binaryCode = '' + imm[0] + imm[10:20] + imm[9] + imm[1:9] + registers[line_parts[1]] + opcode

    return binaryCode

encoder={
"R":encode_R,
"I":encode_I,
"S":encode_S,
"B":encode_B,
"U":encode_U,
"J":encode_J
}

def first_pass(lines):
    global labels, pc, instructions
    for line in lines:
        if(line.strip() == ""): continue
        if(":" in line):
            label, extra = line.split(":", 1)
            if(label.strip() in labels):
                errorHandling(f"Duplicate label {label} found.")

            labels[label.strip()] = pc

            #to manage lines of type:
            # label:
            # stuff on the next line
            if(extra.strip() != ""):
                instructions.append(extra.strip())
                pc += 4

        else:
            instructions.append(line.strip())
            pc += 4
            
def solver():
    global instructions, pc, encoder
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    read_path = None
    if len(sys.argv) > 3:
        read_path = sys.argv[3]

    with open(in_path, "r") as assembly_code:
        lines = assembly_code.readlines()

    #lines is yet to be formatted

    readable = None
    if read_path:
        readable = open(read_path, "w")

    first_pass(lines)
    pc = 0

    flag = False
    with open(out_path, "w") as machine_code:
        for trav in instructions:
            if(isHalt(trav)):
                flag = True
                if(trav != instructions[-1]):
                    print(f"Invalid instruction occured at {pc//4 + 1}. Virtual Halt should be the last instruction")
            
            ins = trav.split()[0]

            if (ins not in instruction_type):
                errorHandling(f"The instruction {ins} does not exist")

            #Also check the instruction for Virtual Halt.

            ins_type = instruction_type[ins]
            # print(len(encoder[ins_type](trav)))
            machine_code.write(encoder[ins_type](trav) + '\n')
            pc += 4

        if (flag == False):
            print("Virtual Halt is missing")
            
    if(readable):
        readable.close()
        
solver()
