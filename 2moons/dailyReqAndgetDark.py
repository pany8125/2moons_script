#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests,json,bs4
import io,sys,os,time
import configparser
import re

'''
自动任务说明：
    1.探险前保持主星各个资源包充足，每个20左右为佳 还在原来主星
    2.配置舰队扣除星球位置，探险前保持舰队扣除星球各种舰队数量充足，每种能扣除5次以上为佳
    4.默认从mianID发渡神级送新手资源，发送资源后系统等待3分钟
    5.保证超旗够用
    6.需配置自己有第几个银河的残卷，任务若是配置外的其他银河残卷，直接删除
crontab 1 2,12 * * *
'''
configPath = "/root/2moons"
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

orimainID=config.get('uni6', '原主星ID',fallback="")

aiwoAll=config.get('uni6', '挨沃收集星球',fallback="")

shipLoc=config.get('uni6', '存放舰队星球号',fallback="")
ticketLoc=config.get('uni6', '残卷对应银河号',fallback="")

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
        os.system("pause")
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

#运输资源任务
def missionTrans(cookie,missionStr):
    targetLoc =  missionStr.split("单位")[0].split("资源")[0].split(">")[1][:-3]
    resNum = missionStr.split("单位")[0].split("资源")[1][1:]
    resType = missionStr.split("单位")[0].split("资源")[0].split("运输")[1]
    print("坐标： ", targetLoc)      #坐标
    print("资源数量： ", resNum)                     #资源数量
    print("资源类型： ", resType)          #资源类型
    
    #第一步 选择舰队
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r=requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+mainID,  headers = header, cookies=jar)
    
    fleetStep1 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep1"
    moom=mainLoc.split(":")
    fleetStep1Data = {
        "galaxy": moom[0],#星球坐标
        "system": moom[1],
        "planet": moom[2],
        "type": 1,
        "target_mission": 0,
        "ship235": 1,     #235 渡神级
    }
    responseRes1 = requests.post(fleetStep1, data = fleetStep1Data, headers = header, cookies=jar)
    subLink = bs4.BeautifulSoup(responseRes1.text,"html.parser")
    try:
        token = subLink.select('input')[0].get('value')
    except:
        print("token 获取失败")
        os.sys.exit()
    
    #第二步 选择目的地
    fleetStep2 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep2"
    target_moom=targetLoc.split(":")
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
    responseRes2 = requests.post(fleetStep2, data = fleetStep2Data, headers = header, cookies=jar)

    #第三步 选择任务类型
    resource = [0, 0, 0] #默认金属 晶体 HH都是1
    if resType == "金属":
        resource[0] = int(resNum)
    elif resType == "晶体":
        resource[1] = int(resNum)
    elif resType == "重氢":
        resource[2] = int(resNum)
    fleetStep3 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep3"
    fleetStep3Data = {
        "token":token,
        "mission":3,
        "metal":resource[0],
        "crystal":resource[1],
        "deuterium":resource[2]
    }
    responseRes3 = requests.post(fleetStep3, data = fleetStep3Data, headers = header, cookies=jar)
    try:
        mission = bs4.BeautifulSoup(responseRes3.text,"html.parser")
        missionboday = mission.find("table", { "class" : "table519" })
        missionbodays=missionboday.findAll("tr")
        print(missionbodays)
        print("资源(金属晶体HH)：" + str(resource) + ", 从" + mainLoc + "运往" + targetLoc + ", 用1条渡神级，运输成功!")
    except:
        print("没有舰队，派遣失败")


