from matplotlib import pyplot as plt
rtt_trad = []
time_trad = []
rtt_OPEN = []
time_OPEN = []
with open('/Users/kushshah/Library/Mobile Documents/com~apple~CloudDocs/Assignments for School/CS/4516/CS4516-Team17/Data/host1_host3_rtt.txt', 'r') as f:
    lines = f.readlines()
    rtt = []
    time = []
    for line in lines:
        rtt_trad.append(float(line.split(":")[0]))
        time_trad.append(float(line.split(":")[1]))
with open('/Users/kushshah/Library/Mobile Documents/com~apple~CloudDocs/Assignments for School/CS/4516/CS4516-Team17/Data/host1_host3_rtt_OPENFLOW.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        rtt_OPEN.append(float(line.split(":")[0]))
        time_OPEN.append(float(line.split(":")[1]))


    plt.plot(time_trad, rtt_trad,color='r',label='Traditional')
    plt.plot(time_OPEN, rtt_OPEN,color='b',label='OpenFlow')
    plt.legend()
    plt.grid()
    plt.axis([0, 6.5, 0, 6]) # [xstart, xend, ystart, yend]    
    plt.xlabel('Time (s)')
    plt.ylabel('RTT (ms)')
    plt.title('RTT vs Time')
    plt.show()