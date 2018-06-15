import socketserver
import os


class Myserver(socketserver.BaseRequestHandler):

    def handle(self):
        pass


# s=socketserver.ThreadingTCPServer((),Myserver)
# s.serve_forever()


local_path=r'd:\12\11.png'

main_path=os.path.dirname(os.path.abspath(__file__))

l=os.path.join(main_path,local_path)
print(l)

