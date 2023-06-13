from bs4 import BeautifulSoup
import boto3
import requests


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("ecb-currency-rates")

    URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "xml")
    date = soup.Cube.Cube.get("time")

    successes = 0
    failures = 0
    for item in soup.Cube.Cube.contents:
        currency_item = {"date": date}
        if item != "\n":
            currency_item["currency"] = item.get("currency")
            currency_item["rate"] = item.get("rate")

            response = table.put_item(Item=currency_item)

            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 200:
                successes += 1
            else:
                failures += 1

    print(f"Successes: {successes}, Failures: {failures}")

    return {
        'statusCode': status_code
    }
