from rest_framework import serializers
from .models import CompanyQuestion, Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name"]


class CompanyQuestionSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True)

    class Meta:
        model = CompanyQuestion
        fields = [
            "id",
            "companies",
            "level",
            "question",
            "answer",
            "date_of_creation",
            "description",
            "role",
            "min_experience",
            "max_experience",
        ]

    def create(self, validated_data):
        companies_data = validated_data.pop("companies")
        question = CompanyQuestion.objects.create(**validated_data)

        for company_data in companies_data:
            company, created = Company.objects.get_or_create(name=company_data["name"])
            question.companies.add(company)

        return question
