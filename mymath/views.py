from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from .models import Exam, Question, UserQuestionSelect, UserTestResult


def index(request):
    exams = Exam.objects.all()
    
    return render(request, "mymath/index.html",
                 {"exams": exams})

def exam(request, exam_id, number=1):
    # /exam/<exam_id>/1~ exam/<exam_id>/10までのexamをできるようにする。
    # /exam/<exam_id>/<number>となるようにurls.pyも指定する
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam).order_by("number")
    total = len(questions) # 問題数を取得
    if not (1 <= number <= total):
        raise Http404("問題番号が正しくありません。")
    question = questions[number-1] # number=1 としているので先頭のインデックを0にする
    
        
    # 最初に未ログインユーザーの処理を行う
    # request.session["exam"] = {"exam_id":1,
    #                            "question_select": {1:1, 2:1, ... ,10:2},
    #                            "answer_correct": {1:True, 2:False, ... , 10, True}}
    # このような形で保存                          
    if not request.user.is_authenticated:
        if number == 1:
            # 一問目のときにセッション作成
            session_exam = request.session.setdefault(
                "exam", {
                    "exam_id": exam_id,
                    "question_select": {},
                    "answer_correct": {},
                        })
        if request.method == "POST":
            user_select_str = request.POST.get(f"question_{question.number}")
            if not user_select_str:
                messages.warning(request, "番号をえらんでから次へを押してください")
                return redirect("mymath:exam", exam_id=exam_id, number=number)
            user_select = int(user_select_str)
            session_exam = request.session.get("exam")
            session_exam["question_select"][str(number)] = user_select
            if user_select == question.answer:
                session_exam["answer_correct"][str(number)] = True
            else:
                session_exam["answer_correct"][str(number)] = False
            # DjangoのセッションはJSONでシリアライズ化されて保存されるので、
            # キーのnumber が 1 のとき "1"として保存される。
            # 値を取り出すときはstr(number)としなければKeyErrorが発生する。
            # ここでは保存するときも一応str(number)として保存
            
            request.session["exam"] = session_exam
            # print(session_exam)
            # print(number)
            # print(session_exam["question_select"])
            # print(session_exam["answer_correct"])
            return redirect("mymath:answer", exam_id=exam_id, number=number)
    

    else:  # ログインユーザーの処理
        if number == 1: # numberが1のときつまり第一問目のときはUserTestResultオブジェクトを作成する
            last_result = UserTestResult.objects.filter(
                user=request.user,
                exam=exam,).order_by('-count').first() # userがexamを最後に行ったデータをさがし、あったとき、なかった時の処理を書く
            if last_result:
                next_count = last_result.count + 1
            else:
                next_count = 1
            usertestresult = UserTestResult.objects.create(
                    user=request.user,
                    exam=exam,
                    count=next_count)
            request.session["current_usertestresult_id"] = usertestresult.id # セッションに保存
        else:
            usertestresult = get_object_or_404(UserTestResult, id=request.session.get("current_usertestresult_id"))
                
        if request.method == "POST": # POSTの処理
            user_select_str = request.POST.get(f"question_{question.number}")
            # ここでint(request.POST.get(f"question_{question.number}"))とすると
            # 選択しないでpostするとint(NoneType)でTypeErrorが起きるので、まずはstrで取得して
            # 未選択時の処理をおこなう
            if not user_select_str:
                messages.warning(request, "番号をえらんでから次へを押してください")
                return redirect("mymath:exam", exam_id=exam_id, number=number)
            user_select = int(user_select_str)
            # ユーザーの解答を取得する
            if user_select == question.answer:
                correct = True
            else:
                correct = False
            # 正解の判定
            # UserQuestionSelectオブジェクトを作成し、解答を記録する
            UserQuestionSelect.objects.get_or_create(
                test_result=usertestresult,
                question=question,
                defaults={'select': user_select, 'correct': correct}
                )
            # UserQuestionSelectは問題ごとに作成されるが、get_or_create() で２重回答防止になる
            return redirect("mymath:answer", exam_id=exam_id, number=number)
        
    return render(request, "mymath/exam.html",
                  {"question": question,
                   "exam": exam})

