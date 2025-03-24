data "archive_file" "dynamo_python" {
    type = "zip"
    source_file = "lambda/dynamo/dynamo.py"
    output_path = "lambda/dynamo/dynamo.zip"
}