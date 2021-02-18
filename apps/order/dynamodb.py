import boto3
from botocore.exceptions import ClientError
import os
resource = {
    "region_name":"us-east-2",
            "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
            "aws_access_key_id":os.environ['AWS_ACCESS_KEY_ID']
}

def create_in_dynamodb(connection_user, dynamodb_table):
    dynamodb = boto3.resource('dynamodb', **resource)
    id = {"user_id": connection_user.pop("user_id")}

    if(get_from_dynamodb(id, dynamodb_table, dynamodb)):
        return update_dynamo_item(id, connection_user, dynamodb_table, dynamodb)
    else:
        connection_user.update(id)
        table = dynamodb.Table(dynamodb_table)
        response = table.put_item(
        Item={
                **connection_user
            }
        )
        return response


def get_from_dynamodb(query_data, dynamodb_table, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(dynamodb_table)

    try:
        response = table.get_item(Key={**query_data})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return "Item" in response

# def update_identifier_list     

def update_dynamo_item(id, new_data, dynamodb_table, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table(dynamodb_table)
    update_expresion = []
    attributes_values = {}
    query_parameter = "set "
    
    for k, v in new_data.items():
        attributes_values[f":{k}"] = v
        if isinstance(v, list):
            update_expresion.append(f"{k} = list_append({k}, :{k})")
        else:
            update_expresion.append(f"{k}=:{k}")
    
    update_expresion_string = query_parameter + ", ".join(update_expresion)
    response = table.update_item(
        Key={
           **id
        },
        UpdateExpression=update_expresion_string,
        ExpressionAttributeValues={
            **attributes_values
        },
        ReturnValues="UPDATED_NEW"
    )
    return response