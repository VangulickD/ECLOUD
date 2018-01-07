
# You have to `pip install rsa`
import rsa

### KEY GENERATION ###
### Run once, on your dev environment
### Store the private key in a secure place; add the pubkey to your program

(pubkey, privkey) = rsa.newkeys(1024)

# This is the private key, keep this secret. You'll need it to sign new updates.
privkey = privkey.save_pkcs1()
print("your private key is the following: ")
print(privkey)
print("_________________________________________________________________________________")
print("your public key is the following: ")

# This is the public key you must distribute with your program and pass to rsa_verify.
pubkey = (pubkey.n, pubkey.e)
print("pubkey = (%#x, %i)" % pubkey)

"""
still working on this part
def sign(message, priv_key, hashAlg="SHA-256"):
    global hash
    signer = PKCS1_v1_5.new(priv_key)
    digest = SHA256.new()
    digest.update(message)
    return signer.sign(digest)



message =123456789
sign(message, priv_key)"""

