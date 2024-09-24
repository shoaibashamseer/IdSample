from django.conf.urls.static import static
from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
        path('', views.generate_id_card, name='generate_id_card'),
        path('success/', views.modified_id_card, name='success'),
        path('download-pdf/<str:emp_id>/', views.download_id_card_pdf, name='download_id_card_pdf'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
