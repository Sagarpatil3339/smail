
from flask import Flask, request, redirect, session
from twilio.twiml.messaging_response import MessagingResponse
from validate_email import validate_email
import smtplib
import os
import time
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app= Flask(__name__)
app.secret_key= os.urandom(24)

#app route to twilio application through URL
@app.route("/twilio", methods= ['GET','POST'])
def sms_reply():

    #response from the user:
    resp = MessagingResponse()
    inbound_message = request.form.get("Body")
    is_valid = validate_email(inbound_message)

    #check for option entered
    if 'option' in session:
        #Option 1: Send Email
        if(inbound_message=='1'or session['option']=='1'):
            session['option']='1'
            #send email code:
            if 'mailid' in session:

                if 'sub' in session:
                    #SMTP server login details
                    fromaddr = "akshayjpatil11@gmail.com"
                    msg = MIMEMultipart()
                    msg['From'] = fromaddr
                    msg['To'] = session['mailid']
                    msg['Subject'] = session['sub']
                    body = inbound_message
                    msg.attach(MIMEText(body, 'plain'))
                    #Conection
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(fromaddr, "Mediaticsoft123")
                    text = msg.as_string()
                    server.sendmail(fromaddr, session['mailid'], text)
                    server.quit()
                    resp.message("YOUR MAIL WAS SENT \n \n"+"EMAIL:"+session['mailid']+"\nSUBJECT:"+session['sub']+"\nBODY:"+inbound_message)
                    session.pop('mailid')
                    session.pop('sub')
                    session.pop('option')
                else:
                    session['sub']= inbound_message
                    resp.message("EMail:"+session['mailid']+"\nSUBJECT:"+session['sub']+"\nEnter BODY:")

            elif is_valid:
                session['mailid']= inbound_message
                resp.message("Email:"+ session['mailid']+"\nEnter SUBJECT:")

            else:
                resp.message("You Have Selected Option 1: \n Please enter a valid email")

        #Option 2: check email
        elif(inbound_message=='2'or session['option']=='2'):
            session['option']='2'
            #check email code:
            ORG_EMAIL   = "akshayjpatil11@gmail.com"
            FROM_PWD    = "***********"
            SMTP_SERVER = "imap.gmail.com"
            SMTP_PORT   = 993

            try:
                print "ok"
                mail = imaplib.IMAP4_SSL(SMTP_SERVER)
                mail.login(ORG_EMAIL,FROM_PWD)
                mail.select('inbox')

                type, data = mail.search(None, 'ALL')
                mail_ids = data[0]

                id_list = mail_ids.split()
                latest_email_id = int(id_list[-1])

                typ, data = mail.fetch(latest_email_id, '(RFC822)' )

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        email_subject = msg['subject']
                        email_from = msg['from']
                        email_body= msg['body']
                        resp.message("FROM:"+ email_from+ "\n SUBJECT:"+ email_subject)
                        session.pop('option')
            except Exception, e:
                print str(e)


        else:
            resp.message("Enter a Valid Option")
    else:
        resp.message("ENTER OPTION:\n 1. Send Email\n 2. Check Email")
        session['option']='0'

    #return response to the user
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
