from collections import namedtuple
from utils import Mapper, ensure
from sympy import symbols, solve
from math import fabs
import sys


# constants
INF = 10**9
# sys.setrecursionlimit(INF)  # you know what...


# vars
Battery = namedtuple('Battery', 'id emf p n')
Resistor = namedtuple('Resistor', 'id resistance')
Junction = namedtuple('Junction', 'id')
mp = Mapper()
rmp = Mapper()  # Resistor maps
batteries = []
objs = {}
edges = []


# global-specific helpers
def is_junction(id):
    global objs
    return id in objs and type(objs[id]) == Junction


# take input
print('-- DEBUG -- Commands')
with open(sys.argv[1]) as f:
    for line in f.readlines():
        cmd_type, *args = line.split()

        obj_id = args[0]
        print(cmd_type, args)
        ensure(obj_id not in objs, f'Duplicate component id {args[0]}')
        mp.add(obj_id)

        if cmd_type == 'battery':
            obj_id, emf, p, n = args
            ensure(is_junction(p) and is_junction(n), f'Positive end {p} and negative end {n} must be junctions')
            objs[obj_id] = Battery(obj_id, float(emf), p, n)
            batteries.append(objs[obj_id])

            edges.append((mp.get(p), mp.get(obj_id)))
            edges.append((mp.get(n), mp.get(obj_id)))
        elif cmd_type == 'junction':
            objs[args[0]] = Junction(args[0])
        elif cmd_type == 'resistor':
            obj_id, resistance, a, b = args
            ensure(is_junction(a) and is_junction(b), f'Endpoints {a} end {b} must be junctions')
            objs[obj_id] = Resistor(obj_id, float(resistance))
            rmp.add(obj_id)

            edges.append((mp.get(a), mp.get(obj_id)))
            edges.append((mp.get(b), mp.get(obj_id)))
        else:
            ensure(False, f'Invalid command type {cmd_type}')


# Graph things
n = mp.n()
rc = sum(type(obj) == Resistor for obj in objs.values())
g = [[] for _ in range(n)]
vis = [False] * n
par = [-1] * n
dep = [0] * n  # so we can keep track of back edges |properly|

# Equation solver things
sym = symbols(' '.join((f'i{i}' for i in range(rc))))
sym_mp = {}
for i, obj in enumerate(filter(lambda obj: type(obj) == Resistor, objs.values())):
    sym_mp[obj.id] = (i, sym[i])
eqns = []
edge_orientation = set()

# Build graph and DFS
for a, b in edges:
    g[a].append(b)
    g[b].append(a)


def dfs(c, p):
    vis[c] = True
    for to in g[c]:
        if to != p:
            if not vis[to]:
                dep[to] = dep[c]+1
                par[to] = c
                dfs(to, c)
                edge_orientation.add((c, to))
            elif dep[to] < dep[c]:  # Back edge c->to
                edge_orientation.add((c, to))
                emf = 0
                eqn = 0

                cur = c
                while cur != to:
                    obj = objs[mp.rget(cur)]
                    if type(obj) == Resistor:  # Add resistor to equation
                        eqn += obj.resistance * sym_mp[obj.id][1]  # Ohm's law (V=IR)
                    elif type(obj) == Battery:
                        if par[c] == obj.p:  # Edges going in increasing order of depth, battery is oriented "backwards"
                            emf -= obj.emf
                        else:
                            emf += obj.emf

                    cur = par[cur]

                eqn -= emf
                eqns.append(eqn)


dfs(0, -1)


# Do some junctions things :)
for junction in filter(lambda obj: type(obj) == Junction, objs.values()):
    eqn = 0

    def find_resistors(c):
        global eqn

        jvis[c] = True
        for to in g[c]:
            tobj = objs[mp.rget(to)]

            if type(tobj) == Resistor:
                cur_sym = sym_mp[tobj.id][1]
                if (c, to) in edge_orientation:  # Resistor going out of junction
                    eqn += cur_sym
                else:  # Resistor coming into junction
                    assert (to, c) in edge_orientation
                    eqn -= cur_sym
            elif not jvis[to]:
                find_resistors(to)

    jvis = [False] * n
    find_resistors(mp.get(junction.id))

    if eqn:
        eqns.append(eqn)

currents = solve(eqns)

# Get Output
print(f'Raw Equations: {eqns}\nRaw Currents: {currents}')
if not currents:
    print('Equation information invalid/insufficient.  Terminating...')
    sys.exit(-1)

print('\nOutputs')
for resistor in filter(lambda obj: type(obj) == Resistor, objs.values()):
    R = resistor.resistance
    I = currents[sym_mp[resistor.id][1]]
    V = I*R

    print(f'Resistor - ID: {resistor.id}, Index: {rmp.get(resistor.id)} | Resistance: {R:.3f} Ohms, Current: {fabs(I):.3f} Amps, Potential Difference: {fabs(V):.3f} Volts')

for battery in filter(lambda obj: type(obj) == Battery, objs.values()):
    print(f'Battery - ID: {battery.id}, EMF: {battery.emf:.3f} Volts')
