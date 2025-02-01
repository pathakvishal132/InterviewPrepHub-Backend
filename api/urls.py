from home.views import emails, delete_email
from django.contrib import admin
from django.urls import path
from questions.views import get_questions, get_feedback, get_user_submission_data
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from loginsignup.views import (
    RegisterView,
    LoginView,
    DashboardView,
    upload_image,
    get_image,
)
from company.views import (
    company_question_handler,
    company_list_create,
    get_company_questions_by_id,
    search_company,
    search_question,
    company_detail,
    get_other_details,
    filter_company_questions,
)


# from loginsignup.views import signup, login_view, logout_view

urlpatterns = [
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
    path("get_company/", company_list_create),
    path("company/<int:company_id>/questions/", get_company_questions_by_id),
    path("search_company/", search_company, name="search-company"),
    path("search_question/", search_question, name="search-question"),
    path("emails/", emails),
    path("delete/emails/<int:id>/", delete_email, name="delete_email"),
    path("companies/<int:pk>/", company_detail, name="company-detail"),
    path("get_other_details/", get_other_details, name="get_other_details"),
    path(
        "filter_company_questions/",
        filter_company_questions,
        name="filter_company_questions",
    ),
    path("upload-image/", upload_image, name="upload_image"),
    path("get-image/<str:image_id>/", get_image, name="get_image"),
    path(
        "get-user-submission-data/",
        get_user_submission_data,
        name="get_user_submission_data",
    ),
]
