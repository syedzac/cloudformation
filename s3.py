#!/usr/bin/python

import boto3
import botocore
import sys

def main():
    #boto3.setup_default_session(profile_name='wam');
    AWS_ACCESS = 'KEY'
    AWS_SECRET = 'SECRET'
    s3 = boto3.resource('s3')

    s3.create_bucket(Bucket='zeeshan')
    s3.create_bucket(Bucket='zeeshan', CreateBucketConfiguration={'LocationConstraint': 'ap-southeast-1'})

    print(connection)
if __name__ == '__main__':
    sys.exit(main())
