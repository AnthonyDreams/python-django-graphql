import boto3
from botocore.config import Config
import json
# Create SQS client
my_config = Config(
    region_name = 'us-east-1',
)
def send_sqs_message(message, url):
    sqs = boto3.client('sqs', config=my_config)
    response = sqs.send_message(
    QueueUrl=url,
    DelaySeconds=0,
    MessageBody=(message)
    )

    return response['MessageId']

def sendEmail(emailObject):
    domain = 'https://sqs.us-east-1.amazonaws.com/806623959432/emailQueue'
    send_sqs_message(json.dumps(emailObject), domain)
