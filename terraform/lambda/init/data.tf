data "archive_file" "init_lambda" {
    type = "zip"
    source_file = "lambda/init/seerInit.py"
    output_path = "lambda/init/seerInit.zip"
}