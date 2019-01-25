from PIL import Image
from PIL import ImageFile
import cv2
import os
import math
import itchat


def get_wx_profiles():
    #扫码登录
    itchat.auto_login()

    #获取好友列表
    friendlist = itchat.get_friends(update=True)

    #列表首位是你自己
    if friendlist[0]["PYQuanPin"]:
        user = friendlist[0]["PYQuanPin"]
    else:
        user = friendlist[0]["NickName"]

    #创建用你微信名字命名的文件夹，存储好友头像
    if not os.path.exists(user):
        os.mkdir(user)

    #先读取你的微信头像，存储为 你的名字.jpg
    self_head = "{}/{}.jpg".format(os.getcwd(),user)
    with open(self_head,'wb') as f:
        head = itchat.get_head_img(friendlist[0]['UserName'])
        f.write(head)

    print("读取本人头像完毕")

    #进入文件夹
    os.chdir(user)
    print("开始读取好友头像...")
    for i in friendlist[1:]:
        try:
            i['head_img'] = itchat.get_head_img(userName=i['UserName'])
            i['head_img_name'] = "%s.jpg" % i['UserName']
        except ConnectionError:
            print('Fail to get %s' % i['UserName'])
        try:
            with open(i['head_img_name'],'wb') as f:
                f.write(i['head_img'])
        except:
            print(i['head_img_name'],"图片下载失败")
    print("读取好友头像完毕")
    return os.getcwd(),self_head

def combine(folder,self_head):
    os.chdir(folder)
    imgList = os.listdir(folder)
    numImages = len(imgList)
    eachLine = int(math.sqrt(numImages)) + 1
    eachSize = 100
    print("好友头像设定为", eachSize, "像素，每行", eachLine, "个好友，合成图为", eachSize * eachLine,"像素的方形图")
    toImage = Image.new('RGB', (eachSize * eachLine, eachSize * eachLine), "#FFFFFF")  # 新建一块画布
    x = 0
    y = 0
    for i in range(eachLine*eachLine):
        try:
            img = Image.open(imgList[i%numImages])  # 打开图片
        except IOError:
            print("第%d位朋友头像可能没有设置头像，稍后用本人头像替代" % i)  # 有些人没设置头像，就会有异常
            img = Image.open(self_head)
        finally:
            img = img.resize((eachSize, eachSize), Image.ANTIALIAS)  # 缩小图片
            toImage.paste(img, (x * eachSize, y * eachSize))  # 拼接图片
            x += 1
        if x == eachLine:
            x = 0
            y += 1

    print("图像拼接完成")

    os.chdir(os.path.pardir)
    os.getcwd()
    print('保存拼接的图片到目录：', os.getcwd())
    toImage.save('all.jpg', quality=100)
    return eachSize * eachLine

def produceImage(file_in, width, height):
    image = Image.open(file_in)
    resized_image = image.resize((width, height), Image.ANTIALIAS)
    resized_image.save("resize.jpg")

if __name__ == '__main__':
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    #扫码登录微信，获取个人头像、好友头像文件夹
    img_folder,self_head = get_wx_profiles()

    # 将好友头像文件夹中图片合成一张方形图
    size = combine(img_folder,self_head)

    file_in = self_head
    produceImage(file_in, size, size)
    print("开始生成新头像...")
    src1 = cv2.imread("resize.jpg")
    src2 = cv2.imread("all.jpg")

    result = cv2.addWeighted(src1,0.7,src2,0.3,0)

    cv2.imwrite("result.jpg",result)
    print("已生成新的头像！")

    # 发给文件助手
    itchat.send_image('result.jpg', 'filehelper')
    print("已将新头像发送至文件传输助手！")
    print('退出登录...')

    #退出登录
    itchat.logout()
