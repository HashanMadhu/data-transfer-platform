import cryptocode

# Secret key used for encryption and decryption processes
# In real production, this should be loaded from an environment variable (.env)
SECRET_KEY = "my_super_secret_key_for_data_transfer"

def encrypt_data(plain_text: str) -> str:
    """
    Encrypts a plain text string into a secure encrypted string.
    """
    if not plain_text:
        return plain_text
    return cryptocode.encrypt(plain_text, SECRET_KEY)

def decrypt_data(encrypted_text: str) -> str:
    """
    Decrypts an encrypted string back into its original plain text.
    """
    if not encrypted_text:
        return encrypted_text
    return cryptocode.decrypt(encrypted_text, SECRET_KEY)