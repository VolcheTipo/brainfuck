import os

page_size = 10
listing_size = 10
tape_size = 1000
pointer_offset = 0
cell_bits = 8
fast_mode = False

pages = set()
memory = [0] * tape_size
pointer = len(memory)//2
stack = []
init = []

program = "+++++++[->+++<]>[->++<]"
last = ""
instruction = 0


def set_poffset():
    global pointer_offset
    pointer_offset = int(input())
    reset()


def set_init():
    global init
    init = list(map(lambda x: int(x) % 2**cell_bits, input().split()))
    reset()


def reset():
    global memory, pointer, pages, stack, instruction, last
    last = "RESET"
    memory = [0] * tape_size
    pointer = len(memory)//2
    memory[pointer:pointer+len(init)] = init
    pages = {pointer // page_size}
    pointer += pointer_offset
    pages.add(pointer // page_size)
    stack = []
    instruction = 0


def load(file):
    global program
    with open(file) as f:
        program = f.read().replace("\r", "\n").replace("\n\n", "\n")
    reset()


def enter():
    global program
    program = ""
    try:
        while True:
            program += input() + "\n"
    except KeyboardInterrupt:
        program = program.replace("\r", "\n").replace("\n\n", "\n")
    reset()

def next_instruction():
    global instruction
    while instruction < len(program) and program[instruction] not in "+-><[].,":
        instruction += 1

def step():
    global  pointer, instruction, last
    reps = 0

    if instruction >= len(program):
        last = "HALT"
        return

    if program[instruction] == ".":
        instruction += 1
        next_instruction()
        last = f"TYPE SYMBOL `{chr(memory[pointer])}`"
        return
    if program[instruction] == ",":
        pointer += 1
        instruction += 1
        next_instruction()
        last = f"TYPE VALUE {chr(memory[pointer])}"
        return
    
    while instruction < len(program) and program[instruction] == "<":
        last = "MOVE LEFT"
        reps += 1
        pointer -= 1
        pages.add(pointer // page_size)
        instruction += 1
        next_instruction()
        if fast_mode:
            continue
        return
    else:
        if reps > 1:
            last += f" x{reps}"
        if reps:
            return

    while instruction < len(program) and program[instruction] == ">":
        last = "MOVE RIGHT"
        reps += 1
        pointer += 1
        pages.add(pointer // page_size)
        instruction += 1
        next_instruction()
        if fast_mode:
            continue
        return
    else:
        if reps > 1:
            last += f" x{reps}"
        if reps:
            return

    while instruction < len(program) and program[instruction] == "+":
        last = "INCREMENT"
        reps += 1
        memory[pointer] = (memory[pointer]+1) % 2**cell_bits
        instruction += 1
        next_instruction()
        if fast_mode:
            continue
        return
    else:
        if reps > 1:
            last += f" x{reps}"
        if reps:
            return

    while instruction < len(program) and program[instruction] == "-":
        last = "DECREMENT"
        reps += 1
        memory[pointer] = (memory[pointer]-1) % 2**cell_bits
        instruction += 1
        next_instruction()
        if fast_mode:
            continue
        return
    else:
        if reps > 1:
            last += f" x{reps}"
        if reps:
            return

    if program[instruction] == "[":
        if memory[pointer] > 0:
            stack.append(instruction)
            instruction += 1
            next_instruction()
            last = "ENTER LOOP"
            return
        braces = 1
        instruction += 1
        while braces > 0 and instruction < len(program):
            if program[instruction] == "[":
                braces += 1
            if program[instruction] == "]":
                braces -= 1
            instruction += 1
        next_instruction()
        last = "SKIP LOOP"
        return
    if program[instruction] == "]":
        instruction = stack.pop()
        last = "GOTO LOOP BEGIN"
        return

    instruction += 1
    last = "-"*10

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def print_data():
    for p in sorted(pages):
        i = p * page_size
        j = i + page_size
        if p == len(memory)//2//page_size:
            print(f"{">>>":>4}:", " ".join(map(lambda x: f"{x:3}", memory[i:j])))
        else:
            print(f"{p:4}:", " ".join(map(lambda x: f"{x:3}", memory[i:j])))
        if i <= pointer < j:
            print(" "*6, " "* 4 * (pointer-i), "^^^", sep="")

def print_listing():
    lines = program.split("\n")
    p = instruction
    i = 0
    while len(lines[i]) < p:
        p -= 1 + len(lines[i])
        i += 1
    if i > listing_size//2:
        print("~"*20)
    print("~ ", *lines[max(0, i-listing_size//2):i], sep="\n~ ")
    print(" " * (p+2) + "v")
    print(" ", lines[i])
    print(" " * (p+2) + "^")
    print("~ ", *lines[i+1:i+listing_size//2], sep="\n~ ")
    if i + listing_size//2 < len(lines):
        print("~"*20)

def switch_fast_mode():
    global fast_mode
    fast_mode = not fast_mode

def iteration():
    if not stack:
        step()
        return
    limit = len(stack)
    while last != "HALT" and limit <= len(stack):
        step()

    ip = instruction
    step()
    
def iterate(n=1):
    if n is None:
        n = 10**100
    if not stack:
        step()
        return
    limit = len(stack)
    for _ in range(n):
        while last != "HALT" and limit <= len(stack):
            step()

        ip = instruction
        step()
        if instruction-ip > 1:
            break

def full():
    while last != "HALT":
        step()

def main():
    # repl loop
    reset()

    while True:
        print("\n"*2)
        if fast_mode:
            print("*" * 40)
        else:
            print("=" * 40)
        print(" "*5, last)
        print()
        print_data()
        print_listing()

        cmd = input()
        if not cmd:
            step()
        elif cmd == "start":
            set_poffset()
        elif cmd.startswith("r"):
            reset()
        elif cmd.startswith("n"):
            set_init()
        elif cmd == "load":
            load(input())
        elif cmd == "enter":
            enter()
        elif cmd == "quit":
            return
        elif cmd == "f":
            switch_fast_mode()
        elif cmd == "ff":
            full()
        elif cmd == "i":
            iterate()
        elif cmd.startswith("i"):
            iterate(int(cmd[1:]))
        elif cmd == "s":
            iterate(None)

if __name__ == "__main__":
    main()









