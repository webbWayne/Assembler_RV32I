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
