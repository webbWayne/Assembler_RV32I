import sys

PC=0
registers=[0]*32
memory={}
instructions=[]
registers[2]=0x0000017C
out_file=None

def errorHANDLING(message):
    print(message)
    if out_file:
        out_file.close()
    sys.exit(1)

def signEXTEND(value,bits):
    if value>=(1<<(bits-1)):
        value-=(1<<bits)
    return value

def validMEMaddress(addr):
    if 0x00000100<=addr<=0x0000017F:
        return True
    if 0x00010000<=addr<=0x0001007F:
        return True
    return False

def execute_R(instr):
    global PC
    ans=0
    funct7=instr[0:7]
    funct3=instr[17:20]
    rs2=int(instr[7:12], 2)
    rd=int(instr[20:25], 2)
    rs1=int(instr[12:17], 2)
    value1=registers[rs1]
    value2=registers[rs2]
    if funct7=="0000000" and funct3=="000":
        ans=value1+value2
    elif funct7=="0000000" and funct3=="001":
        shift_amount=value2 & 31
        ans=value1<<shift_amount
    elif funct7=="0100000" and funct3=="000":
        ans=value1-value2
    
    elif funct7=="0000000" and funct3=="010":
        signed_v1=signEXTEND(value1,32)
        signed_v2=signEXTEND(value2,32)
        if signed_v1<signed_v2:
            ans=1
        else:
            ans=0
    elif funct7=="0000000" and funct3=="011":
        if value1<value2:
            ans=1
        else:
            ans=0
    elif funct7=="0000000" and funct3=="100":
        ans=value1^value2
    elif funct7=="0000000" and funct3=="101":
        shift_amount=value2 & 31
        unsigned_v1=value1%(2**32)
        ans=unsigned_v1>>shift_amount
    elif funct7=="0000000" and funct3=="110":
        ans=value1 | value2
    elif funct7=="0000000" and funct3=="111":
        ans=value1 & value2
    else:
        errorHANDLING(f"Error! unknown R Type funct7={funct7} funct3={funct3} at PC={PC}")
    registers[rd]=ans%(2**32)
    PC=PC+4

def execute_B(instr):
    global PC
    bit_12 = instr[0]
    bit_11 = instr[24]
    bits_10_5 = instr[1:7]
    bits_4_1 = instr[20:24]
    imm_bits = bit_12 + bit_11 + bits_10_5 + bits_4_1 + "0"
    imm1 = int(imm_bits, 2)
    offset = signEXTEND(imm1, 13)
    rs2 = int(instr[7:12], 2)
    rs1 = int(instr[12:17], 2)
    funct3 = instr[17:20]
    v1 = registers[rs1]
    v2 = registers[rs2]
    if rs1 == 0 and rs2 == 0 and offset == 0 and funct3 == "000":
        registers[0] = 0
        printCurrent()
        base_addrress = 0x00010000
        for i in range(32):
            addrress = base_addrress+(i * 4)
            val=memory.get(addrress, 0)
            out_file.write(f"0x{addrress:08X}:0b{format(val, '032b')}\n")
        out_file.close()
        sys.exit(0)
    take_branch = False
    if funct3 == "000":
        if v1 == v2:
            take_branch=True
    elif funct3 == "001":
        if v1 != v2:
            take_branch = True
    elif funct3 == "100":
        signed_v1 = signEXTEND(v1, 32)
        signed_v2 = signEXTEND(v2, 32)
        if signed_v1 < signed_v2:
            take_branch = True
    elif funct3 == "101":
        signed_v1 = signEXTEND(v1, 32)
        signed_v2 = signEXTEND(v2, 32)
        if signed_v1 >= signed_v2:
            take_branch = True
    elif funct3 == "110":
        if v1 < v2:
            take_branch = True
    elif funct3 == "111":
        if v1 >= v2:
            take_branch = True
    else:
        errorHANDLING(f"Error! unknown B-type funct3={funct3} at PC={PC}")
    if take_branch:
        PC = PC + offset
    else:
        PC = PC + 4

def execute_U_lui(instr):
    global PC
    upper_bits = instr[0:20]
    imm_val = int(upper_bits, 2)
    shifted = imm_val * 4096
    rd_bits = instr[20:25]
    rd=int(rd_bits, 2)
    registers[rd] = shifted%(2**32)
    PC = PC + 4

def execute_U_auipc(instr):
    global PC
    upper_bits = instr[0:20]
    imm_val = int(upper_bits, 2)
    shifted = imm_val * 4096
    rd_bits = instr[20:25]
    rd = int(rd_bits, 2)
    ans = PC+shifted
    ans = ans%(2**32)
    registers[rd] = ans
    PC = PC + 4

def execute_J(instr):
    global PC
    bit_20 = instr[0]
    bits_19_12 = instr[12:20]
    bit_11 = instr[11]
    bits_10_1 = instr[1:11]
    imm_bits = bit_20 + bits_19_12 + bit_11 + bits_10_1 + "0"
    imm1 = int(imm_bits, 2)
    offset = signEXTEND(imm1, 21)
    rd_bits = instr[20:25]
    rd = int(rd_bits, 2)
    return_addrress = PC + 4
    registers[rd] = return_addrress%(2**32)
    PC = PC + offset
def printCurrent():
    #format converts PC to binary type with leading zeroes and 32 size.
    line = "0b" + format(PC,'032b')
    for i in range(32):
        reg_val = registers[i]
        line = line + " " + "0b" + format(reg_val,'032b')
    out_file.write(line + "\n")

def load(path):
    global instructions
    f = open(path,"r")
    lineNum = 0
    for line in f:
        lineNum = lineNum + 1
        line = line.strip()
        if line == "":
            continue
        if len(line) != 32:
            f.close()
            errorHANDLING(f"Error! instruction on line {lineNum} is not 32 bits")
        flag = False
        for c in line:
            if c != '0' and c != '1':
                flag = False
        if flag:
            f.close()
            errorHANDLING(f"Error! invalid characters found on line {lineNum}")
        instructions.append(line)
    f.close()
    if len(instructions) == 0:
        errorHANDLING("Error! no instructions found in file")
#main loop of our code
def simulate():
    global PC,out_file
    if len(sys.argv) < 3:
        print("Usage: python3 Simulator.py <input.mc> <output.txt>")
        sys.exit(1)

    load(sys.argv[1])

    out_file = open(sys.argv[2], "w")
    cycle = 0
    prevPC = 0

    while True:
        prevPC = PC
        cycle += 1

        if cycle > 1000000:
            errorHANDLING("Error! exceeded a million cycles. Possible infinite loop.")

        if PC %4 != 0:
            errorHANDLING(f"Error! PC={PC} is not a multiple of 4.")

        if PC < 0:
            errorHANDLING(f"Error! PC is negative (PC={PC})")

        if PC // 4 >= len(instructions):
            errorHANDLING(f"Error! PC={PC} out of instruction bounds.")

        instruction = instructions[PC // 4]

        opcode = instruction[25:32]

        if opcode not in opcodeMAPPING:
            errorHANDLING(f"Error! unknown opcode={opcode} at PC={PC}")
        opcodeMAPPING[opcode](instruction)
        #virtual halt condition
        if prevPC == PC:
            sys.exit(0)
        registers[0] = 0
        printCurrent()

simulate()
