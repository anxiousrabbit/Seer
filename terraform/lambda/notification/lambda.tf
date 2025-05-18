resource "aws_iam_role" "iam_for_seer_notification" {
  name = "iam_for_seer_notification"

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
        "sqs:SendMessage",
        "sqs:GetQueueUrl",
        "s3:GetObject",
        "s3:HeadObject",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
  })
}

resource "aws_iam_role_policy_attachment" "notification_attach" {
  role = aws_iam_role.iam_for_seer_notification.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_lambda_permission" "allow_bucket" {
  statement_id = var.permision_statement
  action = var.action
  function_name = aws_lambda_function.notification_lambda.arn
  principal = var.principal
  source_arn = var.s3_bucket
}

resource "aws_lambda_function" "notification_lambda" {
  filename = data.archive_file.notification_lambda.output_path
  function_name = var.function_name
  role = aws_iam_role.iam_for_seer_notification.arn
  handler = var.handler
  source_code_hash = data.archive_file.notification_lambda.output_base64sha256
  runtime = var.runtime
  timeout = 10
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.notification_lambda.arn
    events = ["s3:ObjectCreated:*"]
    filter_prefix = var.prefix
  }

  depends_on = [
    aws_lambda_permission.allow_bucket
  ]
}