import bcrypt 

senha = '123'

encode_senha = senha.encode('utf-8')

salt = bcrypt.gensalt()

hash = bcrypt.hashpw(encode_senha, salt)

print('salt = ', salt)
print('hash = ', hash)

if (bcrypt.hashpw('123'.encode('utf-8'), salt) == hash):
    print("true hash")
else:
    print("bad...")