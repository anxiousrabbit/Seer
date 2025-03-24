data "archive_file" "notification_lambda" {
    type = "zip"
    source_file = "lambda/notification/seerNotif.py"
    output_path = "lambda/notification/seerNotif.zip"
}