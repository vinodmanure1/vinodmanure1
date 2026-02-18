"""
Student-facing views for taking tests.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Test, TestQuestion


def test_list(request):
    """
    Display list of available tests.
    """
    tests = Test.objects.filter(is_active=True)
    return render(request, 'assessments/test_list.html', {'tests': tests})


def take_test(request, test_id):
    """
    Display test interface for students to take the test.
    """
    test = get_object_or_404(Test, id=test_id, is_active=True)
    test_questions = TestQuestion.objects.filter(test=test).select_related('question').order_by('order')
    
    return render(request, 'assessments/take_test.html', {
        'test': test,
        'test_questions': test_questions,
    })


def test_result(request, attempt_id):
    """
    Display test results after submission.
    """
    from .models import Attempt
    attempt = get_object_or_404(Attempt, id=attempt_id)
    
    return render(request, 'assessments/test_result.html', {
        'attempt': attempt,
    })
