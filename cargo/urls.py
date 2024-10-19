from django.urls import path
from . import views

urlpatterns = [
    

    path('get_cargo_cost/', views.GetCargoCost.as_view(), name='api_get_cargo_cost'),
    path('update_cargo_cost/', views.UpdateCargoCost.as_view(), name='api_update_cargo_cost'),
    

]