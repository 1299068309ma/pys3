import socketserver
import json,configparser
import os
from conf import settings

STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "ready to send file",
    258 : "md5 verification",

    800 : "the file exist,but not enough ,is continue? ",
    801 : "the file exist !",
    802 : " ready to receive datas",

    900 : "md5 valdate success"

}

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while 1:

            data=self.request.recv(1024).strip()
            data=json.loads(data.decode('utf-8'))
            '''
            {'action':'auth',
             'username':'ma',
             'pwd':'123',
            }
            
            '''

            if data.get('action'):
                if hasattr(self,data.get('action')):
                    func=getattr(self,data.get('action'))
                    func(**data)
                else:
                    print('无效')
            else:
                print('无效命令')


    def send_response(self,state_code):
        response={'status_code':state_code}

        self.request.sendall(json.dumps(response).encode('utf-8'))


    def auth(self,**data):
        # print(data)
        username=data['username']
        password=data['password']

        user=self.authenticate(username,password)
        if user:
            self.send_response(254)

        else:
            self.send_response(253)

    def authenticate(self,user,pwd):

        cfg=configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)

        if user in cfg.sections():
            if cfg[user]['Password']==pwd:
                self.user=user
                self.mainPath=os.path.join(settings.BASE_DIR,'home',self.user)
                print('passed server auth')
                return user

    def put(self,**data):
        print('data',data)
        file_name=data.get('file_name')
        file_size=data.get('file_size')
        target_path=data.get('target_path')

        abs_path=os.path.join(self.mainPath,target_path,file_name)

        '''
        1、判断文件是否存在      有/没有
        2、判断文件完整性，大小    完整/不完整
        '''
        has_received=0
        if os.path.exists(abs_path):
            has_file_size=os.stat(abs_path).st_size
            if has_file_size<file_size:
                #断点续传
                pass
            else:
                #文件完全存在
                self.request.sendall('802'.encode('utf-8'))

            f = open(abs_path, 'ab')
        else:
            self.request.sendall('802'.encode('utf-8'))

            f=open(abs_path,'wb')

        while has_received<file_size:
            data=self.request.recv(1024) #有多少收多少，最多1024字节
            f.write(data)
            has_received+=len(data)
        f.close()


