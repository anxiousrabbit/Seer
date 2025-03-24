output "invoke_arn" {
  value = aws_lambda_function.init_lambda.invoke_arn
}

output "function_name" {
    value = aws_lambda_function.init_lambda.function_name
}