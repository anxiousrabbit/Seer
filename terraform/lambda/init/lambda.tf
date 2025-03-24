# provider "aws" {
#   region=var.region
# }

resource "aws_iam_role" "iam_for_seer_init" {
  name = "iam_for_seer_init"

  assume_role_policy = jsonencode( {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "sts:AssumeRole",
  ]
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  })
}

resource "aws_iam_policy" "policy" {
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
    {
      "Action": [
        "sqs:CreateQueue",
        "sqs:ListQueues",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "s3:PutBucketNotification",
        "dynamodb:ListTables",
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable",
        "ssm:GetParameter"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
        "Action": [
          "s3:PutObject",
          "s3:GetObject"
        ],
        "Effect": "Allow",
        "Resource": "*"
    }
  ]
  })
}

resource "aws_iam_role_policy_attachment" "init_attach" {
  role = aws_iam_role.iam_for_seer_init.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_lambda_function" "init_lambda" {
  filename = data.archive_file.init_lambda.output_path
  function_name = var.function_name
  role = aws_iam_role.iam_for_seer_init.arn
  handler = var.handler
  source_code_hash = data.archive_file.init_lambda.output_base64sha256
  runtime = var.runtime
  timeout = 10
  environment {
    variables = {
      BUCKET = var.bucket_name
    }
  }
}