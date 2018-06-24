#在任意Callback中返回STOP,服务器将自动停止响应

#imports
from socket import *
import os
import base64
import _thread
import time
import struct
from urllib import parse


#配置
Err404='/404.html'
Err401='/Unauthorized.html'
Err500='/Syserr.html'
Maximum_Trial_Redirect='/Max.html'
PublicSite=['/','/welcome.html','/welcome.txt']
AuthName='Unsecured File Access System (UFAS)'
UserList={'yyj':'yyj','admin2':'admin'}
Redirect={'/':'/welcome.html'}
Callback={'/server.py':'secure'}
Always_Callback=['securecheck','chinesedetect','filelist']
After_Callback=['modecheck']
Maximum_Trial=5
Delay=7

#Callback Settings
listignore=[Err401,Err404,Err500,Maximum_Trial_Redirect,'/Server.py']

#Callbacks
def chinesedetect(Rq):
    if parse.unquote(Rq)!=Rq:
        return parse.unquote(Rq)
    else:
        return Rq

def filelist(Rq):
    if Rq=='/':
        generatefilelist('')
        return 'STOP'
    if os.path.isdir(os.path.join(os.getcwd(),Rq[1:])):
        generatefilelist(Rq)
        return 'STOP'
    else:
        print('File/No file list generated')
def modecheck(Rq):
    try:
        with open(Rq[1:],'r') as f:
            f.read()
            return Rq
    except:
        for x in Redirect:
            if Rq==x:
                Rq=Redirect[Rq]
        hd='HTTP/1.1 200 OK\nContent-Type:Files/Others\n\n'
        send_response(hd,Rq,'rb')
        return 'STOP'

def generatefilelist(Folder):
    start='''<html>
<head>
<meta charset='utf-8'>
</head>
<body>
<title>File Center - UFAS</title>
</b>Welcome to Lincoln Yan's File Server.</b>
<br>Acroading to permission settings, you may need to sign in to access some files</br>
<hr>
<p>Files available ('''+'/'+Folder[1:]+'):</p>'
    TempDir=os.listdir(os.path.join(os.getcwd(),Folder[1:]))
    for x in TempDir:
        if '/'+x in listignore:
            continue
        if '/'+x in PublicSite:
            start=start+'<p><a href='+parse.quote(Folder)+'/'+parse.quote(x)+'>'+x+'</a> (Public)</p>\n'
        else:
            start=start+'<p><a href='+parse.quote(Folder)+'/'+parse.quote(x)+'>'+x+'</a> (Private)</p>\n'
    start=start+'</body></html>'
    header='HTTP/1.1 200 OK\n\n'
    send_response(header,'',DirectContent=start)
    return 'STOP'

def callbacktest(RequestedUrl):
    print('this is a callback test!!')
    print('Requested Url:'+RequestedUrl)
    print('now redirecting to: /reqs.py')
    return '/reqs.py'

def securecheck(RequestedUrl):
    try:
        return RequestedUrl.lower()
    except:
        return RequestedUrl
def secure(r):
    return Err401

#系统自带!
def send_response(header,filename,OpenMode='r',DirectContent=None):
    if filename=='STOP':
        return
    try:
        if DirectContent!=None:
            outputdata=DirectContent
        else:
            f = open(filename[1:],OpenMode)
            outputdata = f.read()
            f.close()
        connectionSocket.send(header.encode('utf-8'))
        if OpenMode=='r':
            for i in range(0,len(outputdata)):
                connectionSocket.send(outputdata[i].encode('utf-8'))
        else:
            connectionSocket.send(outputdata)
        connectionSocket.close()
    except:
        try:
            #404 with file
            header='\nHTTP/1.1 404 Not Found\n\n'
            filename=Err404
            f = open(filename[1:])
            outputdata = f.read()
            f.close()
            connectionSocket.send(header.encode('utf-8'))
            for i in range(0,len(outputdata)):
                connectionSocket.send(outputdata[i].encode('utf-8'))
            connectionSocket.close()
        except:
            header='\nHTTP/1.1 404 Not Found\n\n'
            outputdata = '''<html>
<body>
<p><b>404 Not Found</b></p>
<hr>
<p>We cannot find your file</p>
</body></html> '''
            try:
                connectionSocket.send(header.encode('utf-8'))
                connectionSocket.send(outputdata.encode('utf-8'))
                connectionSocket.close()
            except:
                return()

def getfilename(filename):
    for x in Always_Callback:
        try:
            Result=eval(x+'(\''+filename+'\')')
            if Result!=None and Result!='STOP':
                filename=Result
            if Result=='STOP':
                return 'STOP'
        except:
            print('Unable to callback:(Always_Callback) '+x)
    for x in Redirect:
        if filename==x:
            filename=Redirect[filename]
    for x in Callback:
        if filename==x:
            try:
                Result=eval(Callback[x]+'(\''+filename+'\')')
                if Result!=None:
                    filename=Result
            except:
                print('Unable to callback:'+Callback[x])
    for x in After_Callback:
        Result=eval(x+'(\''+filename+'\')')
        if Result!=None:
            filename=Result
    return filename

def delay():
    global Trial
    time.sleep(Delay)
    Trial=0
    _thread.exit_thread()

serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',80))
serverSocket.listen(5)
Password_encode=[]
Trial=0
AuthMsg='WWW-Authenticate: Basic realm="'+AuthName+'"'
for x in UserList:
    Password_encode.append(base64.b64encode(str(x+':'+UserList[x]).encode('utf-8')).decode('utf-8'))
while True:
    print('System Ready')
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024)
        msgs=message.split()
        print(msgs[1].decode('utf-8'))
        if parse.unquote(msgs[1].decode('utf-8')) in PublicSite:
            filename = getfilename(msgs[1].decode('utf-8'))
            header = 'HTTP/1.1 200 OK\n\n'
            send_response(header,filename)
            continue
        Trial=Trial+1
        if Trial>Maximum_Trial and Maximum_Trial!=0:
            header = 'HTTP/1.1 200 OK\n\n'
            filename = Maximum_Trial_Redirect
            send_response(header,filename)
        header = 'HTTP/1.1 401 Unauthorized\n'+AuthMsg+'\n\n'
        filename = Err401
        for x in range(len(msgs)):
            if msgs[x].decode('utf-8')=='Authorization:':
                if msgs[x+1].decode('utf-8')=='Basic':
                    if msgs[x+2].decode('utf-8') in Password_encode:
                        header='\nHTTP/1.1 200 OK\n\n'
                        filename = getfilename(msgs[1].decode('utf-8'))
                        Trial=0
                        break
        if Trial==Maximum_Trial:
            _thread.start_new_thread(delay,())
    except Exception:
        header = '\nHTTP/1.1 500 Server Error\n\n'
        filename = Err500
    send_response(header,filename)
