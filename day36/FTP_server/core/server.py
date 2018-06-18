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
        try:
            while 1:

                data=self.request.recv(1024).strip()
                data=json.loads(data.decode('utf-8'))
                '''
                {'action':'auth',
                 'username':'ma',
                 'pwd':'123',
                }
                
                '''
                print(data)
                if data.get('action'):
                    if hasattr(self,data.get('action')):
                        func=getattr(self,data.get('action'))
                        func(**data)
                    else:
                        print('无效')
                else:
                    print('无效命令')
        except Exception as e:
            print(e)


    def send_response(self,state_code):
        response={'status_code':state_code}

        self.request.sendall(json.dumps(response).encode('utf-8'))


    def auth(self,**data):
        print('auth data',data)
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
        print('put data',data)
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
                #文件不完整
                self.request.sendall('800'.encode('utf-8'))

                choice=self.request.recv(1024).decode('utf-8')
                if choice=='Y':
                    self.request.sendall(str(has_file_size).encode('utf-8'))
                    f = open(abs_path, 'ab')
                    has_received=has_file_size
                else:
                    f = open(abs_path, 'wb')

            else:
                #文件完全存在
                self.request.sendall('801'.encode('utf-8'))
                return
                # f = open(abs_path, 'ab')
        else:
            # 文件不存在
            self.request.sendall('802'.encode('utf-8'))
            f=open(abs_path,'wb')

        while has_received<file_size:
            try:
                data=self.request.recv(1024) #有多少收多少，最多1024字节
            except Exception as e:
                print('put error',e)
                break
            f.write(data)
            has_received+=len(data)


        f.close()

    def ls(self,**data):

        file_list=os.listdir(self.mainPath)
        print('ls mainpath:',self.mainPath)
        file_str = '\n'.join(file_list)
        if not file_list:
            file_str='<empty dir>'
        self.request.sendall(file_str.encode('utf-8'))

    def cd(self,**data):
        # print('cd data type:',type(data))
        dirname=data.get('dirname')
        path = os.path.join(self.mainPath, dirname)
        if dirname=='..':
            self.mainPath=os.path.dirname(self.mainPath)
            print('cd .. mainpath:',self.mainPath)
            self.request.sendall(self.mainPath.encode('utf-8'))
        else:
            if dirname in os.listdir(self.mainPath):
                if os.path.isdir(path):
                    self.mainPath=os.path.join(self.mainPath,dirname)
                    self.request.sendall(self.mainPath.encode('utf-8'))
                else:
                    self.request.sendall(('%s不是目录' % dirname).encode('utf-8'))
            else:
                self.request.sendall(('%s目录不存在'%dirname).encode('utf-8'))


    def mkdir(self,**data):
        dirname = data.get('dirname')
        path=os.path.join(self.mainPath,dirname)

        # 判断是否存在
        if not os.path.exists(path):
            #判断是否多重目录
            if '/' in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)
            self.request.sendall(('%s 目录创建成功'%dirname).encode('utf-8'))
        else:
            self.request.sendall(('%s 目录已经存在'%dirname).encode('utf-8'))
