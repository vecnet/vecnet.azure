from settings_local import SUBSCRIPTION_ID, ACCOUNT_NAME, ACCOUNT_KEY, EMAIL_USERNAME, EMAIL_PASSWORD

__author__ = 'Natalie Sanders'

from azure.servicemanagement import *
from azure.storage import *
from subprocess import call
from os import chdir
import os
import socket
import zipfile
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

global user_info

def send_mail( send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if isTls: smtp.starttls()
    smtp.login(username,password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
    
def upload_results():

    ####### Upload Final Results ########

    # Zip output directory
    z = zipfile.ZipFile(user_info["sim"] + '_Results.zip', "w", zipfile.ZIP_DEFLATED)
    for result in os.listdir('Output'):
        chdir("c:/Users/Public/Sim/Output")
        z.write(result)
    z.close()

    result = 'r-' + vm_name
    try:
        blob_service.put_block_blob_from_path(container_name, result, 'c:/Users/Public/Sim/' + user_info["sim"] + '_Results.zip')
    except:
        print "could not upload"


def download_input():
    blob_service.get_blob_to_path(container_name, vm_name, 'c:/Users/Public/Sim/Inputs.zip')
    chdir("C:/Users/Public/Sim")
    z = zipfile.ZipFile('Inputs.zip', 'r')
    z.extractall()
    z.close()


########################################################################################################################
##                                                        MAIN                                                        ##
########################################################################################################################

##### Service Management Object #####
vm_name = socket.gethostname()
split = vm_name.split('-')
username = '-'.join(split[:-1])
container_name = '-'.join(split[:-1]).lower()

subscription_id = SUBSCRIPTION_ID
certificate_path = 'CURRENT_USER\\my\\AzureCertificate'

# Import service management certificate
call(['certutil', '-user', '-f', '-p', '1', '-importPFX', 'c:/temp/azure.pfx'])

sms = ServiceManagementService(subscription_id, certificate_path)

###### Redirect stdout to File ######
chdir('C:/Users/Public/Sim')
output = open("Output/stdout.txt", "wb")

####### Download Input Files ########
blob_service = BlobService(
    account_name=ACCOUNT_NAME,
    account_key=ACCOUNT_KEY)

try:
    download_input()
    f = "C:/Users/Public/Sim/AzureUserInfo.pickle"

    user_info = pickle.load(file(f))
except:
    output.write('Could not download input from the cloud.\n')

########### Run Simulation ##########
call(["eradication.exe", "-C",  "config.json", "-O", "Output"], stdout=output)
output.close()

try:
    ########### Upload Results ##########
    upload_results()

    ########### Email Results ###########
    send_mail( send_from   = 'vecnet.results@gmail.com',
               send_to     = user_info["email"],
               subject     = 'The results for your ' + user_info["sim"] + ' simulation are ready!',
               text        = 'Hi ' + user_info['username'] + ',\n\nYour ' + user_info["sim"] + ' simulation has '
                             'finished running. Look for your results below.\n\nThanks for using VecNet Azure '
                             'resources!\nThe VecNet Team',
               files       = ['c:/Users/Public/Sim/' + user_info["sim"] + '_Results.zip'],
               server      = "smtp.gmail.com",
               port        = 587,
               username    = EMAIL_USERNAME,
               password    = EMAIL_PASSWORD,
               isTls       = True)
    print "sent mail"
except:
    print "mail failed"

