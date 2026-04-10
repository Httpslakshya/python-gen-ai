import tiktoken

enc = tiktoken.encoding_for_model("gpt-3.5-turbo")

text = "hello , i am lakshya dharkar"
tokens=enc.encode(text)
print("input tokens are:", tokens)
print("after decoding token :",enc.decode(tokens))
print("the length of token :",len(tokens))

print(enc.decode([94786]))