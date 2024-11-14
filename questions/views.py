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

api_key = settings.API_KEY
import json

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        print(response)
        return response.text
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
        # questions_dict = {
        #     "result": {
        #         "q1": "What are the main differences between HTML, CSS, and JavaScript, and how do they work together to create a web page?",
        #         "q2": "Explain the concept of responsive design and how it is implemented in web development.",
        #         "q3": "What are the benefits of using a CSS framework like Bootstrap or Tailwind CSS?",
        #         "q4": "What are the main types of web servers, and what are their differences in terms of functionality and use cases?",
        #         "q5": "Describe the role of a Content Delivery Network (CDN) in optimizing website performance.",
        #         "q6": "What are the common security vulnerabilities in web applications, and how can they be prevented?",
        #         "q7": "Explain the difference between client-side and server-side rendering in web development.",
        #         "q8": "How do you ensure accessibility for users with disabilities when designing and developing websites?",
        #         "q9": "What are the advantages and disadvantages of using a static site generator compared to a traditional CMS platform?",
        #         "q10": "What are some emerging trends in web development, and how will they impact the future of the industry?",
        #     }
        # }
        return JsonResponse({"result": questions_dict}, status=200)

    except APIException as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        print("Error:", e)
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)


@api_view(["POST"])
def get_feedback(request):
    question = request.data.get("question")
    answer = request.data.get("answer")
    if not question or not answer:
        return Response(
            {"status": "error", "message": "Both question and answer are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    prompt = f'Provide detailed feedback and actual answer for the given answer "{answer}" to the question "{question}".  Give in json format like "feedback":"your response","actualanswer":"your response".'

    try:
        # Call the model to get the response
        response = model.generate_content(prompt)

        # Parse the response to extract feedback and the actual answer
        feedback, actual_answer = parse_model_response(response.text)

        return JsonResponse(
            {
                "status": "success",
                "modelresponse": response.text,
                "feedback": feedback,
                "actualAnswer": actual_answer,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


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
