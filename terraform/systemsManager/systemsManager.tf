resource "aws_ssm_parameter" "bucket_name" {
    name = var.ssm_name
    type = "String"
    description = "Stores the S3 bucket name for the lambdas"
    value = var.bucket_name
}