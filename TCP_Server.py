import socket
import threading
import time
import json, types,string




# ==========================
# 用於紀錄已連線Client的資料
# ==========================
class ClientData():
    clientsocket=''
    name = 'no name'
    def __init__(self,client):
        self.clientsocket = client
        
        
# ==========================
# 以下為伺服器端程式碼 SocketServer Class
# 伺服器利用TCP做連線
# 並用JSON格式做資料傳輸
#
# 函式部分
# 首先run() 建立聊天室
# accept_clients() 
#    開始監聽 client連線
#    當 client連線時，client加入clients List中，並用threading開啟 recieve() 監聽 client傳送的資料
# recieve()
#    接收client傳送的資料
#    並將資料轉成json格式並存到 jdata
#    jdata中
#        jdata['cmd'] 為 client請求要做的事
#        jdata['name'] 為 client 名字
#        jdata['data'] 為 data
#    轉成jjdata依據jdata['cmd']執行不同function
#    cmd 目前內容有
#        1.say            client在聊天室要輸入訊息
#        2.what time      client想知道現在時間
#        3.disconnect     client想中斷連線
#  
# 下面註解處 OPTIONAL FUNCTION 部分
# 為處理各種不同cmd需求所產生的FUNCTION
#
# 下面註解處 EVENT FUNCTION 部分
# 當SERVER裝態改變時，會呼叫對應的 EVENT FUNCTION
#
# 變數部分
# server_name        伺服器管理員名字
# clients            儲存所有已連線client的List
# dictCmdFunc List   不同cmd對應其執行的FUNCTION
#
# ==========================        

class SocketServer(socket.socket):
    server_name='Rem'
    server_ip='10.1.1.11'
    server_port=5566
    clients = []
    chat_frame=None
    
    # =====================
    # SERVER INIT
    # =====================    
    def __init__(self):
        socket.socket.__init__(self)
        #To silence- address occupied!!
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((self.server_ip, self.server_port))
        self.listen(5)
    # =====================
    # HERE IS SERVER FUNCTION TO HANDLE CLIENT CONNECTION AND RECEIVE DATA
    # =====================
    def run(self):
        print ("Server started")
        try:
            threading.Thread(target=self.accept_clients).start()
#             初始使用者名單
            self.chat_frame.updateClientList()
        except Exception as ex:
            print (ex)
        finally:
            pass
#             print ("Server closed")
#             for client in self.clients:
#                 client.close()
#             self.close()

    def recieve(self, client):
        while 1:
            data = client.clientsocket.recv(8192)
            #Message Received
            self.onmessage(client, data)
            jdata = json.loads(data)

            recv_cmd = jdata['cmd']
            
            if recv_cmd == 'disconnect':
                break
            else:                
                #Start thread 
                threading.Thread(target=self.dictCmdFunc[recv_cmd],args=(self,client,jdata,)).start()

        self.disconnect(client)
    
    def accept_clients(self):
        while 1:
            print("waiting for Client")
            (clientsocket, address) = self.accept()
            
            new_client = ClientData(clientsocket)
            #Adding client to clients list
            self.clients.append(new_client)
            #Client Connected
            self.onopen(clientsocket)
            #Start listening
            threading.Thread(target=self.recieve,args=(new_client,)).start()
            
    def serverSay(self,string):
        msg =  {'cmd':'say','name':self.server_name, 'data':string}
        jmsg=json.dumps(msg)
        self.sendAll(jmsg)

    # =====================
    # HERE IS OPTIONAL FUNCTION TO HANDLE CLIENT CMD
    # =====================
    
    def sendTime(self, client,jdata):
        import locale
        locale.setlocale(locale.LC_CTYPE, 'chinese')
        dict_hour={0:'半夜12點',1:'半夜1點',2:'半夜2點',3:'半夜3點',4:'半夜4點',5:'凌晨5點',6:'凌晨6點',7:'早上7點',
        8:'早上8點',9:'早上9點',10:'早上10點',11:'中午11點',12:'中午12點',13:'中午1點',14:'下午2點',15:'下午3點',
        16:'下午4點',17:'下午5點',18:'晚上6點',19:'晚上7點',20:'晚上8點',21:'晚上9點',22:'晚上10點',23:'晚上11點',}
        year, month, day, hour, minute,second = time.strftime("%Y,%m,%d,%H,%M,%S").split(',')

        time_str="現在是"+dict_hour[int(hour)]+"%s分%s秒呦" %(minute,second,)
        msg = {'cmd':'say','name':self.server_name, 'data':time_str}
        jmsg = json.dumps(msg)
        client.clientsocket.send(str.encode(jmsg))
    
    def greed(self,client,jdata):
        msg = {'cmd':'greed','name':self.server_name, 'data':'wtf'}
        jmsg = json.dumps(msg)
        client.send(str.encode(jmsg))
    
    def someoneSay(self,client,jdata):
        client_name=jdata['name']
        client_msg=jdata['data']
        msg =  {'cmd':'say','name':client_name, 'data':client_msg}
        jmsg=json.dumps(msg)
        self.sendAll(jmsg)
        self.chat_frame.addMsg(client_name,client_msg)
        
    def updateClientName(self,client,jdata):
        client.name = jdata['name']
        self.chat_frame.updateClientList();
        
    def sendAll(self,string):
        for client in self.clients:
            try :
                client.clientsocket.send(str.encode(string));
            except Exception as ex:
                print (ex)
                self.disconnect(client)
            finally:
                pass
    def disconnect(self,client):
        #Removing client from clients list
        self.clients.remove(client)
        #Client Disconnected and send accept to client
        msg = {'cmd':'disconnect accept','name':self.server_name, 'data':'bye'}
        jmsg = json.dumps(msg)
        client.clientsocket.send(str.encode(jmsg))
        self.onclose(client)
        #Closing connection with client
        client.clientsocket.close()   
        
    dictCmdFunc= {'what time':sendTime,
         'my name is':updateClientName,
         'say':someoneSay}

    # ===================
    # SOME EVENT FUNCTION
    # ===================
    def onopen(self, client):
        print ("Client Connected \n",client)

    def onmessage(self, client, message):
        print ("Client send message ",message)
        
    def onclose(self, client):
        print ("Client Disconnected")
        
