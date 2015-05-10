__author__ = 'Natalie'

import os
import contextlib
import shutil
from subprocess import Popen
from getpass import getuser
import Tkinter as tk
import sys
from threading import Lock


class subscriptionDialog:
    def __init__(self):
        # Acquire Lock
        mutex.acquire();

        self.root = tk.Tk()

        self.nameLbl = tk.Label(self.root, text='Azure Subscription Name:')
        self.nameLbl.pack()

        self.nameEntry = tk.Entry(self.root)
        self.nameEntry.pack()

        self.idLbl = tk.Label(self.root, text='Azure Subscription ID:')
        self.idLbl.pack()

        self.idEntry = tk.Entry(self.root)
        self.idEntry.pack()

        self.submitBttn = tk.Button(self.root, text='Submit', command=self.send)
        self.submitBttn.pack()

        self.root.mainloop()


    def send(self):
        subscription_name = self.nameEntry.get()
        subscription_id   = self.idEntry.get()

        if subscription_name and subscription_id:
            upload = Popen(['powershell', 'upload_cert.ps1'])
            r = upload.wait()

            if r < 0:
                sys.stderr.write("ERROR: Certificate upload to Windows Azure failed\n")
                success = False

            mutex.release()
            self.root.destroy()

@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


if __name__ == "__main__":
    global subscription_name, subscription_id, success, mutex

    mutex = Lock()
    subscription_name = None
    subscription_id = None
    success = True

    ############################################ Create Simulations Folder #############################################
    sim_folder = "C:/Users/" + getuser() + "/Simulations/"
    if not os.path.isdir(sim_folder):
        print "Creating VecNet Simulations folder..."
        os.mkdir(sim_folder)

    ############################################# Create Azure certificate #############################################
    print "\nCreating Windows Azure certificate..."
    os.chdir("C:/Program Files/Microsoft SDKs/Windows/v7.1/Bin/")
    create = Popen(['makecert.exe', '-sky', 'exchange', '-r', '-n', 'CN=AzureCertificate',
                    '-pe', '-a', 'sha1', '-len', '2048', '-ss', 'VecNet',
                    'D:\\Naki\'s Data\\My Documents\\CRC Internship\\vecnetCert2.cer'])

    r = create.wait()

    if r < 0:
        sys.stderr.write("ERROR: Microsoft Azure certificate creation failed\n")
        success = False

    ############################################# Install Azure certificate ############################################
    print "\nInstall Windows Azure certificate..."
    os.chdir("D:/Naki's Data/My Documents/CRC Internship/")
    install = Popen(['certutil', '-user', '-f', '-addstore', 'VecNet', 'vecnetCert2.cer'])
    r = install.wait()

    if r < 0:
        sys.stderr.write("ERROR: Installation of Microsoft Azure certificate failed.\n")
        success = False

    ########################### Run powershell script to upload Azure Certificate to Azure #############################
    dialog = subscriptionDialog()

    print "\nUpload certificate to Windows Azure..."

    f = open("upload_cert.ps1", "w")
    f.write("Set-AzureSubscription -SubscriptionName \"" + subscription_name +      #
            "\" -SubscriptionId \"" + subscription_id +                             # 15fee040-58a2-4882-8c49-126902f64612
            "\" -Certificate \"vecnetCert.cer\"")
    f.close()

    ########################################### Run diskpart script to create VHD ######################################
    print "\nCreating VHD data disk for VecNet..."
    f = open("create_datadisk.txt", "w")

    f.write("create vdisk file=vecnetDataDisk.vhd MAXIMUM=100\n")
    f.write("select vdisk file=vecnetDataDisk.vhd\n")
    f.write("attach vdisk\n")
    f.write("convert mbr\n")
    f.write("create partition primary\n")
    f.write("format fs=ntfs label=\"VecNet Data\" quick\n")
    f.write("assign letter=v\n")

    f.close()

    diskpart1 = Popen(['diskpart', '/s', 'create_datadisk.txt'])
    r = diskpart1.wait()

    if r < 1:
        print "VecNet data disk creation failed.\n"

    ############################################## Copy certificate onto VHD ###########################################
    shutil.copy("D:\\Naki\'s Data\\My Documents\\CRC Internship\\vecnetCert.cer", "V:\\vecnetCert.cer")

    ######################################## Run diskpart script to detach VHD #########################################
    f = open("detach_datadisk.txt", "w")

    f.write("select vdisk file=vecnetDataDisk.vhd\n")
    f.write("detach vdisk\n")

    diskpart2 = Popen(['diskpart', '/s', 'detach_datadisk.txt'])
    r = diskpart2.wait()

    if r < 1:
        print "VecNet data disk unsuccessfully detached"

    print "VecNet Azure configuration SUCCESSFUL"


    '''
    # Export Azure certificate to new data drive
    print "\nExport certificate to new data disk..."
    with stdout_redirect(StringIO()) as store_contents:
        store = sys('certutil', '-store', '-user', '-f', '\"VecNet\"')
        r = store.wait()

        if r < 1:
            print "Azure certificate export failed.\n"

    store_contents.seek(0)
    cert_list = split("^={16} Certificate \d ={16}$", store_contents)

    serial_num = None
    for cert in cert_list:
        if "Subject: AzureCertificate" in cert:
            serial_num = split(split("\n", cert)[0])[1]

            export = sys.call('certutil', '-exportPFX', '-p', '\"1\"', 'my', serial_num, 'V:\\vecnetCert.pfx')
            r = export.wait()

            break
    '''
