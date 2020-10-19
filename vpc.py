import boto3
import botocore
import sys
import random
import time


def main():
    #boto3.setup_default_session(profile_name='wam');
    AWS_ACCESS = 'KEY'
    AWS_SECRET = 'SECRET'
    REGION = 'ap-southeast-1'
    REGIONa = 'ap-southeast-1a'
    REGIONb = 'ap-southeast-1b'

    VPC_CIDR = '172.18.0.0/16'
    SUBNET_CIDR = '172.18.10.0/24'
    SUBNET_CIDR2 = '172.18.20.0/24' 
    PORT_INTERNAL = 9090
    PORT_EXTERNAL = 80
    TARGETS_COUNT = 2
    IMAGE_ID = 'ami-f068a193'
    INSTANCE_TYPE = 't2.micro'

    run_index = '%03x' % random.randrange(2**12)

    #print ("Disabling warning for Insecure connection")
    #botocore.vendored.requests.packages.urllib3.disable_warnings(
     #   botocore.vendored.requests.packages.urllib3.exceptions.InsecureRequestWarning)

    ec2_client = boto3.client(service_name="ec2", region_name=REGION,
                              aws_access_key_id = AWS_ACCESS,
                              aws_secret_access_key=AWS_SECRET)
    elb_client = boto3.client(service_name="elbv2", region_name=REGION,
                              aws_access_key_id = AWS_ACCESS,
                              aws_secret_access_key=AWS_SECRET)
    create_vpc_response = ec2_client.create_vpc(CidrBlock=VPC_CIDR)
    if create_vpc_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        vpcId = create_vpc_response['Vpc']['VpcId']
        print("Created VPC with ID %s" % vpcId)
    else:
        print("Create VPC failed")
    create_igw_response = ec2_client.create_internet_gateway()
    if create_igw_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        igwId = create_igw_response['InternetGateway']['InternetGatewayId']
        print("Created InternetGateway with ID %s" % igwId)
    else:
        print("Create InternetGateway failed")
    attach_igw_response = ec2_client.attach_internet_gateway(InternetGatewayId=igwId,
                                                             VpcId=vpcId)

    # check attach internet-gateway returned successfully
    if attach_igw_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Attached InternetGateway with ID %s to VPC %s" % (igwId, vpcId))
    else:
        print("Create InternetGateway failed")
    create_subnet_response = ec2_client.create_subnet(AvailabilityZone=REGIONa, CidrBlock=SUBNET_CIDR, VpcId=vpcId)
    if create_subnet_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        subnetId = create_subnet_response['Subnet']['SubnetId']
        print("Created Subnet with ID %s" % subnetId)
    else:
        print("Create Subnet failed")
    create_subnet_response2 = ec2_client.create_subnet(AvailabilityZone=REGIONb, CidrBlock=SUBNET_CIDR2, VpcId=vpcId)
    if create_subnet_response2['ResponseMetadata']['HTTPStatusCode'] == 200:
        subnetId2 = create_subnet_response2['Subnet']['SubnetId']
        print("Created Subnet with ID %s" % subnetId2)
    else:
        print("Create Subnet failed")
    create_rtb_response = ec2_client.create_route_table(VpcId=vpcId)
    if create_rtb_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        rtbId = create_rtb_response['RouteTable']['RouteTableId']
        print("Created Route Table ID %s in VPC %s" % (rtbId, vpcId))
    else:
        print("Create route-tables failed")
    create_route_response = ec2_client.create_route(DestinationCidrBlock='0.0.0.0/0',
                                                    GatewayId=igwId,
                                                    RouteTableId=rtbId)
    if create_route_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Created routing rule VPC with ID %s" % vpcId)
    else:
        print("Create routing rule failed")
    associate_rtb_response = ec2_client.associate_route_table(RouteTableId=rtbId,
                                                              SubnetId=subnetId)

    # check create route returned successfully
    if associate_rtb_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Associated route table %s to subnet %s" % (rtbId, subnetId))
    else:
        print("Associated route table failed")
    create_sg_response = ec2_client.create_security_group(GroupName='my_ELB_SG_%s' % run_index,
                                                          Description='Allow traffic for ELB',
                                                          VpcId=vpcId)
    if create_sg_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        sgId = create_sg_response['GroupId']
        print("Created security-group with ID %s" % sgId)
    else:
        print("Create security-group failed")
    allow_ingress_response = ec2_client.authorize_security_group_ingress(GroupId=sgId,
                                                                         IpPermissions=[
                                                                             
                                                                             {"IpProtocol": "tcp", "FromPort": PORT_INTERNAL, "ToPort": PORT_INTERNAL, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
                                                                         ])
    if allow_ingress_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Allow security group ingress for HTTP")
    else:
        print("Allow security group ingress failed")
    print ("Starting to run target instances")
    run_instances_response = ec2_client.run_instances(ImageId=IMAGE_ID, InstanceType=INSTANCE_TYPE,
                                                      MaxCount=TARGETS_COUNT, MinCount=TARGETS_COUNT,
                                                      SecurityGroupIds=[sgId], SubnetId=subnetId)
    if run_instances_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        targetIds = [instance['InstanceId'] for instance in run_instances_response['Instances']]
        print ("Created instances: " + ' '.join(p for p in targetIds))
    else:
        print("Create instances failed")
    time.sleep(20)
    def my_list_lbs():
        lbs_list_response = elb_client.describe_load_balancers()
        if lbs_list_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print ("LBs list: " + ' '.join(p for p in [lb['LoadBalancerName']
                                           for lb in lbs_list_response['LoadBalancers']]))
        else:
            print ("List lbs failed")

    my_list_lbs()
    create_lb_sg_response = ec2_client.create_security_group(GroupName='internet-load-balancer_%s' % run_index,
                                                             Description='Security Group for Internet-facing LB',
                                                             VpcId=vpcId)
    if create_lb_sg_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        lbSgId = create_lb_sg_response['GroupId']
        print("Created LB security-group with ID %s" % lbSgId)
    else:
        print("Create LB security-group failed")
    allow_ingress_response = ec2_client.authorize_security_group_ingress(GroupId=lbSgId,
                                                                         IpPermissions=[
                                                                             {"IpProtocol": "tcp", "FromPort": PORT_EXTERNAL,
                                                                              "ToPort": PORT_EXTERNAL, "IpRanges": [{"CidrIp": "0.0.0.0/0"}]}
                                                                         ])
    if allow_ingress_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Allow security group ingress for ICMP and TCP")
    else:
        print("Allow security group ingress failed")
    allow_egress_response = ec2_client.authorize_security_group_egress(GroupId=lbSgId,
                                                                       IpPermissions=[
                                                                           {"IpProtocol": "tcp",
                                                                            "FromPort": PORT_INTERNAL,
                                                                            "ToPort": PORT_INTERNAL,
                                                                            "UserIdGroupPairs": [{'GroupId': sgId}]}
                                                                       ])
    if allow_egress_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Allow security group egress for ICMP and TCP")
    else:
        print("Allow security group egress failed")
    create_lb_response = elb_client.create_load_balancer(Name='my-lb-%s' % run_index,
                                                         Subnets=[subnetId, subnetId2],
                                                         SecurityGroups=[lbSgId],
                                                         Scheme='internet-facing')
    if create_lb_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        lbId = create_lb_response['LoadBalancers'][0]['LoadBalancerArn']
        print ("Successfully created load balancer %s" % lbId)
    else:
        print ("Create load balancer failed")

    my_list_lbs()
    create_tg_response = elb_client.create_target_group(Name='my-lb-tg-%s' % run_index,
                                                        Protocol='HTTP',
                                                        Port=PORT_INTERNAL,
                                                        VpcId=vpcId)

    if create_tg_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        tgId = create_tg_response['TargetGroups'][0]['TargetGroupArn']
        print ("Successfully created target group %s" % tgId)
    else:
        print ("Create target group failed")

    targets_list = [dict(Id=target_id, Port=PORT_INTERNAL) for target_id in targetIds]
    reg_targets_response = elb_client.register_targets(TargetGroupArn=tgId, Targets=targets_list)

    # check register group returned successfully
    if reg_targets_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print ("Successfully registered targets")
    else:
        print ("Register targets failed")

    # create Listener
    create_listener_response = elb_client.create_listener(LoadBalancerArn=lbId,
                                                          Protocol='HTTP', Port=PORT_EXTERNAL,
                                                          DefaultActions=[{'Type': 'forward',
                                                                           'TargetGroupArn': tgId}])
    if create_listener_response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print ("Successfully created listener %s" % tgId)
    else:
        print ("Create listener failed")

if __name__ == '__main__':
    sys.exit(main())
