import pennylane as qml
import numpy as np

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
def damped_with_rotation_GHZ():
    qml.MottonenStatePreparation(starting_state, wires=range(9))
    qml.Hadamard(0)
    # if np.pi is a full rotation, 5% is 1/20th of a rotation
    qml.CNOT(wires=[0, 8])
    qml.PauliX(8, np.pi/20)
    for i in range(1, 7):
        qml.CNOT(wires=[8, i])
    return qml.probs()

qnode = qml.QNode(damped_with_rotation_GHZ, dev)
print(qnode())
