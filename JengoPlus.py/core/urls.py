from django.contrib.auth import views as av
from django.urls import path
from . import views as v
urlpatterns = [
    path("", v.home, name="home"),
    path("login/", av.LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", av.LogoutView.as_view(), name="logout"),
    path("supervisor/", v.sup_home, name="sup_home"),
    path("attendance/<int:pid>/", v.attendance, name="attendance"),
    path("task/<int:tid>/<str:kind>/", v.submit, name="submit"),  # kind: expense | progress
    path("dashboard/", v.dashboard, name="dashboard"),
    path("claims/", v.claims, name="claims"),
    path("claims/<int:pk>/review/", v.review, name="review"),
    path("session/<int:pk>/", v.session_detail, name="session"),
    path("evidence/<path:p>", v.evidence, name="evidence"),
]
