__author__ = 'Natalie'

import Tkinter as tk

class MyDialog:
    def __init__(self):
        #top = self.top = tk.Toplevel(parent)
        self.root = tk.Tk()

        self.myLabel1 = tk.Label(self.root, text='Enter Azure Subscription Name:')
        self.myLabel1.pack()

        self.myEntryBox1 = tk.Entry(self.root)
        self.myEntryBox1.pack()

        self.myLabel2 = tk.Label(self.root, text='Enter Azure Subscription Name:')
        self.myLabel2.pack()

        self.myEntryBox2 = tk.Entry(self.root)
        self.myEntryBox2.pack()

        self.mySubmitButton = tk.Button(self.root, text='Submit', command=self.send)
        self.mySubmitButton.pack()

        self.root.mainloop()

    def send(self):
        global subscription_name, subscription_id
        subscription_name = self.myEntryBox1.get()
        subscription_id   = self.myEntryBox2.get()

        if(subscription_name and subscription_id):
            #TODO check if subscription parameters are valid
            self.root.destroy()


'''
def onClick():
    inputDialog = MyDialog(root)
    root.wait_window(inputDialog.top)
    print('Name: ', subscription_name)
    print('ID: ', subscription_id)
'''

subscription_name = None
subscription_id = None

inputDialog = MyDialog()
#root.wait_window(inputDialog.top)
print('Name: ', subscription_name)
print('ID: ', subscription_id)
'''
mainLabel = tk.Label(root, text='Example for pop up input box')
mainLabel.pack()

mainButton = tk.Button(root, text='Click me', command=onClick)
mainButton.pack()
'''
