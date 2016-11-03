import boto3
import json
import base64
import binascii
from urllib import parse
aws_access_key_id = "AKIAJXIXL4647ST4BBCA"
aws_secret_access_key = "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"

boto3.setup_default_session(
    aws_secret_access_key=aws_secret_access_key,
    aws_access_key_id=aws_access_key_id,
    region_name = "ap-northeast-1"
)

def base64toHex(str):
    b = base64.decodebytes(str.encode())
    return binascii.b2a_hex(b).decode(encoding="utf-8")

class PushNotification:
    def __init__(self, app_arn):
        self.sns = boto3.resource("sns")
        self.app = self.sns.PlatformApplication(app_arn)

    def register(self,endpointBase64, deviceName, *topics):
        value = base64toHex(endpointBase64)
        r = self.app.create_platform_endpoint(Token=value,CustomUserData=deviceName)
        return r


    def message(self, text):
        message = {'default':text, 'message':{'APNS_SANDBOX':{'aps':{'alert':'inner message','sound':'mySound.caf'}}}}
        jsonPayload = json.dumps(message)
        for e in self.app.endpoints.iterator():
            e.publish(Message=jsonPayload, MessageStructure="json")

    def messageToTopic(self,text,topicARN):
        t= self.sns.Topic(topicARN)
        msg = json.dumps({'default': text,
                          'message': {'APNS_SANDBOX': {'aps': {'alert': 'inner message', 'sound': 'mySound.caf'}}}})

        t.publish(Message=msg, MessageStructure='json')


def createApplication(name, p12Path , isDevelopment=True):
    platform = "APNS"
    if isDevelopment :
        platform = "APNS_SANDBOX"

    with open(p12Path,) as reader:
        p = reader.read()
        certificate = getStringInclusive(p,"-----BEGIN CERTIFICATE-----","-----END CERTIFICATE-----")
        secret = getStringInclusive(p,"-----BEGIN RSA PRIVATE KEY-----","-----END RSA PRIVATE KEY-----")


    sns = boto3.resource("sns")
    return sns.create_platform_application(Name=name,
                                    Platform = platform,
                                    Attributes= {
                                        "PlatformPrincipal":certificate,
                                        "PlatformCredential":secret
                                    })


def getStringInclusive(str, beginning, end):
    b = str.find(beginning)
    e = str.find(end)
    value =  str[b+len(beginning):e].replace("\n","")

    return "{0}\n{1}\n{2}".format(beginning,value,end)


if __name__ == "__main__1":
    push = PushNotification("arn:aws:sns:ap-northeast-1:254772566290:app/APNS_SANDBOX/sandbox")
    for i in range(20):
        push.message("This is just a test {0}".format(i))

if __name__ == "__main__":
    #Create Apps

    #createApplication("Prizy.me.ios.dev",r"/Users/jay/Desktop/prizy.me.ios/resources/pushnotification/sandbox/myapnsappprivatekey.pem",True)
    #createApplication("Prizy.me.ios.prod", r"/Users/jay/Desktop/prizy.me.ios/resources/pushnotification/prod/myapnsapprivatekey.pem", False)

    #create topics
    """
    companies = ["Lawson","Mini-Stop","FamilyMart","Starbucks",
                 "BaskinRobbins","KrispyKreme","SoupStock","Amazon",
                 "PointClub","Line","iTunes","mobage"]

    sns = boto3.resource("sns")
    list(map(lambda x: sns.create_topic(Name=x) ,companies))


    #Subscript endpoint to topic
    b = sns.Topic("arn:aws:sns:ap-northeast-1:254772566290:BaskinRobbins")
    b.subscribe(Protocol="application", Endpoint=r.arn)



    baskinARN = "arn:aws:sns:ap-northeast-1:254772566290:BaskinRobbins"
    push = PushNotification("arn:aws:sns:ap-northeast-1:254772566290:app/APNS_SANDBOX/Prizy.me.ios.dev")
    push.messageToTopic("Hello Baskins Customer",baskinARN)
    """
    push = PushNotification("arn:aws:sns:ap-northeast-1:254772566290:app/APNS_SANDBOX/Prizy.me.ios.dev")
    push.register("xWL0iLp7MZe8NNDoW3YjUG1FgNKkVaKjJe+qzVdjpwU=","Herro")
