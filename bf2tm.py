TM_STATES  = "ABCDEFGHIJKLMNOPQRSTUVWXY"
HALT_STATE = "Z"
BF_SYMBOLS = "*<>[]"

def translate(p, debug = False):
    if any(c not in BF_SYMBOLS for c in p):
        print(f"Error: program must only use characters {BF_SYMBOLS}")
        exit()
    # Phase 1: translate BF program to L/S/R TM
    state_map = ""
    state_idx = 0
    brackets = []
    for i,c in enumerate(p):
        if c == BF_SYMBOLS[3]:
            brackets.append(i)
            state_map += TM_STATES[state_idx]
            state_idx += 1
        elif c == BF_SYMBOLS[4]:
            state_map += state_map[brackets.pop()]
        else:
            state_map += TM_STATES[state_idx]
            state_idx += 1
    if debug:
        print("State map:")
        print(p)
        print(state_map)
    tm = {}
    for i,c in enumerate(p):
        state = state_map[i]
        next_state = state_map[i+1] if i<len(p)-1 else HALT_STATE
        if c == BF_SYMBOLS[0]:
            tm[state + '0'] = '1S' + next_state
            tm[state + '1'] = '0S' + next_state
        elif c == BF_SYMBOLS[1]:
            tm[state + '0'] = '0L' + next_state
            tm[state + '1'] = '1L' + next_state
        elif c == BF_SYMBOLS[2]:
            tm[state + '0'] = '0R' + next_state
            tm[state + '1'] = '1R' + next_state
        elif c == BF_SYMBOLS[3]:
            tm[state + '1'] = '1S' + next_state
        else:
            tm[state + '0'] = '0S' + next_state
    if debug:
        print("L/S/R Turing machine:")
        print(tm)
    # Phase 2: translate L/S/R TM to L/R TM
    new_tm = {}
    trap_state = TM_STATES[len(tm) // 2]
    for k,v in tm.items():
        if v[1] != 'S':
            new_tm[k] = v
        else:
            seen_states = set()
            # Statically analyze to find the next time the machine will move.
            # If we get caught in a loop, go to the special "trap state" at the end of the machine.
            while v[1] == 'S' and v[2] != HALT_STATE and v[2] + v[0] not in seen_states:
                seen_states.add(v[2] + v[0])
                v = tm[v[2] + v[0]]
            if v[1] != 'S':
                new_tm[k] = v
            elif v[2] == HALT_STATE:
                new_tm[k] = v[0] + 'R' + v[2]
            else:
                new_tm[k] = v[0] + 'R' + trap_state
                new_tm[trap_state + '0'] = '0R' + trap_state
                new_tm[trap_state + '1'] = '1R' + trap_state
    if debug:
        print("L/R Turing machine:")
        print(new_tm)
    # Phase 3: prune unreachable states
    stack = []
    stack.append(TM_STATES[0])
    used_states = set()
    while stack:
        state = stack.pop()
        used_states.add(state)
        for symbol in '01':
            next_state = new_tm[state + symbol][2]
            if next_state != HALT_STATE and next_state not in used_states:
                stack.append(next_state)
    transitions = [new_tm[s + sym] for s in sorted(used_states) for sym in '01']
    subs = {s: TM_STATES[i] for i,s in enumerate(sorted(used_states))}
    subs.update({HALT_STATE: HALT_STATE})
    transitions = [t[:2] + subs[t[2]] for t in transitions]
    return '_'.join(transitions[2 * i] + transitions[2 * i + 1] for i in range(len(transitions) // 2))

# print(translate("*>*>*[>[*<<]*>*[<<]*>*>]", True))
n = 12
in_file = open(f'BlF({n}).txt', 'r')
out_file = open(f'blftms{n}.txt', 'w')

for line in in_file.readlines():
    tm = translate(line.rstrip())
    out_file.write(tm + '\n')
in_file.close()
out_file.close()