from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from mymath.models import Category, Exam, Question, UserQuestionSelect, UserTestResult


class TestIndex(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="カテゴリー１")
        self.exam = Exam.objects.create(title="テスト1", category=self.category)
        self.question = Question.objects.create(
            number=1,
            exam=self.exam,
            text="text",
            select_1="select1",
            select_2="select2",
            select_3="select3",
            select_4="select4",
            answer=1,
            answer_text="answer_text")
    def test_get_index(self):
        # テンプレートに"maymath/index.html"が使われていることと作成した"テスト1"が表示されていることを確認
        response = self.client.get(reverse("mymath:index"))
        self.assertTemplateUsed(response, "mymath/index.html")
        self.assertContains(response, "テスト1")


class TestExam(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="カテゴリー１")
        self.exam = Exam.objects.create(title="テスト1", category=self.category)
        self.question = Question.objects.create(
            number=1,
            exam=self.exam,
            text="text",
            select_1="select1",
            select_2="select2",
            select_3="select3",
            select_4="select4",
            answer=1,
            answer_text="answer_text")
    def test_get(self):
        response = self.client.get(reverse("mymath:exam", kwargs={"exam_id":self.exam.id, "number":1}))
        self.assertTemplateUsed(response, "mymath/exam.html")
        self.assertContains(response, "text")
        self.assertContains(response, "select1")
        self.assertContains(response, "select2")
        self.assertContains(response, "select3")
        self.assertContains(response, "select4")
    def test_get_not_exist_exam_id(self):
        # 存在しないexam_idを指定したとき
        not_exist_id = self.exam.id + 1 # 確実に存在しないidを指定して404になることを確認
        response = self.client.get(reverse("mymath:exam", kwargs={"exam_id": not_exist_id, "number":1}))
        self.assertEqual(response.status_code, 404)
    def test_get_not_exist_question_number(self):
        response = self.client.get(reverse("mymath:exam", args=(self.exam.id, 2)))
        self.assertEqual(response.status_code, 404)

    def test_post(self):
        response = self.client.post(
            reverse("mymath:exam",
                    kwargs={"exam_id": self.exam.id, "number": 1}), data={"question_1": 1}) # dataはformのnameがキー、valueが値になる
        self.assertRedirects(response, reverse("mymath:answer",
                kwargs={"exam_id":self.exam.id, "number":1}))
    def test_post_without_select(self):
        response = self.client.post(reverse("mymath:exam",
                                    kwargs={"exam_id": self.exam.id, "number":1}),
                                    )
        self.assertRedirects(response, reverse("mymath:exam",
                                            kwargs={"exam_id": self.exam.id, "number":1}))
    
