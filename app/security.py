from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

#give an object configured with recommended pass-hashing algorithm with Argon2  supported


#returns a hash for the password
def hash_password(password:str) -> str:
    return password_hash.hash(password)

#if user enters password again verfiy if matches stored hash
def verify_password(password:str, hashed_password: str) -> bool:
    return password_hash.verify(password,hashed_password)
