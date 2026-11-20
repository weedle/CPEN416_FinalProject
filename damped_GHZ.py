from time import time, localtime, strftime
import pennylane as qml
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
import sys

SHOTS = 1000
ANGLES = 5

# I'm curious as to how much the amount of damping impacts the time of each run
# the ETA assumes each run takes the same amount of time, so seeing how far it's off by
# is a neat way of seeing how much increased damping affects the runtime
# but it prints out a lot, so only enable if you're interested in the stats
print_eta_accuracy = False

dev = qml.device('default.mixed', wires=8)
qml.decomposition.enable_graph()
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
    K0 = np.array([[1, 0], [0, np.sqrt(1 - damping)]])
    K1 = np.array([[0, np.sqrt(damping)], [0, 0]])
    mat = K0 * damping * K0.transpose() + K1 * damping * K1.transpose()
    # note: getH is how you get the Hermitian transpose (complex conjugate) in numpy
    # nvm, don't use np.matrix and getH(), np.array and transpose() work
    #qml.QubitChannel(mat, wires=wires)
    ch = qml.QubitChannel([K0, K1], wires=wires)
    return ch
    #print(ch.compute_decomposition(qml.PauliX, qml.PauliY, qml.PauliZ, qml.Hadamard, wires=wires))

@qml.transforms.decompose(gate_set=["CNOT", "RX", "RY", "RZ", "GlobalPhase"])
@qml.set_shots(SHOTS)
@qml.qnode(dev)
def damped_with_rotation_GHZ(rot, damping):
    qml.MottonenStatePreparation(starting_state, wires=range(8))
    for i in range(8):
        kraus(damping, i)
        #qml.AmplitudeDamping(damping, wires=0)

    qml.Hadamard(0)

    for i in range(0, 7):
        qml.CNOT(wires=[i, i+1])

    qml.RX(rot, wires=7)

    for i in range(7, 0, -1):
        qml.CNOT(wires=[i, i-1])

    return qml.counts(all_outcomes=False)

qnode = qml.QNode(damped_with_rotation_GHZ, dev)

# COMMENT OUT THESE TWO LINES IF YOU WANT TO GENERATE THE GRAPH
print(qml.draw(damped_with_rotation_GHZ)(0.2*np.pi, 0))
exit(0)

# change update_interval if the printouts are too noisy
points = ANGLES
update_interval = 2

start = time()
print("The current time is " + strftime("%m/%d %H:%M:%S", localtime()))
damping_list = [[0, 'r-'], [0.05, 'g-'], [0.15, 'b-']]
total = len(damping_list) * points
progress = 0
results = {}
log_index = 0
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
            eta = elapsed*total/progress - elapsed
            string_print = "For damping amount " + str(damp) + ": " + '%.2g'%(100 * progress/total) + "% estimated time remaining: " +     elapsedTime(eta)
            print(string_print)
            results[log_index] = [string_print, elapsed, eta]
            log_index += 1
    plt.plot(xvals, yvals, col)
    plt.xlabel("Rotation")
    plt.ylabel("Zero population")
    plt.title(f'Damped GHZ simulation ({SHOTS} shots, {ANGLES} angles)')
total_time = time() - start
print("Done! Time elapsed is " + elapsedTime(total_time))
print("The current time is " + strftime("%m/%d %H:%M:%S", localtime()))

if print_eta_accuracy:
    for i in range(0, log_index-1):
        print("expected eta ", results[i][2], " actual was ", total_time - results[i][1],  " accuracy was ", '%.2g'%(results[i][2]/(total_time - results[i][1])))

plt.show()
plt.savefig("damped_GHZ_" + strftime("%m-%d_%H:%M:%S") + f"_{SHOTS}S_{ANGLES}A" + ".png")
