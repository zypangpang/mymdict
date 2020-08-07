import socket,json

def test_client():
    HOST, PORT = "localhost", 9999

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect("/tmp/mmdict_socket")
        data="Lookup,write"
        sock.sendall(data.encode("utf-8"))

        # Receive data from the server and shut down
        msg_list=[]
        while True:
            msg=sock.recv(8192)
            if not msg:
                break
            msg_list.append(msg)
        return_str=b"".join(msg_list).decode("utf-8")
        print(return_str)
        #definition_obj=json.loads(b"".join(msg_list).decode("utf-8"))
        #print(definition_obj['LongmanDict.mdx'])

if __name__ == '__main__':
    test_client()


