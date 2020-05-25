import unittest, os
from ..question import Question, MalformedQuestion, MultiChoiceQuestion, FloatSliderQuestion, IntSliderQuestion
from selenium import webdriver
from ..user_model import User
from .. import create_app, db

base_path = os.path.dirname(os.path.realpath(__file__))
app = create_app()

class SystemTest(unittest.TestCase):
    driver = None

    def setUp(self):
        self.driver = webdriver.Firefox(
            executable_path = base_path + "/drivers/geckodriver"
        )
    
        if not self.driver:
            self.skipTest('Web browser for available')
        else:
            db.init_app(app)
            with app.app_context():
                db.create_all()
                db.session.commit()
            self.driver.maximize_window()
            self.driver.get('http://localhost:5000/')
        
    def tearDown(self):
        if self.driver:
            self.driver.close()
            with app.app_context():
                db.session.query(User).delete()
                db.session.commit()
                db.session.remove()

    def test_signup(self):
        self.driver.get('http://127.0.0.1:5000/signup')
        self.driver.implicitly_wait(5)

        num_field = self.driver.find_element_by_id('email')
        num_field.send_keys('test@test.com')

        pref_name = self.driver.find_element_by_id('name')
        pref_name.send_keys('test')

        new_password = self.driver.find_element_by_id('password')
        new_password.send_keys('pass')

        self.driver.implicitly_wait(5)
        submit = self.driver.find_element_by_id('signup')
        submit.click()
        logout = self.driver.find_element_by_partial_link_text('logout')
        self.assertEqual(logout.get_attribute('innerHTML'), 'logout', msg='logged in')

    def test_quiz(self):
        self.driver.get('http://127.0.0.1:5000/quiz/create')
        self.driver.implicity_wait(5)
        title_field = self.driver.find_element_by_id('title')
        title_field.send_keys('my quiz')
        catg1_field = self.driver.find_element_by_id('catg1')
        catg1_field.send_keys('catg1')
        catg2_field = self.driver.find_element_by_id('catg2')
        catg2_field.send_keys('catg2')
        catg3_field = self.driver.find_element_by_id('catg3')
        catg3_field.send_keys('catg3')
        catg4_field = self.driver.find_element_by_id('catg4')
        catg4_field.send_keys('catg4')


        self.driver.implicitly_wait(3)
        logout = self.driver.find_element_by_partial_link_text('Logout')
        self.assertEqual(logout.get_attribute('innerHTML'), 'Logout', msg='Logout Fail')
        logout.click()

if __name__ == '__main__':
    unittest.main(verbosity=2)

