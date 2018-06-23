from socket import *
import os
import base64
import _thread
import time

Err404='/404.html'
Err401='/Unauthorized.html'
Err500='/Syserr.html'
AuthName='Unsecured File Access System (UFAS)'
UserList={'yyj':'yyj','admin2':'admin'}
Redirect={'/':'/index.html'}
Callback={'/index.html':'callbacktest'}
Maximum_Trial=5
Delay=7
Maximum_Trial_Redirect='/Max.html'

def send_response(header,filename):
    try:
        f = open(filename[1:])
        outputdata = f.read()
        f.close()
        connectionSocket.send(header.encode('utf-8'))
        for i in range(0,len(outputdata)):
            connectionSocket.send(outputdata[i].encode('utf-8'))
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
    return filename

def delay():
    global Trial
    time.sleep(Delay)
    Trial=0
    _thread.exit_thread()

def callbacktest(RequestedUrl):
    print('this is a callback test!!')
    print('Requested Url:'+RequestedUrl)
    print('now redirecting to: /reqs.py')
    return '/reqs.py'

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
        Trial=Trial+1
        if Trial>Maximum_Trial and Maximum_Trial!=0:
            header = 'HTTP/1.1 200 OK\n\n'
            filename = Maximum_Trial_Redirect
            send_response(header,filename)
        header = 'HTTP/1.1 401 Unauthorized\n'+AuthMsg+'\n\n'
        filename = Err401
        msgs=message.split()
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