def answer(request, exam_id, number):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = Question.objects.filter(exam=exam) #examの問題10個をリストとしてquestionsとして取得
    total = len(questions)
    if not (1 <= number <= total): # exam()のときと同様に処理する
        raise Http404("問題番号がただしくありません。")
    question = questions[number - 1] # number=1 なのでnumber-1としてインデックスで問題を取得
    # 未ログインユーザーの処理を先に行う
    if not request.user.is_authenticated:
        session_exam = request.session.get("exam")
        qs = session_exam.get("question_select", {})
        ac = session_exam.get("answer_correct", {})
        
        if (not session_exam 
            or str(number) not in qs
            or str(number) not in ac
            ):
            return redirect("mymath:exam", exam_id=exam_id, number=number)
        useranswer = {
            "select": session_exam["question_select"][str(number)],
            "correct": session_exam["answer_correct"][str(number)],
        }
        # DjangoのセッションはJSONとしてシリアライズ化され、キーは文字列として保存される
        # 値を取り出すときはstr(number)としなければKeyErrorが発生する。
        
        if request.method == "POST":
            if number < total:
                # number = number + 1 として次の試験にリダイレクト。number==10でresultにリダイレト
                return redirect("mymath:exam", exam_id=exam_id, number= number + 1)
            if number == total:
                return redirect("mymath:result", exam_id=exam_id)
        

    else: # ログインユーザーの処理
        result_id = request.session.get("current_usertestresult_id")
        user_result = get_object_or_404(UserTestResult, id=result_id)
        useranswer = get_object_or_404(
            UserQuestionSelect,
            test_result=user_result,
            question=question)
        if request.method == "POST":
            if number < total:
                # number = number + 1 として次の試験にリダイレクト。number==10でresultにリダイレト
                return redirect("mymath:exam", exam_id=exam_id, number= number + 1)
            if number == total:
                return redirect("mymath:result", exam_id=exam_id)
        
    return render(request, "mymath/answer.html",
            {"question": question,
            "useranswer": useranswer})


def result(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    # 未ログインユーザーの処理
    if not request.user.is_authenticated:
        session_exam = request.session["exam"]
        if not session_exam:
            redirect("mymath:exam", exam_id=exam_id, number=1)
        correct_num = 0
        for _, correct in session_exam["answer_correct"].items():
            correct_num += int(correct)
        score = correct_num * 10
        # user_result をテンプレートにあわせて作成する。user_result.exam.idなども対応できるようにネストで作成する。
        user_result = {
            "count": "*",
            "score": score,
            "exam": {
                "id": exam_id,
                "title": exam.title}}
        # useranswers = [{"number":1, "select":1, "correct": True}, {}, ..., {}]
        # useranswer も同様にuseranswer.question.numberをネストで作成。
        # sessionのキーはstrになっていることに注意
        useranswers = []
        for i in range(1, 11):
            useranswers.append({
                "correct": session_exam["answer_correct"][str(i)],
                "question":{
                    "number":i}
                })
        return render(request, "mymath/result.html",
                {"user_result": user_result,
                 "useranswers":useranswers})

    else: # ログインユーザー用の処理
        user_result = get_object_or_404(UserTestResult, id=request.session.get("current_usertestresult_id"))
            
        useranswers = UserQuestionSelect.objects.filter(
            test_result=user_result,)
        correct_num = 0
        for useranswer in useranswers:
            correct_num += int(useranswer.correct) # 正解数
        score = correct_num * 10 # 得点
        user_result.score = score
        user_result.save()
        return render(request, "mymath/result.html",
                {"user_result": user_result,
                 "useranswers":useranswers})

