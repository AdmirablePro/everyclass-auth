import time

from PIL import Image
from pytesseract import pytesseract
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException

from everyclass.auth import logger
from everyclass.auth.messages import Message


def simulate_login_without_captcha(username: str, password: str):
    """
    浏览器模拟登陆,且不需要使用验证码读取，优先使用，更加快捷
    :param username: str
    :param password: str
    :return:
    """

    # 创建chrome参数对象
    options = webdriver.ChromeOptions()
    # 把chrome设置成无界面模式
    options.add_argument('headless')
    options.add_argument("--no-sandbox")
    # 创建chrome无界面对象
    driver = webdriver.Chrome(chrome_options=options)
    url = "http://csujwc.its.csu.edu.cn/jsxsd/view/xskb/queryglkb.jsp#"
    driver.get(url)

    identifying_time = 0
    while identifying_time < 5:
        identifying_time = identifying_time + 1

        try:
            name_input = driver.find_element_by_id("userAccount")  # 找到用户名的框框
            pass_input = driver.find_element_by_id('userPassword')  # 找到输入密码的框框
            name_input.clear()
            name_input.send_keys(username)  # 填写用户名
            time.sleep(0.2)
            pass_input.clear()
            pass_input.send_keys(password)  # 填写密码
            time.sleep(0.3)

            login_button = driver.find_element_by_id('btnSubmit')  # 找到登录按钮
            login_button.click()  # 点击登录
        except Exception as e:
            logger.warning("{} when simulating login as {}".format(repr(e), username))
            return False, Message.INTERNAL_ERROR

        try:
            driver.refresh()
        # 出现alert，一般是用户名或者密码为空或者是其他特殊情况
        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            logger.warning("Alert raised when logging as {}, text is {}".format(username, alert.text))
            return False, Message.INTERNAL_ERROR

        if driver.current_url == 'http://csujwc.its.csu.edu.cn/jsxsd/framework/xsMain.jsp':
            return True, Message.SUCCESS

        # 出现红色提示窗口
        prompt = driver.find_elements_by_css_selector("font[color='red']")
        if len(prompt) > 0:
            # 出现密码错误的提示
            if prompt[0].text == '用户名或密码错误':
                return False, Message.PASSWORD_WRONG
            # 出现其他提示
            else:
                logger.warning("Red prompt raised when logging as {},text is {}".format(username, str(prompt[0].text)))
                return False, Message.INTERNAL_ERROR

    # 验证码识别多次后仍然失败
    logger.warning("Failed too much times for {}".format(username))
    return False, Message.INTERNAL_ERROR


def simulate_login(username: str, password: str):
    """
    浏览器模拟登陆
    :param username: str
    :param password: str
    :return:
    """
    # 创建chrome参数对象
    options = webdriver.ChromeOptions()
    # 把chrome设置成无界面模式
    options.add_argument('headless')
    # 创建chrome无界面对象
    driver = webdriver.Chrome(chrome_options=options)
    url = "http://csujwc.its.csu.edu.cn/"
    driver.get(url)

    name_input = driver.find_element_by_id("userAccount")  # 找到用户名的框框
    pass_input = driver.find_element_by_id('userPassword')  # 找到输入密码的框框
    name_input.clear()
    name_input.send_keys(username)  # 填写用户名
    time.sleep(0.2)
    pass_input.clear()
    pass_input.send_keys(password)  # 填写密码
    time.sleep(0.3)

    identifying_time = 0
    while identifying_time < 10:
        identifying_time = identifying_time + 1

        identifying_input = driver.find_element_by_id('RANDOMCODE')  # 找到验证码输入框
        login_button = driver.find_element_by_id('btnSubmit')  # 找到登录按钮
        identifying_pic = driver.find_element_by_id('SafeCodeImg')  # 找到验证码图片
        # 获取验证码位置
        box = (identifying_pic.rect['x'],
               identifying_pic.rect['y'],
               identifying_pic.rect['x'] + identifying_pic.rect['width'] - 100,
               identifying_pic.rect['y'] + identifying_pic.rect['height'])
        driver.save_screenshot("everyclass/auth/pic/system_screenshot.png")  # 截取屏幕内容，保存到本地
        # 打开截图，获取验证码位置，截取保存验证码
        img1 = Image.open("everyclass/auth/pic/system_screenshot.png")
        identifying_pic = img1.crop(box)
        identifying_pic.save("everyclass/auth/pic/code_screenshot.png")
        # 获取验证码图片，读取验证码
        identifying_code = pytesseract.image_to_string(identifying_pic)
        logger.debug("验证码为：" + identifying_code)
        identifying_input.send_keys(identifying_code)
        login_button.click()  # 点击登录

        # 若验证码判断正确，即不出现验证码错误的提示，就会找不到提示元素，并且跳转到教务系统的主页面，返回true
        try:
            driver.refresh()

        # 出现alert text弹窗
        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            alert.accept()
            logger.warning("In simulated login  Account: %s"
                           "arises alert,alert text is: \"" % username + alert.text + "\"")
            return False, Message.INTERNAL_ERROR

        if driver.current_url == 'http://csujwc.its.csu.edu.cn/jsxsd/framework/xsMain.jsp':
            return True, Message.SUCCESS

        # 出现红色提示
        prompt = driver.find_elements_by_css_selector("font[color='red']")
        if len(prompt) > 0:
            # 出现密码错误的提示
            if prompt[0].text == '该帐号不存在或密码错误,请联系管理员!':
                return False, Message.PASSWORD_WRONG

            # 离奇抽风时会刷新网页，需要重新输入用户名和密码
            if prompt[0] == '用户名或密码为空!':
                name_input = driver.find_element_by_id("userAccount")  # 找到用户名的框框
                pass_input = driver.find_element_by_id('userPassword')  # 找到输入密码的框框
                name_input.clear()
                name_input.send_keys(username)  # 填写用户名
                time.sleep(0.2)
                pass_input.clear()
                pass_input.send_keys(password)  # 填写密码

            # 还有可能弹出验证码无效等等错误提示
            else:
                logger.warning("In simulated login  Account: %s "
                               "arise other prompt,prompt is : \"" % username + str(prompt[0].text) + "\"")
                break

    # 验证码识别多次后仍然失败
    logger.warning("In simulated login  Account: %s identifying too much times")
    return False, Message.INTERNAL_ERROR
