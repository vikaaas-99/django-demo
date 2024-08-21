from django.urls import path
from .views import *


app_name = "analytics"


urlpatterns = [
    path("signup/", signup, name="signup"),  # URL pattern for user signup view.
    path("login/", login, name="login"),  # URL pattern for user login view.

    path("get-summary-report/", get_summary_report, name="get_summary_report"),  
    # URL pattern to fetch the summary report.
]