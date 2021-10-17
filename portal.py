from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import datetime

class User():

    def __init__(self, name, username, password, school, child):
        self.name = name
        self.username = username
        self.password = password
        self.school   = school
        self.child    = child
                            

class SchoolPortal():
    def __init__(self, user):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')

        self.driver = webdriver.Chrome(r'.\\driver\\chromedriver.exe', chrome_options=options) 
        self.user = user

        self.is_logged = False
        self.is_week_opened  = False
        self.is_day_opened = False

    def login(self):

        self.driver.get('https://school.mosreg.ru/feed')
        username = self.driver.find_element_by_name("login")
        password = self.driver.find_element_by_name("password")
        username.send_keys(self.user.username)
        password.send_keys(self.user.password)

        self.driver.find_element_by_xpath("/html/body/div/div/div/form/input[3]").click()
    
        self.is_logged = True

    def open_week(self):
        self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/ul/li[1]/ul/li[3]/a").click()
        self.is_week_opened = True

    def open_week_by_day(self, day):

        print("Open for ", day.day, day.month, day.year)
        wait = WebDriverWait(self.driver, 10)

        self.driver.get('https://school.mosreg.ru/feed')

        self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/ul/li[1]/ul/li[3]/a').click()
        self.driver.find_element_by_xpath('//*[@id="buttondatetimebox1"]/img').click()

        # кликаем календарь
        # wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="calendar"]/a[1]')))
        self.driver.find_element_by_xpath('//*[@id="calendar"]/a[1]').click()
        self.driver.find_element_by_xpath('//*[@id="calendar"]/div[1]/a').click()
        self.driver.find_element_by_xpath('//*[@id="calendar"]/div[1]/a').click()
        self.driver.find_element_by_xpath('//*[@id="calendar"]/div[1]/a').click()
                        
        #выбор года
        xpath = '//*[@id="decade_currentscreen"]/ul/li[{}]/a'.format(day.year - 2018)
        wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
        html_list = self.driver.find_element_by_id("decade_currentscreen")                  
        html_list.find_element_by_xpath(xpath).click()        

        # выбор месяца
        xpath = '//*[@id="year_currentscreen"]/ul/li[{}]/a'.format(day.month)
        wait.until(ec.visibility_of_element_located((By.XPATH, xpath)))
        html_list = self.driver.find_element_by_id("year_currentscreen")
        html_list.find_element_by_xpath(xpath).click()

        # выбор дня
        wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="calendar"]/div[2]/div[2]')))
        html_list = self.driver.find_element_by_id("month_currentscreen")
        items = html_list.find_elements_by_tag_name("li")

        # сначала ищем первое число
        # выполняем поиск новой даты
        # если опять нашли первое число, то это след. месяц    
        is_first_day_found = False
        for item in items:
            text = item.text
            if text == "1":
                # след. месяц
                if is_first_day_found:
                    break;
                # 1-е число месяца                    
                is_first_day_found = True
            # мы еще обрабатываем не числа
            if not is_first_day_found:
                continue

            if text == str(day.day):
                item.click()
                wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="footer"]/div[2]/div[1]/ul/li[4]/a')))
                break
        
        self.is_week_opened = True

    def open_day(self, day):
        self.driver.get(
            "https://school.mosreg.ru/user/calendar.aspx?view=day&year={}&month={}&day={}"
            .format(day.year, day.month, day.day)
            )
        self.is_day_opened = True

    def get_day_timetable(self):

        for i in range(10):
            try :
                name = self.driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[2]/div[2]/div[2]/table/tbody/tr[%d]/td[2]/p[1]/a' % (2+i) ).text
            except:
                print("total count : " , i)
                break;

            try :
                task = self.driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[2]/div[2]/div[2]/table/tbody/tr[%d]/td[5]/p/a' % (2+i) ).text
            except:
                task ='-'

            print("{} : {}".format(name, task))

    def get_day_timetable2(self, day):
        
        timetable = ""
        weekday = day.weekday()
        weekday_xpath = [
            '//*[@id="diarydaysleft"]/div[1]',
            '//*[@id="diarydaysleft"]/div[2]',
            '//*[@id="diarydaysleft"]/div[3]',
            '//*[@id="diarydaysright"]/div[1]',
            '//*[@id="diarydaysright"]/div[2]',   
            '//*[@id="diarydaysright"]/div[3]',
            '//*[@id="diarydaysright"]/div[4]'
        ]
        el = self.driver.find_element_by_xpath(weekday_xpath[weekday] +'/div/h3')
        timetable += el.text + "\n"

        raws = self.driver.find_element_by_xpath(weekday_xpath[weekday] +'/div/div/div[2]/table/tbody')
        items = raws.find_elements_by_tag_name("tr")
        for i in items:
            timetable += i.text + "\n"

        return timetable

def get_next_day(day):
    weekday = day.weekday()
    if weekday == 4:
        delta = 3
    elif weekday == 5:
        delta = 2
    else:
        delta = 1 
    return_day = day + datetime.timedelta(delta)
    return return_day

