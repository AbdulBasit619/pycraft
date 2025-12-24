from caesar_cipher import *

prompt = "Please enter the text you want to Encrypt (leave empty to exit): "


my_secret_message = input(prompt)

encrypted_message = Encrypt(my_secret_message, 1).encrypt(5)
print(encrypted_message)

decrypted_message = Decrypt(encrypted_message, 1).decrypt(5)
print(decrypted_message)
