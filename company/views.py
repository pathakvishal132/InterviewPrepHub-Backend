from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import CompanyQuestion, Company, CompanyReview
from .serializers import (
    CompanyQuestionSerializer,
    CompanySerializer,
    CompanyReviewSerializer,
)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@api_view(["GET", "POST", "PUT", "DELETE"])
def company_question_handler(request, company_question_id=None):
    if request.method == "POST":
        if isinstance(request.data, list):
            serializer = CompanyQuestionSerializer(data=request.data, many=True)
        else:
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


@api_view(["GET", "POST"])
def company_list_create(request):
    if request.method == "GET":
        company_names = Company.objects.all().order_by("id")
        page = request.GET.get("page", 1)
        paginator = Paginator(company_names, 8)

        try:
            companies_page = paginator.page(page)
        except PageNotAnInteger:
            # Return null in case of invalid page format
            return Response(
                {"companies": None, "detail": "Invalid page number format."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except EmptyPage:
            # Return null in case of out-of-range page number
            return Response(
                {"companies": None, "detail": "Page number out of range."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize and return the data if successful
        serializer = CompanySerializer(companies_page.object_list, many=True)
        response_data = {
            "companies": serializer.data,
            "total_pages": paginator.num_pages,
            "current_page": companies_page.number,
            "total_companies": paginator.count,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def company_detail(request, pk):
    try:
        company = Company.objects.get(pk=pk)
    except Company.DoesNotExist:
        return Response(
            {"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "PUT":
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        if not company:
            return Response(
                {"detail": "Company question not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        else:
            company.delete()
            return Response(
                {"detail": "Company deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )


@api_view(["GET"])
def get_company_questions_by_id(request, company_id):
    if request.method == "GET":

        company_questions = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values(
                "id",
                "question",
                "answer",
                "description",
                "role",
                "min_experience",
                "max_experience",
                "level",
            )
            .distinct()
        )
        if not company_questions.exists():
            return Response(
                {"detail": "No questions found for this company."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = request.GET.get("page")
        paginator = Paginator(company_questions, 5)

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
def get_other_details(request):
    """
    Fetch levels, roles, experiences, and descriptions for a specific company ID.
    """
    company_id = request.query_params.get(
        "company_id"
    )  # Get company_id from query parameters

    if not company_id:
        return Response(
            {"error": "Company ID is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Query the database for levels, roles, experiences, and descriptions of the given company_id
        levels = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values_list("level", flat=True)
            .distinct()
        )
        roles = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values_list("role", flat=True)
            .distinct()
        )
        min_experiences = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values_list("min_experience", flat=True)
            .distinct()
        )
        max_experiences = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values_list("max_experience", flat=True)
            .distinct()
        )
        descriptions = (
            CompanyQuestion.objects.filter(companies__id=company_id)
            .values_list("description", flat=True)
            .distinct()
        )

        # Check if any data is found
        if not (levels or roles or min_experiences or max_experiences or descriptions):
            return Response(
                {"message": "No details found for the given company ID."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "company_id": company_id,
                "levels": list(levels),
                "roles": list(roles),
                "min_experiences": list(min_experiences),
                "max_experiences": list(max_experiences),
                "descriptions": list(descriptions),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator


@api_view(["POST"])
def filter_company_questions(request):
    level = request.data.get("level", None)
    role = request.data.get("role", None)
    minExperience = request.data.get("min_experience", None)
    maxExperience = request.data.get("max_experience", None)
    description = request.data.get("description", None)

    # Initialize the queryset to all CompanyQuestions
    queryset = CompanyQuestion.objects.all()

    # Apply filters if they are provided
    if level:
        queryset = queryset.filter(level__iexact=level)

    if role:
        queryset = queryset.filter(role__iexact=role)

    if minExperience is not None and maxExperience is not None:
        queryset = queryset.filter(
            min_experience__lte=maxExperience, max_experience__gte=minExperience
        )

    if description:
        queryset = queryset.filter(description__icontains=description)

    # If no questions match, return a message
    if not queryset.exists():
        return Response(
            {
                "questions": [],
                "total_pages": 0,
                "current_page": 1,
                "total_questions": 0,
            },
            status=status.HTTP_200_OK,
        )

    # Handle pagination
    page = request.GET.get("page", 1)  # Get the page number from the query parameters
    paginator = Paginator(
        queryset, 10
    )  # Set page size to 10 (can be adjusted as needed)

    # If the page number exceeds the total pages, set to the first page
    if int(page) > paginator.num_pages:
        page = 1

    try:
        questions_page = paginator.page(page)
    except Exception as e:
        return Response(
            {"detail": "Invalid page number."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Serialize the paginated results
    serializer = CompanyQuestionSerializer(questions_page.object_list, many=True)

    # Prepare response data
    response_data = {
        "questions": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": questions_page.number,
        "total_questions": paginator.count,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def search_question(request):
    if request.method == "GET":
        word = request.GET.get("word")
        if not word:
            return Response(
                {"detail": "Search word is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        questions = (
            CompanyQuestion.objects.filter(question__icontains=word)
            | CompanyQuestion.objects.filter(answer__icontains=word)
            | CompanyQuestion.objects.filter(description__icontains=word)
            | CompanyQuestion.objects.filter(level__icontains=word)
            | CompanyQuestion.objects.filter(role__icontains=word)
        ).distinct()
        if not questions.exists():
            return Response(
                {"detail": "No matching questions found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        page = request.GET.get("page", 1)
        paginator = Paginator(questions, 1)

        try:
            questions_page = paginator.page(page)
        except:
            return Response(
                {"detail": "Invalid page number."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CompanyQuestionSerializer(questions_page.object_list, many=True)
        response_data = {
            "questions": serializer.data,
            "total_pages": paginator.num_pages,
            "current_page": questions_page.number,
            "total_questions": paginator.count,
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_company_reviews(request):
    company_id = request.GET.get("company_id")
    if not company_id:
        return Response(
            {"detail": "Company ID is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    reviews = CompanyReview.objects.filter(company_id=company_id)
    if not reviews.exists():
        return Response(
            {"detail": "No reviews found for this company."},
            status=status.HTTP_404_NOT_FOUND,
        )

    page = request.GET.get("page", 1)
    paginator = Paginator(reviews, 6)

    try:
        reviews_page = paginator.page(page)
    except:
        return Response(
            {"detail": "Invalid page number."}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = CompanyReviewSerializer(reviews_page.object_list, many=True)

    response_data = {
        "reviews": serializer.data,
        "total_pages": paginator.num_pages,
        "current_page": reviews_page.number,
        "total_reviews": paginator.count,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def post_company_review(request):
    serializer = CompanyReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
