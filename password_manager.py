import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet


PASSWORD_FILE = "passwords.json"
MASTER_FILE = "master.key"


def generate_key(master_password):
    password_bytes = master_password.encode()
    hash_key = hashlib.sha256(password_bytes).digest()
    encryption_key = base64.urlsafe_b64encode(hash_key)
    return encryption_key


def get_cipher(master_password):
    key = generate_key(master_password)
    cipher = Fernet(key)
    return cipher


def save_master_password(master_password):
    password_hash = hashlib.sha256(
        master_password.encode()
    ).hexdigest()

    with open(MASTER_FILE, "w") as file:
        file.write(password_hash)


def verify_master_password(master_password):
    if not os.path.exists(MASTER_FILE):
        return False

    with open(MASTER_FILE, "r") as file:
        stored_hash = file.read()

    entered_hash = hashlib.sha256(
        master_password.encode()
    ).hexdigest()

    return stored_hash == entered_hash


def setup_master_password():
    print("\n--- First Time Setup ---")

    while True:
        password = input("Create master password: ")
        confirm = input("Confirm master password: ")

        if password == confirm:
            save_master_password(password)
            print("Master password created successfully!")
            return password
        else:
            print("Passwords do not match. Try again.")


def login():
    print("\n--- Password Manager Login ---")

    attempts = 3

    while attempts > 0:
        password = input("Enter master password: ")

        if verify_master_password(password):
            print("Login successful!")
            return password
        else:
            attempts -= 1
            print(f"Wrong password! Attempts left: {attempts}")

    print("Too many failed attempts. Exiting...")
    exit()


def encrypt_data(data, cipher):
    json_data = json.dumps(data)

    encrypted_data = cipher.encrypt(
        json_data.encode()
    )

    return encrypted_data


def decrypt_data(encrypted_data, cipher):
    decrypted_data = cipher.decrypt(
        encrypted_data
    )

    data = json.loads(
        decrypted_data.decode()
    )

    return data


def load_passwords(cipher):

    if not os.path.exists(PASSWORD_FILE):
        return {}

    try:
        with open(PASSWORD_FILE, "rb") as file:
            encrypted_data = file.read()

        return decrypt_data(
            encrypted_data,
            cipher
        )

    except Exception:
        print("Error reading password database.")
        return {}


def save_passwords(passwords, cipher):

    encrypted_data = encrypt_data(
        passwords,
        cipher
    )

    with open(PASSWORD_FILE, "wb") as file:
        file.write(encrypted_data)

def add_password(passwords, cipher):

    website = input("Enter website/app name: ")
    username = input("Enter username/email: ")
    password = input("Enter password: ")

    passwords[website] = {
        "username": username,
        "password": password
    }

    save_passwords(passwords, cipher)

    print("Password saved successfully!")


def retrieve_password(passwords):

    website = input("Enter website/app name: ")

    if website in passwords:

        print("\nWebsite:", website)
        print("Username:", passwords[website]["username"])
        print("Password:", passwords[website]["password"])

    else:
        print("No password found for this website.")


def search_password(passwords):

    search_term = input("Enter search keyword: ").lower()

    found = False

    for website in passwords:

        if search_term in website.lower():

            print("\nWebsite:", website)
            print("Username:", passwords[website]["username"])
            print("Password:", passwords[website]["password"])

            found = True


    if not found:
        print("No matching passwords found.")


def delete_password(passwords, cipher):

    website = input("Enter website/app name to delete: ")

    if website in passwords:

        del passwords[website]

        save_passwords(passwords, cipher)

        print("Password deleted successfully!")

    else:

        print("No password found for this website.")
 

def main():

    if not os.path.exists(MASTER_FILE):

        master_password = setup_master_password()

    else:

        master_password = login()


    cipher = get_cipher(master_password)

    passwords = load_passwords(cipher)


    while True:

        print("\n===== Password Manager =====")
        print("1. Add Password")
        print("2. Retrieve Password")
        print("3. Search Password")
        print("4. Delete Password")
        print("5. Exit")


        choice = input("Enter your choice: ")


        if choice == "1":

            add_password(
                passwords,
                cipher
            )


        elif choice == "2":

            retrieve_password(
                passwords
            )


        elif choice == "3":

            search_password(
                passwords
            )


        elif choice == "4":

            delete_password(
                passwords,
                cipher
            )


        elif choice == "5":

            print("Exiting Password Manager...")
            break


        else:

            print("Invalid choice. Try again.")



if __name__ == "__main__":

    main()