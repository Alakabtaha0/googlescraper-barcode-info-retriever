import requests
from bs4 import BeautifulSoup
import re
import pandas
from tkinter import *
from tkinter import ttk
import threading
import time
import sys
import os

# Permanent GOOGLE Search URL
URL = "https://www.google.com/search"


class GoogleScraper:

    brand = pandas.read_csv('brands.csv')
    vendors = pandas.read_csv('vendors.csv')

    # Store in variables to later append to array
    product = []
    description = []
    brand_name = ''
    barcode = ''
    item = ''
    price = ''
    cost = ''
    selected_vendor = ''

    # KEEP PARAMS THE SAME -- You will upload the Query
    params = {
        'client': 'safari',
        'rls': 'en',
        'q': '',
        'ie': 'UTF-8',
        'oe': 'UTF-8'
    }
    headers = {  # Current Header Tags --- NOTE WE NEED TO UPDATE COOKIES EVERYTIME WE USE THE APPLICATION
        'Cookie': 'CONSENT=PENDING+598; NID=511=oSw6rf4I_1-RPykDS4haNklGXahUKO3EqM3LqOkCb4l_4PddUsojfN8UtAqz40Y18reyMt5NVBcdATkwaMNgCz9as2eiV3fDVFwaxuyMpSmHSAjKNIwhz9HfyD8CkHIadohdg2Zek4YLiGIU00QK0pa92XWjujoGFqAmeq4vogw',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'www.google.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15',
        'Accept-Language': 'en-GB, en; q = 0.9',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive'
    }

    # Fetches the response to make soup
    def fetch(self, query):
        print('self.fetch running')
        self.params['q'] = query
        return requests.get(URL, params=self.params, headers=self.headers)

    def get_name(self, response):
        print('get_name running')
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, 'lxml')
            name = []
            # Gets all names NOTE use this later for comparing data and making the software better
            name = [re.sub(r'\n', '', name.text.replace('', '')).strip()
                    for name in soup.findAll("h3", {'class': 'LC20lb'})]
            try:
                selected_name = name
            except IndexError:
                print('Not valid Barcode:: ', self.barcode)
                selected_name = 'No Name Available, Please enter a name here'
            return selected_name
        else:
            print('Bad Response ' + response)
            return response

    def get_info(self, search_query):
        print('get_info running')
        # This is to ensure that theres a 2 second delay between searching with new query. MAX NUMBER OF QUERIES --- 2,500
        # So as to not get our ip's blacklisted by google
        new_response = self.fetch(search_query)
        if (new_response.status_code == 200):
            soup = BeautifulSoup(new_response.text, 'lxml')
            # Gets all names NOTE use this later for comparing data and making the software better
            name = [re.sub(r'\n', '', name.text.replace('', '')).strip()
                    for name in soup.findAll("h3", {'class': 'LC20lb'})]
            # description = [re.sub(r'\n', '', description.text.replace('  ', '')) for description in soup.findAll("div", {
            #    'class': "MUxGbd"})]  # Gets all DESCRIPTIONS NOTE use this later for comparing data and making the software better Currently theres no need to add DESCRIPTION as light speed doesn't take DESCRIPTION
            self.item = name[0]
            check_brand_name(self.item)
        else:
            print('Bad Response, Trying again in 2 seconds...  --- IF TRIED TO MANY TIMES PLEASE EXIT PROGRAM' + new_response)
            self.fetch(search_query)


# THE BLOCK OF CODE ABOVE IS THE GOOGLE SCRAPER FOR GETTING THE INFORMATION
# THE BLOCK OF CODE BELOW IS THE LOGIC FOR MANIPULATING THE DATA
#####

