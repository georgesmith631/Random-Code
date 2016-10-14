import boto3
import botocore
import pickle
import sys

if len(sys.argv) < 2:
	print "Usage : python sandbox_ec2 <action> \n"
	print "Valid entries are: 'new_user', 'del_user', 'new_sanbox', 'del_sandbox', 'new_snap' \n"
	sys.exit()

vRegion = 'us-west2'
vuName = 'smgeo-sandbox'
vuPass = 'sandbox1'
vuGroup = 'FullCLI'
vCidrBlock = '172.72.72.0/28'
vgwCidrBlock = '0.0.0.0/0'
vsgName = 'sandbox2'
vsgDesc = 'Sandbox Security Group'
vKeyName = 'sandbox-keypair2'
vImageId = 'ami-7f77b31f'
vMinCount = 1
vMaxCount = 1
vInstanceType = 'm1.small'
vssDesc = 'Sanbox EBS Snap Shot'
file_Name = "awsInfraVars"


def exception_handle():
	print "=======\nERROR:", err, "\n======="
	fileObject = open(file_Name, 'wb')
	pickle.dump(awsCmds,fileObject)
	fileObject.close()
	fileObject = open(file_Name, 'wb')
	return

try:
	fileObject = open(file_Name, 'rb')
	awsCmds = pickle.load(fileObject)
	fileObject.close()
	fileObject = open(file_Name, 'wb')
except EOFError:
	fileObject.close()
	fileObject = open(file_Name, 'wb')
	awsCmds = {}
except IOError:
	fileObject = open(file_Name, 'wb')
	awsCmds = {}

print "\n=======Command Input: ",sys.argv[1]

