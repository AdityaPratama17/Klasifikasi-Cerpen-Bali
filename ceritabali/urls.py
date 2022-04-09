from django.urls import path
from ceritabali import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dokumen', views.dokumen, name="dokumen"),
    path('detail/<int:id>', views.detail, name="detail"),
    path('pengujian', views.pengujian, name="pengujian"),
    path('klasifikasi', views.klasifikasi, name="klasifikasi"),
    path('update_model', views.update_model, name="update_model"),
    path('refresh', views.refresh, name="refresh"),
]