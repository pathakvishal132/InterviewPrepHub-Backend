from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CompanyQuestion, Company
from .serializers import CompanyQuestionSerializer, CompanySerializer
from django.core.paginator import Paginator


@api_view(["GET", "POST", "PUT", "DELETE"])
def company_question_handler(request, company_question_id=None):
    if request.method == "POST":
        serializer = CompanyQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "GET":
        if company_question_id:
            try:
                company_question = CompanyQuestion.objects.get(id=company_question_id)
                serializer = CompanyQuestionSerializer(company_question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CompanyQuestion.DoesNotExist:
                return Response(
                    {"detail": "Company question not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            company_questions = CompanyQuestion.objects.all()
            serializer = CompanyQuestionSerializer(company_questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        try:
            company_question = CompanyQuestion.objects.get(id=company_question_id)
        except CompanyQuestion.DoesNotExist:
            return Response(
                {"detail": "Company question not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Update the question
        serializer = CompanyQuestionSerializer(
            company_question, data=request.data, partial=True
        )  # partial=True allows updating specific fields
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        try:
            company_question = CompanyQuestion.objects.get(id=company_question_id)
        except CompanyQuestion.DoesNotExist:
            return Response(
                {"detail": "Company question not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete the question
        company_question.delete()
        return Response(
            {"detail": "Company question deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["GET"])
def get_company(request):
    if request.method == "GET":
        company_names = Company.objects.all()

        # Pagination logic
        page = request.GET.get("page")
        paginator = Paginator(company_names, 8)

        try:
            companies_page = paginator.page(page)
        except:
            return Response(
                {"detail": "Invalid page number."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanySerializer(companies_page.object_list, many=True)

        # Preparing response data
        response_data = {
            "companies": serializer.data,
            "total_pages": paginator.num_pages,
            "current_page": companies_page.number,
            "total_companies": paginator.count,
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_company_questions_by_id(request, company_id):
    if request.method == "GET":

        company_questions = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values("question", "answer", "description", "role")
            .distinct()
        )
        if not company_questions.exists():
            return Response(
                {"detail": "No questions found for this company."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = request.GET.get("page")
        paginator = Paginator(company_questions, 1)

        try:
            questions_page = paginator.page(page)
        except:
            return Response(
                {"detail": "Invalid page number."}, status=status.HTTP_400_BAD_REQUEST
            )
        serialized_data = list(questions_page.object_list)
        response_data = {
            "questions": serialized_data,
            "total_pages": paginator.num_pages,
            "current_page": questions_page.number,
            "total_questions": paginator.count,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def search_company(request):
    if request.method == "GET":

        word = request.GET.get("word")

        if not word:
            comp = Company.objects.all()
            page = request.GET.get("page")
            paginator = Paginator(comp, 8)

            try:
                companies_page = paginator.page(page)
            except:
                return Response(
                    {"detail": "Invalid page number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = CompanySerializer(companies_page.object_list, many=True)
            response_data = {
                "companies": serializer.data,
                "total_pages": paginator.num_pages,
                "current_page": companies_page.number,
                "total_companies": paginator.count,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        comp = Company.objects.filter(name__icontains=word).distinct()
        if not comp.exists():
            return Response(
                {"detail": "No companies found matching the search word."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = request.GET.get("page")
        paginator = Paginator(comp, 2)

        try:
            company_page = paginator.page(page)
        except:
            return Response(
                {"detail": "Invalid page number."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CompanySerializer(company_page.object_list, many=True)
        response_data = {
            "companies": serializer.data,
            "total_pages": paginator.num_pages,
            "current_page": company_page.number,
            "total_companies": paginator.count,
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def search_question(request):
    if request.method == "GET":
        word = request.GET.get("word")  # Get 'word' from query parameters
        if not word:
            return Response(
                {"detail": "Search word is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Search for questions and answers containing the search word
        questions = (
            CompanyQuestion.objects.filter(question__icontains=word).distinct()
            | CompanyQuestion.objects.filter(answer__icontains=word).distinct()
        )

        if not questions.exists():
            return Response(
                {"detail": "No matching questions found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = request.GET.get("page", 1)
        paginator = Paginator(questions, 1)  # Paginate with 2 items per page

        try:
            questions_page = paginator.page(page)
        except:
            return Response(
                {"detail": "Invalid page number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize the paginated data
        serializer = CompanyQuestionSerializer(questions_page.object_list, many=True)

        response_data = {
            "questions": serializer.data,
            "total_pages": paginator.num_pages,
            "current_page": questions_page.number,
            "total_questions": paginator.count,
        }

        return Response(response_data, status=status.HTTP_200_OK)
