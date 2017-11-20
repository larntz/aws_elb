#!/usr/bin/python

import boto3
from bson import json_util
import json


# config
aws_owner_id = '' ## add owner/account id before using



ec2_client = boto3.client('ec2')

## Get lists of images, snapshots, and volumes
ec2_images = ec2_client.describe_images(
    Owners=[aws_owner_id])

ec2_snapshots = ec2_client.describe_snapshots(
    OwnerIds=[aws_owner_id])

ec2_volumes = ec2_client.describe_volumes()

aws_snapshots = {}
for snapshot in ec2_snapshots['Snapshots']:
    aws_snapshots[snapshot['SnapshotId']] = {'orphaned': True}
    aws_snapshots[snapshot['SnapshotId']]['size'] = snapshot['VolumeSize']

## Volume Info
print("")
total_volumes = len(ec2_volumes['Volumes'])
unattached_volumes = 0
aws_volume_attached_size = 0
aws_volume_unattached_size = 0
aws_unused_volumes = {}

print("VOLUMES")
for volume in ec2_volumes['Volumes']:
    if volume['State'] == 'in-use':
        aws_volume_attached_size += int(volume['Size'])
    else:
        unattached_volumes += 1
        aws_volume_unattached_size += int(volume['Size'])
        aws_unused_volumes[volume['VolumeId']] = 'unused'
    
print("{} unused vols = {} GB ({} total vols)".format(unattached_volumes,aws_volume_unattached_size,total_volumes))
print("Unused Volumes")
for volume in aws_unused_volumes: print("   {}".format(volume))

## Get Image Info
aws_snapshot_size = 0

for image in ec2_images['Images']:
    ## Get associated volume snapshots
    for bdm in image['BlockDeviceMappings']:
        if 'Ebs' in bdm:
            aws_snapshot_size += int(bdm['Ebs']['VolumeSize'])
            
            aws_snapshots[bdm['Ebs']['SnapshotId']]['orphaned'] = False

## display orphaned snapshots
print ("")
print("SNAPSHOTS")
orphaned_size = sum(values['size'] for snapshot,values in aws_snapshots.items())
print ("{} orphaned snaps = {} GB ({} total snaps)".format(sum(aws_snapshots[is_orphaned]['orphaned'] == True for is_orphaned in aws_snapshots),orphaned_size,len(aws_snapshots)))

print ("Orphaned Snapshots (not associated with an AMI):")

for snapshot in aws_snapshots:
    if aws_snapshots[snapshot]['orphaned'] == True: 
        print("   {}".format(snapshot))

