from io import StringIO
from django.http import HttpResponse
import pandas as pd
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from analytics.models import ProductData
from analytics.serializers import LoginSerializer, SignUpSerializer


# View for user signup
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Handle user signup.

    This view accepts a POST request with `username` and `password`. It validates
    the data using SignUpSerializer and creates a new user if valid.

    Returns:
        - HTTP 201 Created: If the user is created successfully.
        - HTTP 400 Bad Request: If there are validation errors.
    """
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.signup_user(validated_data=serializer.validated_data)
        return Response({"message": f"User `{username}` created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for user login
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Handle user login.

    This view accepts a POST request with `username` and `password`. It validates
    the data using LoginSerializer and returns a JWT token if valid.

    Returns:
        - HTTP 200 OK: If login is successful.
        - HTTP 400 Bad Request: If there are validation errors.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.login_user(validated_data=serializer.validated_data)
        return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to generate summary report
@api_view(["GET"])
def get_summary_report(request):
    """
    Generate and return a summary report as a CSV file.

    This view fetches product data from the database, calculates revenue,
    identifies the top-selling product in each category, and returns a
    CSV file containing the summary report.

    Returns:
        - HTTP 200 OK: CSV file containing the summary report.
    """
    data = ProductData.objects.values()
    df = pd.DataFrame(data)

    # Calculate revenue for each product
    df["revenue"] = df["price"] * df["quantity_sold"]

    # Group by category and product name, then aggregate quantity_sold and revenue
    category_df = df.groupby(["category", "product_name"]).agg({"quantity_sold": "sum", "revenue": "sum"}).reset_index()
    category_df.sort_values(by=["category", "revenue"], ascending=[True, False], inplace=True)

    # Calculate total revenue per category
    category_df["total_revenue"] = category_df.groupby("category")["revenue"].transform("sum")

    # Identify the top-selling product in each category
    top_products_df = category_df.groupby("category").first().reset_index()

    # Prepare the final DataFrame to be saved as CSV
    final_df = top_products_df[["category", "total_revenue", "product_name", "quantity_sold"]]
    final_df.rename(columns={"product_name": "top_product", "quantity_sold": "top_product_quantity_sold"}, inplace=True)

    # Save to a string buffer instead of a file
    buffer = StringIO()
    final_df.to_csv(buffer, index=False)
    buffer.seek(0)

    # Return the CSV file as a download
    response = HttpResponse(buffer, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=summary_report.csv'
    
    return response

    



