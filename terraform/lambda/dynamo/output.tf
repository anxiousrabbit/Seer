output "invoke_arn" {
  value = aws_lambda_function.seer_lambda.invoke_arn
}

output "function_name" {
    value = aws_lambda_function.seer_lambda.function_name
}