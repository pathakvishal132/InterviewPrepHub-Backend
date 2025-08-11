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
from datetime import datetime
from django.utils import timezone
import json

API_KEY = config("API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_response(prompt):
    try:
        if len(API_KEY) > 0:
            response = model.generate_content(prompt)
            return response.text
        else:
            raise APIException("An error occurred while generating the response1.")
    except Exception as e:
        raise APIException("An error occurred while generating the response.")


def parse_questions_from_json_block(response_text):
    try:
        if response_text.strip().startswith("```"):
            response_text = (
                response_text.strip().lstrip("```json").rstrip("```").strip()
            )
        json_data = json.loads(response_text)
        questions_list = json_data.get("questions", [])

        return {
            f"q{i + 1}": q["question"]
            for i, q in enumerate(questions_list)
            if "question" in q
        }

    except json.JSONDecodeError as e:
        print("Failed to parse JSON response:", e)
        return {}
    except Exception as ex:
        print("Unexpected error while parsing Gemini response:", ex)
        return {}


@api_view(["GET"])
def get_questions(request):
    try:
        domain = request.GET.get("domain", "").strip()
        subdomain = request.GET.get("subdomain", "").strip()
        if not subdomain:
            return JsonResponse(
                {"error": "Subdomain parameter is required"}, status=400
            )
        if not domain:
            domain = "general"
        prompt = (
            f"You are a senior {domain} interview expert. "
            f"Generate 10 JavaScript-style interview questions focusing on **'{subdomain}'**. "
            f"Return questions in this strictly valid JSON format:\n\n"
            f'{{"questions":[{{"id":1,"question":"..."}},...]}}\n\n'
            f"Only return the JSON. Do not include any explanation or markdown formatting."
        )
        gemini_response = generate_response(prompt)
        questions_dict = parse_questions_from_json_block(gemini_response)
        return JsonResponse({"result": questions_dict}, status=200)
    except APIException as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        print("Unexpected Exception:", e)
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


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
    today = timezone.now().date()
    tracker, created = SubmissionTracker.objects.get_or_create(
        user_id=user_id, date=today
    )
    tracker.submission_count += 1
    tracker.save()
    prompt = f'Provide detailed feedback and actual answer for the given answer "{answer}" to the question "{question}".  Give in json format like "feedback":"your response","actualanswer":"your response".'
    try:
        response = model.generate_content(prompt)
        feedback, actual_answer = parse_model_response(response.text)
        return Response(
            {
                "status": "success",
                "modelresponse": response.text,
                "feedback": feedback,
                "actualAnswer": actual_answer,
                "submission_count": tracker.submission_count,
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
    user_id = request.query_params.get("user_id")
    if not user_id:
        return Response(
            {"status": "error", "message": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    submission_data = SubmissionTracker.objects.filter(user_id=user_id).order_by("date")
    data = {
        "dates": [entry.date.strftime("%Y-%m-%d") for entry in submission_data],
        "submission_counts": [entry.submission_count for entry in submission_data],
    }
    return JsonResponse(data, status=status.HTTP_200_OK)


def parse_model_response(response_text):
    json_str = response_text.strip("```json\n").strip("``` \n")
    try:
        response_data = json.loads(json_str)
        feedback = response_data.get("feedback", "").strip()
        actual_answer = response_data.get("actualanswer", "").strip()
        feedback = re.sub(r"\s+", " ", feedback)  # Normalize whitespace
        actual_answer = re.sub(r"\s+", " ", actual_answer)
        feedback = feedback.replace('"', "'")
        actual_answer = actual_answer.replace('"', "'")
        feedback = feedback.replace("\n", " ")  # Remove newlines
        actual_answer = actual_answer.replace("\n", " ")  # Remove newlines
        feedback = feedback.replace("**", "").replace("*", "")
        actual_answer = actual_answer.replace("**", "").replace("*", "")
        feedback = (
            feedback.replace("“", '"')
            .replace("’", "")
            .replace("`", "")
            .replace("```", "")
            .replace("//", "")
            .strip()
        )
        actual_answer = (
            actual_answer.replace("“", '"')
            .replace("’", "")
            .replace("`", "")
            .replace("```", "")
            .replace("//", "")
            .strip()
        )
        if not feedback or not actual_answer:
            raise ValueError("Feedback or actual answer is empty.")
        return feedback, actual_answer
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return "", ""
