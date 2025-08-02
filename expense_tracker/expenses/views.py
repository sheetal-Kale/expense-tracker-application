from django.shortcuts import render

# Create your views here.

# expenses/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Expense

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)



# expenses/views.py (continued)
from django.shortcuts import get_object_or_404
from .forms import ExpenseForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
import json
from datetime import datetime, timedelta
from django.utils import timezone


@login_required
def dashboard(request):
    # Get expenses for the current user
    expenses = Expense.objects.filter(user=request.user).order_by('-created_at')

    # Calculate total expenses
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate category-wise expenses for the pie chart
    categories = dict(Expense.CATEGORY_CHOICES)
    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    # Prepare data for the chart
    chart_labels = []
    chart_data = []
    for item in category_data:
        chart_labels.append(categories[item['category']])
        chart_data.append(float(item['total']))

    context = {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/add_expense.html', {'form': form})


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/edit_expense.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return render(request, 'expenses/delete_expense.html', {'expense': expense})


# API Views
from rest_framework import viewsets
from .serializers import ExpenseSerializer
from .models import Expense


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)