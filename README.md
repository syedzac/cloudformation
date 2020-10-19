# Syed Zeeshan Ali

[![N|Solid](https://futurumresearch.com/wp-content/uploads/2020/01/aws-logo.png)](#)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://zaccie.com)


 BOTO3 with AWS SDK on Python3 to create Secure VPC, Subnets, Routing Table, Security Group, LoadBalancer, EC2, RDS with Dummy Data of MariaDB

  - vpc.py (Run this first to create secure VPC, Loadbalancer, Subnets, CIDRs, Routing Table and EC2)
  - rds.py (Run this after successful creation of secure VPC, it creates RDS - MariaDB and add dummy data to populate )
  - s3.py (Run this to create a s3 bucket)
  - dynamodb.py (Run this file to create DynamoDB table with dummy data)



# How to use!

  - Python3 and AWS SDK (Must install or can directly run on AWS Lambda)
  - pip3 install pymysql.cursors
  - pip3 install boto3
  - vpc.py - Add AWS KEY and SECRET ([how to](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html))
  - rds.py - Add AWS KEY and SECRET ([how to](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html))
  - python3 vpc.py (it will take few mins to create VPC)
  - python3 rds.py (it will take 10-15mins to create RDS)
  - python3 s3.py (it will take 20seconds to create bucket)


