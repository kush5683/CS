from matplotlib import pyplot as plt
input = """seq 0: tcp response from 10.61.17.215 [open]  4.992 ms
seq 1: tcp response from 10.61.17.170 [open]  13.978 ms
seq 2: tcp response from 10.61.17.199 [open]  12.886 ms
seq 3: tcp response from 10.61.17.234 [open]  11.387 ms
seq 4: tcp response from 10.61.17.150 [open]  5.736 ms
seq 5: tcp response from 10.61.17.233 [open]  14.078 ms
seq 6: tcp response from 10.61.17.162 [open]  5.415 ms
seq 7: tcp response from 10.61.17.209 [open]  12.397 ms
seq 8: tcp response from 10.61.17.178 [open]  3.037 ms
seq 9: tcp response from 10.61.17.219 [open]  12.618 ms
seq 10: tcp response from 10.61.17.234 [open]  7.046 ms
seq 11: tcp response from 10.61.17.191 [open]  12.879 ms
seq 12: tcp response from 10.61.17.245 [open]  10.600 ms
seq 13: tcp response from 10.61.17.155 [open]  11.957 ms
seq 14: tcp response from 10.61.17.197 [open]  12.356 ms
seq 15: tcp response from 10.61.17.196 [open]  5.047 ms
seq 16: tcp response from 10.61.17.156 [open]  10.122 ms
seq 17: tcp response from 10.61.17.200 [open]  11.420 ms
seq 18: tcp response from 10.61.17.204 [open]  12.033 ms
seq 19: tcp response from 10.61.17.204 [open]  8.730 ms
seq 20: tcp response from 10.61.17.145 [open]  5.553 ms
seq 21: tcp response from 10.61.17.216 [open]  5.118 ms
seq 22: tcp response from 10.61.17.165 [open]  2.647 ms
seq 23: tcp response from 10.61.17.229 [open]  4.789 ms
seq 24: tcp response from 10.61.17.208 [open]  13.745 ms
seq 25: tcp response from 10.61.17.152 [open]  14.532 ms
seq 26: tcp response from 10.61.17.197 [open]  3.694 ms
seq 27: tcp response from 10.61.17.210 [open]  13.294 ms
seq 28: tcp response from 10.61.17.221 [open]  13.515 ms
seq 29: tcp response from 10.61.17.253 [open]  5.376 ms
seq 30: tcp response from 10.61.17.143 [open]  13.599 ms
seq 31: tcp response from 10.61.17.130 [open]  4.019 ms
seq 32: tcp response from 10.61.17.146 [open]  10.701 ms
seq 33: tcp response from 10.61.17.203 [open]  12.726 ms
seq 34: tcp response from 10.61.17.219 [open]  17.850 ms
seq 35: tcp response from 10.61.17.204 [open]  1.104 ms
seq 36: tcp response from 10.61.17.149 [open]  5.054 ms
seq 37: tcp response from 10.61.17.178 [open]  4.072 ms
seq 38: tcp response from 10.61.17.149 [open]  9.388 ms
seq 39: tcp response from 10.61.17.201 [open]  10.745 ms
seq 40: tcp response from 10.61.17.222 [open]  13.114 ms
seq 41: tcp response from 10.61.17.140 [open]  13.086 ms
seq 42: tcp response from 10.61.17.190 [open]  3.405 ms
seq 43: tcp response from 10.61.17.215 [open]  5.537 ms
seq 44: tcp response from 10.61.17.169 [open]  5.774 ms
seq 45: tcp response from 10.61.17.142 [open]  4.811 ms
seq 46: tcp response from 10.61.17.199 [open]  3.407 ms
seq 47: tcp response from 10.61.17.199 [open]  19.129 ms
seq 48: tcp response from 10.61.17.205 [open]  12.500 ms
seq 49: tcp response from 10.61.17.196 [open]  2.777 ms
seq 50: tcp response from 10.61.17.246 [open]  3.594 ms
seq 51: tcp response from 10.61.17.250 [open]  11.124 ms
seq 52: tcp response from 10.61.17.237 [open]  11.393 ms
seq 53: tcp response from 10.61.17.242 [open]  14.592 ms
seq 54: tcp response from 10.61.17.197 [open]  3.463 ms
seq 55: tcp response from 10.61.17.157 [open]  8.764 ms
seq 56: tcp response from 10.61.17.177 [open]  10.829 ms
seq 57: tcp response from 10.61.17.128 [open]  5.084 ms
seq 58: tcp response from 10.61.17.151 [open]  4.771 ms
seq 59: tcp response from 10.61.17.202 [open]  12.628 ms
seq 60: tcp response from 10.61.17.175 [open]  2.599 ms
seq 61: tcp response from 10.61.17.164 [open]  5.678 ms
seq 62: tcp response from 10.61.17.217 [open]  10.436 ms
seq 63: tcp response from 10.61.17.128 [open]  11.959 ms
seq 64: tcp response from 10.61.17.184 [open]  11.932 ms
seq 65: tcp response from 10.61.17.239 [open]  4.477 ms
seq 66: tcp response from 10.61.17.165 [open]  3.657 ms
seq 67: tcp response from 10.61.17.217 [open]  18.997 ms
seq 68: tcp response from 10.61.17.247 [open]  12.929 ms
seq 69: tcp response from 10.61.17.166 [open]  10.836 ms
seq 70: tcp response from 10.61.17.249 [open]  12.764 ms
seq 71: tcp response from 10.61.17.154 [open]  4.938 ms
seq 72: tcp response from 10.61.17.235 [open]  4.674 ms
seq 73: tcp response from 10.61.17.213 [open]  14.122 ms
seq 74: tcp response from 10.61.17.146 [open]  4.052 ms
seq 75: tcp response from 10.61.17.168 [open]  11.977 ms
seq 76: tcp response from 10.61.17.234 [open]  1.024 ms
seq 77: tcp response from 10.61.17.151 [open]  4.125 ms
seq 78: tcp response from 10.61.17.130 [open]  5.678 ms
seq 79: tcp response from 10.61.17.154 [open]  14.927 ms
seq 80: tcp response from 10.61.17.175 [open]  4.947 ms
seq 81: tcp response from 10.61.17.180 [open]  11.470 ms
seq 82: tcp response from 10.61.17.174 [open]  7.025 ms
seq 83: tcp response from 10.61.17.167 [open]  23.406 ms
seq 84: tcp response from 10.61.17.156 [open]  4.935 ms
seq 85: tcp response from 10.61.17.159 [open]  4.674 ms
seq 86: tcp response from 10.61.17.158 [open]  14.149 ms
seq 87: tcp response from 10.61.17.164 [open]  3.536 ms
seq 88: tcp response from 10.61.17.201 [open]  5.385 ms
seq 89: tcp response from 10.61.17.128 [open]  1.456 ms
seq 90: tcp response from 10.61.17.178 [open]  5.560 ms
seq 91: tcp response from 10.61.17.134 [open]  15.654 ms
seq 92: tcp response from 10.61.17.162 [open]  4.544 ms
seq 93: tcp response from 10.61.17.137 [open]  1.200 ms
seq 94: tcp response from 10.61.17.233 [open]  5.620 ms
seq 95: tcp response from 10.61.17.214 [open]  3.477 ms
seq 96: tcp response from 10.61.17.175 [open]  5.117 ms
seq 97: tcp response from 10.61.17.241 [open]  4.809 ms
seq 98: tcp response from 10.61.17.148 [open]  5.737 ms
seq 99: tcp response from 10.61.17.200 [open]  3.928 ms
seq 100: tcp response from 10.61.17.219 [open]  5.281 ms
seq 101: tcp response from 10.61.17.192 [open]  13.691 ms
seq 102: tcp response from 10.61.17.194 [open]  11.147 ms
seq 103: tcp response from 10.61.17.240 [open]  5.274 ms
seq 104: tcp response from 10.61.17.158 [open]  3.710 ms
seq 105: tcp response from 10.61.17.146 [open]  3.048 ms
seq 106: tcp response from 10.61.17.150 [open]  5.079 ms
seq 107: tcp response from 10.61.17.241 [open]  6.159 ms
seq 108: tcp response from 10.61.17.186 [open]  5.287 ms
seq 109: tcp response from 10.61.17.169 [open]  3.628 ms"""

