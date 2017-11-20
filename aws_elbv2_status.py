#!/bin/python

import boto3

elbv2_client = boto3.client('elbv2')

desc_lb  = elbv2_client.describe_load_balancers()

print "{} Total LoadBalancers".format(len(desc_lb['LoadBalancers']))
 
for lb_obj in desc_lb['LoadBalancers']:
    print "------------------------------"
    print "> LB Name: \033[1;32;40m{}\033[0;m".format(lb_obj['LoadBalancerName'])
    print "    Created: {} ".format(lb_obj['CreatedTime'])
    print "    LB ARN: {} ".format(lb_obj['LoadBalancerArn'])

    ## ------------------------------------------------------------------------------
    ## Get additional LB information
    ## listeners, certificates, target groups
    ## ------------------------------------------------------------------------------

    try:
        lb_obj['LoadBalancerArn']
    except:
        print "* Error 8372412362"
    else:
        try: 
           desc_listeners = elbv2_client.describe_listeners(
                LoadBalancerArn=lb_obj['LoadBalancerArn'])
        except:
            print "* Error 867903213469"

        else: 
            for listener in  desc_listeners['Listeners']:
                if (listener['Protocol'] == "HTTPS"):
                    acm_client = boto3.client('acm')                    
                    desc_cert = acm_client.describe_certificate(
                        CertificateArn=listener['Certificates'][0]['CertificateArn'])
                    domains = ", ".join(str(domain) for domain in desc_cert['Certificate']['SubjectAlternativeNames'])
                    print "    Certificate Domains: \033[1;34;40m {} \033[1;m".format(domains)

                    print "    Listener HTTPS on port {} using certificate {}".format(listener['Port'],listener['Certificates'][0]['CertificateArn'])

                    target_group_arn_https =  listener['DefaultActions'][0]['TargetGroupArn']
                    desc_target_groups = elbv2_client.describe_target_groups(
                        TargetGroupArns=[target_group_arn_https])
                    print "    -  Listener target group name: \033[1;34;40m {} \033[1;m".format(desc_target_groups['TargetGroups'][0]['TargetGroupName'])

                    desc_target_group_health = elbv2_client.describe_target_health(
                        TargetGroupArn=target_group_arn_https)
                    print "     - {} instances in target group.".format(len(desc_target_group_health['TargetHealthDescriptions']))
                    for target in desc_target_group_health['TargetHealthDescriptions']:
                        if (target['TargetHealth']['State'] != 'healthy'):
                         print "        \033[1;37;41m-- {} status {}\033[1;m".format(target['Target']['Id'],target['TargetHealth']['State'])
                        else:
                         print "        -- {} status {}".format(target['Target']['Id'],target['TargetHealth']['State'])


                elif (listener['Protocol'] == "HTTP"):
                    print "    Listener HTTP on port {}".format(listener['Port'])
                    target_group_arn_http =  listener['DefaultActions'][0]['TargetGroupArn']
                    desc_target_groups = elbv2_client.describe_target_groups(
                        TargetGroupArns=[target_group_arn_http])
                    print "     - Listener target group name: \033[1;34;40m {} \033[1;m".format(desc_target_groups['TargetGroups'][0]['TargetGroupName'])

                    desc_target_group_health = elbv2_client.describe_target_health(
                        TargetGroupArn=target_group_arn_http)
                    print "     - {} instances in target group.".format(len(desc_target_group_health['TargetHealthDescriptions']))
                    for target in desc_target_group_health['TargetHealthDescriptions']:
                        if (target['TargetHealth']['State'] != 'healthy'):
                         print "        \033[1;37;41m-- {} status {}\033[1;m".format(target['Target']['Id'],target['TargetHealth']['State'])
                        else:
                         print "        -- {} status {}".format(target['Target']['Id'],target['TargetHealth']['State'])

        print "------------------------------"
        print " " # insert a blank line
## Fin. 
