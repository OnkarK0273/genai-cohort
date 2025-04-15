import tiktoken

encoder = tiktoken.encoding_for_model('gpt-4o')

test = 'the cat sat on mat'

token = encoder.encode(test)

print(token)

my_token = [112,112,332,113]
decoding = encoder.decode(my_token)
