#!/usr/bin/python

import sys
import subprocess
import json
import readline

## -------------------------------------------
## Let's make sure we have everything we need. 
## -------------------------------------------

try:
    aws_action = sys.argv[1]
    aws_instance = sys.argv[2]
except: 
    print "USAGE: %s [register|deregister] [instance_id]" % sys.argv[0]
    sys.exit()

if aws_action != 'register' and aws_action != 'deregister':
    print "I don't know how to %s..." % aws_action
    print "USAGE: %s [register|deregister] [instance_id]" % sys.argv[0]
    sys.exit()


## --------------------------------------
## Are we really sure we want to do this?
## --------------------------------------

print "\033[1;41mTHIS ACTION WILL BE PERFORMED ON ALL EXISTING TARGET GROUPS\033[1;m"
print "\033[1;41m%s instance id=%s \033[1;m" %(aws_action.upper(),aws_instance.upper())

proceed = raw_input("Enter YES to proceed, press ENTER to quit: ")

if proceed != "YES":
    print "\nConfucious say, \"Measure twice, cut once.\""
    print "Exiting..."
    sys.exit()


## ----------------------------
## Time for some action...
## ----------------------------

aws_command_tgroups = "aws elbv2 describe-target-groups"
target_groups_data = subprocess.check_output(aws_command_tgroups, shell=True)
tg_json = json.loads(target_groups_data)
exception = 0

for tgroup_obj in tg_json['TargetGroups']:
    #print "## TARGET GROUP: %s " % (tgroup_obj['TargetGroupName'])

    ## ------------------------------------------------------------------------------
    ## Get tags from load balancer if they exists. Hopefully has domain as a tag. 
    ## If there is no tag Key = domain nothing will be displayed.
    ## ------------------------------------------------------------------------------

    try: 
        tgroup_obj['LoadBalancerArns'][0]
    except:
	exception = 1
        #print "## Target group not assigned to an elbv2"
    else:    
        aws_command_tags = "aws elbv2 describe-tags --resource-arns " + tgroup_obj['LoadBalancerArns'][0]
        target_group_tags = subprocess.check_output(aws_command_tags, shell=True)
        tg_tags_json = json.loads(target_group_tags)
        
        try: 
            tg_tags_json['TagDescriptions'][0]['Tags'][0]['Key']
        except: 
	    exception = 1
            #print "## No tags."
        else:
            found_domain = 'false';
            #for keys in tg_tags_json['TagDescriptions'][0]['Tags']:
             #   if (keys['Key'] == "domain"):
                    #print "## %s" % keys['Value']
              #      found_domain = 'true';
            #if found_domain == 'false':
                #print "## No tags."
    
    ## ---------------------------------------------------
    ## These commands register or deregister the instance.
    ## ---------------------------------------------------

    if aws_action == 'deregister': 
        print "aws elbv2 deregister-targets --target-group-arn %s --targets Id=%s" % (tgroup_obj['TargetGroupArn'],aws_instance)
    elif aws_action == 'register':
        print "aws elbv2 register-targets --target-group-arn %s --targets Id=%s" % (tgroup_obj['TargetGroupArn'],aws_instance)
    

## Fin.
