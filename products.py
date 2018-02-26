import requests
import xml.etree.ElementTree as ET
import hmac
import base64
import datetime
import hashlib
import csv
from urllib.parse import quote
from pytz import timezone
import random

class AmazoneApi(object):
    """docstring for AmazoneApi."""
    base_uri = "https://mws.amazonservices.com/"
    awsaccesskeysecret = ""
    awsaccesskeyid = ""
    action = "GetFeedSubmissionList"
    mwsauthtoken = ""
    merchant = ""
    signature = ""
    signaturemethod = "HmacSHA256"
    signatureversion = "2"
    timestamp = ""
    version = "2009-01-01"
    host = ""
    uri_param = ""
    contentmd5 = ""
    feedtype = ""
    marketplaceid1 = ""
    def __init__(self, accesskeyid,accesskeysecret,authtoken,merchant,marketplaceid="",host="https://mws.amazonservices.com/"):
        super(AmazoneApi, self).__init__()
        self.awsaccesskeyid = accesskeyid
        self.mwsauthtoken = authtoken
        self.merchant = merchant
        self.marketplaceid1 = marketplaceid
        self.awsaccesskeysecret = accesskeysecret
        self.host = host
    def getFeedList(self):
        self.action = "GetFeedSubmissionList"
        signature = self.getSignature()
        signature = signature.decode()
        params = self.getParam()+"&Signature="+quote(signature)
        request_url = self.host+"?"+params
        feedlist = requests.post(request_url)
        root = ET.fromstring(feedlist.content)
        for child in root.iter('*'):
            print(child.tag)
    def getCurrentTimeStamp(self):
        now_utc = datetime.datetime.now(timezone('UTC'))
        now_pacific = now_utc.astimezone(timezone('US/Pacific'))
        self.timestamp = now_pacific.isoformat()
    def submitProductFeed(self,row):
        self.action = "SubmitFeed"
        sku = random.randint(0,1000)
        contentbody = """
        <?xml version="1.0" encoding="iso-8859-1"?>
        <AmazonEnvelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="amzn-envelope.xsd">
          <Header>
            <DocumentVersion>1.01</DocumentVersion>
            <MerchantIdentifier>M_EXAMPLE_123456</MerchantIdentifier>
          </Header>
          <MessageType>Product</MessageType>
          <PurgeAndReplace>false</PurgeAndReplace>
          <Message>
            <MessageID>1</MessageID>
            <OperationType>Update</OperationType>
            <Product>
              <SKU>"""+row["Part Number"]+str(sku)+"""</SKU>
              <StandardProductID>
                <Type>ASIN</Type>
                <Value>"""+row["Part Number"]+"""</Value>
              </StandardProductID>
              <ProductTaxCode>"""+row["Part Number"]+"""</ProductTaxCode>
              <DescriptionData>
                <Title>"""+row["Title"]+"""</Title>
                <Brand>"""+row["Brand"]+"""</Brand>
                <Description>"""+row["Description"]+"""</Description>
                <BulletPoint>Example Bullet Point 1</BulletPoint>
                <BulletPoint>Example Bullet Point 2</BulletPoint>
                <MSRP currency="USD">"""+row["Start Price"]+"""</MSRP>
                <Manufacturer>Example Product Manufacturer</Manufacturer>
                <ItemType>example-item-type</ItemType>
              </DescriptionData>
              <ProductData>
                <Health>
                  <ProductType>
                    <HealthMisc>
                      <Ingredients>Example Ingredients</Ingredients>
                      <Directions>Example Directions</Directions>
                    </HealthMisc>
                  </ProductType>
                </Health>
              </ProductData>
            </Product>
          </Message>
        </AmazonEnvelope>
        """
        self.feedtype = "_POST_PRODUCT_DATA_"
        m = hashlib.md5()
        m.update(contentbody.encode('utf-8'))
        print("contentmd5")
        digestvalue = m.digest()
        print(digestvalue)
        self.contentmd5 = (base64.b64encode(digestvalue)).decode()
        print(self.contentmd5)
        signature = self.getSignature()
        signature = signature.decode()
        params = self.getParam()+"&Signature="+quote(signature)
        request_url = self.host+"?"+params
        headers = {'content-type': 'text/xml'}
        feedlist = requests.post(request_url,data=contentbody,headers=headers)
        root = ET.fromstring(feedlist.content)
        for child in root.iter('*'):
            print(child.tag)
        print("-------------------------------")
        print(feedlist.content)
    def getSignature(self):
        self.getCurrentTimeStamp()
        data ="AWSAccessKeyId="+str(self.awsaccesskeyid)
        data +="&Action="+str(self.action)
        if self.contentmd5:
            data +="&ContentMD5Value="+quote(str(self.contentmd5))
        if self.feedtype:
            data +="&FeedType="+str(self.feedtype)
        data +="&MWSAuthToken="+str(self.mwsauthtoken)
        if self.marketplaceid1:
            data +="&MarketplaceIdList.Id.1="+str(self.marketplaceid1)
        data +="&Merchant="+str(self.merchant)
        if self.action == "SubmitFeed":
            data +="&PurgeAndReplace=false"
        data +="&SignatureMethod="+str(self.signaturemethod)
        data +="&SignatureVersion="+str(self.signatureversion)
        data +="&Timestamp="+quote(str(self.timestamp))
        data +="&Version="+str(self.version)

        self.uri_param = data
        StringToSign = "POST"+"\n"+"mws.amazonservices.com"+"\n/"+"\n"+data
        print(StringToSign)
        key_bytes= bytes(self.awsaccesskeysecret , 'latin-1')
        data_bytes = bytes(StringToSign, 'latin-1')
        return base64.b64encode(hmac.new(key_bytes, data_bytes, hashlib.sha256).digest())
    def getParam(self):
        data ="AWSAccessKeyId="+str(self.awsaccesskeyid)
        data +="&Action="+str(self.action)
        if self.contentmd5:
            data +="&ContentMD5Value="+quote(str(self.contentmd5))
        if self.feedtype:
            data +="&FeedType="+str(self.feedtype)
        data +="&MWSAuthToken="+str(self.mwsauthtoken)
        if self.marketplaceid1:
            data +="&MarketplaceIdList.Id.1="+str(self.marketplaceid1)
        data +="&Merchant="+str(self.merchant)
        if self.action == "SubmitFeed":
            data +="&PurgeAndReplace=false"
        data +="&SignatureMethod="+str(self.signaturemethod)
        data +="&SignatureVersion="+str(self.signatureversion)
        data +="&Timestamp="+str(self.timestamp)
        data +="&Version="+str(self.version)

        return data
        # return base64.b64encode(hmac.new(key_bytes, data_bytes, hashlib.sha256))
a = AmazoneApi("AKIAIUFSF6B7TP5RYJ3A","inne0ux16QVqSI73g0IN5qK2fKErTBX2PJSZLGB9","amzn.mws.42b059b1-50ee-d065-34c8-231ed474b401","A1IF11LNLJA1GU","ATVPDKIKX0DER")
# a.getFeedList()
with open('products.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        a.submitProductFeed(row)
        print("-----------------------------------------------------------------")
