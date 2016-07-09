#!/usr/bin/env python

# Script to generate the last report for a given task ID in PDF format,
# containing high, medium and low severities.  Relies on environment
# variables of OV_USER and OV_PASS.

import argparse
import base64
import time
import os
import re
import subprocess
import sys
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

# Get our OpenVAS user and password
OV_USER = os.environ.get('OV_USER', None)
if not OV_USER:
  print "Error: OV_USER undefined"
  exit(1)

OV_PASS = os.environ.get('OV_PASS', None)
if not OV_PASS:
  print "Error: OV_PASS undefined"
  exit(1)

# Get our task ID
parser = argparse.ArgumentParser(description='This script retrieves the latest report for an OpenVAS task, in PDF format.')
parser.add_argument('-t','--task', help='Task ID for report retrieval', required=True)
args = parser.parse_args()

# Figure out id of PDF report type
output = subprocess.check_output(['omp', '-u', OV_USER, '-w', OV_PASS, '-F'])
line = re.search('^.*PDF$', output,re.M)
if line:
  ovformat = line.group().split('  ')[0]
else:
  print "Error: Could not retrieve PDF report type id"
  exit(1)

# Look up latest report for task ID
xmlcmd = "omp -u %s -w %s -iX '<get_tasks task_id=\"%s\" details=\"1\" />'" % (OV_USER, OV_PASS, args.task)
output = subprocess.check_output(xmlcmd, shell=True)
xmlout = ET.fromstring(output)
for node in xmlout.findall('.//task/last_report/report'):
  ovreportid = node.attrib.get('id')
for node in xmlout.findall('.//task/name'):
  ovtaskname = node.text
  ovtaskname = ovtaskname.replace(' ', '_')
  ovtaskname = ovtaskname.replace('/', '-')
  ovtaskname = ovtaskname.replace('\\', '-')

# Now, get our report
xmlcmd = "omp -u %s -w %s -iX '<get_reports report_id=\"%s\" format_id=\"%s\" levels=\"hml\"/>'" % (OV_USER, OV_PASS, ovreportid, ovformat)
output = subprocess.check_output(xmlcmd, shell=True)
xmlout = ET.fromstring(output)
for node in xmlout.findall('.//report'):
  ovreport = node.text

ovreporttime = time.strftime("%Y%m%d", time.gmtime())
target = open("%s-%s.pdf" % (ovreporttime, ovtaskname), 'w')
target.write(base64.b64decode(ovreport))
target.close()
