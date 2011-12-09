#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import ClientCookie
try:
	import simplejson
except:
	import json
	simplejson = json

from StringIO import StringIO
import time
import thread


def getLoginURLDataResponse(url):
	request = urllib2.Request(url)
	request.add_header('Referer', url)
	response = ClientCookie.urlopen(request)
	return response


class mypeople:
	userid = None
	passwd = None
	lastseq = {}
	userlist = {}
	def __init__(self ):
		pass
	
	def startMainLoopThread(self):
		thread.start_new_thread(self.msgloop,())
				

	def daumLogin(self, userid, passwd):
		self.userid = userid
		self.passwd = passwd
		values = {'id':userid,'pw':passwd,'reloginSeq':'0', } 	
		data = urllib.urlencode(values)
		loginurl = 'https://logins.daum.net/accounts/login.do'
		request = urllib2.Request(loginurl, data)
		request.add_header('Referer', 'http://m.mypeople.daum.net/')
		response = ClientCookie.urlopen(request)

	def initUserList(self, channelkey):
		#http://m.mypeople.daum.net/mypeople/mweb/message.do?pkKey=
		if not self.userlist.has_key(channelkey) :
			self.userlist[channelkey] = {}
		url = 'http://m.mypeople.daum.net/mypeople/mweb/message.do?pkKey=%s'%channelkey
		html = getLoginURLDataResponse(url).read()
		idx = html.find('users["')
		while idx != -1 :
			html = html[idx+len('users["'):]
			idx2 = html.find('"')
			key = html[:idx2]
			idx3 = html.find('name:"')
			html = html[idx3+len('name:"'):]
			idx4 = html.find('"')
			name = html[:idx4]
			self.userlist[channelkey][key] = name

			idx = html.find('users["')


	def getLastMsg(self, channel, lastseq):
		if not self.lastseq.has_key(channel) :
			self.lastseq[channel] = 0
		values = {'pkKey':channel,'dummy':time.time()}
		if lastseq > 0:
			values['lastSeq'] = '%d'%lastseq
		data = urllib.urlencode(values)
		action = 'http://m.mypeople.daum.net/mypeople/xmlhttp/getLastMessage.do'
		request = urllib2.Request(action, data)
		request.add_header('Referer', 'http://m.mypeople.daum.net/')
		response = ClientCookie.urlopen(request)

		ret = response.read()[2:-2]
		return self.parseMsg(channel, ret)
		
	def parseMsg(self, channel, raw):
		try:
			data = simplejson.load(StringIO(raw))
		except:
			return []
			
		for userinfo in data['userList'] :
			self.userlist[channel][userinfo['pkKey']] = userinfo['name']

		if len(data['msgList']) > 0:
			self.lastseq[channel] = data['msgList'][0]['msgSeq']

		return data['msgList']


	def msgloop(self):
		counter = 0
		while(1):
			time.sleep(5)
			counter += 1
			for channel in self.lastseq.keys() :
				msgs = []
				try:
					msgs = self.getLastMsg(channel,self.lastseq[channel])
				except:
					print 'connection timeout'
				for msg in msgs:
					self.dispatchMsg(channel,msg)
			if counter > 1440 :
				counter = 0
				self.daumLogin(self.userid, self.passwd)
			
	def dispatchMsg(self, channel, msg):
		if msg['myMsg'] and msg['msg'].startswith('&lt;'):
			return
			
		name =  self.userlist[channel][msg['pkKey']]
		text =  msg['msg'].encode('utf-8')
		self.onReceivedMsg(channel,name, text)

	def onReceivedMsg(self, channel, name, msg):
		pass

	def msgSend(self, channel, msg):
		#http://m.mypeople.daum.net/mypeople/xmlhttp/getPrevMessage.do?
		values = {'pkKey':channel,'dummy':'testsfa','content':msg , 'lastSeq':'%d'%self.lastseq[channel]} 	
		data = urllib.urlencode(values)
		action = 'http://m.mypeople.daum.net/mypeople/xmlhttp/getSendMessage.do'
		request = urllib2.Request(action, data)
		request.add_header('Referer', 'http://m.mypeople.daum.net/')
		response = ClientCookie.urlopen(request)
		ret = response.read()[2:-2]

		ret = response.read()[2:-2]
		data = self.parseMsg(channel, ret)
		for msg in data:
			self.dispatchMsg(channel, msg)
		return data

	def joinRoom(self, channel):
		self.initUserList(channel)
		self.getLastMsg(channel, 0)

	def getRoomList(self):
		url = 'http://m.mypeople.daum.net/mypeople/mweb/top.do'
		html = getLoginURLDataResponse(url).read()
		chunk = '<a class="img" href="message.do?pkKey='
		chunk2 = '<span class="name">'
		idx = html.find(chunk)
		list = []
		while idx != -1:
			html = html[idx+len(chunk):]
			idx2 = html.find('"')
			roomkey = html[:idx2]
			idx2 = html.find(chunk2)
			html = html[idx2+len(chunk2):]
			idx2 = html.find('</span>')
			roomtitle = html[:idx2].strip()
			list.append([roomkey, roomtitle])
			idx = html.find(chunk)
		return list
			



if __name__=='__main__':
	myp = mypeople()
	myp.daumLogin('userid','passwd')
	roomlist = myp.getRoomList()
	for room in roomlist :
		print room[0] , room[1]
    
	myp.joinRoom(roomlist[0][0])
	myp.msgloop()

