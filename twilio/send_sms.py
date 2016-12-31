from twilio.rest import TwilioRestClient
 
# Your Account Sid and Auth Token from twilio.com/user/account
def sendMessage(text = 'Hi doug'):
    #account_sid = "ACa58007d97976ee52909851aa413f6bce"
    account_sid = "PN9e4e2efe7dc577174e6aebde2b23fa22"
    auth_token  = "42af4129af1ef3de94deb46b9cf11a3f"
    client = TwilioRestClient(account_sid, auth_token)
    
    message = client.messages.create(body=text,
                                     from_="+41798072427", # Replace with your Twilio number
                                     to="+41768192135")    # Replace with your phone number
    print message.sid

if __name__ == "__main__":

    print 'may send message'
