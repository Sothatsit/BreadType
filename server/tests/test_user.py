import unittest, os, test
from ..question import Question, MalformedQuestion, MultiChoiceQuestion, FloatSliderQuestion, IntSliderQuestion
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..user_model import User
import unittest, os, time

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
            u1 = User(id=22, email_address='test@gmail.com', name='test',)
            db.session.add(u1)
            db.session.commit()
            self.driver.maximize_window()
            self.driver.get('http://localhost:5000/')
        
    def tearDown(self):
        if self.drvier:
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
        self.assertEqual(logout.get_attribute(innerHTML), 'logout test', msg='logged in')


if __name__ == '__main__':
    unittest.main(verbosity=2)