list = input.split("\n")

data = []

for item in list:
    data.append(float(item[-8:-3]))

trial = []

trialNum = 0
for point in data:
    trialNum += 1
    trial.append(trialNum)
"""
rtt_trad = []
time_trad = []
rtt_OPEN = []
time_OPEN = []
with open('/Users/keithdesantis/PycharmProjects/CS4516-Team17/Data/host1_host3_rtt.txt', 'r') as f:
    lines = f.readlines()
    rtt = []
    time = []
    for line in lines:
        rtt_trad.append(float(line.split(":")[0]))
        time_trad.append(float(line.split(":")[1]))
with open('/Users/keithdesantis/PycharmProjects/CS4516-Team17/Data/host1_host3_rtt_OPENFLOW.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        rtt_OPEN.append(float(line.split(":")[0]))
        time_OPEN.append(float(line.split(":")[1]))


plt.plot(time_trad, rtt_trad,color='r',label='Traditional')
plt.plot(time_OPEN, rtt_OPEN,color='b',label='Simple OpenFlow')
"""
plt.plot(trial, data,color='orange',label='OpenFlow DNS Editing')
plt.legend()
plt.grid()
plt.xlabel('Runtime of Test (s)')
plt.ylabel('RTT (ms)')
plt.title('RTTs')
plt.show()

if __name__ == "__main__":
    pass