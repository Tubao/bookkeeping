class getbklistHandler(BaseHandler):
	def get(self):
		shopid = self.get_argument("shopid")
		mytype = self.get_argument("type")
		term = self.get_argument("term")
		conn,cur = getDBConn()		
		items=[]
		#pdb.set_trace()
		sqlstr = "select distinct content from bookkeeping where type='" + mytype + "' and shopid='" + shopid + "' and content like '%%" + term+ "%%'  order by datadate desc"
		cur.execute(sqlstr)
		rs = cur.fetchall()
		cur.close()
		conn.close()
		for r in rs:
			items.append(r[0])
		
		self.write(json.dumps(items,ensure_ascii=False))
		
		
	def post(self):
		pass	
class newBookkeepingHandler(BaseHandler):
	def get(self):
		shopid = self.get_argument("shopid",default='0')		
		dd = self.get_argument("dd",default=time.strftime('%Y%m%d',time.localtime(time.time())))
		saved = self.get_argument("saved",default='1')
		if shopid == "0":			
			self.write("no shop id specified!")
			return
		logined = True
		shop_token = None
		try:
			shop_token = self.get_secure_cookie("shopid")
		except Exception as ex:
			logined = False
		if shop_token != shopid or not logined:
			self.render("bklogin.html",shopid=shopid,dd=dd)
			return
		conn,cur = getDBConn()
		cur.execute("select id,datadate,type,content,amount,bak from bookkeeping where type='0' and shopid=%s and datadate=%s ",(shopid,dd))
		bklist_payoff = cur.fetchall()
		cur.execute("select id,datadate,type,content,amount,bak from bookkeeping where type='1' and shopid=%s and datadate=%s ",(shopid,dd))
		bklist_income = cur.fetchall()
		cur.close()
		conn.close()
		date_ddate = datetime.datetime.strptime(dd,'%Y%m%d').date()
		predd = (date_ddate-timedelta(1)).strftime("%Y%m%d")
		nextdd = (date_ddate+timedelta(1)).strftime("%Y%m%d")
		self.render('bookkeeping.html',datadate=dd,shopid=shopid,bklist_payoff=bklist_payoff,bklist_income=bklist_income,saved=saved,predd=predd,nextdd=nextdd)
	def post(self):
		try:
			
			shopid = self.get_argument("shopid_txt",default='0')
			dd = self.get_argument("ddate_txt",default='0')
			if shopid=='0' or dd =='0':
				self.write("wrong data!")
				return
			json_payoff = self.get_argument("json_payoff",default='')
			json_income = self.get_argument("json_income",default='')
			
			payoffs = json.loads(json_payoff)
			incomes = json.loads(json_income)
			recs = []
			for payoff in payoffs['data']:
				recs.append([shopid,dd,'0',payoff['content'],payoff['amount'],payoff['bak']])
			for income in incomes['data']:
				recs.append([shopid,dd,'1',income['content'],income['amount'],income['bak']])
			conn,cur = getDBConn()
			cur.execute("delete from bookkeeping where shopid=%s and datadate=%s ",(shopid,dd))
			cur.executemany("insert into bookkeeping(shopid,datadate,type,content,amount,bak) values(%s,%s,%s,%s,%s,%s)",recs)
			conn.commit()
			cur.close()
			conn.close()
			date_ddate = datetime.datetime.strptime(dd,'%Y%m%d').date()
			nextdate = (date_ddate+timedelta(1)).strftime("%Y%m%d")
			nexturl = "/newBookkeeping?shopid=" + shopid + "&dd=" + nextdate
			self.render('msg_jz.html',msg_title='记账',msg_desc="已保存！",msg_url=nexturl)			
		except Exception as e:
			self.render('msg1.html',msg_title='wrong',msg_desc=e,msg_url="")
class bkloginHandler(BaseHandler):
	def get(self):
		pass
	def post(self):
		try:
			shopid = self.get_argument("shopid_txt",default='0')
			dd = self.get_argument("dd_txt",default='0')
			saved = self.get_argument("saved",default='1')
			passwd = self.get_argument("passwd_txt",default='#@!@@@!@')
			if shopid=='0' or dd =='0':
				self.write("wrong data!")
				return
			conn,cur = getDBConn()
			cur.execute("select passwd from bk_user where uid=%s",(shopid,))
			r = cur.fetchone()
			cur.close()
			conn.close()
			url = "/newBookkeeping?shopid=" + shopid + "&dd=" + dd
			if r is None:
				self.render('msg1.html',msg_title='wrong',msg_desc="口令错误".decode('utf-8'),msg_url=url)
				return
			else:
				if r[0] != passwd:
					self.render('msg1.html',msg_title='wrong',msg_desc="口令错误".decode('utf-8'),msg_url=url)
					return
				else:
					self.set_secure_cookie("shopid",shopid)
					self.redirect(url)
		except Exception as e:
			self.render('msg1.html',msg_title='wrong',msg_desc=e,msg_url="")
class getbkinfoHandler(BaseHandler):
	def get(self):
		shopid = self.get_argument("shopid",default='0')
		dd = self.get_argument("dd",default='0')
		if shopid=='0' or dd =='0':
			self.write("wrong data!")
			return
		conn,cur = getDBConn()
		cur.execute("select content,amount,bak from bookkeeping where type='0' and shopid=%s and datadate=%s ",(shopid,dd))
		recs_payoff = cur.fetchall()
		cur.execute("select content,amount,bak from bookkeeping where type='1' and shopid=%s and datadate=%s ",(shopid,dd))
		recs_income = cur.fetchall()
		cur.close()
		conn.close()
		
		payoff_list = []
		for rec in recs_payoff:
			myitem = {}
			myitem['content'] = rec[0]
			myitem['amount'] = rec[1]
			myitem['bak'] = rec[2]
			payoff_list.append(myitem)
			
		income_list = []
		for rec in recs_income:
			myitem = {}
			myitem['content'] = rec[0]
			myitem['amount'] = rec[1]
			myitem['bak'] = rec[2]
			income_list.append(myitem)
		
		retobj = {"payoff":payoff_list,"income":income_list}
		self.write(json.dumps(retobj))
		
	def post(self):
		pass
handlers = [
    
    (r"/newBookkeeping",newBookkeepingHandler),
    (r"/getbklist",getbklistHandler),
    (r"/bklogin",bkloginHandler),
    (r"/getbkinfo",getbkinfoHandler)
]