# ==========================
# 以下為UI介面程式碼
#
# wxpython 程式參考網址：https://itw01.com/V323ENQ.html
# ==========================
import wx
import wx.xrc
class RemChatFrame ( wx.Frame ):
    chat_room_server=None
    def __init__(self, parent ,server):
        
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"RemChatServer", pos = wx.DefaultPosition, size = wx.Size( 1200,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL ) 
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        #=========set server======== 
        self.chat_room_server=server
        #==========================   
        
        gbSizer1 = wx.GridBagSizer( 0, 0 )
        gbSizer1.SetFlexibleDirection( wx.BOTH )
        gbSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        gbSizer1.SetEmptyCellSize( wx.Size( 0,0 ) )
        
        self.APP_Title = wx.StaticText( self, wx.ID_ANY, u"聊天室訊息", wx.Point( 0,10 ), wx.Size( 300,50 ), 0|wx.ALIGN_CENTER )
        self.APP_Title.Wrap( -1 )
        self.APP_Title.SetFont( wx.Font( 24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "微軟正黑體" ) )
        
        gbSizer1.Add( self.APP_Title, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"使用者在線名單", wx.DefaultPosition, wx.Size( 300,50 ), 0|wx.ALIGN_CENTER )
        self.m_staticText5.Wrap( -1 )
        self.m_staticText5.SetFont( wx.Font( 24, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "微軟正黑體" ) )
        
        gbSizer1.Add( self.m_staticText5, wx.GBPosition( 0, 2 ), wx.GBSpan( 1, 3 ), wx.ALL, 5 )
        
        self.client_list_box = wx.StaticText( self, wx.ID_ANY, u"",wx.Point( 300,80 ), wx.Size( 300,300 ), 0|wx.VSCROLL )
        self.client_list_box.Wrap( -1 )
        self.client_list_box.SetBackgroundColour( wx.Colour( 104, 208, 167 ) )
        
        gbSizer1.Add( self.client_list_box, wx.GBPosition( 1, 2 ), wx.GBSpan( 2, 3 ), wx.ALL, 5 )
        
        self.ctrl_servername = wx.TextCtrl( self, wx.ID_ANY,"Admin", wx.DefaultPosition, wx.Size( 100,20 ), 0|wx.TE_PROCESS_ENTER )
        gbSizer1.Add( self.ctrl_servername, wx.GBPosition( 3, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.btn_runserver = wx.BitmapButton( self, wx.ID_ANY,wx.Bitmap("icon_start.jpg"),  wx.DefaultPosition, wx.Size( 60,20 ), 0 )
        gbSizer1.Add( self.btn_runserver, wx.GBPosition( 4, 4 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY,"5566", wx.DefaultPosition,wx.Size( 100,20 ), 0 )
        gbSizer1.Add( self.m_textCtrl3, wx.GBPosition( 4, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.txt_serverename = wx.StaticText( self, wx.ID_ANY, u"管理員名字", wx.DefaultPosition, wx.Size( 100,20 ), 0|wx.ALIGN_CENTER )
        self.txt_serverename.Wrap( -1 )
        gbSizer1.Add( self.txt_serverename, wx.GBPosition( 3, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.txt_serverport = wx.StaticText( self, wx.ID_ANY, u"伺服器Port", wx.DefaultPosition, wx.Size( 100,20 ), 0|wx.ALIGN_CENTER )
        self.txt_serverport.Wrap( -1 )
        gbSizer1.Add( self.txt_serverport, wx.GBPosition( 4, 2 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.msg_box = wx.StaticText( self, wx.ID_ANY, u"", wx.Point( 0,80 ), wx.Size( 300,400 ), 0|wx.VSCROLL|wx.ALL)
        self.msg_box.Wrap( -1 )
        self.msg_box.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )
        self.msg_box.SetBackgroundColour( wx.Colour( 174, 215, 225 ) )
        
        gbSizer1.Add( self.msg_box, wx.GBPosition( 1, 0 ), wx.GBSpan( 4, 2 ), wx.ALL, 5 )
        
        self.InputBox = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 230,60 ), 0 )
        gbSizer1.Add( self.InputBox, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        self.btn_SendMSG = wx.BitmapButton( self, wx.ID_ANY,wx.Bitmap("icon_send.jpg", wx.BITMAP_TYPE_ANY), wx.DefaultPosition, wx.Size( 60,60 ), wx.BU_AUTODRAW )
        gbSizer1.Add( self.btn_SendMSG, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"功能:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        bSizer3.Add( self.m_staticText9, 0, wx.ALL, 5 )
        
        self.m_bpButton11 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 60,60 ), wx.BU_AUTODRAW )
        bSizer3.Add( self.m_bpButton11, 0, wx.ALL, 5 )
        
        self.m_bpButton12 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 60,60 ), wx.BU_AUTODRAW )
        bSizer3.Add( self.m_bpButton12, 0, wx.ALL, 5 )
        
        self.m_bpButton13 = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 60,60 ), wx.BU_AUTODRAW )
        bSizer3.Add( self.m_bpButton13, 0, wx.ALL, 5 )
        
        
        gbSizer1.Add( bSizer3, wx.GBPosition( 5, 2 ), wx.GBSpan( 1, 3 ), wx.EXPAND, 5 )
        
        
        self.SetSizer( gbSizer1 )
        self.Layout()
        
        self.Centre( wx.BOTH )
        self.Show()
        
        # Connect Events
        self.btn_runserver.Bind( wx.EVT_BUTTON, self.runServer )
        self.btn_SendMSG.Bind( wx.EVT_BUTTON, self.sendMsg )
        self.ctrl_servername.Bind(wx.EVT_TEXT_ENTER, self.setServerName)  
    
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def runServer( self, event ):
        self.chat_room_server.run()
    
    def sendMsg( self, event ):
        # 傳送訊息 
        msg = str(self.InputBox.GetLineText(0)).strip() 
        if msg != '': 
            self.chat_room_server.serverSay(msg)
            self.addMsg(self.chat_room_server.server_name,msg)
        self.InputBox.Clear()
        
    def addMsg(self,name,msg):
        new_msg =self.msg_box.GetLabel()+name+"說:"+msg+'\n'
        self.msg_box.SetLabel(new_msg)
    
    
    def updateClientList(self):
        cli_string=""
        for client in self.chat_room_server.clients:
            cli_string=cli_string+client.name+'\n'
        if cli_string=="":
            cli_string="沒有使用者連線"
        self.client_list_box.SetLabel(cli_string)
        print('update')
    
    def setServerName(self,event):
        print('update sever name')
        self.chat_room_server.server_name=self.ctrl_servername.GetValue()
    
    
    

# ==========================
# 以下為主程式碼
# ==========================
def main():
#   執行聊天室SERVER TCP
    server = SocketServer()
    
#   開啟UI畫面
    app = wx.App()
    rem_chat_frame=RemChatFrame(parent=None,server=server)
    server.chat_frame=rem_chat_frame
    app.MainLoop() 

if __name__ == "__main__":
    main()