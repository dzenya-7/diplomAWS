from datetime import *
from threading import Thread
import time
import boto3
import cv2
from boto3.dynamodb.conditions import Key

data = ['AKIARNPSN5CHJD7FBRIF', 'wgHo0zTTRMXhJvreIw4uR+CrDvCd6x+QufgJOUJt', 'eu-central-1']
rekognition_client = boto3.client('rekognition', aws_access_key_id=data[0], aws_secret_access_key=data[1], region_name=data[2])
translate_client = boto3.client("translate", aws_access_key_id=data[0], aws_secret_access_key=data[1], region_name=data[2])
db_client = boto3.client("dynamodb", aws_access_key_id=data[0], aws_secret_access_key=data[1], region_name=data[2])
dynamodb = boto3.resource('dynamodb', aws_access_key_id=data[0], aws_secret_access_key=data[1], region_name=data[2])
rek = dynamodb.Table('rekognition')

def make_image(numder):
    print("Thread" + str(numder))
    cap = cv2.VideoCapture(numder)
    for i in range(50):
        cap.read()
    ret, frame = cap.read()
    image_name = 'image' + str(numder) + '.jpg'
    cv2.imwrite(image_name, frame)
    cap.release()
    rekognition(image_name)

def run_threads():
    thread = Thread(target=make_image(0))
    # thread1 = Thread(target=make_image(1)); thread2 = Thread(target=make_image(2))
    thread.start()
    # thread1.start(); thread2.start()
    thread.join()
    # thread1.join(); thread2.join()

def put_in_table(tr,c):
    item = {
            'date': str(date.today()),
            'time': str(time.strftime("%H:%M:%S", time.localtime())),
            'objects': tr,
            'percent': c,
        }
    print(item)
    rek.put_item(
        Item=item
    )

def parse_answer(response):
    str1 = str(response)
    a, b, c = str1.partition('LabelModelVersion')
    arr = a.rsplit('Name')
    arr.pop(0)
    result = []
    rek = ''
    percent = ''
    for elem in arr:
        el = elem
        elem, x, z = el.partition('Instances')
        elem = elem[3:-3]
        conf = elem.find('Confidence')
        if conf != -1:
            e = elem
            elem, e, r = e.partition(',')
            a, b, c = r.partition(':')
            c = c[1:-1]
            percent += c + ' '
            elem = elem[1:-1]
            result.append(elem)
            tr = str(translate(elem))
            rek += tr + ' '
    print(rek + " " + percent)
    put_in_table(rek, percent)

def translate(word):
    result = translate_client.translate_text(
        Text=word,
        SourceLanguageCode="en",
        TargetLanguageCode='ru'
    )['TranslatedText']
    return result

def rekognition(image_name):
    with open(image_name, 'rb') as source_image:
        source_bytes = source_image.read()
    response = rekognition_client.detect_labels(Image={'Bytes': source_bytes}, MaxLabels=2, MinConfidence=95)
    parse_answer(response)

def get_item():
    response = rek.query(
        KeyConditionExpression=Key('date').eq(str(date.today()))
    )
    for i in response['Items']:
        print(i)

if __name__ == '__main__':
    start = time.time()
    #run_threads()
    get_item()
    print(time.time()-start)