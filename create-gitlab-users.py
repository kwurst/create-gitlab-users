#!/usr/bin/env python3
# Copyright (C) 2013 Karl R. Wurst
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA

####################################################################
# Creates user accounts for GitLab from a class list generated by Blackboard
#
# To get the class list:
#   From within Blackboard, go to Grade Center:Full Grade Center
#   From Work Offline, choose Download
#   Choose Comma delimiter, and click Submit
#   Download the file.
#
# Call as:
#   python create-gitlab-users.py filename
#
# where filename is the path/name of the CSV file
#
# Requires pyapi-gitlab https://github.com/Itxaka/pyapi-gitlab
# Reads your private GitLab API token from the file gitlabtoken.txt

import argparse
import csv
import sys
import gitlab   # Requires pyapi-gitlab https://github.com/Itxaka/pyapi-gitlab

GITLAB_URL = 'https://git.cs.worcester.edu'     # replace with yours
EMAIL_DOMAIN = '@worcester.edu'                 # replace with yours

# Set up to parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('filename', help='Blackboard CSV filename with user information')
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
args = parser.parse_args()

# Get my private GitLab token
# stored in a file so that I can .gitignore the file
token = open('gitlabtoken.txt').readline().strip()

# Create a GitLab object
# For our server, verify_ssl has to be False, since we have a self-signed certificate
git = gitlab.Gitlab(GITLAB_URL, token, verify_ssl=False)

# Needs utf-8 to handle the strange character Bb puts at the beginning of the file
f = open(args.filename, encoding='utf-8')
f.readline() # throw away header line

c = csv.reader(f)
# CSV file stores user information as follows:
# last name, first name, username, student_id, other stuff I ignore...

for row in c:

    name = row[1] + ' ' + row[0]        # rebuild full name
    username = row[2]
    email = row[2] + EMAIL_DOMAIN       # create email address
    
    # GitLab will not include the password in the notification email.
    # GitLab will send a confirmation email that will log the user into their account
    #   but it does not force them to change their password! You should remind them to do so!
    password = row[2] + row[3]          # username + student_id

    # Create the account  
    success = git.createuser(name, username, password, email)

    if not success:
        sys.stderr.write('Failed to create acccount for: '+name+ ', '+username+', '+email+'\n') 
    elif args.verbose:
        sys.stderr.write('Created account for: '+name+', '+username+', '+email+', '+password+'\n')
        
