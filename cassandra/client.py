import socket

# Creating Client Socket
if __name__ == "__main__":
    host = "192.168.194.33"
    port = 10000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connecting with Server
    sock.connect((host, port))

    while True:
        filename = 'topic_doc2.csv'
        try:
            # Reading file and sending data to server
            fi = open(filename, "r")
            data = fi.read()
            if not data:
                break
            while data:
                sock.send(str(data).encode())
                data = fi.read()
            # File is closed after data is sent
            fi.close()

        except IOError:
            print("You entered an invalid filename!")
