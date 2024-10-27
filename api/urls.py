from home.views import get_speeches, create_speech
from django.contrib import admin
from django.urls import path
from questions.views import get_questions, get_feedback
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from loginsignup.views import RegisterView, LoginView, DashboardView
from company.views import (
    company_question_handler,
    get_company,
    get_company_questions_by_id,
    search_company,
    search_question,
)

# from loginsignup.views import signup, login_view, logout_view

urlpatterns = [
    path("get_speeches/", get_speeches),
    path("create_speech/", create_speech),
    path("get_questions/", get_questions),
    path("get_feedback/", get_feedback),
    #     path("signup/", signup),
    #     path("login/", login_view),
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/dashboard/", DashboardView.as_view()),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("company/", company_question_handler),
    path(
        "company/<int:company_question_id>/",
        company_question_handler,
        name="company_question_detail",
    ),
    path("get_company/", get_company),
    path("company/<int:company_id>/questions/", get_company_questions_by_id),
    path("search_company/", search_company, name="search-company"),
    path("search_question/", search_question, name="search-question"),
]
