import os

DIR = "UserData"

# Save user information (save user info + face)
def save_user_info(face):
    # User information
    id = input("Enter ID (ex. 21912254): ")
    name = input("Enter name(ex. Hong Gil Dong): ")
    phone = input("Enter phone number (ex. 010-1234-5678): ")
    birthday = input("Enter birthday (ex. 2023.01.01): ")
    room = input("Enter room (ex. 307): ")

    # Face training with user information
    face.face_dataset(id)
    face.face_training()

    if not os.path.exists(DIR):
        os.makedirs(DIR)
    file_path = os.path.join(DIR, f"{id}.txt")

    user_info = {
        "ID": id,
        "Name": name,
        "Phone": phone,
        "Birthday": birthday,
        "Room": room,
        "Client Address": None
    }

    with open(file_path, "w") as file:
        for key, value in user_info.items():
            file.write(f"{key}: {value}\n")
    print("User info saved successfully.\n")

# Search user informaiton by ID
def search_user_info(id):
    file_path = os.path.join(DIR, f"{id}.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()
            user_info = {}
            for line in lines:
                line = line.strip()
                key, value = line.split(":")
                user_info[key.strip()] = value.strip()
            return user_info
    return None

# Search users informaiton by (ID, name, phone, birthday, room)
def search_users_by_info(info_type, info):
    user_files = os.listdir(DIR)
    found_users = []
    for file_name in user_files:
        file_path = os.path.join(DIR, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
                user_info = {}
                for line in lines:
                    line = line.strip()
                    key, value = line.split(":")
                    user_info[key.strip()] = value.strip()
                if info_type in user_info and user_info[info_type] == info:
                    found_users.append(user_info)
    return found_users

# Delete user information
def delete_user_info(id):
    file_path = os.path.join(DIR, f"{id}.txt")
    if os.path.exists(file_path):
        os.remove(file_path)
        for i in range(1, 51):
            file_name = f"User.{id}.{i}.jpg"
            dataset_path = os.path.join("Dataset", file_name)
            if os.path.exists(dataset_path):
                os.remove(dataset_path)
        print("User info deleted successfully.\n")
    else:
        print("User not found.\n")

# Print user information by ID
def print_user_info(id):
    user_info = search_user_info(id)
    if user_info:
        print("User ID:", user_info["ID"])
        print("Name:", user_info["Name"])
        print("Phone:", user_info["Phone"])
        print("Birthday:", user_info["Birthday"])
        print("Room:", user_info["Room"])
        print()
    else:
        print("User not found.\n")

# User data menu (data management)
def user_data(face_module):
    while True:
        print("=========================")
        print("1. Save User Info")
        print("2. Search User Info by ID")
        print("3. Search Users by Info")
        print("4. Delete User Info")
        print("5. Exit")
        print("=========================")
        choice = input("Enter your choice (1-5): ")
        print()

        # 1. Save User Info
        if choice == "1":
            save_user_info(face_module)
        
        # 2. Search User Info by ID
        elif choice == "2":
            search_id = input("Enter ID to search: ")
            user = search_user_info(search_id)
            if user:
                print_user_info(user["ID"])
                print()
            else:
                print("User not found.\n")

        # 3. Search Users by Info
        elif choice == "3":
            print("-------------------------")
            print("1. Search Users by Name")
            print("2. Search Users by Phone")
            print("3. Search Users by Birthday")
            print("4. Search Users by Room")
            print("5. Exit")
            print("-------------------------")
            search_choice = input("Enter your choice (1-5): ")
            print()

            if search_choice == "1":
                search_info_type = "Name"
                search_info = input("Enter name to search: ")
            elif search_choice == "2":
                search_info_type = "Phone"
                search_info = input("Enter phone number to search: ")
            elif search_choice == "3":
                search_info_type = "Birthday"
                search_info = input("Enter birthday to search: ")
            elif search_choice == "4":
                search_info_type = "Room"
                search_info = input("Enter room to search: ")
            elif search_choice == "5":
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 5.")
                continue

            # Print user information
            found_users = search_users_by_info(search_info_type, search_info)
            if found_users:
                print("Users found:")
                for user in found_users:
                    print_user_info(user["ID"])
            else:
                print("No users found.\n")

        # 4. Delete User Info
        elif choice == "4":
            delete_id = input("Enter ID to delete: ")
            while True:
                user_input = input("Are you sure you want to delete ID? (y/n): ")
                if user_input.lower() == "y":
                    delete_user_info(delete_id)
                    break
                elif user_input.lower() == "n":
                    print("Undelete.\n")
                    break

        # 5. Exit
        elif choice == "5":
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 5.")
