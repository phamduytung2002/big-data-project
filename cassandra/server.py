import socket

while 1:
    if __name__ == "__main__":
        host = "192.168.194.33"
        port = 10000
        total_clients = int(input("Enter number of clients: "))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(total_clients)

        connections = []
        print("Initiating clients")
        for i in range(total_clients):
            conn, addr = sock.accept()
            connections.append((conn, addr))
            print("Connected with client", i + 1, "at address", addr)

        fileno = 0
        for conn, _ in connections:
            # Receiving File Data
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk

            if not data:
                continue

            # Decoding binary data as UTF-8 text
            text_data = data.decode("utf-8")

            # Creating a new file at server end and writing the decoded data
            filename = f"output{fileno}.txt"
            fileno += 1
            with open(filename, "w", encoding="utf-8") as fo:
                fo.write(text_data)

            print()
            print("Receiving file from client")
            print("Received successfully! New filename is:", filename)

        for conn, _ in connections:
            conn.close()
