# -*- coding:utf-8 -*-
import urllib
import urllib.request
import re
 
#处理页面标签类
class Tool:
    #去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    #删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    #把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    #将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    #把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    #将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    #将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n    ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        #strip()将前后多余内容删除
        return x.strip()

#百度贴吧爬虫类
class BDTB:
 
    #初始化，传入地址
    def __init__(self, baseurl, filename, floorTag):
        #切除网址
        if "?pn=" in baseurl:
            self.baseURL, self.unURL = baseurl.split("?pn=", 1)
        else:
            self.baseURL = baseurl
        self.tool = Tool()
        #全局file变量，文件写入操作对象
        self.file = None
        #楼层标号，初始为1
        self.floor = 1
        #文件的标题
        if filename == '':
            self.defaultTitle = u"百度贴吧"
        else:
            self.defaultTitle = u"百度贴吧-" + filename
        #是否写入楼分隔符的标记
        self.floorTag = floorTag

    #传入页码，获取该页帖子的代码
    def getPage(self, pageNum):
        try:
            #构建URL
            URL = self.baseURL + "?pn=" + str(pageNum)
            request = urllib.request.Request(URL)
            response = urllib.request.urlopen(request)
            #返回UTF-8格式编码内容
            return response.read().decode('utf-8')
        #无法连接，报错
        except urllib2.URLError as e:
            if hasattr(e, "reason"):
                print(u"连接百度贴吧失败,错误原因", e.reason)
                return None
 
    #获取帖子标题
    def getTitle(self, page):
        #得到标题的正则表达式
        pattern = re.compile('<h[1-6] class="core_title_txt.*?>(.*?)</h[1-6]>', re.S)
        result = re.search(pattern, str(page))
        if result:
            #如果存在，则返回标题
            #print(result.group(1))
            return result.group(1).strip()
        else:
            return None
 
    #获取帖子一共有多少页
    def getPageNum(self, page):
        #获取帖子页数的正则表达式
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, str(page))
        if result:
            return result.group(1).strip()
        else:
            return None

    #获取用户名和ID及其经验值和头衔
    def getUserProfiles(self, page):
        pattern1 =re.compile('<li class=\"d_name\" data-field=.*?[^\d]*(\d*)[^\d]*}{1}', re.S)
        users_id_list = re.findall(pattern1, str(page))
        pattern2 =re.compile('<a data-field=.*?>(.*?)</a>{1}', re.S)
        usersname_list = re.findall(pattern2, str(page))
        pattern3 = re.compile('本吧头衔(.*?)，点击{1}', re.S)
        badge_list = re.findall(pattern3, str(page))
        pattern7 = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}', re.S)
        retime_list = re.findall(pattern7, str(page))
        pattern5 = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        detail_list = re.findall(pattern5, str(page))
        #print(retime_list)

        all_contents = []
        un_contents = []
        detail_contents = []
        produced_list = {}
        for username in usersname_list:
            un = self.tool.replace(username)
            #userprofiles['user_name'] = un
            un_contents.append(un)
        #print(badge_contents)
        for item in detail_list:
            #将文本进行去除标签处理，同时在前后加入换行符
            content = "\n" + self.tool.replace(item) + "\n"
            detail_contents.append(str(content))
        #将ID, 用户名用户资料的多个列表合成字典，再将用户资料字典生成一个新字典
        mid = map(list, zip(users_id_list, un_contents, badge_list, retime_list, detail_contents))
        for item in mid:
            produced_dict = dict(zip(['user_id: ', 'user_name: ', 'user_badge: ', 'user_reply_time: ', 'tieba_content: '], item))
            all_contents.append((produced_dict))
        #print(all_contents)
        return all_contents
        #return produced_list

    #设置爬虫文件标题
    def setFileTitle(self, title):
        #如果标题不是为None，即成功获取到标题
        if (title is not None)and(self.defaultTitle == u"百度贴吧"):
            self.file = open(u"百度贴吧-" + title + ".txt", "w+", encoding='utf-8')
        else:
            self.file = open(self.defaultTitle + ".txt", "w+", encoding='utf-8')
 
    #写入爬取页面内容到文件
    def writeData(self, contents):
        #向文件写入每一楼的信息
        for i in contents:
            if self.floorTag == 'Y':
                #楼之间的分隔符
                floorLine = "\n" + str(self.floor) + u"楼-----------------------------------------------------------------------\n"
                self.file.write(floorLine)
            for (k, v) in i.items():
                self.file.write(''.join((k+v+'\n')))
                #print(k,v)
            self.floor += 1
 
    def start(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)
        #self.getUserProfiles(indexPage)
        if pageNum == None:
            print("URL已失效，请重试")
            return
        try:
            print("该帖子共有" + str(pageNum) + "页")
            for i in range(1, int(pageNum)+1):
                print("正在写入第" + str(i) + "页数据")
                page_cont = self.getPage(i)
                whole = self.getUserProfiles(page_cont)
                self.writeData(whole)
        #出现写入异常
        except IOError as e:
            print("写入异常，原因" + e.message)
        finally:
            self.file.close()
            print("写入任务完成")
 
baseurl = str(input(u"请输入完整的百度贴吧帖子的网址:"))
confname = input("是否为生成的爬虫文件命名？是输入Y，否输入N，由系统自动为其命名\n")
if confname == 'Y':
    filename = input("爬虫文件命名为：百度贴吧-")
else:
    filename = ''
floorTag = input("是否在文件中标记贴吧楼层信息？ 是输入Y，否输入N\n")
bdtb = BDTB(baseurl, filename, floorTag)
bdtb.start()