if   sys.argv[1] == 'new_user':
	iam_client = boto3.client('iam')
	try:
		awsCmds['new_user'] = iam_client.create_user(UserName=vuName)
		print "=======\nMSG: Created New User ", awsCmds['new_user'], "\n======="
	except	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_profile'] = iam_client.create_login_profile(UserName=vuName,
								Password=vuPass,
								PasswordResetRequired=False
								)
		print "=======\nMSG: Created New Profile ", awsCmds['new_profile'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['user_to_group'] = iam_client.add_user_to_group(GroupName=vuGroup,
							UserName=vuName)
		print "=======\nMSG: Created New User to Group Mapping ", awsCmds['user_to_group'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_access_key'] = iam_client.create_access_key(UserName=vuName)
		print "=======\nMSG: Created New Access Key ", awsCmds['new_access_key'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
elif sys.argv[1] == 'del_user':
	iam_client = boto3.client('iam')
	try:
		awsCmds['del_profile'] = iam_client.delete_login_profile(UserName=vuName)
		print "=======\nMSG: Deleted Login Profile ", awsCmds['del_profile'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['rm_user_from_group'] = iam_client.remove_user_from_group(GroupName=vuGroup,
											UserName=vuName
											)
		print "=======\nMSG: Removed User from Group ", awsCmds['rm_user_from_group'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_access_key'] = iam_client.delete_access_key(UserName=vuName,
						AccessKeyId=awsCmds['new_access_key']['AccessKey']['AccessKeyId']
						)
		print "=======\nMSG: Deleted Access Key ", awsCmds['del_access_key'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_user'] = iam_client.delete_user(UserName=vuName)
		print "=======\nMSG: Deleted User ", awsCmds['del_user'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
elif sys.argv[1] == 'new_sandbox':
	try:
		ec2_client = boto3.client('ec2',
				aws_access_key_id=awsCmds['new_access_key']['AccessKey']['AccessKeyId'],
				aws_secret_access_key=awsCmds['new_access_key']['AccessKey']['SecretAccessKey']
				)
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_vpc'] = ec2_client.create_vpc(CidrBlock=vCidrBlock)
		print "=======\nMSG: Created New VPC ", awsCmds['new_vpc'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['modify_vpc'] = ec2_client.modify_vpc_attribute(VpcId=awsCmds['new_vpc']['Vpc']['VpcId'],
									EnableDnsSupport={'Value':True},
									)
		print "=======\nMSG: Modified VPC ", awsCmds['modify_vpc'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['modify_vpc'] = ec2_client.modify_vpc_attribute(VpcId=awsCmds['new_vpc']['Vpc']['VpcId'],
									EnableDnsHostnames={'Value':True}
									)
		print "=======\nMSG: Modified VPC ", awsCmds['modify_vpc'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_subnet'] = ec2_client.create_subnet(VpcId=awsCmds['new_vpc']['Vpc']['VpcId'],
						CidrBlock=awsCmds['new_vpc']['Vpc']['CidrBlock']
						)
		print "=======\nMSG: Created New Subnet ", awsCmds['new_subnet'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
#  Not sure how to attach the ssh rule to the security group to allow ssh conections in from the igw
	try:
		awsCmds['new_sg'] = ec2_client.create_security_group(GroupName=vsgName,
							Description=vsgDesc,
							VpcId=awsCmds['new_vpc']['Vpc']['VpcId']
							)
		print "=======\nMSG: Created New SG ", awsCmds['new_sg'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_gw'] = ec2_client.create_internet_gateway()
		print "=======\nMSG: Created Internet GW ", awsCmds['new_gw'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_gw_attach'] = ec2_client.attach_internet_gateway(
							InternetGatewayId=awsCmds['new_gw']['InternetGateway']['InternetGatewayId'],
							VpcId=awsCmds['new_vpc']['Vpc']['VpcId']
							)
		print "=======\nMSG: Attached New GW ", awsCmds['new_gw_attach'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
#  Instead of creating a new route table, describe the route table for the VPC and create a new route in the existing route tbl
#	try:
#		awsCmds['new_route_table'] = ec2_client.create_route_table(VpcId=awsCmds['new_vpc']['Vpc']['VpcId'])
#		print "=======\nMSG: Created New Route Table ", awsCmds['new_route_table'], "\n======="
#	except 	botocore.exceptions.ClientError as err:
#		exception_handle()
	try:
		awsCmds['desc_route'] = ec2_client.describe_route_tables(Filters=[
											{
											'Name':'vpc-id',
											'Values':[awsCmds['new_vpc']['Vpc']['VpcId']]
											}
										 ]
									)
		print "=======\nMSG: Describe New Route ", awsCmds['desc_route'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()

	try:
		awsCmds['new_route'] = ec2_client.create_route(RouteTableId=awsCmds['desc_route']['RouteTables'][0]['RouteTableId'],
						DestinationCidrBlock=vgwCidrBlock,
						GatewayId=awsCmds['new_gw']['InternetGateway']['InternetGatewayId']
						)
		print "=======\nMSG: Created New Route ", awsCmds['new_route'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_keypair'] = ec2_client.create_key_pair(KeyName=vKeyName)
		print "=======\nMSG: Created New Keypair ", awsCmds['new_keypair'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['new_instance'] = ec2_client.run_instances(ImageId=vImageId,
						MinCount=vMinCount,
						MaxCount=vMaxCount,
						KeyName=awsCmds['new_keypair']['KeyName'],
						InstanceType=vInstanceType,
						NetworkInterfaces=[
									{
									'DeviceIndex':0,
									'SubnetId': awsCmds['new_subnet']['Subnet']['SubnetId'],
									'AssociatePublicIpAddress':True,
									'Groups': [awsCmds['new_sg']['GroupId']]
									}
								  ]
						)
		print "=======\nMSG: Created New Instance ", awsCmds['new_instance'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
#
#	Potential to add code to loop waiting for the instance to completely start
#
elif sys.argv[1] == 'new_snap':
	ec2_client = boto3.client('ec2',
				aws_access_key_id=awsCmds['new_access_key']['AccessKey']['AccessKeyId'],
				aws_secret_access_key=awsCmds['new_access_key']['AccessKey']['SecretAccessKey']
				)
	try:
		testit = awsCmds['new_instance']['Instances'][0]['InstanceId']
		my_instances = ec2_client.describe_instances(
				InstanceIds=[testit]
				)
		awsCmds['new_snapshot'] = ec2_client.create_snapshot(
					VolumeId=my_instances['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId'],
					Description=vssDesc
					)
		print "=======\nMSG: Created New Snapshot ", awsCmds['new_snapshot'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
elif sys.argv[1] == 'term_instance':
	ec2_client = boto3.client('ec2',
				aws_access_key_id=awsCmds['new_access_key']['AccessKey']['AccessKeyId'],
				aws_secret_access_key=awsCmds['new_access_key']['AccessKey']['SecretAccessKey']
				)
	try:
		awsCmds['term_instance'] = ec2_client.terminate_instances(InstanceIds=[awsCmds['new_instance']['Instances'][0]['InstanceId']])
		print "=======\nMsg: Terminating Instance ", awsCmds['term_instance'], "\n======="
	except  botocore.exceptions.ClientError as err:
		exception_handle()
#
#	Potential to add code to loop waiting for the instance to completely terminate
#
elif sys.argv[1] == 'del_sandbox':
	ec2_client = boto3.client('ec2',
				aws_access_key_id=awsCmds['new_access_key']['AccessKey']['AccessKeyId'],
				aws_secret_access_key=awsCmds['new_access_key']['AccessKey']['SecretAccessKey']
				)
	try:
		awsCmds['del_route'] = ec2_client.delete_route(RouteTableId=awsCmds['desc_route']['RouteTables'][0]['RouteTableId'],
						DestinationCidrBlock=vgwCidrBlock,    # <===== This is the open internet CidrBlock?
						)
		print "=======\nMSG: Deleting Route ", awsCmds['del_route'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
#	try:
#		awsCmds['del_route_table'] = ec2_client.delete_route_table(
#							RouteTableId=awsCmds['new_route_table']['RouteTable']['RouteTableId']
#							)
#		print "=======\nMSG: Deleting Route Table ", awsCmds['del_route_table'], "\n======="
#	except 	botocore.exceptions.ClientError as err:
#		exception_handle()
	try:
		awsCmds['det_gw'] = ec2_client.detach_internet_gateway(
							InternetGatewayId=awsCmds['new_gw']['InternetGateway']['InternetGatewayId'],
							VpcId=awsCmds['new_vpc']['Vpc']['VpcId']
							)
		print "=======\nMSG: Detaching GW ", awsCmds['det_gw'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_gw'] = ec2_client.delete_internet_gateway(
						InternetGatewayId=awsCmds['new_gw']['InternetGateway']['InternetGatewayId']
						)
		print "=======\nMSG: Deleting GW ", awsCmds['del_gw'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_sg'] = ec2_client.delete_security_group( #GroupName=vsgName,  <==== This Worked
							GroupId=awsCmds['new_sg']['GroupId']
							)
		print "=======\nMSG: Deleting Security Group ", awsCmds['del_sg'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_subnet'] = ec2_client.delete_subnet(SubnetId=awsCmds['new_subnet']['Subnet']['SubnetId'])
		print "=======\nMSG: Deleting Subnet ", awsCmds['del_subnet'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_vpc'] = ec2_client.delete_vpc(VpcId=awsCmds['new_vpc']['Vpc']['VpcId'])
		print "=======\nMSG: Deleting VPC ", awsCmds['del_vpc'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
	try:
		awsCmds['del_keypair'] = ec2_client.delete_key_pair(KeyName=awsCmds['new_keypair']['KeyName'])
		print "=======\nMSG: Deleting Keypair ", awsCmds['del_keypair'], "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()
elif sys.argv[1] == 'del_snapshots':
	ec2_client = boto3.client('ec2',
				aws_access_key_id=awsCmds['new_access_key']['AccessKey']['AccessKeyId'],
				aws_secret_access_key=awsCmds['new_access_key']['AccessKey']['SecretAccessKey']
				)
	try:
		awsCmds['del_snapshot'] = ec2_client.delete_snapshot(awsCmds['new_snapshot']['SnapshotId'])
		print "=======\nMSG: Deleting Snapshot ", awsCmds, "\n======="
	except 	botocore.exceptions.ClientError as err:
		exception_handle()

pickle.dump(awsCmds,fileObject)
fileObject.close()

print "\n================= Ending JSON : ", awsCmds, "\n================"