class TestExamLogin(TestCase):    
    # ログイン時の挙動もチェック
    def setUp(self):
        # create_userでアカウントを作成
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.category = Category.objects.create(name="カテゴリー１")
        self.exam = Exam.objects.create(title="テスト1", category=self.category)
        self.question = Question.objects.create(
            number=1,
            exam=self.exam,
            text="text",
            select_1="select1", select_2="select2", select_3="select3", select_4="select4",
            answer=1,
            answer_text="answer_text")
     
    def test_get_login(self):
        self.client.login(username="testuser", password="pass")
        response = self.client.get(reverse("mymath:exam",
                                            kwargs={"exam_id": self.exam.id, "number":1}))
        self.assertTemplateUsed(response, "mymath/exam.html")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "text")
        self.assertContains(response, "select1")
        self.assertContains(response, "select2")
        self.assertContains(response, "select3")
        self.assertContains(response, "select4")

    def test_post_correct_with_login(self):
        self.client.login(username="testuser", password="pass")
        # answerが1でselectが1なので正解をpostしている。
        response = self.client.post(
            reverse("mymath:exam",
                    kwargs={"exam_id": self.exam.id, "number": 1}),
                    data={"question_1": 1}) # dataはformのnameがキー、valueが値になる
        
        self.assertRedirects(response, reverse("mymath:answer",
                            kwargs={"exam_id":self.exam.id, "number":1}))
        self.assertEqual(UserTestResult.objects.count(), 1) # UserTestResultオブジェクトが作成されているかチェック
        user_tr = UserTestResult.objects.first() #実際にUserTestResltオブジェクトをとって中身を確認
        self.assertEqual(user_tr.user, self.user)
        self.assertEqual(user_tr.exam, self.exam)
        # UserQuestionSelectオブジェクトも取得してチェック
        user_qs = UserQuestionSelect.objects.first()
        self.assertEqual(user_qs.select, 1)
        self.assertTrue(user_qs.correct)
    def test_post_not_correct_with_login(self):
        self.client.login(username="testuser", password="pass")
        # answerが1でselectが2なので不正解をpostしている。
        response = self.client.post(
            reverse("mymath:exam",
                    kwargs={"exam_id": self.exam.id, "number": 1}),
                    data={"question_1": 2})
        self.assertRedirects(response, reverse("mymath:answer",
                            kwargs={"exam_id":self.exam.id, "number":1}))
        self.assertEqual(UserTestResult.objects.count(), 1) # UserTestResultオブジェクトが作成されているかチェック
        user_tr = UserTestResult.objects.first() #実際にUserTestResltオブジェクトをとって中身を確認
        self.assertEqual(user_tr.user, self.user)
        self.assertEqual(user_tr.exam, self.exam)
        # UserQuestionSelectオブジェクトも取得してチェック
        user_qs = UserQuestionSelect.objects.first()
        self.assertEqual(user_qs.select, 2) # 選択を確認
        self.assertFalse(user_qs.correct) # 間違っているか確認
    
    
    
    def test_post_login_without_select(self):
        self.client.login(username="testuser", password="pass")

        response = self.client.post(reverse("mymath:exam",
                                    kwargs={"exam_id": self.exam.id, "number":1}),
                                    )
        self.assertRedirects(response, reverse("mymath:exam",
                                            kwargs={"exam_id": self.exam.id, "number":1}))


