#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests,json,bs4
import io,sys,os,time
import configparser
import re

'''
探险功能:
    1.配置文件中配置哎沃个数探险，一次派4队
    2.配置挖矿船个数挖矿
    3.配置暗月个数探险
    4.自动收渣
    5.配置是否自动删除三体星球
    6.自动重置探险(未完成)
crontab 4,9,14,19,24,29,34,39,44,49,54,59 * * * *
'''

configPath = "/root/2moons_gailun"
#configPath ="C:\\Users\\Scott\\Desktop\\uni6 搬物资\\server"

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
header = {
    "Referer": "http://xnova.cc/2moons1/uni6/index.php?code=2",
    'User-Agent': userAgent,
}
config = configparser.ConfigParser(strict=False)
config.read_file(open(os.path.join(configPath, "config.ini"), encoding='UTF-8'))
account=config.get('uni6', '账号',fallback="")
passw=config.get('uni6', '密码',fallback="")

mainLoc=config.get('uni6', 'all星',fallback="")
mainID=config.get('uni6', 'allID',fallback="")

isDelSanti=config.get('uni6', '删除三体星球',fallback="")

cookiePath=os.path.join(configPath, "cookie")

def login(account, password):
    # 登录
    postUrl = "http://xnova.cc/2moons1/uni6/index.php?page=login"
    postData = {
        "uni":6,
        "username": account,
        "password": password,
    }
    loginx = requests.Session()
    responseRes = loginx.post(postUrl, data = postData, headers = header, cookies=getJar(None, True))
    # 无论是否登录成功，状态码一般都是 statusCode = 200
    print("statusCode = ",responseRes.status_code)
    cookies = requests.utils.dict_from_cookiejar(loginx.cookies)
    try:
        cookie=cookies["2Moons"]
    except:
        print("请检查账号密码是否正确")
        print("登陆失败！")
        os.sys.exit()
    print("登录成功！")
    return cookie

def getCookie():
    # 登录
    cookie = ''
#    for i in range(2):
    if os.path.isfile(cookiePath):
        with open(cookiePath, 'r') as f:
            cookie=f.read().strip()
    if not checkLogin(cookie):
        cookie = login(account, passw)
        with open(cookiePath, 'w') as f:
            f.write(cookie)
    return cookie

def getJar(cookie,isLogin):
    jar = requests.cookies.RequestsCookieJar()
    jar.set('lang', 'cn',domain='xnova.cc')
    if not isLogin:
        jar.set('2Moons', cookie,domain='xnova.cc')
    return jar

def checkLogin(cookie):
    #测试cookie
    r = requests.get('http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp='+mainID, headers = header, cookies=getJar(cookie, False))
    subLink = bs4.BeautifulSoup(r.text,"html.parser")

    try:
        print("当前位置："+subLink.select('input')[0].get('value')+","+subLink.select('input')[1].get('value')+","+subLink.select('input')[2].get('value'))
    except:
        print("登录已失效,重新登陆中")
        return False
    print("星球："+subLink.find(selected="selected").get('value'))
    print("当前已登录！")
    return True

