import boto3
from datetime import datetime, timezone
from typing import List
import time
import csv
import sys


MAX_DAYS_INACTIVE = 754
CONFIG = {
    "cliProfiles": [
        "user1",
        "user2",
    ]
}


def getuser(iam_client, market, users):
    # get user arn and update s3 policy
    params = {
        "MaxItems": 1
    }
    if market:
        params["Marker"] = market
    response = iam_client.list_users(**params)
    new_users = response["Users"]
    if response["IsTruncated"]:
        # add a delay to avoid rate limit
        time.sleep(0.5)
        return getuser(
            iam_client,
            response["Marker"],
            users + new_users
        )
    return users + new_users


def filter_user_by_last_used(users: List, cli_profile: str):
    # calculate how many days ago the user was used
    iam = boto3.resource('iam')
    iam_client = boto3.client('iam')
    res = []
    for user_params in users:
        user = iam.User(user_params["UserName"])
        days_ago = None
        min_days_ago = float("+inf")
        for k in user.access_keys.all():
            key_used = iam_client.get_access_key_last_used(AccessKeyId=k.id)
            if not key_used['AccessKeyLastUsed'].get("LastUsedDate"):
                res.append(
                    {
                        "UserName": user_params["UserName"],
                        "AccessKeyId": k.id,
                        "LastUsedDays": "N/A",
                        "Action": "DeleteAccessKey",
                        "CLIprofile": cli_profile
                    }
                )
                min_days_ago = min(min_days_ago, float("+inf"))
                continue
            key_date = key_used['AccessKeyLastUsed']['LastUsedDate']
            days_ago = (datetime.now(timezone.utc) - key_date).days
            if days_ago > MAX_DAYS_INACTIVE:
                res.append(
                    {
                        "UserName": user_params["UserName"],
                        "AccessKeyId": k.id,
                        "LastUsedDays": days_ago,
                        "Action": "DeleteAccessKey",
                        "CLIprofile": cli_profile
                    }
                )
            min_days_ago = min(min_days_ago, days_ago)
        # calculte how many days ago the user was used
        last_used_date = (
            user_params.get("PasswordLastUsed") or
            user_params.get("CreateDate")
        )
        last_days_used_password = (
            datetime.now(timezone.utc) - last_used_date
        ).days
        min_days_ago = min(min_days_ago, last_days_used_password)
        if min_days_ago > MAX_DAYS_INACTIVE:
            res.append(
                {
                    "UserName": user_params["UserName"],
                    "LastUsedDays": min_days_ago,
                    "Action": "DeleteUser",
                    "CLIprofile": cli_profile
                }
            )
    return res


def write_csv(users):
    with open('users.csv', 'w') as csvfile:
        fieldnames = [
            "UserName",
            "AccessKeyId",
            "LastUsedDays",
            "Action",
            "CLIprofile"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in users:
            writer.writerow(user)


def delete_user_and_keys(user, ):
    cli_profile = user["CLIprofile"]
    boto3.setup_default_session(profile_name=cli_profile)
    iam_client = boto3.client('iam')
    if user["Action"] == "DeleteAccessKey":
        iam_client.update_access_key(
            UserName=user["UserName"],
            AccessKeyId=user["AccessKeyId"],
            Status='Inactive'
        )
        iam_client.delete_access_key(
            UserName=user["UserName"],
            AccessKeyId=user["AccessKeyId"]
        )
    elif user["Action"] == "DeleteUser":
        # detach group from user
        for group in iam_client.list_groups_for_user(
            UserName=user["UserName"]
        )["Groups"]:
            iam_client.remove_user_from_group(
                GroupName=group["GroupName"],
                UserName=user["UserName"]
            )
        # delete login profile first
        try:
            iam_client.delete_login_profile(
                UserName=user["UserName"]
            )
        except Exception:
            pass
        # detach all policies first.
        for policy in iam_client.list_attached_user_policies(
            UserName=user["UserName"]
        )["AttachedPolicies"]:
            iam_client.detach_user_policy(
                UserName=user["UserName"],
                PolicyArn=policy["PolicyArn"]
            )
        # delete user
        iam_client.delete_user(
            UserName=user["UserName"]
        )


def generate_list_of_users():
    # set permissions
    users = []
    for cli_profile in CONFIG["cliProfiles"]:
        boto3.setup_default_session(profile_name=cli_profile)
        iam_client = boto3.client('iam')
        new_users = getuser(
            iam_client=iam_client, market=None, users=[]
        )
        users = users + filter_user_by_last_used(new_users, cli_profile)
    write_csv(users)


# def dele_user_from_csv():
#     with open('users.csv', 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             delete_user_and_keys(row)


if __name__ == "__main__":
    # execute only if run as a script with sys.argv[0]
    if sys.argv[1] == "list":
        generate_list_of_users()
        print("List of users generated: users.csv")
    elif sys.argv[1] == "delete":
        # dele_user_from_csv()
        print("Users deleted")
    else:
        print("Invalid command")
