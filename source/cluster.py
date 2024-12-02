# Cluster Setup
def create_security_group_cluster(self):
    response = self.ec2.create_security_group(
        GroupName='my-security-group',
        Description='Security group for ALB and EC2 instances',
        VpcId=self.vpc_id
    )
    security_group_id = response.group_id

    self.ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            # {
            #     'IpProtocol': 'tcp',
            #     'FromPort': 8000,
            #     'ToPort': 8000,
            #     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            # },
            { # Reminder : For ssh -> remove?
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': "0.0.0.0/0"}]
            }
        ]
    )

    print(f"Created Security Group: {security_group_id} for the cluster nodes")
    return security_group_id

def launch_cluster(self):
    security_group_id = self.create_security_group_cluster()

    self.instances_micro = self.ec2.create_instances(
        ImageId='ami-0e86e20dae9224db8',
        MinCount=3,
        MaxCount=3,
        InstanceType='t3.micro',
        SecurityGroupIds= [security_group_id],
        KeyName='my_key_pair',
        UserData = self.userData_SQL
    )