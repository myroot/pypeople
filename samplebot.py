#!/usr/bin/python
# -*- coding: utf-8 -*-

from mypeople import mypeople

class samplebot(mypeople):
    def __init__(self , userid , passwd):
        self.daumLogin(userid, passwd)
        self.roomlist = self.getRoomList()
        for room in self.roomlist:
            print room[0], room[1]
            self.joinRoom(room[0])

    def onReceivedMsg(self, channel, name, msg):
        print '%s>%s'%(name, msg)
        if not msg.startswith('echo'):
            self.msgSend(channel, 'echo %s'%msg)

if __name__ == '__main__':
    bot = samplebot('userid','password')
    bot.msgloop()