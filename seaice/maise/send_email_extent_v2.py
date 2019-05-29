
def send_email_extent(filename): 
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from datetime import datetime
    
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    username = "arcticsat1004"
    password = "K0nadish123"
    subject = filename+' successfully processed @'+now
    to = "pbjhwang@outlook.com"
    
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to
    msg['Subject'] = subject
    #msg.attach(MIMEText(message))
    
    server = smtplib.SMTP("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username,password)
    server.sendmail(username, to, msg.as_string())
    server.quit()