# -*- coding: UTF-8 -*-

import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def autoMail(sender,receivers,id,pw,file,server):

    # 创建一个带附件的实例
    message = MIMEMultipart()
    # message['From'] = Header("销售部", 'utf-8')#邮件标题
    # message['To'] = Header("总经理", 'utf-8')
    # subject = '201901月报'
    # message['Subject'] = Header(subject, 'utf-8')

    message['From'] = "销售部" # 邮件标题
    message['To'] = "总经理"
    subject = '201901月报'
    message['Subject'] =subject

    # 邮件正文内容
    message.attach(MIMEText('201901月报', 'plain', 'utf-8'))

    # 构造附件1
    att1 = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1.add_header('Content-Disposition', 'attachment', filename=file.split('\\')[-1]) # filename邮件中显示的文件名字
    message.attach(att1)
    #
    # # 构造附件2，传送当前目录下的 runoob.txt 文件
    # att2 = MIMEText(open('d:\\abb.xls', 'rb').read(), 'base64', 'utf-8')
    # att2["Content-Type"] = 'application/octet-stream'
    # att2.add_header('Content-Disposition', 'attachment', filename="201902月报.xls") # filename邮件中显示的文件名字
    # message.attach(att2)

    try:
        smtpObj = smtplib.SMTP(server)
        smtpObj.login(id,pw)
        smtpObj.sendmail(sender, receivers.split('%'), message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':

    autoMail(sys.argv[1], sys.argv[2], sys.argv[1], sys.argv[3], sys.argv[4] ,sys.argv[5])
    # autoMail('xkj2000@163.com','18827266@qq.com|18627472125@163.com' ,"xkj2000@163.com", "hh112233",'d:\\send\\abc.xls',"smtp.163.com")