import pandas as pd
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import re


import sys
from bs4 import BeautifulSoup




if __name__ == '__main__':



    course = sys.argv[1]
    project = sys.argv[2]
    pword = None
    uname = None

    

    for i in range(3, len(sys.argv)):
        if sys.argv[i - 1] == '-p':
            pword = sys.argv[i]
        if sys.argv[i - 1] == '-u':
            uname = sys.argv[i]
    
            

    

    


    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options._binary_location = './chrome-win/chrome.exe'
    driver = webdriver.Chrome(options=options)

    driver.get('https://submit.cs.umd.edu/fall2022/view/index.jsp')

    print("Please authenticate into submit server. Press enter when done.")

    if uname != None:
        driver.find_element(by=By.ID, value='username').send_keys(uname)
    
    if pword != None:
        driver.find_element(by=By.ID, value='password').send_keys(pword)

    if uname and pword:
        driver.find_element(by=By.XPATH, value="""/html/body/div[2]/div/div/div[1]/form/div[4]/button""").click()

    
    while True:
        try:
            driver.find_element(by=By.ID, value='trust-browser-button').click()
        except:
            continue
        break



    temp = None
    while True:
        try:
            temp = driver.find_element(by=By.ID, value='continueButton')
        except:
            continue
        break
    
    temp.click()

    driver.find_element(by=By.LINK_TEXT, value=course).click()
    driver.find_element(by=By.ID, value='students').click()

    slist = BeautifulSoup(driver.page_source, features="html.parser").find('div', {'id' : 'studentList'})
    slist = slist.find_all('tr', {'class' : 'r0'}) + slist.find_all('tr', {'class' : 'r1'})
    slist = ['https://submit.cs.umd.edu/' + ele.find('td').find('a')['href'] for ele in slist]
    
    alldata = pd.DataFrame()

    for std in slist:
        
        driver.get(std)

        projlinks = [(ele.find_all('td')[0].get_text().strip(), None if ele.find_all('td')[1].get_text() == 'No submissions' else ele.find_all('td')[1].find('a')['href']) for ele in BeautifulSoup(driver.page_source, features="html.parser").find('table').find_all('tr')[2:]]
        plink = None

        
        sname = re.search(r'Login name: (\w+)', driver.page_source, re.DOTALL).group(1)
        print(sname)

        
        for pname, link in projlinks:
            if pname == project:
                plink = 'https://submit.cs.umd.edu/' + link if not link is None else None
                break
        
        if plink is None:
            continue

        driver.get(plink)

        table = BeautifulSoup(driver.page_source, features="html.parser").find('table').find_all('tr')

        cols = ['name'] + [ele.get_text().strip() for ele in table[0].find_all('th')[0:7]] + [ele.find('a')['title'].strip() for ele in table[1].find_all('th')]

        temp = pd.DataFrame(columns=cols)

        for i, row in enumerate(table[3:]):
            tcols = row.find_all('td')
            temp.at[i, cols[0]] = sname

            for c, data in zip(cols[1:5], tcols[0:4]):
                temp.at[i, c] = data.get_text().strip()
            
            if tcols[3].get_text().strip() == 'did not compile':
                continue
            
            for c, data in zip(cols[5:8], tcols[4:7]):
                temp.at[i, c] = data.get_text().strip()
            

            for c, data in zip(cols[8:], tcols[7:]):
                try:
                    temp.at[i, c] = data['class']
                except:
                    pass
        

        print(temp)
        alldata = pd.concat([alldata, temp])
    
    alldata.to_csv(project + '.csv', index=False)






        

    

