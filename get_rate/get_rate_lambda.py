from datetime import date
import json

import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ecb-currency-rates")

    today = str(date.today())
    try:
        ticker = event["currency"]
    except:
        ticker = None

    if ticker:
        response = table.query(
            KeyConditionExpression=(Key("currency").eq(ticker) & Key("date").eq(today))
        )
    else:
        response = table.query(
            IndexName="date-index", KeyConditionExpression=(Key("date").eq(today))
        )

    response_list = []
    for item in response["Items"]:
        response_list.append({"currency": item["currency"], "rate": item["rate"]})

    if len(response_list) == 0:
        return json.dumps("No matching item found", default=str)
    else:
        return response_list
