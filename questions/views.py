from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.conf import settings
from django.http import JsonResponse
import google.generativeai as genai
import os
import re
from rest_framework.exceptions import APIException
from decouple import config
from datetime import datetime

API_KEY = config("API_KEY")
import json

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_response(prompt):
    try:
        if len(API_KEY) > 0:
            response = model.generate_content(prompt)
            print(response)
            return response.text
        else:
            raise APIException("An error occurred while generating the response1.")

    except Exception as e:
        print("Error:", e)
        raise APIException("An error occurred while generating the response.")


def parse_questions(response_text):
    questions = re.findall(r"\d+\.\s\*\*(.*?)\*\*", response_text, re.DOTALL)
    questions_dict = {
        f"q{i+1}": question.strip()
        for i, question in enumerate(questions)
        if question.strip()
    }
    return questions_dict


@api_view(["GET"])
def get_questions(request):
    try:
        domain = request.GET.get("domain")
        subdomain = request.GET.get("subdomain")

        if not subdomain:
            return JsonResponse(
                {"error": "Subdomain parameter is required"}, status=400
            )

        prompt = f"Generate 10 questions related to {subdomain}"
        res = generate_response(prompt)

        # Parse the questions and return them in the desired format
        questions_dict = parse_questions(res)
        return JsonResponse({"result": questions_dict}, status=200)

    except APIException as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


# @api_view(["POST"])
# def get_feedback(request):
#     question = request.data.get("question")
#     answer = request.data.get("answer")
#     if not question or not answer:
#         return Response(
#             {"status": "error", "message": "Both question and answer are required."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )
#     prompt = f'Provide detailed feedback and actual answer for the given answer "{answer}" to the question "{question}".  Give in json format like "feedback":"your response","actualanswer":"your response".'

#     try:
#         # Call the model to get the response
#         response = model.generate_content(prompt)

#         # Parse the response to extract feedback and the actual answer
#         feedback, actual_answer = parse_model_response(response.text)

#         return JsonResponse(
#             {
#                 "status": "success",
#                 "modelresponse": response.text,
#                 "feedback": feedback,
#                 "actualAnswer": actual_answer,
#             },
#             status=status.HTTP_200_OK,
#         )
#     except Exception as e:
#         return Response(
#             {"status": "error", "message": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
from datetime import datetime
from django.utils import timezone


# @api_view(["POST"])
# def get_feedback(request):
#     question_text = request.data.get("question")
#     answer = request.data.get("answer")
#     user_id = request.data.get("id")

#     if not question_text or not answer or not user_id:
#         return Response(
#             {
#                 "status": "error",
#                 "message": "Question, answer, and user_id are required.",
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     # Get the current date in YYYY-MM-DD format
#     submission_date = timezone.now().date()

#     try:
#         # Fetch the question from the Questions model
#      # question = Questions.objects.filter(question=question_text).first()

#         if not question:
#             return Response(
#                 {"status": "error", "message": "Question not found."},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         # Create a UserSubmission object to store the submission data
#         user_submission = UserSubmission.objects.create(
#             user_id=user_id,
#             question=question,
#             answer=answer,
#             date=submission_date,
#         )

#         # Increment the problem_count for the user on this date
#         problem_count = UserSubmission.objects.filter(
#             user_id=user_id, date=submission_date
#         ).count()

#         # Generate feedback using the model
#         prompt = f'Provide detailed feedback and actual answer for the given answer "{answer}" to the question "{question_text}".  Give in json format like "feedback":"your response","actualanswer":"your response".'
#         response = model.generate_content(prompt)

#         # Parse the model response
#         feedback, actual_answer = parse_model_response(response.text)


#         return JsonResponse(
#             {
#                 "status": "success",
#                 "modelresponse": response.text,
#                 "feedback": feedback,
#                 "actualAnswer": actual_answer,
#                 "problemCount": problem_count,  # Send the updated problem count
#             },
#             status=status.HTTP_200_OK,
#         )
#     except Exception as e:
#         return Response(
#             {"status": "error", "message": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )
@api_view(["POST"])
def get_feedback(request):
    question = request.data.get("question")
    answer = request.data.get("answer")
    user_id = request.data.get("id")

    if not question or not answer:
        return Response(
            {
                "status": "error",
                "message": "question, answer, and user_id are required.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Track the submission for the specific user
    today = timezone.now().date()
    tracker, created = SubmissionTracker.objects.get_or_create(
        user_id=user_id, date=today
    )
    tracker.submission_count += 1
    tracker.save()

    prompt = f'Provide detailed feedback and actual answer for the given answer "{answer}" to the question "{question}".  Give in json format like "feedback":"your response","actualanswer":"your response".'

    try:
        # Call the model to get the response
        response = model.generate_content(prompt)

        # Parse the response to extract feedback and the actual answer
        feedback, actual_answer = parse_model_response(response.text)

        return Response(
            {
                "status": "success",
                "modelresponse": response.text,
                "feedback": feedback,
                "actualAnswer": actual_answer,
                "submission_count": tracker.submission_count,  # Return the submission count for the user for the day
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_user_submission_data(request):
    print("kkk")
    user_id = request.query_params.get("user_id")  # Get user_id from query parameters
    if not user_id:
        return Response(
            {"status": "error", "message": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Fetch submission data for the specific user
    submission_data = SubmissionTracker.objects.filter(user_id=user_id).order_by("date")

    # Format the data for the graph
    data = {
        "dates": [entry.date.strftime("%Y-%m-%d") for entry in submission_data],
        "submission_counts": [entry.submission_count for entry in submission_data],
    }

    return JsonResponse(data, status=status.HTTP_200_OK)


def parse_model_response(response_text):
    json_str = response_text.strip("```json\n").strip("``` \n")

    try:
        response_data = json.loads(json_str)
        print(response_data)
        feedback = response_data.get("feedback", "").strip()
        actual_answer = response_data.get("actualanswer", "").strip()
        return feedback, actual_answer
    except json.JSONDecodeError as e:
        # Handle JSON parsing errors
        print(f"JSON parsing error: {e}")
        return "", ""