#挖矿暗月探险
def mission(cookie,fleetType):

    aiwoNum=config.get('uni6', '探险挨沃数',fallback="")
    anyueNum=config.get('uni6', '暗月科考数',fallback="")
    wakuangNum=config.get('uni6', '挖矿船数',fallback="")
    #第一步 选择舰队
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    if fleetType == 19:
        wakuangID=config.get('uni6', '挖矿出发球ID',fallback="")
        requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+wakuangID,  headers = header, cookies=jar)
    else:
        requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+mainID,  headers = header, cookies=jar)
    
    fleetStep1 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep1"
    if fleetType == 19:
        wakuang=config.get('uni6', '挖矿出发球',fallback="")
        moom=wakuang.split(":")
    else:
        moom=mainLoc.split(":")

    fleetStep1Data = {
        "galaxy": moom[0],#星球坐标
        "system": moom[1],
        "planet": moom[2],
        "type": 1,
        "target_mission": 0,
#        "ship217": 1830,     #217 埃沃运输舰
#        "ship220": 8,        #220 暗月科考船
#        "ship227": 20,       #227 挖矿船
    }
    if fleetType == 15:
        fleetStep1Data["ship217"] = aiwoNum
    elif fleetType == 11:
        fleetStep1Data["ship220"] = anyueNum
    elif fleetType == 19:
        fleetStep1Data["ship227"] = wakuangNum
    else:
        print("错误类型")
        os.sys.exit()
    responseRes1 = requests.post(fleetStep1, data = fleetStep1Data, headers = header, cookies=jar)
    subLink = bs4.BeautifulSoup(responseRes1.text,"html.parser")
    try:
        token = subLink.select('input')[0].get('value')
    except:
        print("token 获取失败")
        os.sys.exit()
    
    #第二步 选择目的地
    fleetStep2 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep2"    
    if fleetType == 15:
        target_moom = config.get('uni6', '探险球',fallback="")
    elif fleetType == 11:
        target_moom = config.get('uni6', 'all星',fallback="")
    elif fleetType == 19:
        target_moom = config.get('uni6', '挖矿球',fallback="")
    target_moom=target_moom.split(":")
    fleetStep2Data = {
        "token":token,
        "fleet_group":0,
        "galaxy": target_moom[0],#星球坐标 到达
        "system": target_moom[1],
        "planet": target_moom[2],
        "target_mission": 0,
        "type": 1,#任务类型
        "speed": 10,#速度
    }
    if fleetType == 11:
        fleetStep2Data["type"]=3 #月球
    responseRes2 = requests.post(fleetStep2, data = fleetStep2Data, headers = header, cookies=jar)

    #第三步 选择任务类型
    fleetStep3 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep3"
    if fleetType == 15:
        fleetStep3Data = {
        "token":token,
        "mission":fleetType,
        "staytime":1
        }
    elif fleetType == 11:
        fleetStep3Data = {
        "token":token,
        "mission":fleetType,
        "staytime":1
        }
    elif fleetType == 19:
        fleetStep3Data = {
        "token":token,
        "mission":fleetType,
        "staytime":4
        }
    responseRes3 = requests.post(fleetStep3, data = fleetStep3Data, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(responseRes3.text,"html.parser")
#    print(soup)
    if fleetType == 15:
        try:
            print(soup.find_all("div", id="content")[0].find_all(class_="success")[0].contents[0]) #探险成功才不报错
            print("探险已派遣!")
        except:    
            print(soup.find_all("div", id="content")[0].find_all("td")[0].contents[0]) #探险失败时 可用舰队不足/探险次数已用尽
    elif fleetType == 11:
        try:
            print(soup.find_all("div", id="content")[0].find_all(class_="success")[0].contents[0]) #探险成功才不报错
            print("暗月科考已派遣!")
        except:    
            print(soup.find_all("div", id="content")[0].find_all("td")[0].contents[0]) #科考失败时 没有足够的飞船/不能启动更多科考
    elif fleetType == 19:
        try:
            print(soup.find_all("div", id="content")[0].find_all(class_="success")[0].contents[0]) #探险成功才不报错
            print("挖矿已派遣!")
        except: 
            print(soup.find_all("div", id="content")[0].find_all("td")[0].contents[0]) #采矿失败时 可用舰队不足
    
#删除三体星球
def delSanti(cookie, isDelSanti):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=galaxy",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=galaxy&cp="+mainID,  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    try:
        print(soup.findAll("a",attrs={"href":re.compile(r"removeplanet")})[0].find_all("img")[0]["title"])
        santiLoc = soup.findAll("a",attrs={"href":re.compile(r"removeplanet")})[0]["href"].split("(")[1][:-1].split(",")
        print("三体坐标为：" , santiLoc)
        if int(isDelSanti) != 1:
            print("本次选择不删除三体")
            return
        santi="http://xnova.cc/2moons1/uni6/removeplanet.php"
        santiData = {
            "id":santiLoc[0],
            "uid":santiLoc[1],
        }
        santiRes = requests.post(santi, data = santiData, headers = header, cookies=jar)
        santisoup = bs4.BeautifulSoup(santiRes.text,"html.parser")
        print(santisoup)
    except:
        print("当前无三体，无需删除!")

#收渣
def recycleRes(cookie,targetId):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+targetId,  headers = header, cookies=jar)
    responseRes1 = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetAjax&ajax=1&mission=8&planetID=" + targetId,  headers = header, cookies=jar)
#    print(bs4.BeautifulSoup(responseRes1.text,"html.parser"))
#    TODO:校验回收成功
    print("已发送飞船收渣！")

#查看是否有渣 
def checkRes(cookie,targetId):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=galaxy&cp="+targetId,  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    remainsList = soup.find_all("a", class_="tooltip_sticky", attrs={"data-tooltip-content": re.compile("doit\(8\,")})
    for remains in remainsList:
        toolSoup = bs4.BeautifulSoup(remains["data-tooltip-content"],"html.parser")
        res = toolSoup.find_all("a")
        scriptStr = "doit(8, " + mainID
        print(scriptStr)
        for resOne in res:
            if "回收" in resOne.contents and scriptStr in str(resOne):
                print("当前主星有渣，准备回收！")
                return True
    print("当前主星没渣，无需回收！")
    return False

#是否需要重置探险
def checkReset(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+mainID,  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    infoStr = soup.find_all("th", colspan="9")[1].contents[0].split("探险次数")[1]
    print(infoStr)
    infoList = infoStr[1:].split("/")
    print(infoList)
    curTime = int(infoList[0].lstrip().rstrip())
    allTime = int(infoList[1][1:3])
    resetTime = int(infoList[1][-2:-1])
    print("curTime:", infoList[0].lstrip().rstrip(), ", allTime:", infoList[1][1:3], ", resetTime:", infoList[1][-2:-1])
    if resetTime <= 1 and curTime == allTime:
        return True
    else:
        return False

#重置探险
def resetTime(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=fleetTable",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/resetExpeditionTimes.php",  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    print(soup)

if __name__ == "__main__":
    print("------------------本次任务开始------------------")
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    cookie = getCookie()

#重置探险
    print("------------------重置探险开始------------------")
    if checkReset(cookie):
        resetTime(cookie)
#删除三体星球
    print("------------------删除三体星球开始------------------")
    delSanti(cookie,isDelSanti)
#收渣
    print("------------------收渣开始------------------")
    if checkRes(cookie, mainID):
        recycleRes(cookie,mainID)
#11 暗月科考船
    print("------------------暗月科考开始------------------")
    mission(cookie,11)
#15 探险
    print("------------------探险开始------------------")
    for i in range(4):
        print("===================第" + str(i+1) + "次探险开始===================")
        mission(cookie,15)
#19 挖矿
    print("------------------挖矿开始------------------")
    mission(cookie,19)
    
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    print("------------------本次任务结束------------------")
