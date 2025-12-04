from Server.Server import Server

if __name__ == "__main__":
    server = Server(port=8585)
    server.run()