import time
import datetime
import re
import argparse
from mylogging import logger

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

    def __init__(self, data, selenium_url, disable_all=False, max_tries=10):
        self.data = data
        self.driver = None
        self.disable_all = disable_all
        self.logged_in = False
        self.is_remote = True

        try:
            self.driver = webdriver.Firefox()
            self.is_remote = False
        except WebDriverException as e:
            logger.info('Could not run firefox locally. Switching to remote option. Error message: ' + str(e))

            n_tries = 0
            logger.info("Connecting to selenium at " + selenium_url)
            while self.driver is None:
                try:
                    self.driver = webdriver.Remote(selenium_url, DesiredCapabilities.FIREFOX)
                    logger.info('Successfully connected to selenium')
                except MaxRetryError:
                    n_tries += 1
                    logger.warning('Remote webdriver is not running yet ({}/{})...'.format(n_tries, max_tries))
                    if n_tries >= max_tries:
                        raise Exception('Remote webdriver does not seem to be running...')
                    else:
                        time.sleep(1)

    def navigate_to_page(self):
        sport_db_url = 'https://www.sportdb.ch'
        logger.debug('Navigating to %s', sport_db_url)
        self.driver.get(sport_db_url)
        logger.debug('Navigated to %s', sport_db_url)

    def login(self, username, password):
        logger.debug('Filling out login form...')
        username_field = self.driver.find_element_by_id('j_username')
        username_field.clear()
        username_field.send_keys(username)

        username_field = self.driver.find_element_by_id('j_password')
        username_field.clear()
        username_field.send_keys(password)

        logger.debug('Clicking login button')
        login = self.driver.find_element_by_id('ButtonLogin')
        login.click()

        self.logged_in = True
        logger.debug('Clicked login button')

        src = self.driver.page_source
        if 'Bitte überprüfen Sie Benutzername und Passwort' in src or 'Bitte Benutzername und Passwort angeben' in src:
            raise Exception('Something went wrong. Most likely, you provided the wrong username or password')

    def to_awk(self, course_id):
        logger.debug('Browsing to AWK with course id %s...', course_id)
        if course_id is None:
            logger.debug('Mode: manual')
            input('No course_id provided. Manually navigate to "Anwesenheitskontrolle" for your course.')
        else:
            logger.debug('Mode: automatic')
            self.driver.get('https://www.sportdb.ch/extranet/kurs/kursEditAwk.do?kursId={}'.format(course_id))

            logger.debug('Waiting a bit for page to fully load')
            time.sleep(1)

        if 'Error' in self.driver.title:
            raise Exception('Something went wrong. Most likely, you entered the wrong course id.')
        logger.debug('Browsed to AWK...')

    def set_attendance(self, attended, box, name, date):
        if attended:
            logger.debug("Attended")
        attended = attended and not self.disable_all
        logger.debug('Setting attendance for %s on %s', name, date)
        if attended and not box.is_selected():
            logger.debug('{} attended on {}'.format(name, date))
            box.click()
            return True
        elif not attended and box.is_selected():
            logger.debug('{} did not attend on {}'.format(name, date))
            box.click()
            return True
        elif attended and box.is_selected():
            logger.debug('{} attended on {} (already entered)'.format(name, date))
        elif not attended and not box.is_selected():
            logger.debug('{} did not attend on {} (already entered)'.format(name, date))
        else:
            logger.error('Program error')
            assert False

        return False

    def enter_data(self):
        any_changed = False

        # match ids and days
        logger.debug('Determining days on the current page')
        days = self.driver.find_elements_by_xpath(".//*[contains(@class, 'awkDay')]//span")
        days = [d.text for d in days if date_regex.match(d.text)]
        logger.debug('Determining day ids on the current page')
        day_ids = self.driver.find_elements_by_xpath(".//*[contains(@class, 'select-all leiter')]")
        day_ids = [d.get_attribute('name') for d in day_ids]
        logger.debug("Asserting length of results matches: \t\n%s, \t\n%s", days, day_ids)
        assert(len(days) == len(day_ids))
        day_to_id = {day: day_id for day, day_id in zip(days, day_ids)}
        logger.debug('Found days: %s', day_to_id)

        # enter data
        logger.debug('Entering data...')
        for column in self.data:
            date = column.to_pydatetime().strftime('%d.%m.%Y')
            for key, val in self.data[column].iteritems():
                js_id = key[0]
                last_name = key[1]
                first_name = key[2]
                name = first_name + ' ' + last_name

                attended = val == 'x'

                if date in day_to_id:
                    day_id = day_to_id[date]
                    path = ".//input[contains(@name, 'kursAktivitaetTeilnehmerMap({})')][contains(@value, 'I-{}')]"\
                        .format(day_id, js_id)
                    logger.debug('Locating checkbox for %s (%s) on %s by path %s', name, js_id, date, path)
                    box = self.driver.find_element_by_xpath(path)
                    logger.debug('Filling out checkbox')
                    changed = self.set_attendance(attended, box, name, date)
                    any_changed = any_changed or changed
                    logger.debug('Filled out checkbox')

        logger.debug('Wait a bit for page to process changes')
        time.sleep(1)

        # save
        if any_changed:
            logger.debug('Saving data...')
            save = self.driver.find_element_by_id('formSave')
            save.click()
            logger.debug('Saved data')
        else:
            logger.debug('Not saving, since there were no changes.')

    def to_previous(self):
        previous = self.driver.find_element_by_id('previousLink')
        c = previous.get_attribute("class")
        if 'disabled' not in c:
            previous.click()

            logger.debug('Waiting a bit for page to fully load')
            time.sleep(1)

            return True
        else:
            return False

    def __del__(self):
        if self.logged_in:
            logger.debug('Logging out...')
            logout = self.driver.find_element_by_id('logout')
            logout.click()
            logger.debug('Closing driver...')
            self.driver.close()


