"""
Encryption utilities for securing sensitive data like session tokens
"""
import base64
from cryptography.fernet import Fernet
import config

def get_or_create_key():
    """
    Get or create encryption key
    If key file exists, load it; otherwise generate new key
    """
    key_file = config.ENCRYPTION_KEY_FILE
    
    if key_file.exists():
        with open(key_file, 'rb') as f:
            return f.read()
    
    # Generate new key
    key = Fernet.generate_key()
    
    with open(key_file, 'wb') as f:
        f.write(key)
    
    return key

def get_fernet():
    """Get Fernet encryptor/decryptor instance"""
    key = get_or_create_key()
    return Fernet(key)

def encrypt_token(token: str) -> str:
    """
    Encrypt a token string
    
    Args:
        token: Plain text token
        
    Returns:
        Base64 encoded encrypted token
    """
    fernet = get_fernet()
    encrypted = fernet.encrypt(token.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt an encrypted token
    
    Args:
        encrypted_token: Base64 encoded encrypted token
        
    Returns:
        Plain text token
    """
    fernet = get_fernet()
    decoded = base64.b64decode(encrypted_token.encode())
    decrypted = fernet.decrypt(decoded)
    return decrypted.decode()
