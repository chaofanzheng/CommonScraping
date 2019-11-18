from bs4 import BeautifulSoup

def check_response(check_list,html):
    bs = BeautifulSoup(self.req.text,'html.parser')
    tag = bs.find("div",attrs = {'role':'status','class':'box-error'})

    try:
        print(tag.text)
    except:
        return True
    else:
        return False
