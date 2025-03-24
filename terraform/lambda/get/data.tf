data "archive_file" "get_python" {
    type = "zip"
    source_file = "lambda/get/seerGet.py"
    output_path = "lambda/get/seerGet.zip"
}