from time import time
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import sys

#dev = qml.device("default.qubit", wires=8)
# 8 qubits, 1 ancil qubit
# I thought we might need 7 ancil qubits but that breaks my compy so one of you guys try it
dev = qml.device('default.mixed', wires=9)
#dev = qml.device('default.qubit', wires=9)

# all in 0 state
starting_state = np.append(np.array([1]), np.zeros(2**9 - 1))
starting_state = np.sqrt(starting_state)

def printElapsed(elapsed):
    h = int(elapsed / 3600)
    elapsed -= h * 3600
    m = int(elapsed / 60)
    elapsed -= m * 60
    s = int(elapsed)
    print("Done! Took {}h {}m {}s".format(h, m, s))

def kraus(damping, wires):
    # prototype using Kraus operators from the wiki on Amplitude_damping_channel
    # we'll want to replace these with those defined in our paper
    K0 = np.matrix([[1, 0], [0, np.sqrt(1 - damping)]])
    K1 = np.matrix([[0, np.sqrt(damping)], [0, 0]])
    mat = K0 * damping * K0.getH() + K1 * damping * K1.getH()
    print(mat)
    print(mat * np.matrix([[1, 0], [0, 1]]))
    # note: getH is how you get the Hermitian transpose (complex conjugate) in numpy
    qml.QubitChannel(mat, wires=wires)
    # TODO: not trace preserving, throws error
    #qml.QubitChannel([K0, K1], wires=wires)

#@qml.set_shots(1_000)
@qml.set_shots(1_000)
@qml.qnode(dev)
def damped_with_rotation_GHZ(rot, damping):
    qml.MottonenStatePreparation(starting_state, wires=range(9))
    qml.Hadamard(0)

    # TODO: the kraus fn applies the Kraus operators needed for the damping channel
    # but I'm missing something to actually apply it as an operation
    # temprarily just using built-in damping channel
    qml.AmplitudeDamping(damping, wires=0)
    qml.AmplitudeDamping(damping, wires=1)
    qml.AmplitudeDamping(damping, wires=2)
    qml.AmplitudeDamping(damping, wires=3)
    qml.AmplitudeDamping(damping, wires=4)
    qml.AmplitudeDamping(damping, wires=5)
    qml.AmplitudeDamping(damping, wires=6)
    qml.AmplitudeDamping(damping, wires=7)

    #qml.CNOT(wires=[0, 8])
    #qml.PauliX(wires=8)
    #qml.RX(rot, wires=8)
 
    for i in range(0, 8):
        qml.CNOT(wires=[i, i+1])
    qml.RZ(rot, wires=8)
    for i in range(8, 0, -1):
        qml.CNOT(wires=[i-1, i])
    return qml.counts(all_outcomes=False)

qnode = qml.QNode(damped_with_rotation_GHZ, dev)

# Note: change shots and 10 to maybe 500, and 100 to get a better graph
# but even with just 50 and 10 it takes 7 minutes
# change update_interval if the printouts are too noisy
points = 1000
update_interval = 10
start = time()
for damp, col in [[0.2, 'r-'], [0.4, 'g-'], [0.6, 'b-']]:
    rot = 0
    xvals = []
    yvals = []
    for rot_amount in range(points):
        if rot_amount % update_interval == 0:
            print("For damping amount " + str(damp) + ": " + '%.2g'%(100 * rot_amount/points) + "%")
        rot = (rot_amount/points) * np.pi
        x = qnode(rot, damp)
        zeropop = 0
        for key in x.keys():
            if key[:7] == "0000000":
                zeropop += x[key]
        xvals.append(rot)
        yvals.append(x[key])
    plt.plot(xvals, yvals, col)
printElapsed(time() - start)
plt.show()
