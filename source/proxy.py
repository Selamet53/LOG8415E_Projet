# Proxy Setup
def create_security_group_proxy(self):
    response = self.ec2.create_security_group(
        GroupName='proxy-security-group',
        Description='Security group for proxy instance',
        VpcId=self.vpc_id
    )
    security_group_id = response.group_id

    self.ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            # { # Port open to any ip outside
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

    print(f"Created Security Group: {security_group_id} for the proxy")
    return security_group_id

def launch_proxy(self):
    security_group_id = self.create_security_group_proxy()

    self.proxy = self.ec2.create_instances(
        ImageId='ami-0e86e20dae9224db8',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.large',
        SecurityGroupIds= [security_group_id],
        KeyName='my_key_pair',
        UserData = self.userData_Proxy
    )
