import random

class ThrottlingException(Exception):
    pass

class FakeEC2Client:
    """Mimics boto3 ec2.describe_volumes. Returns 2 volumes per page."""
    def __init__(self):
        self._volumes = [
            {"VolumeId": "vol-01", "State": "in-use", "Size": 100,
             "Tags": [{"Key": "Owner", "Value": "billing"}, {"Key": "Env", "Value": "prod"}]},
            {"VolumeId": "vol-02", "State": "available", "Size": 500,
             "Tags": [{"Key": "Owner", "Value": "data"}]},
            {"VolumeId": "vol-03", "State": "available", "Size": 50},
            {"VolumeId": "vol-04", "State": "in-use", "Size": 200,
             "Tags": [{"Key": "Env", "Value": "dev"}]},
            {"VolumeId": "vol-05", "State": "in-use", "Size": 20,
             "Tags": [{"Key": "Owner", "Value": "ops"}, {"Key": "Env", "Value": "prod"}]},
        ]

    def describe_volumes(self, NextToken=None):
        if random.random() < 0.3:
            raise ThrottlingException("Rate exceeded")
        start = int(NextToken) if NextToken else 0
        page = self._volumes[start:start + 2]
        resp = {"Volumes": page}
        if start + 2 < len(self._volumes):
            resp["NextToken"] = str(start + 2)
        return resp