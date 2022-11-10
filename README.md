## How to use
1. install aws CLI https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. install python3 and pip3 https://www.python.org/downloads/
3. install boto3 with pip3 https://pypi.org/project/boto3/
    * pip3 install boto3
4. update S3_CONFIG variable into main.py and add the origins and destination buckets with the AWS CLI profile depending on each account
5. Make sure the destination bucket does not have Block all public access, if you have it activated you will not be able to update the policy, don't worry, this does not enable public write access, the policy is what enables it and it is limitated by the aws account.
```
    S3_CONFIG = {
        "origins": [
            {
                "bucketName": "bucket1",
                "cliProfile": "user1"
            },
            {
                "bucketName": "bucket2",
                "cliProfile": "user2"
            }
        ],
        "destination": {
            "bucketName": "bucket3",
            "cliProfile": "user3"
        }
    }
```
5. open a console and run the main.py script 
    * python3 main.py