from time import time, gmtime, strftime
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import sys

#dev = qml.device("default.qubit", wires=8)
# 8 qubits, 1 ancil qubit
# I thought we might need 7 ancil qubits but that breaks my compy so one of you guys try it
dev = qml.device('default.mixed', wires=8)
#dev = qml.device('default.qubit', wires=9)

# all in 0 state
starting_state = np.append(np.array([1]), np.zeros(2**8 - 1))
starting_state = np.sqrt(starting_state)

def elapsedTime(elapsed):
    h = int(elapsed / 3600)
    elapsed -= h * 3600
    m = int(elapsed / 60)
    elapsed -= m * 60
    s = int(elapsed)
    return "{}h {}m {}s".format(h, m, s)

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
    qml.MottonenStatePreparation(starting_state, wires=range(8))
    qml.Hadamard(0)
    #qml.CNOT(wires=[0, 8])
    #qml.PauliX(wires=8)
    #qml.RX(rot, wires=8)

    for i in range(0, 7):
        qml.CNOT(wires=[i, i+1])

    qml.RX(rot, wires=7)

    # TODO: the kraus fn applies the Kraus operators needed for the damping channel
    # but I'm missing something to actually apply it as an operation
    # temporarily just using built-in damping channel
    qml.AmplitudeDamping(damping, wires=0)
    qml.AmplitudeDamping(damping, wires=1)
    qml.AmplitudeDamping(damping, wires=2)
    qml.AmplitudeDamping(damping, wires=3)
    qml.AmplitudeDamping(damping, wires=4)
    qml.AmplitudeDamping(damping, wires=5)
    qml.AmplitudeDamping(damping, wires=6)
    qml.AmplitudeDamping(damping, wires=7)

    for i in range(7, 0, -1):
        qml.CNOT(wires=[i, i-1])

    return qml.counts(all_outcomes=False)

qnode = qml.QNode(damped_with_rotation_GHZ, dev)

# Note: change shots and 10 to maybe 500, and 100 to get a better graph
# but even with just 50 shots and 10 points it takes 7 minutes
# 10 shots and 20 points takes 14min
# 200 and 200 takes 5h+
# on my (Kevin's) machine, update here with your times
# change update_interval if the printouts are too noisy
points = 50
update_interval = 10
start = time()
print("The current time is " + strftime("%m/%d %H:%M:%S", gmtime()))
damping_list = [[0, 'r-'], [0.05, 'g-'], [0.15, 'b-']]
total = len(damping_list) * points
progress = 0
for damp, col in damping_list:
    rot = 0
    xvals = []
    yvals = []
    for rot_amount in range(points):
        progress += 1
        rot = (rot_amount/points) * 4 * np.pi # scale rotation
        x = qnode(rot, damp)
        if "00000000" in x.keys():
            yvals.append(x["00000000"])
        else:
            yvals.append(0) 
        #for key in x.keys():
        #    if key[:7] == "0000000":
        #        zeropop += x[key]
        xvals.append(rot)
        if rot_amount % update_interval == 0 and progress > 1:
            elapsed = time() - start
            print("For damping amount " + str(damp) + ": " + '%.2g'%(100 * progress/total) + "% estimate time remaining: " +     elapsedTime(elapsed*total/progress - elapsed))
    plt.plot(xvals, yvals, col)
    plt.xlabel("Rotation")
    plt.ylabel("Zero population")
    plt.title("Damped GHZ simulation")
print("Done! Time elapsed is " + elapsedTime((time() - start)))
print("The current time is " + strftime("%m/%d %H:%M:%S", gmtime()))
plt.show()
