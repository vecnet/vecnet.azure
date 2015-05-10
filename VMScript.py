from settings_local import STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, SUBSCRIPTION_ID, EMAIL_PASSWORD, EMAIL_USERNAME

__author__ = 'Natalie Sanders'

import os
import socket
import zipfile
import pickle
import smtplib
import logging
import subprocess
from azure.servicemanagement import *
from azure.storage import *
from subprocess import call
from os import chdir
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

global user_info


def end_sequence():

    if user_info["delete"]:
        delete_vm()

    sys.exit


def delete_vm():
    hosted_service = sms.get_hosted_service_properties(service_name=username, embed_detail=True)

    if hosted_service.deployments:
        deployment = sms.get_deployment_by_name(username, username)
        roles = deployment.role_list

        for instance in roles:
            if vm_name == instance.role_name:
                if len(roles) == 1:
                    sms.delete_deployment(service_name=username, deployment_name=username)
                else:
                    sms.delete_role(service_name=username, deployment_name=username, role_name=vm_name)
                    break

                
def send_mail(send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)

    if isTls:
        smtp.starttls()

    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

    
def upload_results():

    ####### Upload Final Results ########
    z = zipfile.ZipFile(user_info["sim"] + '_Results.zip', "w", zipfile.ZIP_DEFLATED)

    if user_info["sim_type"] == "Mock":
        for f in os.listdir("Input"):
            chdir("c:/Users/Public/Sim/Input")
            z.write(f)
        chdir("c:/Users/Public/Sim/Output")
        z.write("stdout.txt")
    else:
        # Zip output directory
        for result in os.listdir('Output'):
            chdir("c:/Users/Public/Sim/Output")
            z.write(result)
        z.close()

    result = 'r-' + vm_name
    blob_service.put_block_blob_from_path(container_name, result, 'c:/Users/Public/Sim/' + user_info["sim"] + '_Results.zip')


def download_input():

    if not os.path.exists('c:/Users/Public/Sim') or not os.path.isdir('c:/Users/Public/Sim'):
        os.mkdir('c:/Users/Public/Sim')

    blob_service.get_blob_to_path(container_name, vm_name, 'c:/Users/Public/Sim/Inputs.zip')
    chdir("C:/Users/Public/Sim")
    z = zipfile.ZipFile('Inputs.zip', 'r')
    z.extractall()
    z.close()

    for f in os.listdir('C:/Users/Public/Sim'):
        if ".xml" in f:
            return f

    return 0

class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())


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

##### Import service management certificate ####
call(['certutil', '-user', '-f', '-p', '1', '-importPFX', 'c:/temp/azure.pfx'])

sms = ServiceManagementService(subscription_id, certificate_path)

###### Redirect stdout and stderr to File ######
chdir('C:/Users/Public/Sim')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    filename="Output/stdout.log",
    filemode='a')

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl
 
stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl

f = open("Output/stdout.log")

############# Download Input Files #############
blob_service = BlobService(
    account_name=STORAGE_ACCOUNT_NAME,
    account_key=STORAGE_ACCOUNT_KEY)

try:
    scenario = download_input()
    f = "C:/Users/Public/Sim/AzureUserInfo.pickle"
    user_info = pickle.load(file(f))

except:
    sys.stdout.write('Could not download and/or initialize input.\n')
    stderr_logger.exception("Download Input: ")
    end_sequence()

######### Determine Simulation to Run ##########
sim_type = user_info["sim_type"]

################ Run Simulation ################
if sim_type == "EMOD":
    sys.stdout.write("Executing EMOD simulation...\n")
    call(["eradication.exe", "-C",  "config.json", "-O", "Output"])
elif sim_type == "OM":
    sys.stdout.write("Executing Open Malaria simulation...\n")
    if scenario == 0:
        sys.stderr.write("No valid input for xml scenario\n")
    else:
        call(["openMalaria.exe", "-s",  scenario, "-ctsout", "Output/ctsout.txt"], stdout = f, stderr = f)
        
elif sim_type == "mock":
    sys.stdout.write("Executing Mock Model...\n")
else:
    sys.stderr.write(sim_type + " is not a valid simulation\n")


################# Send Results #################
try:
    send_mail(send_from='vecnet.results@gmail.com',
              send_to=user_info["email"],
              subject='The results for your ' + user_info["sim"] + ' simulation are ready!',
              text='Hi ' + user_info['username'] + ',\n\nYour ' + user_info["sim"] + ' simulation has '
                   'finished running. Look for your results below.\n\nThanks for using VecNet Azure '
                   'resources!\nThe VecNet Team',
              files=['c:/Users/Public/Sim/' + user_info["sim"] + '_Results.zip'],
              server="smtp.gmail.com",
              port=587,
              username=EMAIL_USERNAME,
              password=EMAIL_PASSWORD,
              isTls=True)
    sys.stdout.write("Emailed results.\n")

except:
    sys.stderr.write('Could not email results to user.\n')
    stderr_logger.exception("Email Results: ")

# Also try uploading results
try:
    upload_results()
    sys.stdout.write("Uploaded results to cloud.\n")

except:
    sys.stderr.write('Could not upload results to the cloud.\n')
    stderr_logger.exception("Upload Input: ")

########## Cleanup Sequence of Script ##########
end_sequence()
