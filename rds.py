#!/usr/bin/python

import boto3
import botocore
import sys
import pymysql.cursors
import time

def main():
    #boto3.setup_default_session(profile_name='wam');
    AWS_ACCESS = 'KEY'
    AWS_SECRET = 'SECRET
    ENGINE_NAME = 'mariadb'
    ENGINE_VERSION = '10.4.13'
    DB_INSTANCE_TYPE = 'db.t2.small'
    DB_NAME = 'invoices'
    DB_STORAGE = 100
    DB_USER_NAME = 'zeeshan'
    DB_USER_PASSWORD = 'Zeeshan786'
    db_instance_name = 'lambda-RDS-786'
    db_param_grp_name = 'lambda-Group-786'

    rds_client = boto3.client(
    'rds',
    region_name = 'ap-southeast-1',
    aws_access_key_id = AWS_ACCESS,
    aws_secret_access_key = AWS_SECRET,
)

    describe_eng_ver_response = rds_client.describe_db_engine_versions()

    if describe_eng_ver_response['ResponseMetadata']['HTTPStatusCode'] \
    == 200:
        eng_list = [engine for engine in
        describe_eng_ver_response['DBEngineVersions']
        if engine['Engine'] == ENGINE_NAME
        and engine['EngineVersion'] == ENGINE_VERSION
    ]
    assert len(eng_list) == 1, 'Cannot find engine'
    db_param_grp_family = eng_list[0]['DBParameterGroupFamily']
    print('Successfully described DB Engine Versions')
    #else:
        #print("Couldn't describe DB Engine Versions")

    create_db_params_response = \
    rds_client.create_db_parameter_group(DBParameterGroupName = db_param_grp_name,
        DBParameterGroupFamily = db_param_grp_family,
        Description = 'Test DB Params Group')

    create_db_instance_response = rds_client.create_db_instance(
    DBInstanceIdentifier = db_instance_name,
    DBInstanceClass = DB_INSTANCE_TYPE,
    DBName = DB_NAME,
    Engine = ENGINE_NAME,
    EngineVersion = ENGINE_VERSION,
    AllocatedStorage = DB_STORAGE,
    MasterUsername = DB_USER_NAME,
    MasterUserPassword = DB_USER_PASSWORD,
    DBParameterGroupName = db_param_grp_name,
)

    if create_db_instance_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print ('Successfully created DB instance %s' %db_instance_name)
    else :
        print ("Couldn't create DB instance")

    print('waiting for db instance %s to become ready' %db_instance_name)

    number_of_retries = 20
    db_success = False
    for i in range(number_of_retries):
	    time.sleep(30)
	    db_status = \
        rds_client.describe_db_instances(DBInstanceIdentifier = db_instance_name)['DBInstances'][0]['DBInstanceStatus']
	    if db_status == 'available':
					    db_success = True
					    print('DB instance %s is ready' % db_instance_name)
					    break
	    else :
		    print('DB instance %s is initializing. Attempt %s' % (db_instance_name, i))

    assert db_success, 'DB failed %s to initialize' % db_instance_name

    instances = rds_client.describe_db_instances(DBInstanceIdentifier = db_instance_name)
    rds_host = instances.get('DBInstances')[0].get('Endpoint').get('Address')

    time.sleep(30)
    connection = pymysql.connect(
        host = rds_host,
        user = DB_USER_NAME,
        password = DB_USER_PASSWORD,
        db = DB_NAME,
        charset = 'utf8mb4',
        cursorclass = pymysql.cursors.DictCursor)

    print(connection)
if __name__ == '__main__':
    sys.exit(main())
