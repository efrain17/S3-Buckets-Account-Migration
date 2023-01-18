import os
import boto3
import json


# you can add one or more include patterns, if you want to add everything use "*"
S3_CONFIG = {
    "origins": [
        {
            "bucketName": "bucket1",
            "cliProfile": "user1",
            "include": [
                "AWSlogs/*/Cloudtrail/*/2021/*",
                "AWSlogs/*/Cloudtrail/*/2022/*"
            ]
        },
        {
            "bucketName": "bucket2",
            "cliProfile": "user2",
            "include": [
                "AWSlogs/*/Cloudtrail/*/2021/*",
            ]
        }
    ],
    "destination": {
        "bucketName": "bucket3",
        "cliProfile": "user3"
    }
}

destination_bucket_name = S3_CONFIG["destination"]["bucketName"]

destinationBucketPolicy = {
	"Version": "2012-10-17",
	"Id": "Policy1611277539797",
	"Statement": [
		{
			"Sid": "Stmt1611277535086",
			"Effect": "Allow",
			"Principal": {
                "AWS": ""
            },
			"Action": "s3:PutObject",
			"Resource": f"arn:aws:s3:::{destination_bucket_name}/*"
		},
		{
			"Sid": "Stmt1611277877767",
			"Effect": "Allow",
			"Principal": {
                "AWS": ""
            },
			"Action": "s3:ListBucket",
			"Resource": f"arn:aws:s3:::{destination_bucket_name}"
		}
	]
}


def main():
    # set permissions

    # coping the files from origin to destination
    destination_bucket = S3_CONFIG["destination"]["bucketName"]
    destination_cli_profile = S3_CONFIG["destination"]["cliProfile"]
    for origin in S3_CONFIG["origins"]:
        origin_bucket = origin["bucketName"]
        # get user arn and update s3 policy
        boto3.setup_default_session(profile_name=origin["cliProfile"])
        iam = boto3.resource('iam')
        current_user = iam.CurrentUser()
        destinationBucketPolicy["Statement"][0]["Principal"]["AWS"] = "*"
        destinationBucketPolicy["Statement"][1]["Principal"]["AWS"] = "*"
        # set access to sync folder into destination
        policy = json.dumps(destinationBucketPolicy)
        boto3.setup_default_session(profile_name=destination_cli_profile)
        s3 = boto3.client('s3')
        s3.put_bucket_policy(Bucket=destination_bucket, Policy=policy)
        # sync files
        iclude_command = ""
        for include in origin["include"]:
            iclude_command += f' --include "{include}"'
        sync_command = f"aws s3 sync s3://{origin_bucket} s3://{destination_bucket}/{origin_bucket} " \
            f"--profile {origin['cliProfile']} " \
            f'--exclude "*" {iclude_command}'
        os.system(sync_command)


if __name__ == "__main__":
    main()
