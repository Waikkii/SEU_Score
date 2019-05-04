import requests
import re
import cv2
import pytesseract
import multiprocessing
from PIL import Image
import numpy as np
from retrying import retry
from datetime import datetime
req = requests.Session()
global test
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

#@retry
def signin():
    global test
    # 获取图片
    response = req.get('http://xk.urp.seu.edu.cn/studentService/getCheckCode')
    codeImg = response.content
    fn = open('C:\\Users\\OMEN\\Desktop\\jwc\\code.png', 'wb')
    fn.write(codeImg)
    fn.close()
    pic = cv2.imread('C:\\Users\\OMEN\\Desktop\\jwc\\code.png', 1)
    image = consele(pic)
    print('识别的结果：', change_Image_to_text(image))
    code = change_Image_to_text(image)
    data = {
        'password': 'caozheng19971211',
        'userName': '213161205',
        'vercode': code
    }
    req.post('http://xk.urp.seu.edu.cn/studentService/system/login.action', data = data, headers = headers)
    scorehtml = req.get('http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action')
    title = re.findall(r'<title>(.*?)</title>', scorehtml.text)
    print(title[0])
    if title[0] == '东南大学成绩查询':
        print('验证码校验成功！')
        test = 1
    else:
        print('验证码校验失败！')
        signin()
        return
    pattern1 = re.compile(r'>(.*?)</tr>', re.S | re.M)
    pattern2 = re.compile(r'>(.*?)</td>')
    pattern3 = re.compile(r'>(.*?)&nbsp;</td>')
    rowinfo = pattern1.findall(scorehtml.text)
    score = [([0] * 3) for i in range(25)]
    for num in range(2, 20):
        hanglie = pattern2.findall(rowinfo[num])
        shuzi = pattern3.findall(rowinfo[num])
        if hanglie[1] == '17-18-2':
            score[num - 1][0] = hanglie[2]
            score[num - 1][1] = shuzi[1]
            score[num - 1][2] = shuzi[2]
    for ii in range(1, 19):
        if score[ii][0] != 0:
            print(score[ii][0], score[ii][1], score[ii][2])

def change_Image_to_text(img):
    #手动找训练库的位置,
    testdata_dir_config = '--tessdata-dir "D:\\Tesseract-OCR\\tessdata"'
    textCode = pytesseract.image_to_string(img, lang='eng', config=testdata_dir_config)
    # 去掉非法字符，只保留字母数字
    textCode = re.sub("\W", "", textCode)
    return textCode

def convert_Image(img, standard=127.5):
    #灰度转换
    image = img.convert('L')

    #二值化根据阈值 standard , 将所有像素都置为 0(黑色) 或 255(白色), 便于接下来的分割

    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            if pixels[x, y] > standard:
                pixels[x, y] = 255
            else:
                pixels[x, y] = 0
    return image

def getImage(filename):
    img = Image.open(filename)
    # 打印当前图片的模式以及格式
    print('未转化前的: ', img.mode, img.format)
    # 使用系统默认工具打开图片
    # img.show()
    return img

def consele(img):
    gray = cv2.GaussianBlur(img, (3, 3), 0)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    result = img.copy()
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 60, minLineLength=130, maxLineGap=29)
    lines1 = lines[:, 0, :]  # 提取为二维
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    point = [0] * 210
    for x1, y1, x2, y2 in lines1[:]:
        t = (y2 - y1) / (x2 - x1)
        for num in range(x1, x2):
            point[num] = int(round((num - x1) * t) + y1)
            if point[num] != 0 and point[num] < 98:
                if img[(point[num] + 1), num, 0] > 250 or img[(point[num] - 1), num, 0] > 250:
                    cv2.line(result, (num, (point[num] + 2)), (num, (point[num] - 2)), (255, 255, 255), 2)
        point = [0] * 210
    kernel0 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    #eroded0 = cv2.erode(result, kernel)
    dil = cv2.dilate(result, kernel)
    eroded1 = cv2.erode(dil, kernel0)
    '''
    cv2.imshow("gray", gray)
    cv2.imshow("edges", edges)
    cv2.imshow("result", result)
    cv2.imshow("eroded0", eroded0)
    cv2.imshow("dil", dil)
    cv2.imshow("ero", eroded1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    return eroded1

if __name__ == '__main__':
    start = datetime.now()
    #pool = multiprocessing.Pool(processes=4)
    #for i in range(10):
    #    pool.apply_async(signin)
    #pool.close()
    #pool.join()
    signin()
    end = datetime.now()
    print('程序结束，用时',end-start)
