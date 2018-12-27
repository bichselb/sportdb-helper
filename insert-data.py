from selenium import webdriver
import pandas as pd
import datetime
import re
import argparse
import sys


# UTILS

def get_week_difference(d1, d2):
    monday1 = (d1 - datetime.timedelta(days=d1.weekday()))
    monday2 = (d2 - datetime.timedelta(days=d2.weekday()))

    return int((monday2 - monday1).days / 7)


# allow computation of the week id
epoch = datetime.datetime(1980, 1, 6)
specific_week_difference = get_week_difference(epoch, datetime.datetime(2018, 1, 22))
off_by = 43328566 - specific_week_difference


def get_week_id(d):
    return get_week_difference(epoch, d) + off_by


# PARSE DATA

def parse_data(file):
    data = pd.read_excel(file, header=0, index_col=[0, 1, 2])
    return data


# ENTER DATA


class DataInserter:

    def __init__(self, data):
        self.data = data

    def navigate_to_page(self):
        sport_db_url = 'https://www.sportdb.ch'
        self.driver = webdriver.Firefox()
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

    def insert_attendance(self, date,  js_id, name, attended):
        week_id = get_week_id(date)
        xpath = ".//*[@name='kursAktivitaetTeilnehmerMap({})']".format(week_id)
        boxes = self.driver.find_elements_by_xpath(xpath)
        for box in boxes:
            value = box.get_property("value")
            pattern = re.compile("^I-{}\\|[0-9]+$".format(js_id))
            if pattern.match(value):
                if attended and not box.is_selected():
                    print('{} attended on {}'.format(name, date))
                    box.click()
                if not attended and box.is_selected():
                    print('{} did not attend on {}'.format(name, date))
                    box.click()

    def enter_data(self):
        for column in self.data:
            date = column.to_pydatetime()
            for key, val in self.data[column].iteritems():
                js_id = key[0]
                name = key[2]
                attended = val == 'x'
                self.insert_attendance(date, js_id, name, attended)

        save = self.driver.find_element_by_id('formSave')
        save.click()

    def to_previous(self):
        previous = self.driver.find_element_by_id('previousLink')
        c = previous.get_attribute("class")
        if 'disabled' not in c:
            previous.click()
            return True
        else:
            return False

    def __del__(self):
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
        ins.enter_data()
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
                        help='Kurs ID (z.B. 1234567). Wenn nicht angegeben, wirst du interaktiv angefragt, zur korrekten Anwesenheitskontrolle zu navigieren.')
    parser.add_argument('--data-file', dest='data_file', action='store',
                        type=str, default='data/attendance.xls',
                        help='File mit Daten. Siehe data/reference.xls für ein Referenzfile')
    args = parser.parse_args()

    if args.password is None:
        password = input("Password? ")
    else:
        password = args.password

    run(args.data_file, args.username, password, args.course_id)


