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
    driver1 = None
    driver2 = None
    driver3 = None
    
    def setUp(self):
        # Test with Firefox
        try:
            self.driver1 = webdriver.Firefox()
        except:
            print('Firefox webdriver not found. Ignoring...')
        # Test with Chrome - soz theres probs a better way to do this
        try:
            self.driver2 = webdriver.Chrome()
        except:
            print('Chrome webdriver not found. Ignoring...')
        # Test with IE if windows
        try:
            self.driver3 = webdriver.IE()
        except:
            print('Internet Explorer webdriver not found. Ignoring...')
        if not self.driver1 and not self.driver2 and not self.driver3:
            self.skipTest('No webdrivers are available. Add the files to PATH. Skipping test.')
        else:
            db.init_app(app)
            with app.app_context():
                db.create_all()
                db.session.commit()

        
    def tearDown(self):
        for driver in [self.driver1, self.driver2, self.driver3]:
            if driver != None:
                driver.close()
        with app.app_context():
            for quiz in load_all_quizzes():
                delete_db_quiz(quiz)
                db.session.query(User).delete()
                db.session.commit()
                db.session.remove()

    def test_signup_quiz(self):
        for driver in [self.driver1, self.driver2, self.driver3]:
            if driver == None:
                continue
            driver.get('http://localhost:5000/signup')
            driver.implicitly_wait(5)

            if driver == self.driver1:
                num_field = driver.find_element_by_id('email')
                num_field.send_keys('test1@test.com')

                pref_name = driver.find_element_by_id('name')
                pref_name.send_keys('test1')
            elif driver == self.driver2:
                num_field = driver.find_element_by_id('email')
                num_field.send_keys('test2@test.com')

                pref_name = driver.find_element_by_id('name')
                pref_name.send_keys('test2')

            new_password = driver.find_element_by_id('password')
            new_password.send_keys('pass')

            driver.implicitly_wait(5)
            submit = driver.find_element_by_id('signup')
            submit.click()
            logout = driver.find_element_by_partial_link_text('Logout')
            self.assertEqual(logout.get_attribute('innerHTML'), 'Logout', msg='Can\'t log out')

            # Start testing the functionality of quizzes

            driver.get('http://localhost:5000/quiz/create')
            driver.implicitly_wait(5)
            
            # Find and fill in the title and category fields
            title_field = driver.find_element_by_name('title')
            title_field.send_keys('my quiz')

            catg1_field = driver.find_element_by_id('catg1')
            catg1_field.send_keys('catg1')
            catg2_field = driver.find_element_by_id('catg2')
            catg2_field.send_keys('catg2')
            catg3_field = driver.find_element_by_id('catg3')
            catg3_field.send_keys('catg3')
            catg4_field = driver.find_element_by_id('catg4')
            catg4_field.send_keys('catg4')

            # MULTI : Fill in the first question title, options and select some answers
            q1_field = driver.find_element_by_name('question_1_text')
            q1_field.send_keys('q1')

            multi_1 = driver.find_element_by_name('question_1_multi_choice_1')
            multi_1.send_keys('option 1')
            multi_2 = driver.find_element_by_name('question_1_multi_choice_2')
            multi_2.send_keys('option 2')
            multi_3 = driver.find_element_by_name('question_1_multi_choice_3')
            multi_3.send_keys('option 3')
            multi_4 = driver.find_element_by_name('question_1_multi_choice_4')
            multi_4.send_keys('option 4')

            box_1 = driver.find_element_by_name('question_1_multi_choice_1_category_1')
            box_1.click()
            box_2 = driver.find_element_by_name('question_1_multi_choice_2_category_2')
            box_2.click()
            box_3 = driver.find_element_by_name('question_1_multi_choice_3_category_3')
            box_3.click()
            box_4 = driver.find_element_by_name('question_1_multi_choice_4_category_4')
            box_4.click()

            # INT_SLIDER: Same as above
            add_question = driver.find_element_by_id("add_question")
            add_question.click()

            q2_field = driver.find_element_by_name('question_2_text')
            q2_field.send_keys('q2')

            int_radio = driver.find_element_by_id("question_2_type_discrete_slider")
            int_radio.click()

            peak_1 = driver.find_element_by_name("question_2_slider_category_0_peak")
            peak_1.send_keys('10')
            peak_2 = driver.find_element_by_name("question_2_slider_category_1_peak")
            peak_2.send_keys('30')
            peak_3 = driver.find_element_by_name("question_2_slider_category_2_peak")
            peak_3.send_keys('50')
            peak_4 = driver.find_element_by_name("question_2_slider_category_3_peak")
            peak_4.send_keys('70')

            # FLOAT_SLIDER: same as above
            add_question = driver.find_element_by_id("add_question")
            add_question.click()

            q3_field = driver.find_element_by_name('question_3_text')
            q3_field.send_keys('q3')

            float_radio = driver.find_element_by_id("question_3_type_continuous_slider")
            float_radio.click()

            peak_1 = driver.find_element_by_name("question_3_slider_category_0_peak")
            peak_1.send_keys('10')
            peak_2 = driver.find_element_by_name("question_3_slider_category_1_peak")
            peak_2.send_keys('30')
            peak_3 = driver.find_element_by_name("question_3_slider_category_2_peak")
            peak_3.send_keys('50')
            peak_4 = driver.find_element_by_name("question_3_slider_category_3_peak")
            peak_4.send_keys('70')

            # Now that we have all questions filled, create the quiz
            create_quiz = driver.find_element_by_id("create_quiz")
            create_quiz.click()

            # Check we got brought to the view quiz page
            url = driver.current_url
            if self.driver1:
                if driver == self.driver1:
                    self.assertEqual(url, 'http://localhost:5000/quiz/1')
                elif self.driver2:
                    if driver == self.driver2:
                        self.assertEqual(url, 'http://localhost:5000/quiz/2')
                    elif self.driver3:
                        self.assertEqual(url, 'http://localhost:5000/quiz/3')
                elif self.driver3:
                    self.assertEqual(url, 'http://localhost:5000/quiz/2')
            elif self.driver2:
                if driver == self.driver2:
                    self.assertEqual(url, 'http://localhost:5000/quiz/1')
                elif self.driver3:
                    self.assertEqual(url, 'http://localhost:5000/quiz/2')
            elif self.driver3:
                self.assertEqual(url, 'http://localhost:5000/quiz/1')


            # Select the first multi option
            option = driver.find_element_by_id("q0-o0")
            option.click()

            # Check that the sliders registered as float and int successfully
            int_slider = driver.find_element_by_id("question-2_slider_val")
            float_slider = driver.find_element_by_id("question-3_slider_val")

            self.assertEqual(int_slider.get_attribute('innerHTML').strip(), '50', msg='int slider successful')
            self.assertEqual(float_slider.get_attribute('innerHTML').strip(), '50.0', msg='float slider successful')

            submit = driver.find_element_by_id("submit")
            submit.click()

            # Check that answer is catg2
            answer = driver.find_element_by_id('answer')
            self.assertEqual(answer.get_attribute('innerHTML').strip(), 'catg2', msg='Correct answer')
            time.sleep(3)

            # Check we can log out
            logout = driver.find_element_by_partial_link_text('Logout')
            self.assertEqual(logout.get_attribute('innerHTML'), 'Logout', msg='Logout Fail')
            logout.click()

if __name__ == '__main__':
    unittest.main(verbosity=0)

