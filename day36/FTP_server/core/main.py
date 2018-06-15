

import optparse,socketserver,sys,os

# BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(BASE_DIR)

from conf import settings
from core import server


class ArgvHandle():
    def __init__(self):
        self.op=optparse.OptionParser()

        # self.op.add_option('-s','--server',dest='server')
        # self.op.add_option('-P','--port',dest='port')
        options,args=self.op.parse_args()
        r'''
        C:\Users\may\PycharmProjects\python_s3\day36\FTP_server\bin>python ftp_server
        .py -s 127.0.0.1 -P 8080 yy uu
        {'server': '127.0.0.1', 'port': '8080'} <class 'optparse.Values'>
        127.0.0.1
        ['yy', 'uu'] <class 'list'>

        '''
        # print(options,type(options))
        # print(options.server)
        # print(args,type(args))


        self.verify_args(options,args)

    def verify_args(self,options,args):

        cmd=args[0]
        if hasattr(self,cmd):
            func=getattr(self,cmd)
            func()


    def start(self):
        print('server start...')
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT), server.ServerHandler)
        s.serve_forever()

    def help(self):
        pass