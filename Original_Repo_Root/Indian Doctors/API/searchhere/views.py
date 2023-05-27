from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import*
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import numpy as np
from bs4 import BeautifulSoup
import time, requests, json
from django.views.generic.base import View
def home_views(request):
	return render(request,'home.html',{})
def form_views(request):
    context = {}
    if request.method=='POST':
        First_name=request.POST['First_name']
        Last_Name=request.POST['Last_Name']
        City=request.POST['City']
        accounts = []
        

        first=First_name
        last=Last_Name



        city = City

        doctor = f"{first} {last}"
    

        print('Please Wait for Results....')
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")

        prefs = {"profile.default_content_setting_values.notifications": 2}

        options.add_experimental_option("prefs", prefs)

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        def btnClick(path):
            conButton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, path)))
            conButton.click()

        def sendInput(path, data):
            location = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, path)))
            location.clear()
            location.send_keys(data)
            time.sleep(2)

        class timesmed():
            def __init__(self, location, doc):
                self.doc_name = doc.capitalize()
                self.location = location.upper()
                self.base_url = 'https://www.timesmed.com'
                driver.get(self.base_url)
                time.sleep(2)

            def clean_list(self, path):
                items = driver.find_element(By.XPATH, path).find_elements(By.TAG_NAME, 'li')
                return [li.text for li in items if li is not None]

            def clean_data(self,path):
                item = driver.find_element(By.XPATH, path)
                return item.text if item is not None else ''

            def get_doctor_data(self):
                final_data = {
            'Doctor Name': self.doc_name, 'Ratings': np.nan, 'Conditions Treated': np.nan,
            'Education': np.nan,'Speciality': np.nan, 'Procedure': np.nan
                }
                try:
                    final_data['Doctor Name'] = self.clean_data('//*[@id="body"]/section/div[1]/section/div/div/div[1]/div[4]/div[2]/div[1]/h2')
                    final_data['Ratings'] = self.clean_data('//*[@id="body"]/section/div[1]/section/div/div/div[1]/div[4]/div[2]/div[1]/p[4]')
                    final_data['Conditions Treated'] = self.clean_list('//*[@id="autocols"]/div[1]')
                    final_data['Education'] = self.clean_list('//*[@id="autocols"]/div[2]')
                    final_data['Speciality'] = self.clean_list('//*[@id="autocols"]/div[3]')
                except Exception as e:
                    print(e)
        # print(final_data)
                return final_data

            def execute(self):
                try:
                    btnClick('//*[@id="doc-trigger"]')
                    btnClick('//*[@id="Location_Label_Desktop"]')
                    sendInput('//*[@id="Location_Text_Desktop"]', self.location)
                    btnClick('//*[@id="doctor-list"]/div/div[1]/div[2]/div[2]/div[1]/ul[4]/li[1]/a')
                    time.sleep(2)
                    btnClick('//*[@id="search_text"]')
                    sendInput('//*[@id="search_text"]', self.doc_name)

                    time.sleep(3)
                    names = driver.find_element_by_xpath('//*[@id="doctor-list"]/div/div[1]/div[2]/div[2]/div[1]/ul[1]')
                    # print(f'\n\n\n\n{names.text}')
                    index = 0

                    for name in names.find_elements_by_tag_name('li'):
                        doctor = name.text.replace('-', ' ').replace('HOSPITALS\n', '').replace('DOCTORS\n', '').strip()
                        if (doctor.find(self.doc_name.upper()) != -1) or (self.doc_name.upper().find(doctor) != -1):
                            class_name = name.get_attribute('class')
                            btnClick(f'//*[@id="doctor-list"]/div/div[1]/div[2]/div[2]/div[1]/ul[1]/li[{index + 1}]/a')
                            time.sleep(3)
                            if class_name == 'h ui-menu-item':
                                btnClick(f'//*[@id="Hospital_Doctor_List"]/ul/li/div/div[1]/div[1]/div[2]/h2/a')
                                time.sleep(3)
                            break
                        index += 1

                    return self.get_doctor_data()
                except:
                    return {
                'Ratings': np.nan, 'Conditions Treated': np.nan, 'Procedures': np.nan,
                'Doctor Name': self.doc_name, 'Speciality': np.nan, 'Education': np.nan
                    }

        class justdial:
            def __init__(self, city, doctor):
                self.city = city.capitalize()
                self.doctor = doctor.capitalize().strip()

            def execute(self):
                url = f'https://www.justdial.com/{self.city}/{"Dr-"+ self.doctor.replace(" ", "-")}/'
                driver.get(url)
                time.sleep(2)
                item = self.get_details()
                return item

            def get_details(self):
                time.sleep(2)
                try:
                    # driver.find_element(By.XPATH, '//*[@id="insrch"]')
                    # btnClick('//*[@id="srIconwpr"]')
                    a = driver.find_element_by_xpath('//*[@id="tab-5"]/ul')
                    lis = a.find_elements_by_tag_name('li')
                    for li in lis:
                        # doc_name = li.find_element_by_class_name('store-name')
                        index = lis.index(li)
                        # print(index)
                        span = driver.find_element(By.XPATH, f'//*[@id="bcard{index}"]/div[1]/section/div[1]/p[1]/a/span[1]').text
                        if span is None or span == '':
                            continue
                        elif float(span) > 0:
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="bcard{index}"]/div[1]/section/div[1]/h2/span/a'))).click()
                            break

                except Exception as e:
                    print(e)
                time.sleep(2)
                data = {}
                data['Ratings'] = driver.find_element(By.CSS_SELECTOR, 'body > div.holder > div:nth-child(4) > div > div.row.dtlwpr > div.company-details > div > div > div > span > span.rating > span.total-rate > span').text
                data['Doctor Name'] = driver.find_element(By.CSS_SELECTOR, 'body > div.holder > div:nth-child(4) > div > div.row.dtlwpr > div.company-details > div > div > h1 > span > span.fn').text
                # data['Speciality'] = driver.find_element(By.CLASS_NAME, "comp-text also-list more ").find_element(By.TAG_NAME, 'a').text
                data['Speciality'] = [a.text for a in driver.find_element(By.XPATH, '//*[@id="comp-contact"]/li[2]/span[2]').find_elements(By.TAG_NAME, 'a')]
                data['Conditions Treated'] = [li.text for li in driver.find_element(By.XPATH, '//*[@id="qckinf"]/div/ul').find_elements_by_tag_name('li')]
                data['Education'] = 'N.A.'
                return data

            def compare_result(self, data):
                results = driver.find_element_by_xpath('//*[@id="auto"]')
                index = [i for i in results.find_elements_by_tag_name('li') if i.text.lower().find(data.lower())]
                print(self.city.capitalize())
                return [i.find_element(By.TAG_NAME, 'a').get_attribute('id') for i in index]

        class doc360():
            def second(self,l):
                source = requests.get(l).content
                soup = BeautifulSoup(source, 'lxml')
                #print(source)
                name = soup.find('div', class_='info col-md-9 col-sm-12 col-lg-9').h1.text
                # print("Name :",name)
                specialist = soup.find('div', class_='info col-md-9 col-sm-12 col-lg-9').find("h2", class_="head-address text-capitalize").text
                # print("Speciality :",specialist)
                rating = soup.find("div", class_='rating-number').text
                # print("Rating :",rating)
                Address = soup.find('div', class_='col-md-5 col-lg-5 col-sm-12').find('div').find("span", class_="info_data").text
                # print("Address :",Address)
                Details = soup.find('div', class_='col-md-5 col-lg-5 col-sm-12').find('div').find("h2", class_="info_data").text
                # print("Clinic :",Details)
                Details_1 = soup.find('div', class_='col-md-7 col-lg-7 col-sm-12 extra_info table-responsive').text
                # print("Other Details :",Details_1)
                Treatment = soup.find_all("ul",class_="condition-list")[0].find_all("li", class_="service-list-item")
                lst=[]
                for i in Treatment:
                    lst.append(i.text)
                # print("Procedure :",lst)
                conditionsTreated = soup.find_all("ul",class_="condition-list")[2].find_all("li", class_="service-list-item")
                lst1=[i.text for i in conditionsTreated]
                # print("Conditions Treated :",lst1)

                d= {
            'Doctor Name': name,
            'Ratings':rating,
            'Speciality': specialist,
            'Address': Address,
            'Clinic': Details,
            'Procedure': lst,
            'Conditions Treated': lst1
                }
                return d

            def info(self, city, doc):
                url="https://www.doctor360.in/"
                driver.get(url)
                time.sleep(2)
                # btnClick('//*[@id="react-select-location_select-input"]')
                sendInput('//*[@id="react-select-location_select-input"]', city)

                btnClick('//*[@id="react-select-location_select-option-0"]/div/i')
                time.sleep(3)

                sendInput('//*[@id="react-select-value_select-input"]', doc)
                time.sleep(3)
                doc_profile_url = driver.find_element(By.XPATH, '//*[@id="react-select-value_select-option-0"]/a')

                if doc_profile_url.text == doc:
                    return self.second(doc_profile_url.get_attribute('href'))
                else:
                    return {
                        'Doctor Name': doc, 'Ratings': np.nan, 'Speciality': np.nan, 'Address': np.nan,
                        'Clinic': np.nan, 'Procedure': np.nan, 'Conditions Treated': np.nan
                    }

        class ask_apollo():

            def __init__(self, location, doc):
                self.doc = doc.capitalize()
                self.location = location.upper()
                base_url = 'https://www.askapollo.com/'
                driver.get(base_url + 'physical-appointment')
                time.sleep(2)

            def get_details(self):
                data = {
            'Ratings': np.nan, 'Conditions Treated': np.nan, 'Procedures': np.nan,
            'Doctor Name': self.doc.capitalize(), 'Speciality': np.nan, 'Education': np.nan
                }

                city_names = [driver.find_element(By.XPATH, f'//*[@id="header-city"]/div/div/div/app-city-selection/div/div[1]/div[{a+1}]/span').text.upper() for a in range(12)]

                if self.location in city_names:
                    index = city_names.index(self.location)
                    btnClick(f'//*[@id="header-city"]/div/div/div/app-city-selection/div/div[1]/div[{index+1}]/a')
                else:
                    btnClick(f'//*[@id="header-city"]/div/div/div/app-city-selection/div/div[1]/div[12]/a')
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, self.location.capitalize()))).click()

                btnClick('/html/body/app-root/app-physical-appointment/app-doctor-search/div[1]/section[1]/div/app-pc-search/div/form/div[1]/app-autocomplete/div/input')
                sendInput('/html/body/app-root/app-physical-appointment/app-doctor-search/div[1]/section[1]/div/app-pc-search/div/form/div[1]/app-autocomplete/div/input', self.doc)

                try:
                    btnClick('//*[@id="myInputautocomplete-list"]/section/div')
                    time.sleep(5)
                    data['Name'] = driver.find_element(By.XPATH, '/html/body/app-root/app-doctor-profile/div[1]/section[2]/div/div[1]/div[2]/div[1]/div[1]/div/h2[1]').text
                    data['Speciality'] = driver.find_element(By.XPATH, '/html/body/app-root/app-doctor-profile/div[1]/section[2]/div/div[1]/div[2]/div[1]/div[1]/div/div/span/a').text
                    data['Education'] = driver.find_element(By.XPATH, '//*[@id="overview"]/p[1]').text
                except Exception as e:
                    print(e)

                return data

        def practo(city, first, last):
            # getting link for the doctor

            link = None
            req = requests.get(
                f'https://www.practo.com/client-api/v1/cerebro/v3/autocomplete?query={first}%20{last}&exclude=%5B%22locality%22%2C%20%22region%22%2C%20%22insurance_providers%22%5D&contexts=%7B%22city%22%3A%20%22{city}%22%7D')
            result = json.loads(req.content)
            grouped = result['results']['grouped']
            for item in grouped:
                if item['display_name'].lower() == 'doctors':
                    index = grouped.index(item)
                    for match in grouped[index]['matches']:
                        link = f"https://www.practo.com/{city.lower()}/doctor/{match['slug']}"
                        break

            # scraping the link

            data = {
        'Doctor Name': f'{first} {last}', 'Ratings': np.nan, 'Conditions Treated': np.nan,
        'Procedures': np.nan, 'Speciality': np.nan, 'Education': np.nan
            }
            if link:
                source = requests.get(link).text
                soup = BeautifulSoup(source, 'lxml')
                name = soup.find('h1', class_='c-profile__title u-bold u-d-inlineblock')
                if name is not None:
                    data['Speciality'] = soup.find('div', class_="u-d-inline-flex flex-ai-center").text
                    data['Education'] = soup.find('p', {'data-qa-id': "doctor-qualifications"}).text
                    data['Ratings'] = soup.find('span', class_="common__star-rating__value").text
            return data

        class mg1:
            dm = {}
            def first_me(self, city, doc):
                url1="https://www.1mg.com/doctors"
                driver.get(url1)
                driver.find_element_by_class_name('fa.fa-map-marker').click()
                driver.find_element_by_partial_link_text(city).click()
                ele = driver.find_element_by_class_name("AutoCompleteDefault__input___13_wY")
                ele.send_keys(doc)
                ele.send_keys(Keys.ENTER)
                time.sleep(10)
                lm = driver.find_elements_by_class_name("DoctorName__name___2fjjE")

                d = {
            'Doctor Name': doc,
            'Ratings': np.nan,
            'Speciality': np.nan,
            'Education': np.nan,
            'Conditions Treated': np.nan,
            'Procedures': np.nan
                }
                self.dm[0] = d
                try:
                    for i in range(len(lm)):
                        name = lm[i].find_element_by_class_name('t-doctor-listing-profile-selected')
                        if name.text.find(doc):
                            # print(name.text.find(doc))
                            l = name.get_attribute('href')
                            d = self.me_second(l)
                            self.dm[i] = d
                            break
                except:
                    pass
        # driver.quit()
                return self.dm

            def me_second(self, l):
                source = requests.get(l)
                #print(source)
                soup = BeautifulSoup(source.text, 'html.parser')
                name = soup.find_all('div', class_='DoctorName__name___2fjjE')[1].text
                # print(name)
                # print(rating)
                speciality = soup.find_all('div', class_='hide-on-med-and-down')[2].find('div').find_all('div')[1].find('div').text.strip()
                # print(speciality)
                eds = soup.find('div', {'style':'display:inline-block;vertical-align:middle;margin:0px 0px 4px 8px;max-width:87%'})
                eds = eds.find_all('span')
                education = ''
                for ed in eds:
                    education = education + ed.text + ' '
                try:
                    rating = soup.find_all('div', class_='hide-on-med-and-down')[1].find_all('div')[1].find('span').text.strip()
                except IndexError:
                    rating = np.nan
                # print(education)
                d= {
            'Doctor Name': name,
            'Ratings':rating,
            'Speciality': speciality,
            'Education': education ,
            'Conditions Treated': np.nan,
            'Procedures': np.nan
                }
                return d


        def apollo247(doc):
            dm = {}
            url1="https://www.apollo247.com/specialties"
            driver.get(url1)
            input_box  = driver.find_element_by_class_name('MuiInputBase-input.MuiInput-input')
            input_box.send_keys(doc)
            time.sleep(5)
            links =  driver.find_elements_by_partial_link_text(doc)
            for i in range(len(links)):
                links[i].click()
                time.sleep(5)
                edu = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[3]/div[1]/div[2]').text.split('Education')[1].rstrip()
                Experience = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/span[3]').text
                spe = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[2]/span[1]').text
                loc = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[2]/div[3]/div[2]/div[2]/div[2]').text
                d = {
            'Doctor Name': doc,
            'Speciality': spe.replace('\n',''),
            'Experience': Experience.replace('\n',''),
            'Education': edu.replace('\n',''),
            'Location': loc.replace('\n',''),
            'Ratings': np.nan,
            'Conditions Treated': np.nan,
            'Procedures': np.nan
                }
                dm[i] = d
            if(bool(dm)==False):
                d={
                'Doctor Name': doc,
            'Speciality': np.nan,
            'Experience': np.nan,
            'Education': np.nan,
            'Location': np.nan,
            'Ratings': np.nan,
            'Conditions Treated': np.nan,
            'Procedures': np.nan 
                }
                dm[0]=d
    # driver.quit()
            return dm


        def fetch_details():
            url = 'https://www.nmc.org.in/information-desk/indian-medical-register/'

            driver.get(url)
            time.sleep(2)

            doc = f'{last.strip()} {first.strip()}'
            placeholder = driver.find_element_by_id('doctorName')
            placeholder.send_keys(doc)
            submit = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'doctor_advance_Details')))
            submit.click()
            time.sleep(5)

            table = driver.find_element_by_id('doct_info5').find_elements(By.TAG_NAME, 'tr')
            th = [th.text for th in table[0].find_elements(By.TAG_NAME, 'th')[:6]]
            # print(f'\n\n')
            # csv_file = open(f'{doc}.csv', 'w', newline='')
            # writer = csv.writer(csv_file)
            data = []

            for tr in table[1:]:
                td = [td.text for td in tr.find_elements(By.TAG_NAME, 'td')]
                if len(td) > 2:
                    data.append({th[index]: td[index] for index in range(len(th))})
                else:
            # print('Ah, No Details Found!')
                    data.append({th[index]: np.nan for index in range(len(th))})
                    break

            return data
    # csv_file.close()
    # driver.close()


        output = {}
        nmc = None
        try:
            output['1mg'] = mg1().first_me(city, doctor)[0]
            output['apollo247'] = apollo247(doctor)[0]
             # output['Ask Apollo'] = ask_apollo(city, doctor).get_details()
            output['practo'] = practo(city, first, last)
            output['Doctors 360'] = doc360().info(city, doctor)
            # output['Justdial'] = justdial(city, doctor).execute()
            nmc = fetch_details()
            output['Timesmed'] = timesmed(city, doctor).execute()
        except Exception as e:
            print(e)

        def format_print(value):
            print("here it starts")
            accounts.append(value)
            print(value)
            for k, val in value.items():
                print (f'\t{k} : {val}')

            print('\n')

        for key, value in output.items():
            print(f"{key} :")
            format_print(value)

        print('NMC:')

        for val in nmc:
            format_print(val)

        with pd.ExcelWriter(f'./{doctor}_{city}.xlsx', mode='w') as writer:
            df1 = pd.DataFrame(output)
            df2 = pd.DataFrame(nmc)

            df1.to_excel(writer, sheet_name='Doctor Details')
            df2.to_excel(writer, sheet_name='NMC', index=False)



# with open(f"{doctor}_{city}.txt", 'w') as txt:
#     txt.write(json.dumps(output))
        driver.quit()
        context["accounts"] = accounts
        print(accounts)
        return render(request,'results.html',context)
        
    else:
        return render(request,'form.html',{})
        

       
