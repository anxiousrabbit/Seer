resource "aws_iam_role" "iam_for_seer_dynamo" {
  name = "iam_for_seer_dynamo"

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
        "dynamodb:DescribeStream",
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:ListStreams",
        "dynamodb:PutItem",
        "dynamodb:DescribeTable",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "sqs:SendMessage",
        "sqs:GetQueueUrl",
        "ssm:GetParameter"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
        "Action": [
          "s3:GetObject",
          "s3:GetBucketLocation",
          "s3:ListAllMyBuckets",
          "s3:CreateBucket",
          "s3:PutObject",
          "s3:DeleteObject"
        ],
        "Effect": "Allow",
        "Resource": "*"
    }
  ]
  })
}

resource "aws_iam_role_policy_attachment" "dynamo_attach" {
  role = aws_iam_role.iam_for_seer_dynamo.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_lambda_function" "seer_lambda" {
  filename = data.archive_file.dynamo_python.output_path
  function_name = var.function_name
  role = aws_iam_role.iam_for_seer_dynamo.arn
  handler = var.handler
  source_code_hash = data.archive_file.dynamo_python.output_base64sha256
  runtime = var.runtime
  timeout = 10
  environment {
    variables = {
      BUCKET = var.bucket_name
    }
  }
}