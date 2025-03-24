resource "aws_s3_bucket" "seerBucket" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_acl" "seerBucket_acl" {
  bucket = aws_s3_bucket.seerBucket.id
	acl = var.acl
}