#自动打包资源
def packageRsc(cookie,missionStr):
    resource = [0, 0, 0] #默认金属 晶体 HH卖的个数都是0
    price = [1, 1, 1] #默认金属 晶体 HH卖的价格都是1
    
    pkgNum = int(missionStr.split("资源包")[1][:1])
    rscPrice = int(missionStr.split("暗物质")[0].split("请以")[1])
    rscType = missionStr.split("资源包")[0][-2:]
    if rscType == "金属":
        resource[0] = pkgNum
        price[0] = rscPrice
    if rscType == "晶体":
        resource[1] = pkgNum
        price[1] = rscPrice
    if rscType == "重氢":
        resource[2] = pkgNum
        price[2] = rscPrice
    
    #切到主星
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=galaxy&cp="+orimainID,  headers = header, cookies=jar)
    
    #处理打包
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=bag",
        "Origin": "http://xnova.cc",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    packageData = {
        "cmd" : "sale",
        "package_metal_bag_tosale":  resource[0],
        "package_metal_bag_price":   price[0],
        "package_crystal_bag_tosale":resource[1],
        "package_crystal_bag_price": price[1],
        "package_deuterium_bag_tosale": resource[2],
        "package_deuterium_bag_price": price[2]
    }
    packageUrl = "http://xnova.cc/2moons1/uni6/game.php?page=bag"
    packageRes = requests.post(packageUrl, data = packageData, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(packageRes.text,"html.parser")
    if "上架成功" in str(soup):
        print("资源",rscType,"以价格",rscPrice,"上架", pkgNum, "个成功!")
    else:
        print("上架失败")

#领取任务
def getMission(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=quests",
        "Origin": "http://xnova.cc",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    missionData = {
        "rank" : "3",
        "operation" : "add"
    }
    missionUrl = "http://xnova.cc/2moons1/uni6/quests.php"

    returnStr = ["0", ""]
    
    missionRes = requests.post(missionUrl, data = missionData, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(missionRes.text,"html.parser")
    missionStr = str(soup)
    if missionStr == "上次交给你的任务还没完成，怎么又来？":
        print(missionStr)
        missionStr = getMissionInfo(cookie)
    if missionStr == "当前任务：帝国需要建造超级旗舰，请去搜集一张超级旗舰许可证交给我。(提示:你的帝国仓库如果有这样物品，直接点击完成任务即可，物品会自动扣除。)":
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["1", missionStr]
        return returnStr
    if "请调遣足够的舰船停放在当前星球" in missionStr:
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["1", missionStr]
        return returnStr
    if "为协助新人发展" in missionStr:
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["2", missionStr]
        return returnStr
    if "为了帮助帝国研究各个银河系详细情况" in missionStr:
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["3", missionStr]
        return returnStr
    if "为繁荣米索不达亚帝国星际市场" in missionStr:
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["4", missionStr]
        return returnStr
    if missionStr == "今日任务次数已全部用完，明日继续。":
        print("-------本次任务：")
        print(missionStr)
        returnStr = ["5", missionStr]
        return returnStr
    return returnStr

#放弃任务
def delMission(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=quests",
        "Origin": "http://xnova.cc",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    missionData = {
        "operation" : "delete"
    }
    missionUrl = "http://xnova.cc/2moons1/uni6/quests.php"
    missionRes = requests.post(missionUrl, data = missionData, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(missionRes.text,"html.parser")
    print(soup)

#点击任务完成
def finishMission(cookie):
    #切到舰队所在星球
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=galaxy&cp="+shipLoc,  headers = header, cookies=jar)
    
    #完成任务
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=quests",
        "Origin": "http://xnova.cc",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    missionData = {
        "operation" : "finish"
    }
    missionUrl = "http://xnova.cc/2moons1/uni6/quests.php"
    missionRes = requests.post(missionUrl, data = missionData, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(missionRes.text,"html.parser")
    if str(soup) == "开什么玩笑，你还没有接受任何委托。":
        print(soup)
        return 0
    if str(soup) == "任务已完成！":
        print(soup)
        return 0
    if str(soup) == "做人要诚信，您的任务并未完成":
        print(soup)
        return 0
    return 1

#查看任务页面，获取任务类型和任务string
def getMissionInfo(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=quests",
        'User-Agent': userAgent,
        'Host': "xnova.cc"
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=quests",  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    missionStr = str(soup.findAll("span",id="questContent")[0].contents)[2:-2]
    print(missionStr)
    return missionStr

#领取暗物质
def getGift(cookie):
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php?page=gift",
        'User-Agent': userAgent,
        'Host': "xnova.cc"
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/getdarkmatter.php",  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    print(soup)

#领取任务奖励
def getMissionGift(cookie):
    #切到舰队所在星球
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=galaxy&cp="+mainID,  headers = header, cookies=jar)
    
    header["Referer"] = "http://xnova.cc/2moons1/uni6/game.php?page=service"
    pageUrl = "http://xnova.cc/2moons1/uni6/game.php?page=service"
    pageData = {
        "_mode": 9,
        "npccreatemoon": "领取俸禄"
    }
    responseRes = requests.post(pageUrl, data = pageData, headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(responseRes.text,"html.parser")
    missionbody = soup.find("table", { "class" : "table519" })
    print(missionbody.findAll("td")[0].contents)

#获取星球物资
def getResource(cookie, loc):
    resource = [1, 1, 1] #默认金属 晶体 HH都是1
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    cp = config.get('loctoid', loc.replace(":","-"),fallback="")
    r = requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+cp,  headers = header, cookies=jar)
    soup = bs4.BeautifulSoup(r.text,"html.parser")
    print(soup.find_all(id="current_metal"))
    print(soup.find_all(id="current_crystal"))
    print(soup.find_all(id="current_deuterium"))
    resource[0] = int(soup.find_all(id="current_metal")[0].contents[0].replace(",",""))
    resource[1] = int(soup.find_all(id="current_crystal")[0].contents[0].replace(",",""))
    resource[2] = int(soup.find_all(id="current_deuterium")[0].contents[0].replace(",","")) - 200000 #减20万HH的燃料
    print(resource)
    return resource


#转移物资
def trans(cookie,src,target,resource,shipNum):
    #第一步 选择舰队
    header = {
        "Referer": "http://xnova.cc/2moons1/uni6/game.php",
        'User-Agent': userAgent,
    }
    jar = getJar(cookie, False)
    cp = config.get('loctoid', src.replace(":","-"),fallback="")
    requests.get("http://xnova.cc/2moons1/uni6/game.php?page=fleetTable&cp="+cp,  headers = header, cookies=jar)
    
    fleetStep1 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep1"
    moom=src.split(":")
    fleetStep1Data = {
        "galaxy": moom[0],#星球坐标
        "system": moom[1],
        "planet": moom[2],
        "type": 1,
        "target_mission": 0,
        "ship217": shipNum,#217 埃沃运输舰
    }
    responseRes1 = requests.post(fleetStep1, data = fleetStep1Data, headers = header, cookies=jar)
    subLink = bs4.BeautifulSoup(responseRes1.text,"html.parser")
    try:
        token = subLink.select('input')[0].get('value')
    except:
        print("token 获取失败")
        os.sys.exit()
    
    #第二步 选择目的地
    fleetStep2 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep2"
    target_moom=target.split(":")

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
    responseRes2 = requests.post(fleetStep2, data = fleetStep2Data, headers = header, cookies=jar)

    #第三步 选择任务类型
    fleetStep3 = "http://xnova.cc/2moons1/uni6/game.php?page=fleetStep3"
    fleetStep3Data = {
        "token":token,
        "mission":3,
        "metal":resource[0],
        "crystal":resource[1],
        "deuterium":resource[2]
    }
    responseRes3 = requests.post(fleetStep3, data = fleetStep3Data, headers = header, cookies=jar)
    try:
        mission = bs4.BeautifulSoup(responseRes3.text,"html.parser")
        missionboday = mission.find("table", { "class" : "table519" })
        missionbodays=missionboday.findAll("tr")
        print(missionbodays)
        print("资源(金属晶体HH)：" + str(resource) + ", 从" + src + "运往" + target + ", 用" + str(shipNum) + "条挨沃，运输成功!")
    except:
        print("没有舰队，派遣失败")


#收集到主星
def collect(cookie):
    for loc in aiwoAll.split(";"):
        print(loc)
        resource = getResource(cookie, loc)
        shipNum = (resource[0] + resource[1] + resource[2]) // 80000000 + 1 #有军官的话挨沃是8kw，向上取整
        trans(cookie,loc,mainLoc,resource,shipNum)

#    任务清单：
#1    当前任务：帝国需要建造超级旗舰，请去搜集一张超级旗舰许可证交给我。(提示:你的帝国仓库如果有这样物品，直接点击完成任务即可，物品会自动扣除。)
#2    当前任务：为协助新人发展，请向位于 [ ', <a href="?page=galaxy&amp;galaxy=1&amp;system=381">1:381:5</a>, ' ] 的新人行星运输晶体资源 4300156单位。注意：运输的资源量不能多也不能少,并且无法累计计算，必须一次性完成！
#3    当前任务：为了帮助帝国研究各个银河系详细情况，请去搜集一张第3银河系概况图残卷交给我。你的帝国仓库如果有这样物品，直接点击完成任务即可，物品会自动扣除。
#1    当前任务：帝国现在急需1000艘战列舰，请调遣足够的舰船停放在当前星球。(提示:你的当前星球如果有这样物品，直接点击完成任务即可，物品会自动扣除。)
#!    当前任务：帝国现在急需500艘战列巡洋舰，请调遣足够的舰船停放在当前星球。(提示:你的当前星球如果有这样物品，直接点击完成任务即可，物品会自动扣除。)
#4    当前任务：为繁荣米索不达亚帝国星际市场，请以538暗物质的单价向星际市场挂单重氢资源包1个。
#1    当前任务：帝国现在急需500艘毁灭者战舰，请调遣足够的舰船停放在当前星球。(提示:你的当前星球如果有这样物品，直接点击完成任务即可，物品会自动扣除。)
#4    当前任务：为繁荣米索不达亚帝国星际市场，请以518暗物质的单价向星际市场挂单金属资源包5个。
#1    当前任务：帝国现在急需2000艘巡洋舰，请调遣足够的舰船停放在当前星球。(提示:你的当前星球如果有这样物品，直接点击完成任务即可，物品会自动扣除。)
#4    当前任务：为繁荣米索不达亚帝国星际市场，请以536暗物质的单价向星际市场挂单重氢资源包5个。
#5    今日任务次数已全部用完，明日继续。
if __name__ == "__main__":
#做任务
    print("------------------做任务开始------------------")
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    cookie = getCookie()
    while finishMission(cookie) == 0:
        returnStr = getMission(cookie)
        if returnStr[0] == "0":
            print("还不支持这种任务!")
            break
        elif returnStr[0] == "1":
            continue
        elif returnStr[0] == "2":   #运输任务
            missionTrans(cookie,returnStr[1])
            time.sleep(180)
            continue
        elif returnStr[0] == "3":   #银河残卷
            if int(returnStr[1].split("一张第")[1][0]) == int(ticketLoc):
                continue
            else:
                delMission(cookie)
                continue
        elif returnStr[0] == "4":   #挂单资源包
            packageRsc(cookie,returnStr[1])
            continue
        elif returnStr[0] == "5":   #任务已用完
            break
        else:
            break
    
    
    #领取任务奖励
    print("------------------领取任务奖励开始------------------")
    getMissionGift(cookie)
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    
    #领取暗物质
    print("------------------领取暗物质开始------------------")
    getGift(cookie)
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    
    #收集星球资源
    print("------------------收集星球资源开始------------------")
    collect(cookie)
    print(time.strftime('%Y.%m.%d %H:%M:%S',time.localtime(time.time())))
    print("------------------本次任务结束------------------")
