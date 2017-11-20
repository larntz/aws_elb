#!/usr/bin/python

import sys
import subprocess
import json
import readline
import boto3

## ----------------------------
## Time for some action...
## ----------------------------
aws_command_desc_lb = "aws elbv2 describe-load-balancers"
desc_lb_data = subprocess.check_output(aws_command_desc_lb, shell=True)
lb_json = json.loads(desc_lb_data)

for lb_obj in lb_json['LoadBalancers']:
    print "LB Name: %s " % (lb_obj['LoadBalancerName'])
    print "    LB ARN: %s " % (lb_obj['LoadBalancerArn'])


    ## ------------------------------------------------------------------------------
    ## Get tags from load balancer if they exists. Hopefully has domain as a tag. 
    ## If there is no tag Key = domain pring ####
    ## ------------------------------------------------------------------------------

    try: 
        lb_obj['LoadBalancerArn']
    except:
        print "Error 123412362"
    else:    
        aws_command_tags = "aws elbv2 describe-tags --resource-arns " + lb_obj['LoadBalancerArn']
        lb_tags = subprocess.check_output(aws_command_tags, shell=True)
        lb_tags_json = json.loads(lb_tags)
        
        try: 
            lb_tags_json['TagDescriptions'][0]['Tags'][0]['Key']
        except: 
            print "    ####"
        else:
            found_domain = 'false';
            for keys in lb_tags_json['TagDescriptions'][0]['Tags']:
                if (keys['Key'] == "domain"):
                    print "    domain tag: %s" % keys['Value']
                    found_domain = 'true';
            if found_domain == 'false':
                print "## No tags."
    

## Fin.
