from datetime import date
import json

import boto3
from boto3.dynamodb.conditions import Key, Attr


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
            KeyConditionExpression=(Key("currency").eq(ticker)),
            Limit=2,
            ScanIndexForward=False,
        )

        print(response["Items"])

        rate_today = float(response["Items"][0]["rate"])
        rate_yesterday = float(response["Items"][1]["rate"])
        absolute_change = round(rate_today - rate_yesterday, 5)
        percentage_change = round(
            (rate_today - rate_yesterday) * 100 / rate_yesterday, 5
        )

        rate_change = [
            {
                "currency": ticker,
                "rate_today": rate_today,
                "rate_yesterday": rate_yesterday,
                "absolute_change": absolute_change,
                "percentage_change": percentage_change,
            }
        ]

    else:
        response_today = table.query(
            IndexName="date-index", KeyConditionExpression=(Key("date").eq(today))
        )

        currencies = [item["currency"] for item in response_today["Items"]]

        # TODO: Improve unoptimized query
        response_yesterday = []
        for currency in currencies:
            response = table.query(
                KeyConditionExpression=(
                    Key("currency").eq(currency) & Key("date").lt(today)
                ),
                Limit=1,
                ScanIndexForward=False,
            )
            response_yesterday.append(response["Items"][0])

        rate_change = []
        for currency in currencies:
            rate_today = float(
                [
                    item["rate"]
                    for item in response_today["Items"]
                    if item["currency"] == currency
                ][0]
            )
            rate_yesterday = float(
                [
                    item["rate"]
                    for item in response_yesterday
                    if item["currency"] == currency
                ][0]
            )
            absolute_change = round(rate_today - rate_yesterday, 5)
            percentage_change = round(
                (rate_today - rate_yesterday) * 100 / rate_yesterday, 5
            )
            rate_change.append(
                {
                    "currency": currency,
                    "rate_today": rate_today,
                    "rate_yesterday": rate_yesterday,
                    "absolute_change": absolute_change,
                    "percentage_change": percentage_change,
                }
            )

    return rate_change
