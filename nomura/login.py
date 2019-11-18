import requests
from getpass import getpass

class NomuraHometradeAccess():

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36)"}

    def  __init__(self):
        #初期化
        self.loginType = ''
        self.btnCd = input('取引店コード（半角）:')
        self.kuzNo = input('口座番号（半角）:')
        self.gnziLoginPswd = getpass ('ログインパスワード（半角）')
        self.loginTuskLoginId = self.btnCd + self.kuzNo
        self.data = {'loginType':self.loginType,'btnCd':self.btnCd,'kuzNo':self.kuzNo,'gnziLoginPswd':self.gnziLoginPswd,'loginTuskLoginId':self.loginTuskLoginId}
        self.ses = requests.Session()

    def login(self,url = 'https://hometrade.nomura.co.jp/web/rmfCmnCauSysLgiAction.do'):

        #cookiesを取得する（野村證券の仕様）
        # self.cookies = requests.request('get','https://hometrade.nomura.co.jp/web/rmfIndexWebAction.do',headers  = self.headers).cookies
        self.ses.request('get','https://hometrade.nomura.co.jp/web/rmfIndexWebAction.do',headers  = self.headers)
        #method,url,post_data,headers,cookies
        self.req = self.ses.request('post',url,data = self.data,headers = self.headers)
        #返却値確認
        self.req.raise_for_status()
        # check_response(self.req.text)

        #エンコードを変更
        self.req.encoding = self.req.apparent_encoding
        #cookiesを保存
        self.cookies = self.req.cookies

    def request(self,method,url):
        #自由アクセス
        return self.ses.request(method,url,headers = self.headers)

    def get_text(self):
        return self.req.text
