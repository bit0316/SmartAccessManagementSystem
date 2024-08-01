import os
import threading
import socket
import home

SERVER_IP = "192.168.0.15"
SERVER_PORT = 9999
client_sockets = []
client_addresses = []

# Start server
def start(doorlock):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Server started. Waiting for clients...\n")

    while True:
        client_socket, client_address = server_socket.accept()
        client_sockets.append(client_socket)
        client_addresses.append(client_address)
        print(f"Client connected: {client_address}\n")
        threading.Thread(target=handle_client, args=(client_socket, doorlock)).start()

# Client connected
def handle_client(client_socket, doorlock):
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8").strip()
            if not data:
                break
            # Receive user ID
            elif data == "user_id":
                print(f"Received: user_id from {client_socket.getpeername()}")
                user_id = client_socket.recv(1024).decode("utf-8").strip()
                print(f"Received user_id: {user_id}\n")
                update_client_address(user_id, client_socket.getpeername())
            # Send home sensor values
            elif data == "condition":
                print(f"Received: condition from {client_socket.getpeername()}")
                home_sensor = return_home_sensor()
                client_socket.sendall(home_sensor.encode("utf-8"))
                print("Sent: home sensor values\n")
                home.print_values()
            # Send Guest.jpg (Client -> Server)
            elif data == "check":
                print(f"Received: check from {client_socket.getpeername()}")
                send_image(client_socket, "Dataset/Guest/Guest.jpg")
                print("Sent: Guest.jpg\n")
            # Doorlock open
            elif data == "open":
                if doorlock.isLock:
                    print(f"Received: open from {client_socket.getpeername()}")
                    doorlock.open()

    # Print Error
    except Exception as e:
        print(f"Client error: {e}\n")
    finally:
        client_socket.close()
        client_sockets.remove(client_socket)

# Update client address with user id
def update_client_address(user_id, client_address):
    # Create the file path
    filename = os.path.join("UserData", f"{user_id}.txt")

    # Check if the file exists
    if os.path.exists(filename):
        # Read the existing content
        with open(filename, "r") as file:
            content = file.readlines()

        # Modify the content
        modified_content = []
        for line in content:
            if "Client Address:" in line:
                # Update the line with the client socket
                line = f"Client Address: {client_address}\n"
            modified_content.append(line)

        # Write the modified content back to the file
        with open(filename, "w") as file:
            file.writelines(modified_content)

        print(f"Updated user_id.txt for {user_id}\n")
    else:
        print(f"File {filename} does not exist...\n")

# Send image to client
def send_image(client_socket, image_path):
    # Chunk size for sending the image
    chunk_size = 1024

    # Read the image and get its size
    with open(image_path, "rb") as file:
        image_data = file.read()
    image_size = len(image_data)

    # Send the image size to the client
    client_socket.sendall(image_size.to_bytes(4, 'big'))

    # Send the image data in chunks
    total_bytes_sent = 0
    while total_bytes_sent < image_size:
        end_index = min(total_bytes_sent + chunk_size, image_size)
        image_chunk = image_data[total_bytes_sent:end_index]
        client_socket.sendall(image_chunk)
        total_bytes_sent += len(image_chunk)

# Knock Knock (Server -> Client)
def knock_knock(user):
    # Check client address
    for client_socket, client_address in zip(client_sockets, client_addresses):
        client_address_str = f"('{client_address[0]}', {client_address[1]})"
        if user["Client Address"] == client_address_str:
            send_image(client_socket, "Dataset/Guest/Knock_Knock.jpg")
            print(f"knock, knock, {client_address}\n")

# Send home sensor values (Arduino -> Client)
def return_home_sensor():
    pm2p5, pm10, humi, temp, flame = home.parse_sensor_values()
    data_list = [str(pm2p5), str(pm10), str(humi), str(temp), str(flame)]
    data_str = ",".join(data_list)
    return data_str
