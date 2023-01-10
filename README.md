## How to use
1. install aws CLI https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. install python3 and pip3 https://www.python.org/downloads/
3. install boto3 with pip3 https://pypi.org/project/boto3/
    * pip3 install boto3
4. update S3_CONFIG variable into [main.py](https://github.com/efrain17/S3-Buckets-Account-Migration/blob/master/main.py#L6) and add the origins and destination buckets with the AWS CLI profile depending on each account
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
5. Make sure the destination bucket does not have Block all public access, if you have it activated you will not be able to update the policy, don't worry, this does not enable public write access, the policy is what enables it and it is limitated by the aws account.
5. open a console and run the main.py script 
    * python3 main.py


##  How to use user cleaner script

#### Generate list of user into a csv
1) Set [MAX_DAYS_INACTIVE](https://github.com/efrain17/S3-Buckets-Account-Migration/blob/master/user_cleaner.py#L9) in order to delete all of the user with more days of inactivity
2) set [cliProfiles](https://github.com/efrain17/S3-Buckets-Account-Migration/blob/master/user_cleaner.py#L11-L13) in order to get users from multiples aws accounts
3) run the command 
    * python3 user_cleaner.py list


#### Delete list of user into a csv, remenber the script will delete the user using the data from the csv so take care of new updates.
1) run the command 
    * python3 user_cleaner.py delete
