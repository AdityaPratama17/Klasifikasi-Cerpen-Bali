from django.urls import path
from ceritabali import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dokumen', views.dokumen, name="dokumen"),
    path('detail/<int:id>', views.detail, name="detail"),
    path('refresh', views.refresh, name="refresh"),
    path('pengujian', views.pengujian, name="pengujian"),
    path('test', views.test, name="test"),
]