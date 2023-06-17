terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = var.region
  shared_credentials_files = ["$HOME/.aws/credentials"]
}

resource "aws_dynamodb_table" "ecb_currency_rates_table" {
  name = var.dynamodb_table_name
  billing_mode = "PROVISIONED"
  read_capacity = 1
  write_capacity = 1
  hash_key = "currency"
  range_key = "date"

  attribute {
    name = "currency"
    type = "S"
  }

  attribute {
    name = "date"
    type = "S"
  }

  attribute {
    name = "rate"
    type = "S"
  }

  global_secondary_index {
    name = "date-index"
    hash_key = "date"
    read_capacity = 1
    write_capacity = 1
    projection_type = "ALL"
  }

  lifecycle {
    ignore_changes = [ read_capacity, write_capacity ]
  }
}

module "table_autoscaling" {
  source = "snowplow-devops/dynamodb-autoscaling/aws"
  table_name = aws_dynamodb_table.ecb_currency_rates_table.name
}


resource "aws_iam_role" "iam_for_lambda" {
 name = "iam_for_lambda"

 assume_role_policy = jsonencode({
   "Version" : "2012-10-17",
   "Statement" : [
     {
       "Effect" : "Allow",
       "Principal" : {
         "Service" : "lambda.amazonaws.com"
       },
       "Action" : "sts:AssumeRole"
     }
   ]
  })
}
          
resource "aws_iam_role_policy_attachment" "lambda_policy" {
   role = aws_iam_role.iam_for_lambda.name
   policy_arn = "arn:aws:iam::aws:policy/servicerole/AWSLambdaBasicExecutionRole"
}
          
resource "aws_iam_role_policy" "dynamodb-lambda-read-policy" {
   name = "dynamodb_lambda_read_policy"
   role = aws_iam_role.iam_for_lambda.id
   policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
           "Effect": "Allow",
            "Action": [
                "dynamodb:BatchGetItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
           "Resource" : "${aws_dynamodb_table.tf_notes_table.arn}"
        }
      ]
   })
}

resource "aws_iam_role_policy" "dynamodb-lambda-write-policy" {
   name = "dynamodb_lambda_write_policy"
   role = aws_iam_role.iam_for_lambda.id
   policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
           "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem"
            ],
           "Resource" : "${aws_dynamodb_table.tf_notes_table.arn}"
        }
      ]
   })
}