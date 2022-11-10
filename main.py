import os
import boto3
import json


S3_CONFIG = {
    "origins": [
        {
            "bucketName": "efrainorigin",
            "cliProfile": "default"
        },
        {
            "bucketName": "bitcoind-prediction",
            "cliProfile": "default"
        }
    ],
    "destination": {
        "bucketName": "efraindestination2",
        "cliProfile": "user1"
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
        destinationBucketPolicy["Statement"][0]["Principal"]["AWS"] = current_user.arn
        destinationBucketPolicy["Statement"][1]["Principal"]["AWS"] = current_user.arn
        # set access to sync folder into destination
        policy = json.dumps(destinationBucketPolicy)
        boto3.setup_default_session(profile_name=destination_cli_profile)
        s3 = boto3.client('s3')
        s3.put_bucket_policy(Bucket=destination_bucket, Policy=policy)
        # sync files
        sync_command = f"aws s3 sync s3://{origin_bucket} s3://{destination_bucket}/{origin_bucket} " \
            f"--profile {origin['cliProfile']}"
        os.system(sync_command)


if __name__ == "__main__":
    main()
