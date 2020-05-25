import unittest, os, time
from ..question import Question, MalformedQuestion, MultiChoiceQuestion, FloatSliderQuestion, IntSliderQuestion
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..user_model import User
from .. import create(app)


base_path = os.path.dirname(os.path.realpath(__file__))

class SystemTest(unittest.TestCase):
    driver = None

    def setUp(self):
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = False

        self.driver = webdriver.Firefox(capabilities=cap,
            executable_path = base_path + "/drivers/geckodriver"
        )
    
        if not self.driver:
            self.skipTest('Web browser for available')
        else:
            db.init_app(app)
            db.create_all()
            u1 = User(id=22, email_address='test@gmail.com', name='test')
            db.session.add(u1)
            db.session.commit()
            self.driver.maximize_window()
            self.driver.get('http://localhost:5000/')
        
    def tearDown(self):
        if self.driver:
            self.driver.close()
            db.session.query(User).delete()
            db.session.commit()
            db.session.remove()

    def test_signup(self):
        u = User.query.get(22)
        self.assertEqual(u.name, 'test', msg='user exist in db')
        self.driver.get('http://127.0.0.1:5000/signup')
        self.driver.implicity_wait(5)
        num_field = self.driver.find_element_by_id('email')
        num_field.send_keys('test@gmail.com')
        pref_name = self.driver.find_element_by_id('name')
        num_field.send_keys('test')
        new_password = self.driver.find_element_by_id('password')
        num_field.send_keys('testy')
        time.sleep(1)
        self.driver.implicity_wait(5)
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



if __name__ == '__main__':
    unittest.main(verbosity=2)

