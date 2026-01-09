from django.shortcuts import redirect, render
from .models import Exam, Question, UserQuestionSelect, UserTestResult

def exam(request, exam_id, number=1):
    # /exam/<exam_id>/1~ exam/<exam_id>/10まで
    # を処理する
    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam).order_by("number")
    question = questions[number-1] # number=1 としているので先頭のインデックを0にする
    if request.method == "POST": # POSTの処理
        user_select = int(request.POST.get(f"question_{question.number}"))
        # ユーザーの解答を取得する
        if user_select == question.answer:
            correct = True
        else:
            correct = False
        # 正解の判定
        last_result = UserTestResult.objects.filter(user=request.user, test=exam).order_by('-count').first()
        next_count = last_result.count + 1
        # UserTestResult からユーザーのこのテストに回数をチェックし、count+1する
        usertestresult = UserTestResult.objects.create(
            user=request.user,
            test=exam,
            count=next_count)
        # 今回のテストのUsertestResultを作成し,それに紐づいている
        # UserQuestionSelectオブジェクトを作成し、解答を記録する
      
        useranswer = UserQuestionSelect.objects.create(
            user=usertestresult,
            question=question,
            select=user_select,
            correct=correct
            )
        useranswer.save()
        if number < 10:
            return redirect("exam", exam_id=exam_id, number=number+1)
            # number = number + 1 にして次の問題をジャンプできるようにする
        elif number == 10:
            # number が10に到達するとテストが終了なので,点数を計算して、resultページにリダイレクトする
            useranswers = UserQuestionSelect.objects.filter(
                user=usertestresult)
            correct_num = 0
            for user_a in useranswers:
                correct_num += user_a.correct
            score = correct_num * 10
            # 正解数x10 で点数をだす
            usertestresult.score = score
            usertestresult.save()

            return redirect("result", exam_id=exam_id)
        
    return render(request, "mymath/exam.html",
                  {"question": question,
                   "exam": exam})    




def mymath(request):
    exams = Exam.objects.all()
    
    return render(request, "mymath/mymath.html", {"exams": exams})

def exam(request, exam_id):
# テストページの処理、問題を提示、答えを選択、解答を表示(正解、不正解の表示)（ユーザーの解答を記録）、次の問題へ
    exam = Exam.objects.get(id=exam_id)
    questions = Question.objects.filter(exam=exam).order_by("number") # 問題１０問を取得する
    current_question = int(request.GET.get("current_question", 1)) # 何問目かを取得
    question = questions[current_question-1]
    
    if request.method == "POST": # POSTの処理
        user_select = int(request.POST.get(f"question_{question.number}"))
        if user_select == question.answer:
            correct = True
        else:
            correct = False
        
        last_result = UserTestResult.objects.filter(user=request.user, test=exam).order_by('-count').first()
        next_count = last_result.count + 1

        usertestresult = UserTestResult.objects.create(
            user=request.user,
            test=exam,
            count=next_count)
              
        useranswer = UserQuestionSelect.objects.create(
            user=usertestresult,
            question=question,
            select=user_select,
            correct=correct
            )
        useranswer.save()
        if current_question < 10:
            return redirect(f"/exam/{exam_id}/?current_question={current_question + 1}")
        
        elif current_question == 10:
            useranswers = UserQuestionSelect.objects.filter(
                user=usertestresult)
            correct_num = 0
            for user_a in useranswers:
                correct_num += user_a.correct
            score = correct_num * 10
            usertestresult.score = score
            usertestresult.save()

            return redirect("result", exam_id=exam_id)
    return render(request, "mymath/exam.html",
                 {"question": question,
                  "exam": exam})

def result(request, exam_id):
    exam = Exam.objects.get(id=exam_id)
    user_result = UserTestResult.objects.filter(
            user=request.user,
            test=exam) # model の方でorder しておく
    user_selects = UserQuestionSelect.objects.filter(
        user=user_result,)  
    return render(request, "mymath/result.html",
                {"user_result": user_result,
                 "user_selects":user_selects})