def run(data_file, username, password, course_id, disable_all, selenium_url, test):
    logger.debug("Running...")

    # parse data
    data = parse_data(data_file)

    # navigate
    ins = DataInserter(data, selenium_url, disable_all)
    ins.navigate_to_page()
    ins.login(username, password)
    ins.to_awk(course_id)

    if not test:
        # enter data
        while True:
            logger.info('Entering data...')
            ins.enter_data()
            logger.info('Entered data. Going to previous page...')
            more = ins.to_previous()
            if not more:
                break
    
        logger.info("Einträge vollständig. Keine Garantie für Korrektheit, bitte Daten überprüfen. Vergiss nicht, den Kurs noch abzuschliessen.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Eintragehilfe für Anwesenheitskontrolle bei sportdb')
    parser.add_argument('data_file', action='store', type=str,
                        help='File mit Daten. Siehe data/reference.xls für ein Referenzfile (letztes Argument)')
    parser.add_argument('--username', dest='username', action='store',
                        type=str, help='Username für sportdb (z.B. js-123456)', required=True)
    parser.add_argument('--password', dest='password', action='store',
                        type=str, default=None,
                        help='Passwort für sportdb (default: interaktive Eingabe)')
    parser.add_argument('--course-id', dest='course_id', action='store', default=None, type=str,
                        help='Kurs ID (z.B. 1234567). Kann aus der URL der Anwesenheitskontrolle abgelesen werden. Wenn nicht angegeben, wirst du interaktiv angefragt, zur korrekten Anwesenheitskontrolle zu navigieren.')
    parser.add_argument('--disable-all', dest='disable_all', action='store_true', default=False,
                        help='Deaktiviere die Anwesenheit für alle Personen und Daten im File.')
    parser.add_argument('--test', action='store_true', default=False,
                        help='Nur Login&Logout.')
    parser.add_argument('--selenium-url', default="http://selenium:4444/wd/hub",
                        help='URL unter der Selenium erreicht werden kann.')

    args = parser.parse_args()

    if args.password is None:
        password = input("Password? ")
    else:
        password = args.password

    run(args.data_file, args.username, password, args.course_id, args.disable_all, args.selenium_url, args.test)


