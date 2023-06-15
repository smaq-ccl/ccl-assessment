import boto3
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ecb-currency-rates")

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

        rate_change = []
        if response["Items"]:
            rate_today = float(response["Items"][0]["rate"])
            rate_yesterday = float(response["Items"][1]["rate"])
            absolute_change = round(rate_today - rate_yesterday, 5)
            percentage_change = round(
                (rate_today - rate_yesterday) * 100 / rate_yesterday, 5
            )

            rate_change.append(
                {
                    "date": response["Items"][0]["date"],
                    "currency": ticker,
                    "rate_today": rate_today,
                    "rate_yesterday": rate_yesterday,
                    "absolute_change": absolute_change,
                    "percentage_change": percentage_change,
                }
            )

    else:
        # Query is used to fetch the last 2 dates with data
        response_dates = table.query(
            KeyConditionExpression=(Key("currency").eq("USD")),
            Limit=2,
            ScanIndexForward=False,
        )
        date_today = response_dates["Items"][0]["date"]
        date_yesterday = response_dates["Items"][1]["date"]

        response_today = table.query(
            IndexName="date-index", KeyConditionExpression=(Key("date").eq(date_today))
        )
        response_yesterday = table.query(
            IndexName="date-index",
            KeyConditionExpression=(Key("date").eq(date_yesterday)),
        )

        rate_change = []
        for item_today in response_today["Items"]:
            currency = item_today["currency"]

            rate_today = float(item_today["rate"])
            rate_yesterday = float(
                [
                    item["rate"]
                    for item in response_yesterday["Items"]
                    if item["currency"] == currency
                ][0]
            )
            absolute_change = round(rate_today - rate_yesterday, 5)
            percentage_change = round(
                (rate_today - rate_yesterday) * 100 / rate_yesterday, 5
            )
            rate_change.append(
                {
                    "date": date_today,
                    "currency": currency,
                    "rate_today": rate_today,
                    "rate_yesterday": rate_yesterday,
                    "absolute_change": absolute_change,
                    "percentage_change": percentage_change,
                }
            )

    if len(rate_change) == 0:
        rate_change = {"status": 404, "msg": "No matching item found"}

    return rate_change
