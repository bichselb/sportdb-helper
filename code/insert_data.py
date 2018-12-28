import time
import datetime
import re
import argparse

from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import MaxRetryError
from selenium.common.exceptions import WebDriverException


# UTILS

date_regex = re.compile("^[0-9]+\.[0-9]+\.[0-9]+$")

# PARSE DATA

def parse_data(file):
    data = pd.read_excel(file, header=0, index_col=[0, 1, 2])
    return data


# ENTER DATA


class DataInserter:

    def __init__(self, data):
        self.data = data
        self.driver = None
        self.max_tries = 10

    def navigate_to_page(self):
        sport_db_url = 'https://www.sportdb.ch'
        try:
            self.driver = webdriver.Firefox()
        except WebDriverException:
            print('Could not run firefox locally. Switching to remote option.')

            n_tries = 0
            while self.driver is None:
                try:
                    self.driver = webdriver.Remote("http://localhost:4444/wd/hub", DesiredCapabilities.FIREFOX)
                    print('Successfully opened sportdb')
                except MaxRetryError:
                    n_tries += 1
                    print('Remote webdriver is not running yet ({}/{})...'.format(n_tries, self.max_tries))
                    if n_tries >= self.max_tries:
                        raise Exception('Remote webdriver does not seem to be running...')
                    else:
                        time.sleep(2)

        self.driver.get(sport_db_url)

    def login(self, username, password):
        username_field = self.driver.find_element_by_id('j_username')
        username_field.clear()
        username_field.send_keys(username)

        username_field = self.driver.find_element_by_id('j_password')
        username_field.clear()
        username_field.send_keys(password)

        login = self.driver.find_element_by_id('ButtonLogin')
        login.click()

        src = self.driver.page_source
        if 'Bitte überprüfen Sie Benutzername und Passwort' in src or 'Bitte Benutzername und Passwort angeben' in src:
            raise Exception('Something went wrong. Most likely, you provided the wrong username or password')

    def to_awk(self, course_id):
        if course_id is None:
            input('No course_id provided. Manually navigate to "Anwesenheitskontrolle" for your course.')
        else:
            self.driver.get('https://www.sportdb.ch/extranet/kurs/kursEditAwk.do?kursId={}'.format(course_id))
        if 'Error' in self.driver.title:
            raise Exception('Something went wrong. Most likely, you entered the wrong course id.')

    @staticmethod
    def set_attendance(attended, box, name, date):

        if attended and not box.is_selected():
            print('{} attended on {}'.format(name, date))
            box.click()
            return True
        if not attended and box.is_selected():
            print('{} did not attend on {}'.format(name, date))
            box.click()
            return True

        return False

    def enter_data(self):
        changed = False

        # match ids and days
        days = self.driver.find_elements_by_xpath(".//*[contains(@class, 'awkDay')]//span")
        days = [d.text for d in days if date_regex.match(d.text)]
        day_ids = self.driver.find_elements_by_xpath(".//*[contains(@class, 'select-all leiter')]")
        day_ids = [d.get_attribute('name') for d in day_ids]
        assert(len(days) == len(day_ids))
        day_to_id = {day: day_id for day, day_id in zip(days, day_ids)}
        print('Found days:', day_to_id)

        # enter data
        for column in self.data:
            date = column.to_pydatetime().strftime('%d.%m.%Y')
            for key, val in self.data[column].iteritems():
                js_id = key[0]
                name = key[2]
                attended = val == 'x'

                if date in day_to_id:
                    day_id = day_to_id[date]
                    box = self.driver.find_element_by_xpath(
                        ".//input[contains(@name, 'kursAktivitaetTeilnehmerMap({})')][contains(@name, 'I-{}')]"
                        .format(day_id, js_id)
                    )
                    changed = changed or self.set_attendance(attended, box, name, date)

        # save
        if changed:
            save = self.driver.find_element_by_id('formSave')
            save.click()

    def to_previous(self):
        previous = self.driver.find_element_by_id('previousLink')
        c = previous.get_attribute("class")
        if 'disabled' not in c:
            # reload to prevent stale elements (a bit of a hack)
            previous = self.driver.find_element_by_id('previousLink')
            previous.click()
            return True
        else:
            return False

    def __del__(self):
        if self.driver is not None:
            logout = self.driver.find_element_by_id('logout')
            logout.click()
            self.driver.close()


def run(data_file, username, password, course_id):
    # parse data
    data = parse_data(data_file)

    # navigate
    ins = DataInserter(data)
    ins.navigate_to_page()
    ins.login(username, password)
    ins.to_awk(course_id)

    # enter data
    while True:
        print('Entering data...')
        ins.enter_data()
        print('Entered data. Going to previous page...')
        more = ins.to_previous()
        if not more:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eintragehilfe für Anwesenheitskontrolle bei sportdb')
    parser.add_argument('--username', dest='username', action='store',
                        type=str, help='Username für sportdb (z.B. js-123456)', required=True)
    parser.add_argument('--password', dest='password', action='store',
                        type=str, default=None,
                        help='Passwort für sportdb (default: interaktive Eingabe)')
    parser.add_argument('--course-id', dest='course_id', action='store', default=None, type=str,
                        help='Kurs ID (z.B. 1234567). Kann aus der URL der Anwesenheitskontrolle abgelesen werden. Wenn nicht angegeben, wirst du interaktiv angefragt, zur korrekten Anwesenheitskontrolle zu navigieren.')
    parser.add_argument('--data-file', dest='data_file', action='store',
                        type=str, default='data/attendance.xls',
                        help='File mit Daten. Siehe data/reference.xls für ein Referenzfile')
    args = parser.parse_args()

    if args.password is None:
        password = input("Password? ")
    else:
        password = args.password

    run(args.data_file, args.username, password, args.course_id)


