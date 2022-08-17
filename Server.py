import os
import socket
import threading

IP = "localhost"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"


### to handle the clients
def handle_client(conn, addr):
    files = os.listdir(SERVER_PATH)

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.send("OK@Welcome to the server".encode(FORMAT))

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        data = data.split("@")
        cmd = data[0]

        send_data = "OK@"

        if cmd == "LOGOUT":
            break

        elif cmd == "RENAME":
            data = conn.recv(SIZE).decode(FORMAT)
            files = os.listdir(SERVER_PATH)
            fileName, rename = data.split('@')

            if fileName in files:  ##  condition if file exist in the server.
                file_add = os.path.join(SERVER_PATH, fileName)
                rename_add = os.path.join(SERVER_PATH, rename)
                os.rename(file_add, rename_add)
                send_data += "File renamed"
                conn.send(f"{send_data}".encode(FORMAT))
            else:
                send_data += fileName + " does not exist"
                conn.send(f"{send_data}".encode(FORMAT))

        elif cmd == "UPLOAD":
            # receive the file infos
            # receive using client socket, not server socket
            file_prop = conn.recv(SIZE).decode(FORMAT)
            file_prop = file_prop.split("@")
            file_name = file_prop[0]
            file_name = os.path.basename(file_name)
            file_size = file_prop[1]

            # Opens
            with open(os.path.join(SERVER_PATH, file_name), "wb") as file:
                bytecount = 0

                # Running the loop while file is recieved.
                while bytecount < int(file_size):
                    data = conn.recv(SIZE)
                    if not (data):
                        break
                    file.write(data)
                    bytecount += len(data)
            # Ending the upload.
            send_data += "file upload complete"
            conn.send(send_data.encode(FORMAT))

        elif cmd == "DOWNLOAD":
            file_name = conn.recv(SIZE).decode(FORMAT)
            files = os.listdir(SERVER_PATH)
            if file_name in files:
                file_add = os.path.join(SERVER_PATH, file_name)
                file_size = os.path.getsize(file_add)
                conn.send(f"EXISTS".encode(FORMAT))
                conn.send(str(file_size).encode(FORMAT))
                with open(file_add, "rb") as file:
                    bytecount = 0
                    # Running loop while bytecount is less than file_size.
                    while bytecount < file_size:
                        data = file.read(SIZE)
                        if not data:
                            break
                        conn.sendall(data)
                        bytecount += len(data)

                send_data += "file download complete"
                conn.send(f"{send_data}".encode(FORMAT))
            else:
                conn.send(f"ERROR".encode(FORMAT))
                conn.send(f"{send_data}".encode(FORMAT))

        elif cmd == "DELETE":
            file_name = conn.recv(SIZE).decode(FORMAT)
            files = os.listdir(SERVER_PATH)
            if file_name in files:
                file_add = os.path.join(SERVER_PATH, file_name)
                os.remove(file_add)
                send_data += file_name + " has been removed"
                conn.send(f"{send_data}".encode(FORMAT))
            else:
                send_data += file_name + " does not exist"
                conn.send(f"{send_data}".encode(FORMAT))

        elif cmd == "DIR":
            files = os.listdir(SERVER_PATH)
            file_sizes = []
            for file in files:
                file_sizes.append(os.path.getsize(os.path.join(SERVER_PATH, file)))

            conn.send(f"{files}@{file_sizes}".encode(FORMAT))

    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ## used IPV4 and TCP connection
    server.bind(ADDR)  # bind the address
    server.listen()  ## start listening
    print(f"server is listening on {IP}: {PORT}")
    while True:
        conn, addr = server.accept()  ### accept a connection from a client
        thread = threading.Thread(target=handle_client, args=(conn, addr))  ## assigning a thread for each client
        thread.start()


if __name__ == "__main__":
    main()