class TestExamResultLogin(TestCase):
    """ログイン中のリザルトまでのテスト"""
    def setUp(self):
        self.category = Category.objects.create(name="カテゴリー１")
        self.exam = Exam.objects.create(title="テスト1", category=self.category)
        self.questions = []
        for i in range(10):
            question= Question.objects.create(
                number=i+1,
                exam=self.exam,
                text="text",
                select_1="select1", select_2="select2", select_3="select3", select_4="select4",
                answer=1,
                answer_text="answer_text")
            self.questions.append(question) # questionが10個入ったself.questionsを作成
        
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.login(username="testuser", password="pass")
    
    def test_complete_exam_to_result_all_correct(self):
        """全問正解のパターン"""
        for number in range(1, 11):
            response1 = self.client.post(reverse(
                "mymath:exam",
                kwargs={"exam_id": self.exam.id, "number":number}
                ),
                data={f"question_{number}": 1})
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            response2 = self.client.post(reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam", kwargs={"exam_id": self.exam.id, "number":number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
        # answerが1 で selectが1を10回行っているので正解数は10で100点になっているはず
        user_tr = UserTestResult.objects.first()
        user_qss = UserQuestionSelect.objects.all()
        for user_qu in user_qss:
            self.assertTrue(user_qu.correct)
        self.assertEqual(len(user_qss), 10)
        self.assertEqual(user_tr.user, self.user)
        self.assertEqual(user_tr.exam, self.exam)
        self.assertEqual(user_tr.score, 100)

    def test_complete_exam_to_result_all_uncorrect(self):
        """全問不正解パターン"""
        for number in range(1, 11):
            response1 = self.client.post(reverse(
                "mymath:exam",
                kwargs={"exam_id": self.exam.id, "number":number}
                ),
                data={f"question_{number}": 2})
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            response2 = self.client.post(reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam", kwargs={"exam_id": self.exam.id, "number":number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
        # answerが1 で selectが2を10回行っているので正解数は0で0点になっているはず
        user_tr = UserTestResult.objects.first()
        user_qss = UserQuestionSelect.objects.all()
        for user_qu in user_qss:
            self.assertFalse(user_qu.correct)
        self.assertEqual(len(user_qss), 10)
        self.assertEqual(user_tr.user, self.user)
        self.assertEqual(user_tr.exam, self.exam)
        self.assertEqual(user_tr.score, 0)

    def test_complete_exam_to_result_correct_and_uncorrect(self):
        """正解と不正解が混ざったパターン"""
        for number in range(1, 11):
            # 選択肢3, 4を選んで不正解になっているかをチェック
            if number == 5:
                data={f"question_{number}": 3}
            elif number == 6:
                data={f"question_{number}": 4}
            else:
                data={f"question_{number}": 1}
            response1 = self.client.post(reverse(
                "mymath:exam",
                kwargs={"exam_id": self.exam.id, "number":number}
                ),
                data=data)
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            response2 = self.client.post(reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam", kwargs={"exam_id": self.exam.id, "number":number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
        # answerが1 で selectが1を8回行っているので正解数は8で80点になっているはず
        user_tr = UserTestResult.objects.first()
        user_qss = UserQuestionSelect.objects.all()
        
        self.assertEqual(len(user_qss), 10)
        self.assertEqual(user_tr.user, self.user)
        self.assertEqual(user_tr.exam, self.exam)
        self.assertEqual(user_tr.score, 80)


class TestResultExamAnonymous(TestCase):
    """未ログインでリザルトまでのテスト"""
    def setUp(self):
        self.category = Category.objects.create(name="カテゴリー１")
        self.exam = Exam.objects.create(title="テスト1", category=self.category)
        self.questions = []
        for i in range(10):
            question= Question.objects.create(
                number=i+1,
                exam=self.exam,
                text="text",
                select_1="select1", select_2="select2", select_3="select3", select_4="select4",
                answer=1,
                answer_text="answer_text")
            self.questions.append(question) # questionが10個入ったself.questionsを作成
    
    def test_complete_exam_to_result_all_correct(self):
        """全問正解時の挙動をチェック"""
        for number in range(1, 11):
            question = self.questions[number-1] # self.questionsからquestionをインデックス番号で取り出す
            response1 = self.client.post(
                reverse(
                    "mymath:exam",
                    kwargs={"exam_id":self.exam.id, "number": number}),
                data={f"question_{number}": question.answer}) # quesion.answerはsetUp()から1
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id":self.exam.id, "number": number}))
            # sessionの中身をチェック
            session = self.client.session
            self.assertEqual(session["exam"]["exam_id"], self.exam.id)
            # answer_d = {}
            # for i in range(1, number+1):
            #    answer_d[str(i)] = question.answer
            # ↑を内包表記で書いてみる
            self.assertEqual(session["exam"]["question_select"], {str(i): question.answer for i in range(1, number+1)})
            self.assertEqual(session["exam"]["answer_correct"], {str(i): True for i in range(1, number+1)})
            response1_1 = self.client.get(
                reverse("mymath:answer",
                        kwargs={"exam_id":self.exam.id, "number": number})
            )
            self.assertContains(response1_1, f"{number}問目")
            self.assertContains(response1_1, "正解")
            response2 = self.client.post(
                reverse("mymath:answer",
                        kwargs={"exam_id":self.exam.id, "number": number}))
            
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam",
                                                        kwargs={"exam_id": self.exam.id, "number": number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                # resultをチェック
                response3 = self.client.get(reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                self.assertContains(response3, "100点")
                # response.contextで渡すcontextをチェック
                # 未ログイン時の処理でモデルオブジェクトを模した辞書が正しくわたされているかチェック
                self.assertEqual(response3.context["user_result"]["count"], "*")
                self.assertEqual(response3.context["user_result"]["score"], 100)
                self.assertEqual(response3.context["user_result"]["exam"]["id"], self.exam.id)
                self.assertEqual(response3.context["user_result"]["exam"]["title"], self.exam.title)
                self.assertTrue(response3.context["useranswers"][0]["correct"])
                self.assertEqual(response3.context["useranswers"][0]["question"]["number"], 1)
    def test_complete_exam_to_result_all_uncorrect(self):
        """全問不正解時の挙動をチェック"""
        for number in range(1, 11):
            question = self.questions[number-1] # self.questionsからquestionをインデックス番号で取り出す
            response1 = self.client.post(
                reverse(
                    "mymath:exam",
                    kwargs={"exam_id":self.exam.id, "number": number}),
                data={f"question_{number}": question.answer + 1}) # quesion.answer+1にして不正解にする
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id":self.exam.id, "number": number}))
            # sessionの中身をチェック
            session = self.client.session
            self.assertEqual(session["exam"]["exam_id"], self.exam.id)
            self.assertEqual(session["exam"]["question_select"], {str(i): question.answer+1 for i in range(1, number+1)})
            self.assertEqual(session["exam"]["answer_correct"], {str(i): False for i in range(1, number+1)})
            response1_1 = self.client.get(
                reverse("mymath:answer",
                        kwargs={"exam_id":self.exam.id, "number": number})
            )
            self.assertContains(response1_1, f"{number}問目")
            self.assertContains(response1_1, "不正解")
            response2 = self.client.post(
                reverse("mymath:answer",
                        kwargs={"exam_id":self.exam.id, "number": number}))
            
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam",
                                                        kwargs={"exam_id": self.exam.id, "number": number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                response3 = self.client.get(reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                self.assertContains(response3, "0点")
                # response.contextで渡すcontextをチェック
                # 未ログイン時の処理でモデルオブジェクトを模した辞書が正しくわたされているかチェック
                self.assertEqual(response3.context["user_result"]["count"], "*")
                self.assertEqual(response3.context["user_result"]["score"], 0)
                self.assertEqual(response3.context["user_result"]["exam"]["id"], self.exam.id)
                self.assertEqual(response3.context["user_result"]["exam"]["title"], self.exam.title)
                self.assertFalse(response3.context["useranswers"][0]["correct"]) # Falseか確認
                self.assertEqual(response3.context["useranswers"][0]["question"]["number"], 1)
    def test_complete_exam_to_result_correct_and_uncorrect(self):
        """正解と不正解が混ざったパターン"""
        for number in range(1, 11):
            question = self.questions[number - 1]
            # 選択肢3, 4を選んで不正解になっているかをチェック
            if number == 5:
                data={f"question_{number}": 3}
            elif number == 6:
                data={f"question_{number}": 4}
            else:
                data={f"question_{number}": question.answer} # 正解を解答
            response1 = self.client.post(reverse(
                "mymath:exam",
                kwargs={"exam_id": self.exam.id, "number":number}
                ),
                data=data)
            self.assertRedirects(response1, reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            
            # sessionの中身をチェック
            session = self.client.session
            self.assertEqual(session["exam"]["exam_id"], self.exam.id)
            # 内包表記だと可読性がさがりそうなので、辞書を作成
            answer_dict = {}
            for i in range(1, number+1):
                if i == 5:
                    answer_dict[str(i)] = 3
                elif i == 6:
                    answer_dict[str(i)] = 4
                else:
                    answer_dict[str(i)] = question.answer 
            self.assertEqual(session["exam"]["question_select"], answer_dict)
            # こっちは内包表記
            self.assertEqual(session["exam"]["answer_correct"], {str(i): (i not in (5, 6)) for i in range(1, number+1)})
            response2 = self.client.post(reverse("mymath:answer", kwargs={"exam_id": self.exam.id, "number":number}))
            if number < 10:
                self.assertRedirects(response2, reverse("mymath:exam", kwargs={"exam_id": self.exam.id, "number":number+1}))
            else:
                self.assertRedirects(response2, reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                response3 = self.client.get(reverse("mymath:result", kwargs={"exam_id": self.exam.id}))
                # answerが1 で selectが1を8回行っているので正解数は8で80点になっているはず
                self.assertContains(response3, "80点")
                # response.contextで渡すcontextをチェック
                # 未ログイン時の処理でモデルオブジェクトを模した辞書が正しくわたされているかチェック
                self.assertEqual(response3.context["user_result"]["count"], "*")
                self.assertEqual(response3.context["user_result"]["score"], 80)
                self.assertEqual(response3.context["user_result"]["exam"]["id"], self.exam.id)
                self.assertEqual(response3.context["user_result"]["exam"]["title"], self.exam.title)
                self.assertTrue(response3.context["useranswers"][0]["correct"]) # 1問目は正解なのでTrue
                self.assertFalse(response3.context["useranswers"][4]["correct"]) # 5問目がFalseか確認
                self.assertFalse(response3.context["useranswers"][5]["correct"]) # 6問目がFalseか確認
                self.assertEqual(response3.context["useranswers"][0]["question"]["number"], 1)
        

               