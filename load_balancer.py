from xmlrpc.server import SimpleXMLRPCServer
server_pool = [8000, 8001, 8002, 8003]
index = 0


def round_robin():
    global index, server_pool
    index = (index+1) % len(server_pool)
    return index


if __name__ == "__main__":
    # Define local XML RPC server
    server = SimpleXMLRPCServer(("localhost", 9000), allow_none=True)

    # Registering the function to the server
    server.register_function(round_robin)

    try:
        print("Load Balancer listening on port 9000...")
        print("Press Ctrl + C to exit.")
        server.serve_forever()

    except:
        print("Exit successful.")
