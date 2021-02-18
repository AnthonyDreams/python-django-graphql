import boto3
from botocore.config import Config

# Create SQS client

queue_url = ''

my_config = Config(
    region_name = 'us-east-2',
)
def send_sqs_message(message):
    sqs = boto3.client('sqs', config=my_config)
    response = sqs.send_message(
    QueueUrl=queue_url,
    DelaySeconds=0,
    MessageBody=(message)
    )

    return response['MessageId']