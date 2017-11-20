#!/usr/bin/python

import boto3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

## Email Config
TO = "larntz@weissinc.com"
FROM = "larntz@weissinc.com"
SUBJECT = "AWS Load Balancer Configuration"

## html page Config
FILE = "/var/www/html/awslb.html"
DATE = datetime.datetime.now()

awslbhtml = open(FILE,"w")

awslbhtml.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"UTF-8\">\n<title>AWS Load Balancer Configuration</title></head>\n")
awslbhtml.write("<body style=\"font-family:consolas\">\n")
awslbhtml.write("<h1>AWS Load Balancer Configuration</h1>\n<small>Updated: " + str(DATE) + "</small>\n")




elbv2_client = boto3.client('elbv2')

desc_lb  = elbv2_client.describe_load_balancers()

awslbhtml.write("<h2>{} Total LoadBalancers</h2>\n".format(len(desc_lb['LoadBalancers'])))


for lb_obj in desc_lb['LoadBalancers']:
    awslbhtml.write("<hr>\n")
    awslbhtml.write( "<h3>LB Name: {}</h3>\n".format(lb_obj['LoadBalancerName']))
    awslbhtml.write( "<small>Created: {}</small><br>\n".format(lb_obj['CreatedTime']))
    awslbhtml.write( "<p style=\"margin-left:2em\">LB ARN: {}</p>\n".format(str(lb_obj['LoadBalancerArn'])))

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
                    awslbhtml.write("<p style=\"margin-left:2em\"><blue>Certificate Domains: {}</blue><br>\n".format(domains))

                    awslbhtml.write("Listener HTTPS on port {} using certificate {}<br>\n".format(listener['Port'],listener['Certificates'][0]['CertificateArn']))

                    target_group_arn_https =  listener['DefaultActions'][0]['TargetGroupArn']
                    desc_target_groups = elbv2_client.describe_target_groups(
                        TargetGroupArns=[target_group_arn_https])
                    awslbhtml.write("-  Listener target group name: {}<br>\n".format(desc_target_groups['TargetGroups'][0]['TargetGroupName']))

                    desc_target_group_health = elbv2_client.describe_target_health(
                        TargetGroupArn=target_group_arn_https)
                    awslbhtml.write("- {} instances in target group.<br>\n".format(len(desc_target_group_health['TargetHealthDescriptions'])))
                    for target in desc_target_group_health['TargetHealthDescriptions']:
                        if (target['TargetHealth']['State'] != 'healthy'):
                         awslbhtml.write("-- {} status {}<br>\n".format(target['Target']['Id'],target['TargetHealth']['State']))
                        else:
                         awslbhtml.write("-- {} status {}<br>\n".format(target['Target']['Id'],target['TargetHealth']['State']))
                    awslbhtml.write("</p>\n")

                elif (listener['Protocol'] == "HTTP"):
                    awslbhtml.write("<p style=\"margin-left:2em\">Listener HTTP on port {}<br>\n".format(listener['Port']))
                    target_group_arn_http =  listener['DefaultActions'][0]['TargetGroupArn']
                    desc_target_groups = elbv2_client.describe_target_groups(
                        TargetGroupArns=[target_group_arn_http])
                    awslbhtml.write("- Listener target group name: {}<br>\n".format(desc_target_groups['TargetGroups'][0]['TargetGroupName']))

                    desc_target_group_health = elbv2_client.describe_target_health(
                        TargetGroupArn=target_group_arn_http)
                    awslbhtml.write("- {} instances in target group.<br>\n".format(len(desc_target_group_health['TargetHealthDescriptions'])))
                    for target in desc_target_group_health['TargetHealthDescriptions']:
                        if (target['TargetHealth']['State'] != 'healthy'):
                         awslbhtml.write("-- {} status {}<br>\n".format(target['Target']['Id'],target['TargetHealth']['State']))
                        else:
                         awslbhtml.write("-- {} status {}<br>\n".format(target['Target']['Id'],target['TargetHealth']['State']))
                    awslbhtml.write("</p>\n")

awslbhtml.write("</body></html>\n")
awslbhtml.close()


## Fin. 
