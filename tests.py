import time
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


class FilmCatalogTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        options = Options()
        options.add_argument('start-maximized')
        self.driver = webdriver.Chrome('chromedriver.exe', options=options)
        self.driver.implicitly_wait(10)

    def test_add_film(self):
        self.driver.get('http://localhost:5000/action')
        table = self.driver.find_element_by_id('films_table')
        self.assertTrue(table.is_displayed(), 'Page is not loaded!')
        time.sleep(3)
        self.driver.find_element_by_id('add_film_button').click()
        form = self.driver.find_element_by_id('add_film_form')
        self.assertTrue(form.is_displayed(), 'Page is not loaded!')
        time.sleep(3)
        self.driver.find_element_by_id('title').send_keys('aaa')
        category = Select(self.driver.find_element_by_id('category'))
        category.select_by_visible_text('Horror')
        self.driver.find_element_by_id('release_year').send_keys(2021)
        self.driver.find_element_by_id('length').send_keys(111)
        self.driver.find_element_by_id('submit_button').click()
        alert = self.driver.find_element_by_id('alert_container')
        self.assertTrue(alert.is_displayed(), 'Alert is not displayed!')
        time.sleep(3)

    def test_edit_film(self):
        self.driver.find_element_by_class_name('fa-edit').click()
        form = self.driver.find_element_by_id('edit_film_form')
        self.assertTrue(form.is_displayed(), 'Page is not loaded!')
        time.sleep(3)
        title = self.driver.find_element_by_id('title').get_attribute('value')
        self.assertEqual(title, 'aaa', 'Title is not equal to "aaa"')
        self.driver.find_element_by_id('description').send_keys('aaaaa')
        rating = Select(self.driver.find_element_by_id('rating'))
        rating.select_by_visible_text('NC-17')
        self.driver.find_element_by_id('submit_button').click()
        alert = self.driver.find_element_by_id('alert_container')
        self.assertTrue(alert.is_displayed(), 'Alert is not displayed!')
        time.sleep(3)

    def test_remove_film(self):
        self.driver.find_element_by_class_name('fa-trash').click()
        alert = self.driver.find_element_by_id('alert_container')
        self.assertTrue(alert.is_displayed(), 'Alert is not displayed!')
        time.sleep(3)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
