from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.conf import settings
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@api_view(["GET", "POST"])
def emails(request):
    try:
        if request.method == "POST":
            # Extract data from POST request body
            name = request.data.get("name")
            message = request.data.get("message")
            email = request.data.get("email")

            # Validate required fields
            if not message:
                return Response(
                    {"detail": "Message is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not email:
                return Response(
                    {"detail": "Email is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Serialize and validate data
            data = {"name": name, "message": message, "email": email}
            serializer = EmailSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle GET request: List all emails
        elif request.method == "GET":
            emails = Email.objects.all()
            page = request.GET.get("page", 1)
            paginator = Paginator(emails, 5)  # Show 10 emails per page

            try:
                emails_page = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver the first page
                emails_page = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results
                emails_page = paginator.page(paginator.num_pages)

            serializer = EmailSerializer(emails_page, many=True)

            # Adding pagination metadata in the response
            response_data = {
                "total_pages": paginator.num_pages,
                "current_page": emails_page.number,
                "total_items": paginator.count,
                "results": serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the exception (optional) and return a generic error message
        print(f"Error occurred: {e}")
        return Response(
            {"detail": e},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
def delete_email(request, id):
    try:
        email = Email.objects.get(id=id)
        email.delete()
        return Response(
            {"detail": "Email deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Email.DoesNotExist:
        return Response(
            {"detail": "Email not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
