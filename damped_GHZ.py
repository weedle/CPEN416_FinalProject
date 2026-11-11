import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import sys

#dev = qml.device("default.qubit", wires=8)
# 8 qubits, 1 ancil qubit
# I thought we might need 7 ancil qubits but that breaks my compy so one of you guys try it
#dev = qml.device('default.mixed', wires=9)
dev = qml.device('default.qubit', wires=9)

# all in 0 state
starting_state = np.append(np.array([1]), np.zeros(2**9 - 1))
starting_state = np.sqrt(starting_state)
@qml.set_shots(1_000)
@qml.qnode(dev)
def damped_with_rotation_GHZ(rot):
    qml.MottonenStatePreparation(starting_state, wires=range(9))
    qml.Hadamard(0)
    # if np.pi is a full rotation, 5% is 1/20th of a rotation
    qml.CNOT(wires=[0, 8])
    #qml.PauliX(wires=8)
    qml.RX(rot, wires=8)
    for i in range(1, 8):
        qml.CNOT(wires=[8, i])
    qml.CNOT(wires=[0, 8])
    return qml.counts(all_outcomes=False)

qnode = qml.QNode(damped_with_rotation_GHZ, dev)
rot = 0
xvals = []
yvals = []
points = 10000
for rot_amount in range(points):
    if rot_amount % 100 == 0:
        print('%.2g'%(100 * rot_amount/points) + "%")
    rot = (rot_amount/points) * 2*np.pi
    x = qnode(rot)
    zeropop = 0
    for key in x.keys():
        if key[:7] == "0000000":
            zeropop += x[key]
    xvals.append(rot)
    yvals.append(x[key])
plt.plot(xvals, yvals)
plt.show()
