variable "region" {
  description = "AWS Region"
  type = string
  default = "us-east-2"
}

variable "dynamodb_table_name" {
  description = "The DynamoDB table name"
  type = string
  default = "ecb-currency-rates"
}

variable "ingest_lambda_name" {
    description = "The name of the data ingestor lambda"
    type = string
    default = "data_ingester"
}

variable "get_rate_lambda_name" {
    description = "The name of the GET API lambda"
    type = string
    default = "get_rate"
}