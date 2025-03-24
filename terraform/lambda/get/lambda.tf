resource "aws_iam_role" "iam_for_seer_get" {
  name = "iam_for_seer_get"

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
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject",
        "sqs:ReceiveMessage",
        "sqs:ListQueues",
        "sqs:GetQueueUrl",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ssm:GetParameter"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
  })
}

resource "aws_iam_role_policy_attachment" "get_attach" {
  role = aws_iam_role.iam_for_seer_get.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_lambda_function" "get_lambda" {
  filename = data.archive_file.get_python.output_path
  function_name = var.function_name
  role = aws_iam_role.iam_for_seer_get.arn
  handler = var.handler
  source_code_hash = data.archive_file.get_python.output_base64sha256
  runtime = var.runtime
  timeout = 10
  environment {
    variables = {
      BUCKET = var.bucket_name
    }
  }
}