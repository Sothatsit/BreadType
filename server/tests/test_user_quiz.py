import unittest, os, time
from ..question import Question, MalformedQuestion, MultiChoiceQuestion, FloatSliderQuestion, IntSliderQuestion
from selenium import webdriver
from ..user_model import User, DBUserAnswer
from .. import create_app, db
from ..quiz_model import load_all_quizzes, delete_db_quiz

base_path = os.path.dirname(os.path.realpath(__file__))
app = create_app()
app.testing = True

class SystemTest(unittest.TestCase):
    driver = None

    def setUp(self):
        self.driver = webdriver.Firefox(
            executable_path = base_path + "/drivers/geckodriver"
        )
    
        if not self.driver:
            self.skipTest('Web browser not available')
        else:
            db.init_app(app)
            with app.app_context():
                db.create_all()
                db.session.commit()
            # self.driver.maximize_window()
            self.driver.get('http://localhost:5000/')

        
    def tearDown(self):
        if self.driver:
            self.driver.close()
            with app.app_context():
                for quiz in load_all_quizzes():
                    delete_db_quiz(quiz)
                db.session.query(User).delete()
                db.session.commit()
                db.session.remove()

    def test_signup_quiz(self):
        self.driver.get('http://localhost:5000/signup')
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
        logout = self.driver.find_element_by_partial_link_text('Logout')
        self.assertEqual(logout.get_attribute('innerHTML'), 'Logout', msg='Can\'t log out')

        # Start testing the functionality of quizzes

        self.driver.get('http://localhost:5000/quiz/create')
        self.driver.implicitly_wait(5)
        
        # Find and fill in the title and category fields
        title_field = self.driver.find_element_by_name('title')
        title_field.send_keys('my quiz')

        catg1_field = self.driver.find_element_by_id('catg1')
        catg1_field.send_keys('catg1')
        catg2_field = self.driver.find_element_by_id('catg2')
        catg2_field.send_keys('catg2')
        catg3_field = self.driver.find_element_by_id('catg3')
        catg3_field.send_keys('catg3')
        catg4_field = self.driver.find_element_by_id('catg4')
        catg4_field.send_keys('catg4')

        # MULTI : Fill in the first question title, options and select some answers
        q1_field = self.driver.find_element_by_name('question_1_text')
        q1_field.send_keys('q1')

        multi_1 = self.driver.find_element_by_name('question_1_multi_choice_1')
        multi_1.send_keys('option 1')
        multi_2 = self.driver.find_element_by_name('question_1_multi_choice_2')
        multi_2.send_keys('option 2')
        multi_3 = self.driver.find_element_by_name('question_1_multi_choice_3')
        multi_3.send_keys('option 3')
        multi_4 = self.driver.find_element_by_name('question_1_multi_choice_4')
        multi_4.send_keys('option 4')

        box_1 = self.driver.find_element_by_name('question_1_multi_choice_1_category_1')
        box_1.click()
        box_2 = self.driver.find_element_by_name('question_1_multi_choice_2_category_2')
        box_2.click()
        box_3 = self.driver.find_element_by_name('question_1_multi_choice_3_category_3')
        box_3.click()
        box_4 = self.driver.find_element_by_name('question_1_multi_choice_4_category_4')
        box_4.click()

        # INT_SLIDER: Same as above
        add_question = self.driver.find_element_by_id("add_question")
        add_question.click()

        q2_field = self.driver.find_element_by_name('question_2_text')
        q2_field.send_keys('q2')

        int_radio = self.driver.find_element_by_id("question_2_type_discrete_slider")
        int_radio.click()

        peak_1 = self.driver.find_element_by_name("question_2_slider_category_0_peak")
        peak_1.send_keys('10')
        peak_2 = self.driver.find_element_by_name("question_2_slider_category_1_peak")
        peak_2.send_keys('30')
        peak_3 = self.driver.find_element_by_name("question_2_slider_category_2_peak")
        peak_3.send_keys('50')
        peak_4 = self.driver.find_element_by_name("question_2_slider_category_3_peak")
        peak_4.send_keys('70')

        # FLOAT_SLIDER: same as above
        add_question = self.driver.find_element_by_id("add_question")
        add_question.click()

        q3_field = self.driver.find_element_by_name('question_3_text')
        q3_field.send_keys('q3')

        float_radio = self.driver.find_element_by_id("question_3_type_continuous_slider")
        float_radio.click()

        peak_1 = self.driver.find_element_by_name("question_3_slider_category_0_peak")
        peak_1.send_keys('10')
        peak_2 = self.driver.find_element_by_name("question_3_slider_category_1_peak")
        peak_2.send_keys('30')
        peak_3 = self.driver.find_element_by_name("question_3_slider_category_2_peak")
        peak_3.send_keys('50')
        peak_4 = self.driver.find_element_by_name("question_3_slider_category_3_peak")
        peak_4.send_keys('70')

        # Now that we have all questions filled, create the quiz
        create_quiz = self.driver.find_element_by_id("create_quiz")
        create_quiz.click()

        # Check we got brought to the view quiz page
        url = self.driver.current_url
        self.assertEqual(url, 'http://localhost:5000/quiz/1')

        # Select the first multi option and submit the quiz
        option = self.driver.find_element_by_id("q0-o0")
        option.click()

        submit = self.driver.find_element_by_id("submit")
        submit.click()

        # Check that answer is catg2
        answer = self.driver.find_element_by_id('answer')
        self.assertEqual(answer.get_attribute('innerHTML').strip(), 'catg2', msg='Correct answer')
        time.sleep(3)
        logout = self.driver.find_element_by_partial_link_text('Logout')
        self.assertEqual(logout.get_attribute('innerHTML'), 'Logout', msg='Logout Fail')
        logout.click()

if __name__ == '__main__':
    unittest.main(verbosity=2)