# Checking if the barcode is redundant or not and increasing the quantity if it is Redundant
def check_redundant(barcode):
    print('check_redundant running... ')
    isRedundant = False
    for index, UPC in enumerate(data["UPC"]):
        if(int(barcode) == UPC):
            # This is to select the Quantity Cell of that particular barcode and increment by 1
            # This is the quantity at Nano Tech Kensington
            data.at[index, 'Nano Tech - Kensington'] += 1
            data.at[index, 'Qty.'] += 1  # This is the quantity at both stores
            # This is to write the changes to the CSV file
            data.to_csv('data.csv')
            restart_programme()
    return isRedundant


# Thread loop to excute
def input_loop():
     while True:
        if(len(barcodeVar.get()) <= 10):
            time.sleep(1)
            continue
        else:
            if(barcodeVar.get().isdigit() != True):
                enter_valid_label = ttk.Label(text='Please enter a valid barcode', padding=10)
                enter_valid_label.grid(row=10, column=1)
                print(barcodeVar.get())
                barcodeVar.set('')
            else:
                try:
                    enter_valid_label.destroy()
                except:
                    pass
                select_name_label = ttk.Label(text='Please select a name', padding=10)
                select_name_label.grid(row=10, column=1)
                scraper.barcode = barcodeVar.get()  # Puts the barcode into the scraper class
                # Check if the barcode is redundant, if it is increments the current quantity by 1 otherwise just carries on
                if(check_redundant(scraper.barcode) != True):
                    print(scraper.barcode)
                    # Gets the first response from GOOGLE - Query uses the Barcode
                    response = scraper.fetch(scraper.barcode)
######
                    # This code mines the NAME data which - we will use in the next step for searching the exact info we want- from GOOGLE
                    selecting_name(scraper.get_name(response))
                    select_name_label.destroy()
                break


# Input barcode
def input_barcode():
    print('input_barcode running...')
    # Create Thread
    thread = threading.Thread(target=input_loop)
    # Terminate thread on exit and START Thread
    thread.daemon = True
    thread.start()
    



# Upload to CSV --- NOTE WE NEED TO APPEND THE INFO TO PRODUCT
def upload_to_csv():
    print('upload_to_csv running...')

    scraper.product.append({
        'UPC': scraper.barcode,
        'Item': scraper.item,
        'Nano Tech - Kensington': 1,
        'Qty.': 1,
        'Price': scraper.price,
        'Tax': 'Yes',
        'Tax Class': 'Item',
        'Brand': scraper.brand_name,
        'RRP': scraper.price,
        'Default Cost': scraper.cost,
        'Vendor': scraper.selected_vendor
    })

    index = len(data.index)
    # iterate over product list
    for i in range(0, len(scraper.product)):
        for info in scraper.product[i]:
            data.at[index, info] = scraper.product[i].get(info)
        data.to_csv('data.csv')

    return_to_default()
    



# Bind the selected search to the Text box and finish the final Google Scrape
def selected_search(event):
    # This gets the new information from the Name Query -- AGAIN MINING THE DATA FROM GOOGLE
    new_search_query = selectedName.get()
    scraper.get_info(new_search_query)

def selecting_name(name):
    print('selecting_name running... ')
    # selection_made = False
    # This prints all of the names mined only of the number of names is greater than 2. This is to ensure the user can select the actual Product they want
    if(len(name) >= 2):
        print("Multiple product names have been gathered... Please select a option from the list below to ensure reliable Scraping:: ")
        # Sets the name options for the user to choose from
        nameOptions['values'] = [name[index] for index in range(0, len(name))]
    else:
        nameOptions['values'] = name[0]


# input_* just saves the values to the scraper.* variables
def input_brand():
    if(scraper.brand_name == ''):
        scraper.brand_name = brandVar.get()

def input_price():
    scraper.price = ''.join(('£', priceVar.get()))

def input_cost():
    scraper.cost = ''.join(('£', costVar.get()))


