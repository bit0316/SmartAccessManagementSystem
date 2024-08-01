import time
import threading
import LCD
import face
import server
import user_data
import doorlock as dl

# Define main doorlock
doorlock = dl.DoorLock()

# Main function
def main():
    # Create and Run server thread
    server_thread = threading.Thread(target=server.start, args=(doorlock,))
    server_thread.start()
    time.sleep(1)

    while True:
        # Print menu
        print("=========================")
        print("1. Start Doorlock System")
        print("2. User Data Management")
        print("3. Exit")
        print("=========================")

        # Select menu
        choice = input("Enter your choice (1-3): ")
        print()

        # 1. Start Doorlock System
        if choice == "1":
            doorlock.reset()
            LCD.print_main()
            LCD.start_doorlock(server, face, doorlock)

        # 2. User Data Management
        elif choice == "2":
            user_data.user_data(face)

        # 3. Exit
        elif choice == "3":
            # Waiting for server thread to end
            server_thread.join()
            break

        # Invalid choice
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")
            continue


# Start main function
if __name__ == "__main__":
    main()
