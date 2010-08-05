from urllib import urlencode
import httplib2
import datetime



# full GET URL example:
# https://g1m.me/send_sms?messageText=hello&deviceAddress=919880700000&password=847yhhgfj
# should return "OK"

GATEWAY_URL = "https://g1m.me/send_sms"
GATEWAY_URL_DIRECT = "https://extend.ref1.lightsurf.net/acceptar/sendmsg.jsp"
# GATEWAY_URL = "http://127.0.0.1:30824/send_sms"

OVI_NUM_FROM = "919900095039"

TEST_NUM = "919880703078" #91-98807-03078
TEST_NUM = "919880700000"

def send_sms(deviceAddress, messageText, _from):
    """ Send an SMS to the given deviceAddress phone.
    Considering we send only messages to India, we add the India prefix here.
    
    deviceAddress: cellphone number in India only
    messageText: content of SMS
    _from: cellphone number for the 'from' phone
    """
    # Fix the number if necessary
    if len(deviceAddress)==10:
        deviceAddress = "91"+deviceAddress # India country code
    elif deviceAddress[0:4]=="0091":
        deviceAddress = deviceAddress[2:]

    data = {'deviceAddress':deviceAddress,
            'messageText':  messageText,
            'fromAddress':  _from and _from or OVI_NUM_FROM,
            'password':     "847yhhgfj",
            }
    http = httplib2.Http()
    resp, content = http.request(GATEWAY_URL + "?" + urlencode(data), "GET")
    if content and content[0:2]=="OK":
        return True
    return False



# def send_sms(deviceAddress, messageText, _from):
def send_sms_direct_to_gateway(deviceAddress, messageText, _from):
    data = {'deviceAddress':deviceAddress,
            'messageText':  messageText,
            'from':         _from and _from or OVI_NUM_FROM,
            'loginName':    "nokiaovi",
            'password':     "Nok1@0v!",
            }

    http = httplib2.Http()
    resp, content = http.request(GATEWAY_URL_DIRECT, "POST", urlencode(data))
    print "SMS TO GATEWAY HTTP", resp, content
    print "SMS TO GATEWAY ", data
    return True


if __name__=="__main__":
    TEST_NUM = "919880703078" #91-98807-03078 Verisign guy
    # TEST_NUM = "919586550654" # NEIL
    TEST_NUM = "919880700000" # FAKE

    send_sms(TEST_NUM,"Test from Agathe/Nokia. Thanks!!", OVI_NUM_FROM)
    send_sms_direct_to_gateway(TEST_NUM,"Test from Agathe/Nokia. Thanks!!", OVI_NUM_FROM)
    
    
    