# This is going to check the Brand name against the Description_list and the Name_list
def check_brand_name(name):
    print('check_brand_name running')
    # Cycle through the brand names
    for brand_name in scraper.brand["Name"]:
        if ((' ' + brand_name.lower() + ' ') in (' ' + name.lower() + ' ')):
            scraper.brand_name = brand_name
            ttk.Label(root, text=f'found brand name {scraper.brand_name}, if not happy with this brand name please enter another one and that will be saved').grid(row=8, column=2)
            break
    if (scraper.brand_name == ''):
        ttk.Label(root, text='Input a brand Name as none could be found').grid(row=8, column=2)

def return_to_default():
    print('Removing saved names and RESTARTING TO DEFAULT')
    scraper.product = []
    scraper.barcode = ''
    scraper.brand_name = ''
    scraper.description = []
    scraper.item = ''
    scraper.price = ''
    scraper.cost = ''
    scraper.selected_vendor = ''
    barcodeVar.set('')
    barcode_entry.delete('0', 'end')
    selectedName.set('')
    nameOptions.set('')
    priceVar.set('')
    price_entry.delete('0', 'end')
    costVar.set('')
    cost_entry.delete('0', 'end')
    nameOptions['values'] = []
    selectedVar.set('')

    restart_programme()

def restart_programme():
    python = sys.executable
    os.execl(python, python, * sys.argv)

root = Tk()
# This is the Window settings
root.geometry('1000x1000')
root.title('Barcode Scanner')
scraper = GoogleScraper()


if __name__ == "__main__":

        data = pandas.read_csv('data.csv', index_col=[0])
        # Run the input_barcode function
        barcodeVar = StringVar()
        barcode_text = ttk.Label(root, text='Input Barcode', padding=10).grid(row=0, column=1)
        barcode_entry = ttk.Entry(root, width=30, textvariable=barcodeVar, validate='focus', validatecommand=input_barcode)
        barcode_entry.grid(row=0, column=2)



        # Show the drop down menu for Selecting the NAME
        selectedName = StringVar(value='Select a item name')
        nameText = ttk.Label(root, text='Select the Name', padding=10).grid(row=1, column=1)
        nameOptions = ttk.Combobox(root, textvariable=selectedName)
        nameOptions.grid(row=1, column=2)
        nameOptions.bind('<<ComboboxSelected>>', selected_search)


        # Entry widget for entering the price
        priceVar = StringVar()
        price_text = ttk.Label(root, text='Input price', padding=10).grid(row=3, column=1)
        price_entry = ttk.Entry(root, width=10, textvariable=priceVar, validate='focusout', validatecommand=input_price)
        price_entry.grid(row=3, column=2)

        # Entry widget for entering the cost
        costVar = StringVar()
        cost_text = ttk.Label(root, text='Input Cost', padding=10).grid(row=4, column=1)
        cost_entry = ttk.Entry(root, width=10, textvariable=costVar, validate='focusout', validatecommand=input_cost)
        cost_entry.grid(row=4, column=2)
        
        # Entry widget for selecting the brand name
        brandVar = StringVar()
        brand_text = ttk.Label(root, text='Input Brand', padding=10).grid(row=2, column=1)
        brand_entry = ttk.Entry(root, width=30, textvariable=brandVar, validate='focusout', validatecommand=input_brand)
        brand_entry.grid(row=2, column=2)

        def vendor_select(event):
            scraper.selected_vendor = selectedVar.get()

        # ComboBox for Vendor List
        vendor_text = ttk.Label(text='Pick a Vendor', padding=10)
        vendor_text.grid(row=5, column=1)
        selectedVar = StringVar()
        vendor_cb = ttk.Combobox(root, textvariable=selectedVar)
        vendor_cb['values'] = [vendor for vendor in scraper.vendors['Vendor']]
        vendor_cb.grid(row=5, column=2)
    
        vendor_cb.bind('<<ComboboxSelected>>', vendor_select)

        # Button to add to CSV
        addToCSV = ttk.Button(root, text='Add to CSV', command=upload_to_csv).grid(row=6, column=2)
        
        
        root.mainloop()
