def lambda_handler(event, context):
	# TODO implement
	import boto3
	import botocore

	vRegion = 'us-west2'
	vInstance = 'i-0754fc16ea28e6e6c'

	def exception_handle():
		print "=======\nERROR:", err, "\n======="
		return

	print "\n=======Command Input: event =", event, "context = ", context

	if event['key1'] == 'describe':
		try:
			ec2_client = boto3.client('ec2')
			awsCmds = ec2_client.describe_instances(InstanceIds=[vInstance])
			print "=======\nMSG: Describe Instances ", awsCmds, "\n======="
		except botocore.exceptions.ClientError as err:
			exception_handle()
	else:
		print "\n=======Invalid input: ", event['key1']