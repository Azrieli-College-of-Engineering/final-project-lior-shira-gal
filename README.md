# Insecure Deserialization Demonstration

## Overview

This project demonstrates an **Insecure Deserialization vulnerability** in a simulated **flight booking web application built with Flask**.

The application stores user session data inside a browser cookie using **Python's `pickle` module**, and deserializes it with **`pickle.loads()`** without verifying the integrity of the data. This allows an attacker to **decode, modify, and re-encode session data**, potentially leading to privilege escalation or remote code execution.

The goal of this project is to:

- Explain **what Insecure Deserialization is**
- Show **how the vulnerability appears in web applications**
- Demonstrate **attack scenarios**
- Present **secure practices to prevent the vulnerability**

---

# Vulnerability Description and Theoretical Background

## What is Insecure Deserialization?

**Insecure Deserialization** occurs when a system **deserializes untrusted data without validation**. If an attacker can manipulate the serialized input, they may control the resulting object and execute arbitrary code or bypass security mechanisms.

## How It Occurs

Serialization converts complex data structures (objects, dictionaries) into a **byte stream** for storage or transmission. Deserialization reconstructs the original object from this byte stream.

When deserialization is performed on **user-controlled data** without verification, vulnerabilities arise. In Python, **`pickle`** can execute code during deserialization, making it extremely unsafe for untrusted input.

## Where This Vulnerability Appears in Web Applications

- **Cookies**
- **Session data**
- **HTTP request parameters**
- **Communication between services through APIs**

Since these values are controlled by the user, attackers can modify them before sending to the server. Without verification, the server may deserialize altered objects, leading to **logic manipulation, privilege escalation, or RCE**.

---

# Why `pickle.loads()` is Dangerous

`pickle` can serialize and deserialize Python objects, but **it can also execute code embedded in the object**. When deserializing untrusted data:

- Attackers can **modify application data**
- **Escalate privileges**
- **Execute arbitrary code**

Trusting client-side cookies serialized with pickle is therefore very dangerous.

---

# Session Structure

The application stores user session data in a dictionary like this:

```python
{
  "logged_in": True,
  "user": "bob",
  "is_vip": False,
  "bookings": [],
  "loyalty_points": 0
}
```

The **VIP lounge page** checks:

```python
if not s.get("is_vip"):
    return "Access denied"
```

An attacker can modify the cookie to set **`"is_vip": True`** and gain unauthorized access.

---

# Attack Demonstration

## forge_cookie.py – Cookie Forgery Demonstration

The **forge_cookie.py** script demonstrates how an attacker can exploit **Insecure Deserialization** in a web application that stores serialized session objects inside cookies.

In the vulnerable application, the session data is serialized using Python’s **pickle** module and then encoded using **Base64** before being stored in the user's browser cookie. Because the cookie is **not signed or validated**, it can be decoded, modified, and re‑encoded by an attacker.

---

## Script Workflow

The script performs the following steps:

### step 1: Extract the original cookie value

The script starts with a cookie value that was captured from the browser.  
This cookie contains serialized session data.

---

### step 2: Decode the cookie

The cookie is Base64 encoded, so it is first decoded:

```python
raw = base64.urlsafe_b64decode(cookie_value.encode())
```

---

### step 3: Deserialize the session object

The decoded data is deserialized using Python's `pickle.loads()` function to reconstruct the original session dictionary.

```python
session = pickle.loads(raw)
```

---

### step 4: Modify the session data

The script then injects a malicious modification by setting:

```python
session["is_vip"] = True
```

This simulates a **privilege escalation attack**, where the attacker changes their role or permissions inside the session.

---

### step 5: Re‑serialize the modified session

The manipulated session object is serialized again using `pickle.dumps()`.

```python
new_raw = pickle.dumps(session, protocol=pickle.HIGHEST_PROTOCOL)
```

---

### step 6: Encode the new cookie

The serialized object is encoded back into Base64 so it can be used as a cookie value.

```python
new_cookie = base64.urlsafe_b64encode(new_raw).decode()
```

---

### step 7: Output the forged cookie

The script prints the new cookie value, which can then be inserted into the browser to impersonate a **privileged user**.

```python
print(new_cookie)
```

---

---

# How to Run the Project

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Start the Vulnerable Server

Run the Flask application:

```bash
python insecure_server.py
```

The application will start locally at: http://127.0.0.1:5000

Open this address in your browser to access the unsecured server.

---

# User Guide – Exploiting the Vulnerability

## Exploitation Steps

1. **Login**

Log in as a regular user (for example **Alice**).

---

2. **Retrieve the Cookie**

Open the browser's developer tools:

```
F12 → Application → Cookies → http://127.0.0.1:5000
```

Locate the cookie named:

```
booking_session
```

Copy its value.

---

3. **Modify the Cookie Using the Attack Script**

Open the Python file:

```
forge_cookie.py
```

Paste the copied cookie value into the variable:

```python
cookie_value = "PASTE_THE_COOKIE_HERE"
```

The script reads the cookie value and deserializes it using:

```python
pickle.loads()
```

It then grants VIP permissions to the regular user by modifying the session data:

```python
session["is_vip"] = True
```

---

4. **Generate the Malicious Cookie**

Run the script:

```bash
python forge_cookie.py
```

The script will:

- Serialize the modified session using `pickle.dumps()`
- Encode it back to Base64
- Print a **new forged cookie value**

---

5. **Inject the Forged Cookie**

Return to the browser developer tools and **replace the original value** of the `booking_session` cookie with the new value generated by the script.

---

6. **Exploit the Vulnerability**

Click the **VIP Lounge** button.

Because the server trusts the modified cookie, it believes the user is a **VIP** and grants full access.

---

# Impact

Exploitation allows:

- **Privilege escalation (VIP access)**
- **Manipulation of booking history**
- **Modification of loyalty points**
- **Potential remote code execution via malicious pickle payloads**

In real-world systems, this could lead to **full server compromise**.

---

# Defense Mechanisms and Prevention

## Why Existing Protections Fail

- The server uses **`pickle.loads()`** on **client-sent cookies**
- No **cryptographic signing or verification** is performed
- Users can **modify session data** and escalate privileges

This causes **Insecure Deserialization**.

## How to Prevent the Vulnerability

- **Do not deserialize untrusted data**
- Use safe serialization formats like **JSON** or **MessagePack**
- Keep session data **server-side only**
- Store only a **random session ID** on the client
- Protect client-side data with **cryptographic signatures**

## Security Best Practices

- **Always validate input received from the client**
- Prefer **safe data formats** over object serialization
- Run services with **minimal privileges**
- Implement **logging and monitoring** for deserialization attempts
- Detect and block **tampered cookies or signature forgery**
- Apply **defense-in-depth principles**
