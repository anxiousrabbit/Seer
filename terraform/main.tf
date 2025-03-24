module "dynamo_lambda" {
  source = "./lambda/dynamo"
  bucket_name = module.lambda_systems_manager.ssm_name
  depends_on = [ 
    module.lambda_systems_manager
   ]
}

module "init_lambda" {
	source = "./lambda/init"
  bucket_name = module.lambda_systems_manager.ssm_name
  depends_on = [ 
    module.lambda_systems_manager
   ]
}

module "get_lambda" {
  source = "./lambda/get"
  bucket_name = module.lambda_systems_manager.ssm_name
  depends_on = [ 
    module.lambda_systems_manager
   ]
}

module "seerGateway" {
  source = "./apiGateway/seerGateway"
  api_gateway_region = data.aws_region.current.name
  api_gateway_account_id = data.aws_caller_identity.current.account_id
  post_function_name = module.dynamo_lambda.function_name
  post_invoke_arn = module.dynamo_lambda.invoke_arn
	init_function_name = module.init_lambda.function_name
	init_invoke_arn = module.init_lambda.invoke_arn
  get_invoke_arn = module.get_lambda.invoke_arn
  get_function_name = module.get_lambda.function_name
  depends_on = [
    module.dynamo_lambda,
		module.init_lambda,
    module.get_lambda
  ]
}

module "seerS3" {
	source = "./s3"
  bucket_name = var.bucket_name
}

module "notification_lambda" {
  source = "./lambda/notification"
  s3_bucket = module.seerS3.bucket_arn
  bucket_id = module.seerS3.bucket_id
  depends_on = [
    module.seerS3
  ]
}

module "lambda_systems_manager" {
  source = "./systemsManager"
  bucket_name = module.seerS3.bucket_id
  depends_on = [ 
    module.seerS3
   ]
}