from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime

from .models import Question

# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        fq = Question(pub_date=time)
        self.assertIs(fq.was_published_recently(), False)

    def test_was_published_recently_with_todays_question(self):
        time = timezone.now() - datetime.timedelta(hours=12)
        tq = Question(pub_date=time)
        self.assertIs(tq.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=30)
        oq = Question(pub_date=time)
        self.assertIs(oq.was_published_recently(), False)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        q = create_question(question_text="Past Question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [q])
    
    def test_future_question(self):
        create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_two_past_questions(self):
        q1 = create_question(question_text="Past Question 1", days=-30)
        q2 = create_question(question_text="Past Question 2", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [q2, q1])

    def test_future_and_past_question(self):
        q = create_question(question_text="Past Question", days=-30)
        create_question(question_text="Future Question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [q])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        fq = create_question(question_text="Future Question", days=5)
        response = self.client.get(reverse("polls:detail", args=(fq.id,)))
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        pq = create_question(question_text="Past Question", days=-5)
        response = self.client.get(reverse("polls:detail", args=(pq.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, pq.question_text)