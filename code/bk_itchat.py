#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 15:29:19 2018

@author: xdw
"""
#http://itchat.readthedocs.io/zh/latest/api/
#https://www.jianshu.com/p/fa4f41dc8a51
##sudo pip install itchat

import itchat

#friends = itchat.get_friends(update=True)[1:]
#myfriend = itchat.search_friends(name='sophia')
#print myfriend['NickName']
#chatrooms = itchat.get_chatrooms(update=True)
#myroom = itchat.search_chatrooms(name='somegroupname')
#print myroom['NickName']
#
#itchat.send(msg='hello',toUserName=myfriend['UserName'])
#itchat.send(msg='hello',toUserName=myroom['UserName'])

# 带对象参数注册，对应消息对象将调用该方法
#@itchat.msg_register(TEXT, isFriendChat=True, isGroupChat=True, isMpChat=True)
#def text_reply(msg):
#    msg.user.send('%s: %s' % (msg.type, msg.text))
#

import urllib2
import json
import re
@itchat.msg_register(itchat.content.TEXT,isGroupChat=True)
def send_bkdata(msg):	
	if msg['FromUserName'] != uname and msg['ToUserName'] != uname :
		return
#    if msg['Text'] == u'test':
#        itchat.send('going to show bookkeeping data', uname)
	
	patten = re.compile("^mmj(\d{8})$")
	if patten.match(msg['Text']):
		dd = patten.match(msg['Text']).group(1)   		
		url = r'http://tensor.applinzi.com/getbkinfo?shopid=mmj&dd=' + dd
		f = urllib2.urlopen(url) 
		data = f.read() 
		bk = json.loads(data)		
		payoff_amount = 0
		income_amount = 0
		ret = '日期：'.decode("utf-8") + dd + ' [支出]：'.decode("utf-8")
		for i,payoff_item in enumerate(bk['payoff']):  
			payoff_amount = payoff_amount + payoff_item['amount'];
			ret = ret + str(i+1) + '.' + payoff_item['content'] + " "         
			ret	= ret + str(payoff_item['amount']) + "元 ".decode("utf-8")        
			ret = ret + payoff_item['bak'] + "; "
		ret = ret + ' 支出合计：'.decode("utf-8")  + str(payoff_amount) + '元。 '.decode("utf-8")
		ret = ret + ' [收入]：'.decode("utf-8")
		for i,income_item in enumerate(bk['income']):
			income_amount = income_amount + income_item['amount']
			ret = ret + str(i+1) + '.' + income_item['content']+ " " 
			ret	= ret + str(income_item['amount']) + "元 ".decode("utf-8")
			ret = ret + income_item['bak'] + "; "
		ret = ret + ' 收入合计：'.decode("utf-8")  + str(income_amount) + '元。 '.decode("utf-8")
		print ret
		itchat.send(ret,uname)
	
itchat.login(enableCmdQR=2)
#itchat.auto_login(True)
room = itchat.search_chatrooms(name='报帐群'.decode("utf-8"))
uname = room[0]['UserName']
print uname
itchat.run()
