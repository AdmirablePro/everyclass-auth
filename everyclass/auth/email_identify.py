from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

import smtplib

from everyclass.auth.config import get_config

config = get_config()


def send_email(email, token):
    """
    给指定账号发送含有指定token的邮件
    :param email: str,需要发送的邮箱账号
    :param token: str，需要给该邮箱账号发送的token
    """
    # 第三方 SMTP 服务
    mail_host = config.EMAIL['HOST']  # 设置服务器
    mail_user = config.EMAIL['USERNAME']  # 用户名
    mail_pass = config.EMAIL['PASSWORD']  # 口令

    sender = config.EMAIL['sender']
    receivers = email
    # message = MIMEText(token, 'html', 'utf-8')
    message = MIMEMultipart('related')
    message['From'] = _format_address("每课 <verification@mail.everyclass.xyz>")
    message['To'] = _format_address("每课用户 <%s>" % email)
    message['Subject'] = Header('每课@CSU 学生身份验证', charset='utf-8').encode()

    message_alternative = MIMEMultipart('alternative')
    message.attach(message_alternative)

    file = open('everyclass/static/everyclass_email.html', 'r', encoding='utf-8')
    original_text = file.read()
    text = original_text.format(token)
    file.close()

    message_alternative.attach(MIMEText(text, 'html', 'utf-8'))

    # 指定图片为当前目录
    file2 = open('everyclass/static/everyclass_icon.png', 'rb')
    message_image = MIMEImage(file2.read())
    file2.close()

    # 定义图片 ID，在 HTML 文本中引用
    message_image.add_header('Content-ID', '<image1>')
    message.attach(message_image)

    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, config.EMAIL['SMTP_port'])  # SMTP 端口号

    smtpObj.ehlo()
    smtpObj.starttls()

    smtpObj.login(mail_user, mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    smtpObj.quit()


def _format_address(email):
    """邮件地址的格式化"""
    name, address = parseaddr(email)
    return formataddr((Header(name, 'utf-8').encode(), address))
