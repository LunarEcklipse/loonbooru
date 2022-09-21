import uuid
import hashlib

instr = "nopedagger"

hash_obj = hashlib.sha256(instr.encode('utf-8'))
hex_dig = hash_obj.hexdigest()
print(hex_dig)
