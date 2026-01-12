from django.db import models
from django.contrib.auth.models import User




class Category(models.Model):
    GRADE_CHOICES = [
        ('elementary', '小学生'),
        ('junior', '中学生'),
        ('high', '高校生'),
    ]

    name = models.CharField(max_length=50)
    grade = models.CharField(
        max_length=20,
        choices=GRADE_CHOICES,
        verbose_name="学年区分",
        default='elementary',
        )

    def __str__(self):
        return f"{self.name}（{self.get_grade_display()}）"


class Exam(models.Model):
    title = models.CharField(verbose_name="テスト名",max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # 1テストを10個の問題に制限するのはviews.pyで行う
    
    def __str__(self):
        return self.title

class Question(models.Model):
    ANSWER_CHOICES = [(1, '1'), (2, '2'), (3, '3'), (4, '4')]
    
    number = models.PositiveSmallIntegerField(
        verbose_name="問題番号",
        editable=False,
        )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    select_1 = models.CharField(verbose_name="選択肢1", max_length=100)
    select_2 = models.CharField(verbose_name="選択肢2", max_length=100)
    select_3 = models.CharField(verbose_name="選択肢3", max_length=100)
    select_4 = models.CharField(verbose_name="選択肢4", max_length=100)
    answer = models.IntegerField(verbose_name="正解番号", choices=ANSWER_CHOICES)
    answer_text = models.TextField(verbose_name="解答の解説", blank=True)
    
    #exam_image = models.ImageField(upload_to="questions/exam/", blank=True, null=True)
    #answer_image = models.ImageField(upload_to="questions/answer/", blank=True, null=True)
    #画像導入用
    class Meta:
        ordering = ["number"]
        constraints = [models.UniqueConstraint(
            fields=["exam", "number"],
            name="unique_exam_question_number",
        )]
    # データベースにユニーク制約を作成 ここでは"exam", "number"をユニークなセットにする
    def save(self, *args, **kwargs):
        # number を連番で取得する
        if self.pk is None:
            last = Question.objects.filter(
                exam=self.exam
            ).order_by("-number").first()
            if not last:
                self.number =1
            else:
                self.number = last.number + 1
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"問{self.number}: {self.text[:30]}"



class UserTestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name="回数", default=0)
    score = models.IntegerField(verbose_name="点数", default=0)
    submitted = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.exam.title} ({self.count}回目)"
    
    class Meta:
        ordering = ('-count', '-submitted')
        unique_together = ('user', 'exam', 'count')
    
class UserQuestionSelect(models.Model):
    test_result = models.ForeignKey(UserTestResult, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    select = models.IntegerField(verbose_name="解答")
    correct = models.BooleanField(verbose_name="")

    class Meta:
        unique_together = ('test_result', 'question')